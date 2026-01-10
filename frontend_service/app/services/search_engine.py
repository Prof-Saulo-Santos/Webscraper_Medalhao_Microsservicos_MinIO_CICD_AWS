import streamlit as st
import pandas as pd
import boto3
import json
from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
from app.core.config import settings


class SearchEngine:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.tokenizer = None
        self.model = None
        self.df = pd.DataFrame()

    @st.cache_resource
    def load_model(_self):
        """Carrega o modelo BERT para memória (Singleton)."""
        tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
        model = AutoModel.from_pretrained(settings.MODEL_NAME)
        return tokenizer, model

    @st.cache_data
    def load_data(_self):
        """Baixa TODOS os JSONs da Silver e cria um DataFrame."""
        # 1. Listar objetos
        try:
            response = _self.s3.list_objects_v2(Bucket=settings.S3_BUCKET_SILVER)
        except Exception:
            return pd.DataFrame()

        if "Contents" not in response:
            return pd.DataFrame()

        data = []
        # 2. Ler cada JSON (Para prod, usar Parquet é melhor!)
        for obj in response["Contents"]:
            key = obj["Key"]
            file_obj = _self.s3.get_object(Bucket=settings.S3_BUCKET_SILVER, Key=key)
            content = json.loads(file_obj["Body"].read())
            data.append(content)

        return pd.DataFrame(data)

    def get_bronze_count(self) -> int:
        """Retorna a contagem de objetos na camada Bronze (sem baixar conteúdo)."""
        try:
            response = self.s3.list_objects_v2(Bucket=settings.S3_BUCKET_BRONZE)
            return response.get("KeyCount", 0)
        except Exception:
            return 0

    def get_silver_count(self) -> int:
        """Retorna a contagem de objetos na camada Silver (sem baixar conteúdo)."""
        try:
            response = self.s3.list_objects_v2(Bucket=settings.S3_BUCKET_SILVER)
            return response.get("KeyCount", 0)
        except Exception:
            return 0

    def search(self, query: str, top_k: int = 5):
        # Inicializa resources se necessário
        if self.model is None:
            self.tokenizer, self.model = self.load_model()

        # Recarrega dados se estiver vazio (ou implementa botão de refresh)
        if self.df.empty:
            self.df = self.load_data()

        if self.df.empty:
            return []

        # 1. Embed da Query
        inputs = self.tokenizer(
            query, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Mean Pooling (Mesma lógica da Fase 2)
        embeddings = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"]
        mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
        sum_embeddings = torch.sum(embeddings * mask_expanded, 1)
        sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
        query_embedding = (sum_embeddings / sum_mask)[0].numpy()

        # 2. Calcular Similaridade (Matrix operation)
        # Assume que o DF tem coluna 'embedding' como lista de floats
        doc_embeddings = list(self.df["embedding"].values)

        # Scikit-learn cosine_similarity
        scores = cosine_similarity([query_embedding], doc_embeddings)[0]

        # 3. Adicionar scores e filtrar
        self.df["score"] = scores
        results = self.df.sort_values(by="score", ascending=False).head(top_k)

        return results.to_dict("records")
