# 🎴 Sistema de Captura Automática de Cartas - Guia de Uso

## Visão Geral

Este sistema captura automaticamente imagens da tela em regiões específicas onde as cartas aparecem, identifica cada carta usando algoritmos de hash (pHash, dHash, aHash), envia os dados para uma API externa e exibe os resultados em uma interface web amigável.

## Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Interface     │────▶│  API Principal   │────▶│  API Externa    │
│   Web (HTML)    │     │   (porta 8000)   │     │  (porta 8001)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Screen Capture   │
                       │ Config (ROIs)    │
                       └──────────────────┘
```

## Como Funciona

### 1. Configuração das Regiões de Interesse (ROIs)

O arquivo `screen_capture_config.py` contém as coordenadas exatas de onde as cartas aparecem na tela:

```python
CONFIG = {
    "target_monitor_id": 1,  # Monitor onde o jogo está aberto
    "cards_roi": [
        {
            "id": "card_1",
            "percent_x": 0.481481,  # Posição X relativa (48% da largura)
            "percent_y": 0.709378,  # Posição Y relativa (71% da altura)
            "percent_w": 0.018258,  # Largura relativa (1.8%)
            "percent_h": 0.044568   # Altura relativa (4.5%)
        },
        # ... mais cartas
    ]
}
```

**Vantagens das coordenadas relativas:**
- Funciona em diferentes resoluções de monitor
- Fácil de ajustar se a janela do jogo mudar de tamanho
- Independente da posição absoluta na área de trabalho

### 2. Fluxo de Captura Automática

1. **Usuário clica no botão** na interface web
2. **Backend captura todas as ROIs** configuradas usando `mss`
3. **Cada região é processada** individualmente:
   - Calcula hashes (pHash, dHash, aHash)
   - Compara com dataset de 54 cartas
   - Identifica a carta com menor distância de Hamming
4. **API externa é chamada** para validação
5. **Resultados são salvos** no dataset do mestrado
6. **Interface exibe**:
   - Carta identificada (nome, valor, naipe)
   - Screenshot real capturado
   - Métricas de tempo (captura, identificação, API, total)
   - Status de validação

### 3. Múltiplos Monitores

O sistema suporta configuração para múltiplos monitores:

- **Monitor 1**: Onde o jogo está aberto (captura automática)
- **Monitor 2**: Onde você trabalha normalmente (sem interferência)

A biblioteca `mss` gerencia monitores independentemente:
```python
monitors = sct.monitors
# monitors[0] = Todos os monitores combinados
# monitors[1] = Monitor principal
# monitors[2] = Monitor secundário
# etc.
```

## Como Usar

### Passo 1: Iniciar os Servidores

```bash
# Terminal 1: API Externa (validação)
python external_api.py

# Terminal 2: API Principal (captura + identificação)
python main.py
```

### Passo 2: Acessar a Interface

Abra no navegador:
```
http://localhost:8000
```

### Passo 3: Capturar e Identificar

1. Selecione o monitor onde estão as cartas
2. Clique em **"📸 Capturar e Identificar Carta"**
3. Aguarde o processamento (~150-200ms)
4. Veja o resultado na tela

### Passo 4: Ajustar Coordenadas (se necessário)

Se as cartas não forem identificadas corretamente:

1. Tire um screenshot da tela do jogo
2. Use uma IA para analisar e gerar novas coordenadas
3. Atualize `screen_capture_config.py` com os novos valores
4. Reinicie o servidor

## Endpoints da API

### GET `/`
Interface web completa com botão de captura.

### POST `/identify`
Captura tela e identifica carta(s).

**Parâmetros:**
- `region` (opcional): JSON com região específica
- `capture_all` (opcional): `true` para capturar todas as ROIs configuradas

**Exemplo:**
```bash
# Capturar todas as ROIs configuradas
curl -X POST http://localhost:8000/identify?capture_all=true

# Capturar região específica
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"region": "{\"left\": 100, \"top\": 100, \"width\": 200, \"height\": 300}"}'
```

### POST `/identify/upload`
Upload manual de imagem para identificação.

**Exemplo:**
```bash
curl -X POST http://localhost:8000/identify/upload \
  -F "file=@carta.png"
```

### GET `/health`
Verifica status do servidor.

### GET `/deck`
Lista todas as cartas no dataset.

## Estrutura de Resposta

### Sucesso (uma carta):
```json
{
  "success": true,
  "capture_mode": "single",
  "card": {
    "id": "AS_COPAS",
    "valor": "AS",
    "naipe": "COPAS",
    "filename": "AS_COPAS.png"
  },
  "screenshot": "data:image/png;base64,...",
  "metrics": {
    "capture_time_ms": 52.3,
    "identification_time_ms": 45.2,
    "external_api_time_ms": 12.5,
    "total_time_ms": 110.0
  },
  "external_api_response": {
    "status": "validated",
    "message": "Carta validada com sucesso"
  }
}
```

### Sucesso (múltiplas cartas):
```json
{
  "success": true,
  "capture_mode": "all_rois",
  "cards": [
    {
      "roi_id": "card_1",
      "description": "Primeira carta da esquerda...",
      "id": "AS_COPAS",
      "valor": "AS",
      "naipe": "COPAS",
      "screenshot": "data:image/png;base64,..."
    },
    {
      "roi_id": "card_2",
      "description": "Segunda carta da direita...",
      "id": "REI_OUROS",
      "valor": "REI",
      "naipe": "OUROS",
      "screenshot": "data:image/png;base64,..."
    }
  ],
  "metrics": {
    "capture_time_ms": 98.5,
    "total_time_ms": 245.3,
    "cards_found": 2
  }
}
```

## Dataset do Mestrado

Todos os resultados são salvos em `dataset/dataset_mestrado.jsonl`:

```jsonl
{"timestamp": "2025-01-15T10:30:45.123456", "capture_all": true, "identified": true, "cards_data": [...], "capture_time_ms": 98.5, "total_time_ms": 245.3, "external_api_responses": [...]}
```

## Troubleshooting

### "Nenhuma carta identificada"
- Verifique se as coordenadas estão corretas
- Confirme que o jogo está na posição esperada
- Ajuste zoom/escala do navegador se necessário

### Erro de API externa
- Verifique se `external_api.py` está rodando na porta 8001
- O sistema continua funcionando mesmo sem API externa

### Captura muito lenta
- Reduza número de ROIs se possível
- Diminua resolução do monitor de captura
- Feche aplicativos desnecessários

## Performance Esperada

| Operação | Tempo Médio |
|----------|-------------|
| Captura de tela | 50-100ms |
| Identificação (1 carta) | 40-60ms |
| API externa | 10-20ms |
| **Total (1 carta)** | **~150ms** |
| **Total (2 cartas)** | **~250ms** |

## Próximos Passos

1. **Calibrar coordenadas** para seu setup específico
2. **Testar com jogo real** em produção
3. **Coletar dados** para o dataset do mestrado
4. **Ajustar tolerância** de identificação se necessário

---

**Status**: ✅ Sistema completo e operacional
**Versão**: 2.0 com suporte a múltiplas ROIs
**Última atualização**: Janeiro 2025
