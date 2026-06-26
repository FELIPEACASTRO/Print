# 🃏 Poker Vision - Detecção Automática de Cartas por Visão Computacional

## 🚀 Nova Funcionalidade: Detecção Automática

O sistema agora possui **detecção automática de cartas** usando visão computacional avançada. Isso significa que ele pode identificar cartas em **QUALQUER posição da tela**, sem precisar de coordenadas pré-definidas!

### ✨ O Que Isso Significa?

1. **Funciona com QUALQUER baralho**: O algoritmo detecta o formato retangular das cartas, independente do design.
2. **Qualquer posição na tela**: Não importa se as cartas estão no topo, centro, lados ou cantos.
3. **Correção de perspectiva e rotação**: Se a carta estiver inclinada, o sistema corrige automaticamente.
4. **Mesas com até 9 jogadores**: Detecta todas as cartas visíveis simultaneamente.

---

## 🔍 Como Funciona a Detecção Automática

### Algoritmo em 5 Etapas:

```
1. CAPTURA DE TELA INTEIRA
   ↓
2. PRÉ-PROCESSAMENTO (escala de cinza, bordas, threshold)
   ↓
3. DETECÇÃO DE CONTORNOS (encontra formas retangulares)
   ↓
4. FILTRAGEM GEOMÉTRICA (valida proporção de carta)
   ↓
5. CORREÇÃO DE PERSPECTIVA + IDENTIFICAÇÃO (hash)
```

### Detalhes Técnicos:

| Etapa | Técnica | Parâmetros Ajustáveis |
|-------|---------|----------------------|
| **Pré-processamento** | GaussianBlur + Canny Edge | kernel_size, thresholds |
| **Detecção** | findContours (OpenCV) | - |
| **Filtragem** | approxPolyDP + aspect_ratio | min_area, max_area, aspect_ratio_min/max |
| **Correção** | warpPerspective | - |
| **Identificação** | pHash + dHash + aHash | tolerance |

---

## 📡 Novo Endpoint: `/detect-auto`

### Requisição

```bash
curl -X POST "http://localhost:8000/detect-auto?monitor_id=1"
```

**Parâmetros:**
- `monitor_id` (opcional): ID do monitor para captura (default: 1)

### Resposta

```json
{
  "status": "success",
  "timestamp": "2023-10-27T14:30:00.123456",
  "monitor_id": 1,
  "resolution": {"width": 1920, "height": 1080},
  "metrics": {
    "total_time_ms": 1250,
    "capture_time_ms": 80,
    "processing_time_ms": 1100,
    "cards_detected": 7,
    "detection_method": "computer_vision_contours"
  },
  "cards": [
    {
      "roi_id": "auto_detected_0",
      "player_name": null,
      "position": "auto_detected",
      "screen_coordinates": {"x": 925, "y": 767, "width": 31, "height": 42},
      "identified_card": {
        "code": "4S",
        "rank": "4",
        "suit": "SPADES",
        "name": "4 de Espadas",
        "is_coringa": false
      },
      "confidence": {
        "score": 0.98,
        "hamming_distance": 2,
        "algorithm_used": "pHash+dHash+perspective_correction"
      },
      "validation": {
        "external_status": "not_validated",
        "api_latency_ms": 0,
        "message": "Detecção automática - sem validação externa"
      },
      "screenshot_base64": "data:image/png;base64,iVBORw...",
      "processing_details": {
        "hash_calculation_ms": 45,
        "perspective_correction_applied": true
      }
    }
  ],
  "detection_info": {
    "total_contours_analyzed": 15,
    "min_area_threshold": 500,
    "aspect_ratio_range": [1.2, 1.8]
  }
}
```

---

## ⚙️ Configuração de Parâmetros

Os parâmetros de detecção podem ser ajustados no `config.json`:

```json
{
  "detection_params": {
    "min_card_area": 500,
    "max_card_area": 50000,
    "card_aspect_ratio_min": 1.2,
    "card_aspect_ratio_max": 1.8,
    "contour_approx_epsilon": 0.02,
    "edge_detection_canny_low": 50,
    "edge_detection_canny_high": 150,
    "morphology_kernel_size": 5
  }
}
```

### Guia de Ajuste:

