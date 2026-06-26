# Sistema de Identificação de Cartas via Screen Capture

## Visão Geral

Solução completa para **captura de tela em tempo real** e identificação de cartas de baralho usando **pHash + dHash + aHash**, integrada com API externa de validação.

## Arquitetura

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Captura de Tela   │────▶│  Identificação   │────▶│  API Externa    │
│   (mss - porta 8000)│     │  (pHash+dHash)   │     │  (porta 8001)   │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
         │                         │                         │
         ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Dataset (JSONL)                              │
│              dataset/dataset_mestrado.jsonl                     │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes

### 1. API Principal (`main.py` - porta 8000)

**Endpoints:**

- `POST /identify` - Captura tela e identifica carta
  - Parâmetro opcional: `region` (JSON string)
  - Exemplo: `{"left": 100, "top": 100, "width": 200, "height": 300}`

- `POST /identify/upload` - Upload direto de imagem
  - Parâmetro: `file` (imagem PNG/JPG)

- `GET /health` - Saúde do sistema
- `GET /deck` - Lista todas as cartas cadastradas

### 2. API Externa (`external_api.py` - porta 8001)

- `POST /validate` - Valida dados da carta identificada
- `GET /health` - Saúde da API

### 3. Configuração do Baralho (`deck_config.py`)

- Carrega 54 cartas do diretório `cards/`
- Calcula hashes combinados (pHash + dHash + aHash)
- Identificação por busca aproximada com tolerância

## Instalação

```bash
pip install fastapi uvicorn pillow imagehash mss aiofiles httpx python-multipart
```

## Uso

### 1. Iniciar API Externa (porta 8001)

```bash
python external_api.py
```

### 2. Iniciar API Principal (porta 8000)

```bash
python main.py
```

### 3. Testar Identificação por Upload

```bash
curl -X POST http://localhost:8000/identify/upload \
  -F "file=@cards/AS_COPAS.png"
```

### 4. Testar Captura de Tela

```bash
# Captura tela inteira
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{}'

# Captura região específica
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"region": "{\"left\": 100, \"top\": 100, \"width\": 200, \"height\": 300}"}'
```

### 5. Verificar Saúde

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

## Resposta da API

```json
{
  "success": true,
  "card": {
    "id": "AS_COPAS",
    "filename": "AS_COPAS.png",
    "valor": "AS",
    "naipe": "COPAS",
    "path": "cards/AS_COPAS.png",
    "hash": "952d4ead73e14ae0_f0a0828c8ca28080_007e7e66667e7e00"
  },
  "metrics": {
    "capture_time_ms": 15.23,
    "identification_time_ms": 2.13,
    "external_api_time_ms": 139.07,
    "total_time_ms": 158.38
  },
  "external_api_response": {
    "validated": true,
    "card_id": "AS_COPAS",
    "valor": "AS",
    "naipe": "COPAS",
    "validation_timestamp": "2026-06-26T17:57:45.637172",
    "status": "approved",
    "message": "Carta AS_COPAS validada com sucesso"
  }
}
```

## Dataset

Os registros são salvos em `dataset/dataset_mestrado.jsonl`:

```json
{
  "timestamp": "2026-06-26T17:57:45.638559",
  "capture_region": null,
  "identified": true,
  "card_data": {...},
  "capture_time_ms": 15.23,
  "identification_time_ms": 2.13,
  "external_api_time_ms": 139.07,
  "total_time_ms": 158.38,
  "external_api_response": {...}
}
```

## Performance

- **Captura de tela**: ~15ms
- **Identificação**: ~2ms (54 cartas)
- **API externa**: ~100-150ms
- **Total**: ~150-200ms

## Correções Implementadas

1. ✅ **Bug CORINGA**: Naipe agora é "CORINGA" em vez de "1"
2. ✅ **API externa**: Criada e rodando na porta 8001
3. ✅ **Import cv2 removido**: Dependência inútil eliminada
4. ✅ **Screen capture**: Implementado com biblioteca `mss`
5. ✅ **Dois endpoints**: `/identify` (screen) e `/identify/upload` (upload)
6. ✅ **Dataset limpo**: Novos registros sem erro 404

## Estrutura de Arquivos

```
/workspace/
├── main.py              # API principal (porta 8000)
├── external_api.py      # API externa (porta 8001)
├── deck_config.py       # Configuração do baralho
├── cards/               # 54 imagens de cartas
├── dataset/             # Dataset JSONL
├── screenshots/         # Capturas temporárias
└── README.md            # Esta documentação
```

## Próximos Passos

1. Implementar endpoint de captura contínua (streaming)
2. Adicionar cache de hashes para performance
3. Implementar testes unitários
4. Gerar OpenAPI automaticamente com FastAPI
5. Adicionar autenticação nas APIs
