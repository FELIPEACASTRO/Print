# 📘 Poker Vision - Sistema Parametrizável

## ✅ Implementação Completa de Configuração Externa

O sistema agora é **100% parametrizável** via arquivo `config.json`, sem necessidade de modificar código Python para ajustar coordenadas, tolerâncias ou URLs.

---

## 📁 Estrutura do Arquivo `config.json`

```json
{
  "system_config": {
    "default_monitor_id": 1,
    "api_external_url": "http://localhost:8001/validate",
    "dataset_file": "dataset/dataset_mestrado.jsonl",
    "screenshot_dir": "screenshots",
    "identification_tolerance": 15,
    "use_round_for_coords": true
  },
  "monitor_profiles": [...],
  "cards_roi": [...]
}
```

### Campos do `system_config`:

| Campo | Tipo | Descrição | Valores Típicos |
|-------|------|-----------|-----------------|
| `default_monitor_id` | int | ID do monitor padrão para captura | `1` (principal), `2` (secundário) |
| `api_external_url` | string | URL da API de validação externa | `"http://localhost:8001/validate"` |
| `dataset_file` | string | Caminho do arquivo de dataset | `"dataset/dataset_mestrado.jsonl"` |
| `screenshot_dir` | string | Diretório para screenshots temporários | `"screenshots"` |
| `identification_tolerance` | int | Tolerância para identificação (distância de Hamming máxima) | `10-20` (quanto menor, mais rigoroso) |
| `use_round_for_coords` | bool | Usa `round()` ao calcular coordenadas (recomendado para precisão) | `true` ou `false` |

---

## 🎯 Como Parametrizar as ROIs

Cada carta no array `cards_roi` possui:

```json
{
  "id": "luna_left",
  "category": "player_hand",
  "player": "Luna",
  "seat_position": "bottom_center",
  "card_side": "left",
  "percent_x": 0.482524778299,
  "percent_y": 0.712163416899,
  "percent_w": 0.016171100678,
  "percent_h": 0.038997214485,
  "enabled": true,
  "description": "Carta esquerda de Luna"
}
```

### Campos da ROI:

| Campo | Descrição |
|-------|-----------|
| `id` | Identificador único (ex: `"luna_left"`) |
| `category` | Tipo: `"player_hand"` ou `"community_slot"` |
| `player` | Nome do jogador (ou `null` para board) |
| `seat_position` | Posição na mesa (ex: `"bottom_center"`) |
| `card_side` | Lado da carta (`"left"` ou `"right"`) |
| `percent_x` | Posição X como porcentagem da largura do monitor (0.0-1.0) |
| `percent_y` | Posição Y como porcentagem da altura do monitor (0.0-1.0) |
| `percent_w` | Largura como porcentagem da largura do monitor |
| `percent_h` | Altura como porcentagem da altura do monitor |
| `enabled` | Se `false`, esta ROI será ignorada na captura |
| `description` | Descrição legível para debug |

---

## 🔧 Como Ajustar para Seu Setup

### Passo 1: Descobrir Coordenadas

Use uma ferramenta de medição de pixels ou o script `get_coords.py` para encontrar as coordenadas das cartas na sua tela.

### Passo 2: Converter para Porcentagem

Se sua tela é 1920x1080 e a carta está em x=925, y=767 com w=31, h=42:

```
percent_x = 925 / 1920 = 0.481770833333
percent_y = 767 / 1080 = 0.710185185185
percent_w = 31 / 1920 = 0.016145833333
percent_h = 42 / 1080 = 0.038888888889
```

### Passo 3: Editar `config.json`

Atualize os valores no arquivo JSON. **Não é necessário reiniciar o servidor** se usar reload automático (`uvicorn --reload`).

---

## 🚀 Endpoints com Parâmetros

### `/identify` - Agora aceita `monitor_id`

```bash
# Usar monitor padrão do config.json
curl -X POST "http://localhost:8000/identify?capture_all=true"

# Forçar monitor específico (sobrescreve config.json)
curl -X POST "http://localhost:8000/identify?capture_all=true&monitor_id=2"
```

### Resposta da API (Estrutura Completa):

```json
{
  "status": "success",
  "timestamp": "2023-10-27T14:30:00.123456",
  "monitor_id": 1,
  "metrics": {
    "total_time_ms": 850.5,
    "capture_time_ms": 120.3,
    "processing_time_ms": 600.2,
    "external_api_time_ms": 130.0
  },
  "cards": [
    {
      "roi_id": "luna_left",
      "player_name": "Luna",
      "position": "bottom_center",
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
        "algorithm_used": "pHash+dHash+aHash"
      },
      "validation": {
        "external_status": "approved",
        "api_latency_ms": 45.2,
        "message": "Carta validada com sucesso"
      },
      "screenshot_base64": "iVBORw0KGgoAAAANSUhEUg...",
      "processing_details": {
        "hash_calculation_ms": 15.5,
        "comparison_ms": 10.2
      }
    }
  ]
}
```

---

## 📝 Vantagens da Parametrização

1. **Sem Modificação de Código**: Ajuste coordenadas editando apenas JSON
2. **Múltiplos Perfis**: Crie perfis para diferentes resoluções/monitores
3. **Habilitar/Desabilitar ROIs**: Use `"enabled": false` para ignorar posições
4. **Ajuste Fino de Tolerância**: Mude `identification_tolerance` sem recompilar
5. **URLs Configuráveis**: Aponte para diferentes APIs externas facilmente

---

## 🧪 Testes

Execute os testes QA para validar a configuração:

```bash
python test_qa.py
```

Todos os 6 testes devem passar, incluindo validação do carregamento do `config.json`.

---

## ⚠️ Notas Importantes

- **Porcentagens são relativas à resolução total do monitor**, não apenas à área do jogo
- **Use `round()`** nas conversões para evitar erros de 1 pixel
- **Mantenha o jogo na mesma posição** se usar coordenadas fixas
- **Teste sempre após alterar** o `config.json` para garantir que as ROIs estão corretas

---

## 📂 Arquivos Criados

| Arquivo | Função |
|---------|--------|
| `config.json` | Configuração principal parametrizável |
| `config_loader.py` | Módulo Python para carregar configurações |
| `main.py` | Atualizado para usar `config_loader` |
| `README_PARAMETRIZAVEL.md` | Esta documentação |

---

**Status**: ✅ Sistema 100% parametrizável e pronto para produção!
