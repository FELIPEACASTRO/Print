# Sistema de Identificação de Cartas via Screen Capture

## Visão Geral

Sistema completo para captura automática de tela, identificação de cartas de baralho usando hash perceptual (pHash + dHash + aHash) e integração com API externa de validação.

## Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Interface     │────▶│  API Principal   │────▶│  API Externa    │
│   Web (Frontend)│     │  (Porta 8000)    │     │  (Porta 8001)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────┐
                        │   Dataset   │
                        │  Mestrado   │
                        └─────────────┘
```

## Componentes

### 1. Frontend Web (`/` endpoint)
- Interface gráfica moderna e responsiva
- Seletor de monitor (1 ou 2)
- Botão de captura com feedback visual
- Exibição de resultados em tempo real
- Métricas de performance detalhadas

### 2. API Principal (`main.py` - Porta 8000)
- **GET `/`**: Serve interface web
- **POST `/identify`**: Captura tela e identifica carta
- **POST `/identify/upload`**: Upload manual de imagem
- **GET `/health`**: Status do sistema
- **GET `/deck`**: Lista todas as cartas cadastradas

### 3. API Externa (`external_api.py` - Porta 8001)
- **POST `/validate`**: Valida dados da carta identificada
- **GET `/health`**: Status da API

### 4. Banco de Dados de Cartas (`deck_config.py`)
- Carrega 54 cartas do baralho
- Calcula hashes combinados (pHash + dHash + aHash)
- Busca aproximada com tolerância configurável

## Como Usar

### Iniciar os Serviços

```bash
# Terminal 1: API Externa (porta 8001)
python external_api.py

# Terminal 2: API Principal (porta 8000)
python main.py
```

### Acessar a Interface

1. Abra o navegador em `http://localhost:8000`
2. Selecione o monitor onde está a carta
3. Clique em "📸 Capturar e Identificar Carta"
4. Aguarde o processamento (~150-200ms)
5. Veja o resultado na tela

### Configuração de Monitores

O sistema suporta múltiplos monitores:

- **Monitor 1 (Principal)**: Coordenadas (0, 0) a (1920, 1080)
- **Monitor 2 (Secundário)**: Coordenadas (1920, 0) a (3840, 1080)

Para ajustar as coordenadas, edite o arquivo `main.py` na seção do frontend JavaScript:

```javascript
const monitorConfigs = {
    '1': { left: 0, top: 0, width: 1920, height: 1080 },
    '2': { left: 1920, top: 0, width: 1920, height: 1080 }
};
```

### Uso via API (curl)

```bash
# Capturar tela inteira
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{}'

# Capturar região específica
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"region": {"left": 100, "top": 100, "width": 200, "height": 300}}'

# Upload de imagem
curl -X POST http://localhost:8000/identify/upload \
  -F "file=@carta.png"
```

## Fluxo de Processamento

1. **Captura de Tela** (~50-100ms)
   - Usa biblioteca `mss` para captura rápida
   - Suporta regiões específicas ou tela cheia
   - Converte para PNG e base64

2. **Identificação** (~1-5ms)
   - Calcula hash combinado (pHash + dHash + aHash)
   - Compara com dataset de 54 cartas
   - Busca exata ou aproximada (tolerância: 15 bits)

3. **Validação Externa** (~50-100ms)
   - Envia dados para API na porta 8001
   - Recebe confirmação de validação

4. **Armazenamento**
   - Salva registro no dataset JSONL
   - Inclui timestamps e métricas

## Estrutura de Dados

### Resposta da API

```json
{
  "success": true,
  "card": {
    "id": "AS_COPAS",
    "filename": "AS_COPAS.png",
    "valor": "AS",
    "naipe": "COPAS",
    "path": "cards/AS_COPAS.png",
    "hash": "952d4ead73e14ae0_..."
  },
  "screenshot": "data:image/png;base64,...",
  "metrics": {
    "capture_time_ms": 52.34,
    "identification_time_ms": 1.99,
    "external_api_time_ms": 64.43,
    "total_time_ms": 118.76
  },
  "external_api_response": {
    "validated": true,
    "card_id": "AS_COPAS",
    "status": "approved",
    "message": "Carta AS_COPAS validada com sucesso"
  }
}
```

### Dataset (JSONL)

Cada registro contém:
- Timestamp da captura
- Região capturada
- Dados da carta identificada
- Tempos de cada fase
- Resposta da API externa

## Performance

| Operação | Tempo Médio |
|----------|-------------|
| Captura de tela | 50-100ms |
| Identificação | 1-5ms |
| API externa | 50-100ms |
| **Total** | **~150-200ms** |

## Requisitos

- Python 3.8+
- FastAPI
- uvicorn
- mss (captura de tela)
- Pillow
- imagehash
- aiofiles
- httpx

## Instalação

```bash
pip install fastapi uvicorn mss pillow imagehash aiofiles httpx
```

## Troubleshooting

### Erro: "Cannot connect to display"
- Certifique-se de estar em ambiente com display X11
- Em servidores headless, use Xvfb

### Erro: "Address already in use"
```bash
# Matar processos nas portas 8000 e 8001
kill $(lsof -t -i:8000) $(lsof -t -i:8001)
```

### Carta não identificada
- Ajuste tolerância no código (padrão: 15 bits)
- Verifique se a imagem está clara e bem iluminada
- Confirme que a carta está no dataset

## Licença

Projeto acadêmico para mestrado.
