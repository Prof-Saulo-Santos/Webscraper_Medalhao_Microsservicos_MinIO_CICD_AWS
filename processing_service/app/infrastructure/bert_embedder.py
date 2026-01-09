from transformers import AutoTokenizer, AutoModel
import torch
from app.domain.ports import EmbedderProtocol
from app.core.config import settings


class BERTEmbedder(EmbedderProtocol):
    def __init__(self):
        # Carrega modelo pré-treinado (leve)
        self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
        self.model = AutoModel.from_pretrained(settings.MODEL_NAME)

    def generate_embedding(self, text: str) -> list[float]:
        # WARN: Em multi-thread (asyncio.gather), o modelo compartilhado pode sofrer race conditions.
        # Se escalar, usar thread-local storage ou locks.
        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Mean Pooling para obter um vetor único por sentença
        embeddings = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"]

        mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
        sum_embeddings = torch.sum(embeddings * mask_expanded, 1)
        sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)

        mean_pooled = sum_embeddings / sum_mask
        # Normalização (opcional, bom para similaridade de cosseno)
        return mean_pooled[0].tolist()
