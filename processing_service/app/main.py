from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.routes import router, get_processor_service
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if settings.RUN_ON_STARTUP:
        print("🚀 RUN_ON_STARTUP=True. Iniciando Job de Processamento...")
        service = get_processor_service()
        
        async def run_batch_loop():
             # Processa em loops até acabar (ou um limite alto)
             total_processed = 0
             while True:
                 files = await service.repo.list_unprocessed_files()
                 if not files:
                     print("✅ Nenhum arquivo novo para processar.")
                     break
                 
                 # Processa lote de 10
                 for f in files[:10]:
                     await service.process_one_file(f)
                     total_processed += 1
                 
                 print(f"🔄 Lote processado. Total até agora: {total_processed}")
                 await asyncio.sleep(1) # Breve pausa
        
        asyncio.create_task(run_batch_loop())

    yield
    # Shutdown


app = FastAPI(
    title="Processing Service (Phase 2)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
