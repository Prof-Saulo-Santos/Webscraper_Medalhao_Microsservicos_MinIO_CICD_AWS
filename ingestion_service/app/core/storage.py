import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.logger import logger


def initialize_buckets():
    """Garante que o bucket configurado existe."""
    if not settings.USE_S3:
        return

    client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    bucket = settings.S3_BUCKET_NAME
    try:
        client.head_bucket(Bucket=bucket)
        logger.info(f"Bucket '{bucket}' já existe.")
    except ClientError as e:
        error_code = e.response["Error"].get("Code")
        if error_code == "404":
            try:
                client.create_bucket(Bucket=bucket)
                logger.info(f"Bucket '{bucket}' criado com sucesso.")
            except Exception as create_error:
                logger.error(f"Erro ao criar bucket '{bucket}': {create_error}")
                # Não relança para não quebrar o startup se for problema de permissão menor,
                # mas idealmente deveria falhar se for crítico.
                # Aqui vamos logar e prosseguir.
        else:
            logger.error(f"Erro ao verificar bucket: {e}")
            # Dependendo da robustez desejada, poderíamos levantar exceção aqui.
