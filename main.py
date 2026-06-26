"""
API Principal - FastAPI
Recebe imagens, identifica cartas, chama API externa e salva dataset.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import httpx
import aiofiles
import json
import time
import os
from datetime import datetime
from typing import Optional
from deck_config import deck_db

app = FastAPI(title="Sistema de Identificação de Cartas", version="1.0")

# Configurações
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "http://localhost:8000/validate")  # Sua API pronta
DATASET_FILE = "dataset/dataset_mestrado.jsonl"

async def call_external_api(card_data: dict, response_time_ms: float) -> dict:
    """Chama a API externa já existente com os dados da carta identificada."""
    try:
        payload = {
            "card_id": card_data.get("id"),
            "valor": card_data.get("valor"),
            "naipe": card_data.get("naipe"),
            "filename": card_data.get("filename"),
            "identification_time_ms": response_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(EXTERNAL_API_URL, json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Falha ao chamar API externa: {str(e)}", "status": "external_api_error"}

async def save_to_dataset(record: dict):
    """Salva o registro no dataset do mestrado."""
    os.makedirs(os.path.dirname(DATASET_FILE), exist_ok=True)
    async with aiofiles.open(DATASET_FILE, mode='a') as f:
        await f.write(json.dumps(record, ensure_ascii=False) + '\n')

@app.post("/identify")
async def identify_card(file: UploadFile = File(...)):
    """
    Endpoint principal:
    1. Recebe imagem
    2. Identifica a carta via pHash
    3. Chama API externa
    4. Salva no dataset
    5. Retorna resultado
    """
    start_time = time.perf_counter()
    
    # Validar tipo de arquivo
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Apenas imagens PNG, JPG são aceitas")
    
    # Salvar temporariamente
    temp_path = f"temp_{int(time.time())}_{file.filename}"
    try:
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Fase 1: Identificação da carta (CRÍTICO PARA PERFORMANCE)
        id_start = time.perf_counter()
        card_data = deck_db.identify_card(temp_path, tolerance=5)
        id_time = (time.perf_counter() - id_start) * 1000  # ms
        
        if not card_data:
            os.remove(temp_path)
            total_time = (time.perf_counter() - start_time) * 1000
            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "filename": file.filename,
                "identified": False,
                "card_data": None,
                "identification_time_ms": id_time,
                "total_time_ms": total_time,
                "external_api_response": None
            }
            await save_to_dataset(record)
            return JSONResponse(
                status_code=404,
                content={"message": "Carta não identificada", "time_ms": total_time}
            )
        
        # Fase 2: Chamar API externa
        api_start = time.perf_counter()
        external_response = await call_external_api(card_data, id_time)
        api_time = (time.perf_counter() - api_start) * 1000
        
        # Calcular tempo total
        total_time = (time.perf_counter() - start_time) * 1000
        
        # Preparar resposta
        result = {
            "success": True,
            "card": card_data,
            "metrics": {
                "identification_time_ms": round(id_time, 2),
                "external_api_time_ms": round(api_time, 2),
                "total_time_ms": round(total_time, 2)
            },
            "external_api_response": external_response
        }
        
        # Salvar no dataset para mestrado
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "filename": file.filename,
            "identified": True,
            "card_data": card_data,
            "identification_time_ms": id_time,
            "external_api_time_ms": api_time,
            "total_time_ms": total_time,
            "external_api_response": external_response
        }
        await save_to_dataset(record)
        
        # Limpar arquivo temporário
        os.remove(temp_path)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/health")
async def health_check():
    """Verifica saúde do sistema e quantidade de cartas carregadas."""
    return {
        "status": "healthy",
        "cards_loaded": len(deck_db.hash_map),
        "external_api_url": EXTERNAL_API_URL
    }

@app.get("/deck")
async def list_deck():
    """Lista todas as cartas cadastradas no sistema."""
    return {
        "total_cards": len(deck_db.hash_map),
        "cards": list(deck_db.hash_map.values())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
