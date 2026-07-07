"""
API Externa de Validação - FastAPI (porta 8001)
Recebe dados de cartas identificadas e valida/processa para o dataset.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Externa de Validação de Cartas", version="1.0")

class CardValidationRequest(BaseModel):
    card_id: str
    valor: str
    naipe: str
    filename: str
    identification_time_ms: float
    timestamp: str

@app.post("/validate")
async def validate_card(request: CardValidationRequest):
    """
    Endpoint de validação da API externa.
    Recebe dados da carta identificada e retorna validação.
    """
    logger.info(f"Validando carta: {request.card_id}")
    
    # Simula processamento/validação
    validation_result = {
        "validated": True,
        "card_id": request.card_id,
        "valor": request.valor,
        "naipe": request.naipe,
        "validation_timestamp": datetime.utcnow().isoformat(),
        "status": "approved",
        "message": f"Carta {request.card_id} validada com sucesso"
    }
    
    return JSONResponse(content=validation_result)

@app.get("/health")
async def health_check():
    """Verifica saúde da API de validação."""
    return {
        "status": "healthy",
        "service": "external-validation-api",
        "port": 8001
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