| Parâmetro | Descrição | Quando Ajustar |
|-----------|-----------|----------------|
| `min_card_area` | Área mínima em pixels | Aumentar se detectar ruído como carta |
| `max_card_area` | Área máxima em pixels | Diminuir se detectar objetos grandes como carta |
| `card_aspect_ratio_min` | Proporção largura/altura mínima | Ajustar se cartas forem muito estreitas |
| `card_aspect_ratio_max` | Proporção largura/altura máxima | Ajustar se cartas forem muito largas |
| `contour_approx_epsilon` | Precisão da aproximação | Menor = mais preciso, Maior = mais rápido |
| `edge_detection_canny_low` | Threshold baixo do Canny | Aumentar em ambientes ruidosos |
| `edge_detection_canny_high` | Threshold alto do Canny | Aumentar para detectar apenas bordas fortes |
| `morphology_kernel_size` | Tamanho do kernel morfológico | Aumentar para conectar regiões fragmentadas |

---

## 🎯 Casos de Uso

### 1. Mesa de Poker Completa (9 Jogadores)
```bash
# Detecta todas as cartas visíveis na mesa
curl -X POST "http://localhost:8000/detect-auto"
```
**Resultado esperado:** Suas 2 cartas + cartas comunitárias (quando reveladas) + cartas de oponentes (se visíveis).

### 2. Monitor Secundário
```bash
# Especifica monitor 2 para captura
curl -X POST "http://localhost:8000/detect-auto?monitor_id=2"
```

### 3. Análise de Screenshot Salvo
Use o endpoint tradicional `/identify/upload` para imagens estáticas.

---

## 🔬 Comparação: ROI Fixo vs. Detecção Automática

| Característica | ROI Fixo (`/identify`) | Detecção Automática (`/detect-auto`) |
|----------------|------------------------|-------------------------------------|
| **Precisão** | Alta (posição conhecida) | Média-Alta (depende do contraste) |
| **Performance** | ~150ms por carta | ~1200ms para tela completa |
| **Flexibilidade** | Baixa (requer config) | Alta (funciona em qualquer lugar) |
| **Baralhos Diferentes** | Requer novo dataset | Funciona automaticamente |
| **Rotação/Perspectiva** | Não suporta | Corrige automaticamente |
| **Ideal Para** | Ambiente fixo, baixa latência | Ambientes variáveis, testes |

---

## ⚠️ Limitações Conhecidas

1. **Cartas Viradas para Baixo**: Não é possível identificar cartas de oponentes que estão fechadas (óbvio!).
2. **Contraste Insuficiente**: Se a carta tiver cor similar ao fundo, pode não ser detectada.
3. **Oclusão**: Botões, fichas ou outros elementos sobrepostos podem interferir.
4. **Performance**: Mais lento que o método de ROI fixo (~8x).
5. **Falsos Positivos**: Elementos retangulares da interface podem ser confundidos com cartas.

---

## 🧪 Testes e Validação

Execute os testes QA para validar a instalação:

```bash
python test_qa.py
```

Teste manual de detecção:

```bash
# Com servidores rodando:
curl -X POST "http://localhost:8000/detect-auto" | python -m json.tool
```

---

## 📊 Exemplo de Fluxo Completo

```
Usuário clica "Detectar Automaticamente" no frontend
           ↓
Frontend chama POST /detect-auto
           ↓
CardDetector captura tela inteira (mss)
           ↓
OpenCV pré-processa imagem (cinza → blur → edges)
           ↓
Encontra 15 contornos candidatos
           ↓
Filtra para 7 contornos com formato de carta
           ↓
Para cada contorno:
  - Recorta região
  - Corrige perspectiva (warpPerspective)
  - Calcula hashes (pHash, dHash, aHash)
  - Compara com dataset de 54 cartas
  - Identifica melhor match
           ↓
Retorna JSON com 7 cartas identificadas
           ↓
Frontend exibe cards com screenshots e confiança
```

---

## 🛠️ Troubleshooting

### Problema: Nenhuma carta detectada
**Solução:** 
- Verifique contraste entre cartas e fundo
- Ajuste `min_card_area` para valor menor
- Aumente iluminação ou brilho da tela

### Problema: Muitas detecções falsas
**Solução:**
- Aumente `min_card_area`
- Ajuste `card_aspect_ratio_min/max` para faixa mais estreita
- Aumente thresholds do Canny edge detection

### Problema: Cartas identificadas incorretamente
**Solução:**
- Verifique se a correção de perspectiva está funcionando
- Aumente tolerância no `identify_card()`
- Adicione mais amostras ao dataset de referência

---

## 📄 Licença

Parte integrante do projeto Poker Vision para pesquisa acadêmica.

**Versão:** 2.0.0  
**Data:** Outubro 2023
