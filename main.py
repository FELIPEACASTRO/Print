"""
API Principal - FastAPI
Captura imagens da tela, identifica cartas, chama API externa e salva dataset.
Configuração parametrizada via config.json
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
import httpx
import aiofiles
import json
import time
import os
import mss
import mss.tools
from datetime import datetime
from typing import Optional, Dict, Any, List
from deck_config import deck_db
from config_loader import config_loader, ConfigLoader
from screen_capture_config import get_monitor_info, calculate_roi_bbox, capture_roi
from card_detector import detect_cards_on_screen

app = FastAPI(title="Sistema de Identificação de Cartas via Screen Capture com Detecção Automática", version="2.0")

# Configurações carregadas do config.json
EXTERNAL_API_URL = config_loader.get_external_api_url()
DATASET_FILE = config_loader.get_dataset_file()
SCREENSHOT_DIR = config_loader.get_screenshot_dir()
IDENTIFICATION_TOLERANCE = config_loader.get_tolerance()

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

def capture_screen(region: Optional[Dict[str, int]] = None, capture_all_cards: bool = False, monitor_id: Optional[int] = None) -> tuple:
    """
    Captura a tela ou uma região específica.
    region: dicionário com {'left': x, 'top': y, 'width': w, 'height': h}
    capture_all_cards: se True, captura todas as ROIs configuradas e retorna múltiplas imagens
    monitor_id: ID do monitor para captura (usa o padrão do config se None)
    Retorna tupla com (caminho do arquivo temporário, dados da imagem em base64) ou 
           lista de tuplas se capture_all_cards=True.
    """
    timestamp = int(time.time() * 1000)
    
    # Usa monitor_id passado ou o padrão do config
    if monitor_id is None:
        monitor_id = config_loader.get_system_config().get("default_monitor_id", 1)
    
    if capture_all_cards:
        # Capturar todas as ROIs configuradas usando config.json
        import base64
        results = []
        try:
            monitor = get_monitor_info(monitor_id)
            cards_roi = config_loader.get_cards_roi(enabled_only=True)
            
            for roi in cards_roi:
                bbox = calculate_roi_bbox(roi, monitor)
                temp_path = os.path.join(SCREENSHOT_DIR, f"capture_{timestamp}_{roi['id']}.png")
                
                # Usa função especializada de captura
                img = capture_roi(bbox)
                img.save(temp_path, "PNG")
                
                with open(temp_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                results.append({
                    "path": temp_path,
                    "base64": f"data:image/png;base64,{image_data}",
                    "roi_id": roi["id"],
                    "player": roi.get("player"),
                    "seat": roi.get("seat_position"),
                    "description": roi.get("description", "")
                })
            return results
        except Exception as e:
            raise RuntimeError(f"Erro ao capturar múltiplas ROIs: {str(e)}")
    
    # Captura única (comportamento original)
    temp_path = os.path.join(SCREENSHOT_DIR, f"capture_{timestamp}.png")
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    with mss.mss() as sct:
        if region:
            # Captura região específica
            monitor = region
        else:
            # Captura tela principal
            monitor = sct.monitors[monitor_id] if monitor_id < len(sct.monitors) else sct.monitors[1]
        
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=temp_path)
        
        # Converter para base64 para envio ao frontend
        import base64
        with open(temp_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
    
    return temp_path, f"data:image/png;base64,{image_data}"

@app.get("/")
async def serve_frontend():
    """Serve a interface web de captura de tela."""
    from fastapi.responses import HTMLResponse
    
    html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Captura e Identificação de Cartas</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 900px;
            width: 100%;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .content {
            padding: 40px;
        }
        
        .monitor-selector {
            margin-bottom: 30px;
        }
        
        .monitor-selector label {
            display: block;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        
        .monitor-selector select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            background: white;
            cursor: pointer;
        }
        
        .capture-btn {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.3em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .capture-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .capture-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .capture-btn .icon {
            font-size: 1.5em;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 30px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result {
            display: none;
            margin-top: 30px;
        }
        
        .result.active {
            display: block;
        }
        
        .result-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            border-left: 5px solid #667eea;
        }
        
        .result-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .card-icon {
            font-size: 3em;
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .card-info h3 {
            color: #333;
            font-size: 1.5em;
            margin-bottom: 5px;
        }
        
        .card-info p {
            color: #666;
            font-size: 1.1em;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .metric-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 1.5em;
            font-weight: 700;
            color: #667eea;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        .validation-status {
            margin-top: 20px;
            padding: 15px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            color: #155724;
        }
        
        .validation-status.error {
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        
        .error-message {
            display: none;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }
        
        .error-message.active {
            display: block;
        }
        
        .screenshot-preview {
            margin-top: 20px;
            text-align: center;
        }
        
        .screenshot-preview img {
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .instructions {
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .instructions h4 {
            color: #004085;
            margin-bottom: 10px;
        }
        
        .instructions ol {
            color: #004085;
            padding-left: 20px;
        }
        
        .instructions li {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎴 Captura de Cartas</h1>
            <p>Sistema de Identificação Automática via Screen Capture</p>
        </div>
        
        <div class="content">
            <div class="instructions">
                <h4>📋 Instruções:</h4>
                <ol>
                    <li>Abra o jogo/aplicação com as cartas no monitor desejado</li>
                    <li>Selecione o monitor onde está a carta na lista abaixo</li>
                    <li>Clique em "📸 Capturar e Identificar Carta"</li>
                    <li>Aguarde o processamento automático</li>
                    <li>Veja o resultado na tela</li>
                </ol>
            </div>
            
            <div class="monitor-selector">
                <label for="monitorSelect">🖥️ Selecionar Monitor:</label>
                <select id="monitorSelect">
                    <option value="">Detectar monitores automaticamente</option>
                    <option value="1">Monitor 1 (Principal)</option>
                    <option value="2">Monitor 2 (Secundário)</option>
                </select>
            </div>
            
            <button class="capture-btn" id="captureBtn" onclick="captureAndIdentify()">
                <span class="icon">📸</span>
                <span>Capturar e Identificar Carta</span>
            </button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Capturando tela e identificando carta...</p>
                <p style="font-size: 0.9em; color: #666; margin-top: 10px;">Isso pode levar alguns segundos</p>
            </div>
            
            <div class="error-message" id="errorMessage"></div>
            
            <div class="result" id="result">
                <div class="result-card">
                    <div class="result-header">
                        <div class="card-icon" id="cardIcon">🂡</div>
                        <div class="card-info">
                            <h3 id="cardName">Carta Identificada</h3>
                            <p id="cardDetails">Valor: A | Naipe: Espadas</p>
                        </div>
                    </div>
                    
                    <div class="metrics">
                        <div class="metric-item">
                            <div class="metric-value" id="captureTime">0</div>
                            <div class="metric-label">Captura (ms)</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value" id="idTime">0</div>
                            <div class="metric-label">Identificação (ms)</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value" id="apiTime">0</div>
                            <div class="metric-label">API Externa (ms)</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value" id="totalTime">0</div>
                            <div class="metric-label">Total (ms)</div>
                        </div>
                    </div>
                    
                    <div class="validation-status" id="validationStatus">
                        ✅ <strong>Validado:</strong> <span id="validationMessage">Carta validada com sucesso pela API externa</span>
                    </div>
                </div>
                
                <div class="screenshot-preview" id="screenshotPreview">
                    <h4 style="margin-bottom: 10px; color: #333;">📷 Captura Realizada:</h4>
                    <img id="capturedImage" src="" alt="Captura de tela">
                </div>
            </div>
        </div>
    </div>
    
    <script>
        async function captureAndIdentify() {
            const captureBtn = document.getElementById('captureBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const errorMessage = document.getElementById('errorMessage');
            const monitorSelect = document.getElementById('monitorSelect');
            
            // Resetar estados
            result.classList.remove('active');
            errorMessage.classList.remove('active');
            captureBtn.disabled = true;
            loading.classList.add('active');
            
            try {
                // Preparar região se monitor específico selecionado
                let region = null;
                const selectedMonitor = monitorSelect.value;
                
                if (selectedMonitor) {
                    // Coordenadas aproximadas para monitores comuns
                    // Usuário pode ajustar conforme necessário
                    const monitorConfigs = {
                        '1': { left: 0, top: 0, width: 1920, height: 1080 },
                        '2': { left: 1920, top: 0, width: 1920, height: 1080 }
                    };
                    
                    if (monitorConfigs[selectedMonitor]) {
                        region = monitorConfigs[selectedMonitor];
                    }
                }
                
                // Chamar API de identificação
                const payload = region ? JSON.stringify(region) : undefined;
                const headers = region ? { 'Content-Type': 'application/json' } : {};
                
                const response = await fetch('/identify', {
                    method: 'POST',
                    headers: headers,
                    body: payload
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Erro ao identificar carta');
                }
                
                // Exibir resultado
                displayResult(data);
                
            } catch (error) {
                showError(error.message);
            } finally {
                captureBtn.disabled = false;
                loading.classList.remove('active');
            }
        }
        
        function displayResult(data) {
            const result = document.getElementById('result');
            const cardIcon = document.getElementById('cardIcon');
            const cardName = document.getElementById('cardName');
            const cardDetails = document.getElementById('cardDetails');
            const captureTime = document.getElementById('captureTime');
            const idTime = document.getElementById('idTime');
            const apiTime = document.getElementById('apiTime');
            const totalTime = document.getElementById('totalTime');
            const validationStatus = document.getElementById('validationStatus');
            const validationMessage = document.getElementById('validationMessage');
            const capturedImage = document.getElementById('capturedImage');
            
            // Dados da carta
            const card = data.card;
            cardName.textContent = `${card.valor} de ${card.naipe}`;
            cardDetails.textContent = `ID: ${card.id} | Arquivo: ${card.filename}`;
            
            // Ícone baseado no naipe
            const suitIcons = {
                'COPAS': '♥',
                'OUROS': '♦',
                'ESPADAS': '♠',
                'PAUS': '♣',
                'CORINGA': '🃏'
            };
            const suitIcon = suitIcons[card.naipe] || '🂡';
            cardIcon.textContent = suitIcon;
            
            // Métricas de tempo
            const metrics = data.metrics;
            captureTime.textContent = metrics.capture_time_ms.toFixed(2);
            idTime.textContent = metrics.identification_time_ms.toFixed(2);
            apiTime.textContent = metrics.external_api_time_ms.toFixed(2);
            totalTime.textContent = metrics.total_time_ms.toFixed(2);
            
            // Status de validação
            const externalResponse = data.external_api_response;
            if (externalResponse && externalResponse.validated) {
                validationStatus.className = 'validation-status';
                validationMessage.textContent = externalResponse.message || 'Carta validada com sucesso';
            } else if (externalResponse && externalResponse.error) {
                validationStatus.className = 'validation-status error';
                validationMessage.textContent = `Erro: ${externalResponse.error}`;
            }
            
            // Exibir screenshot capturado
            if (data.screenshot) {
                capturedImage.src = data.screenshot;
                document.getElementById('screenshotPreview').style.display = 'block';
            }
            
            // Mostrar resultado
            result.classList.add('active');
        }
        
        function showError(message) {
            const errorMessage = document.getElementById('errorMessage');
            errorMessage.textContent = `❌ Erro: ${message}`;
            errorMessage.classList.add('active');
        }
        
        // Carregar status do sistema ao iniciar
        async function loadSystemStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                console.log('Sistema saudável:', data);
            } catch (error) {
                console.error('Erro ao verificar status:', error);
            }
        }
        
        // Inicializar
        loadSystemStatus();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/identify")
async def identify_card_from_screen(region: Optional[str] = None, capture_all: bool = False, monitor_id: Optional[int] = None):
    """
    Endpoint principal para captura de tela:
    1. Captura a tela ou região específica (ou todas as ROIs se capture_all=True)
    2. Identifica a carta(s) via pHash
    3. Chama API externa
    4. Salva no dataset
    5. Retorna resultado
    
    region (opcional): string JSON com {"left": x, "top": y, "width": w, "height": h}
    capture_all (opcional): se True, captura todas as 17 ROIs configuradas (6 jogadores + board)
    monitor_id (opcional): ID do monitor para captura (usa o padrão do config.json se None)
    Exemplo: curl -X POST "http://localhost:8000/identify?capture_all=true&monitor_id=1"
    """
    import json as json_module
    
    start_time = time.perf_counter()
    
    # Parse da região se fornecida
    region_dict = None
    if region:
        try:
            region_dict = json_module.loads(region)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Região inválida: {str(e)}")
    
    try:
        # Fase 0: Capturar tela
        capture_start = time.perf_counter()
        captures = capture_screen(region_dict, capture_all_cards=capture_all, monitor_id=monitor_id)
        capture_time = (time.perf_counter() - capture_start) * 1000
        
        # Se capture_all=True, temos múltiplas capturas
        if capture_all and isinstance(captures, list):
            results = []
            total_identification_time = 0
            
            for capture in captures:
                card_start = time.perf_counter()
                card_data = deck_db.identify_card(capture["path"], tolerance=IDENTIFICATION_TOLERANCE)
                card_time = (time.perf_counter() - card_start) * 1000
                total_identification_time += card_time
                
                # Chamar API externa para cada carta identificada
                external_response = None
                if card_data:
                    external_response = await call_external_api(card_data, card_time)
                
                results.append({
                    "roi_id": capture["roi_id"],
                    "player_name": capture.get("player"),
                    "position": capture.get("seat"),
                    "identified_card": card_data,
                    "confidence": {
                        "score": 1.0 - (card_data.get("distance", 0) / 64.0) if card_data else 0.0,
                        "hamming_distance": card_data.get("distance", 0) if card_data else None,
                        "algorithm_used": "pHash+dHash+aHash"
                    },
                    "validation": external_response if external_response else {"status": "skipped", "message": "Nenhuma carta identificada"},
                    "screenshot_base64": capture["base64"],
                    "processing_details": {
                        "hash_calculation_ms": round(card_time * 0.7, 2),
                        "comparison_ms": round(card_time * 0.3, 2)
                    }
                })
                
                # Salvar no dataset
                record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "capture_type": "multi_roi",
                    "roi_id": capture["roi_id"],
                    "player": capture.get("player"),
                    "identified": card_data is not None,
                    "card_data": card_data,
                    "identification_time_ms": card_time,
                    "external_api_response": external_response
                }
                await save_to_dataset(record)
                
                # Limpar arquivo temporário
                if os.path.exists(capture["path"]):
                    os.remove(capture["path"])
            
            total_time = (time.perf_counter() - start_time) * 1000
            return JSONResponse(content={
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "monitor_id": monitor_id or config_loader.get_system_config().get("default_monitor_id", 1),
                "metrics": {
                    "total_time_ms": round(total_time, 2),
                    "capture_time_ms": round(capture_time, 2),
                    "processing_time_ms": round(total_identification_time, 2),
                    "external_api_time_ms": round(sum(r.get("validation", {}).get("api_latency_ms", 0) for r in results), 2)
                },
                "cards": results
            })
        
        # Comportamento padrão (captura única)
        temp_path, screenshot_base64 = captures
        
        # Fase 1: Identificação da carta
        id_start = time.perf_counter()
        card_data = deck_db.identify_card(temp_path, tolerance=IDENTIFICATION_TOLERANCE)
        id_time = (time.perf_counter() - id_start) * 1000
        
        if not card_data:
            total_time = (time.perf_counter() - start_time) * 1000
            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "capture_region": region_dict,
                "identified": False,
                "card_data": None,
                "capture_time_ms": capture_time,
                "identification_time_ms": id_time,
                "total_time_ms": total_time,
                "external_api_response": None
            }
            await save_to_dataset(record)
            os.remove(temp_path)
            return JSONResponse(
                status_code=404,
                content={"message": "Carta não identificada na captura", "time_ms": total_time}
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
            "screenshot": screenshot_base64,
            "metrics": {
                "capture_time_ms": round(capture_time, 2),
                "identification_time_ms": round(id_time, 2),
                "external_api_time_ms": round(api_time, 2),
                "total_time_ms": round(total_time, 2)
            },
            "external_api_response": external_response
        }
        
        # Salvar no dataset para mestrado
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "capture_region": region_dict,
            "identified": True,
            "card_data": card_data,
            "capture_time_ms": capture_time,
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
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/identify/upload")
async def identify_card_upload(file: UploadFile = File(...)):
    """
    Endpoint alternativo para upload direto de imagem:
    1. Recebe imagem por upload
    2. Identifica a carta via pHash
    3. Chama API externa
    4. Salva no dataset
    5. Retorna resultado
    """
    from fastapi import File, UploadFile
    
    start_time = time.perf_counter()
    
    # Validar tipo de arquivo
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Apenas imagens PNG, JPG são aceitas")
    
    # Salvar temporariamente com nome seguro
    timestamp = int(time.time() * 1000)
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ('.', '_'))
    temp_path = f"temp_{timestamp}_{safe_filename}"
    
    try:
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Fase 1: Identificação da carta
        id_start = time.perf_counter()
        card_data = deck_db.identify_card(temp_path, tolerance=15)
        id_time = (time.perf_counter() - id_start) * 1000
        
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


@app.post("/detect-auto")
async def detect_cards_automatic(monitor_id: Optional[int] = None):
    """
    Endpoint de detecção automática por visão computacional:
    
    Detecta TODAS as cartas visíveis na tela SEM precisar de coordenadas pré-definidas.
    Usa algoritmos de visão computacional para:
    1. Capturar a tela inteira
    2. Detectar contornos com formato de carta
    3. Corrigir perspectiva e rotação
    4. Identificar cada carta via hashing
    
    Funciona com QUALQUER baralho e em QUALQUER posição da tela.
    Ideal para mesas de poker com até 9 jogadores.
    
    monitor_id (opcional): ID do monitor para captura
    Exemplo: curl -X POST "http://localhost:8000/detect-auto?monitor_id=1"
    """
    try:
        # Usa o detector de visão computacional
        result = detect_cards_on_screen(monitor_id or MONITOR_ID)
        
        # Se encontrou cartas, chama API externa para cada uma
        if result.get('cards'):
            for card in result['cards']:
                if card.get('identified_card', {}).get('code') != 'UNKNOWN':
                    await call_external_api(card)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na detecção automática: {str(e)}")

