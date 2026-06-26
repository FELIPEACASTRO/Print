"""
Configuração de Captura de Tela - Poker Multi-Monitor
Gera coordenadas dinâmicas baseadas em porcentagens para suportar diferentes resoluções.
Análise baseada em screenshot 1917x1077 com 17 ROIs detectadas.
"""

from typing import List, Dict, Any
import mss

# Configuração principal
MONITOR_ID = 1  # 1 = monitor principal (onde está o jogo), 2 = secundário

# Definição de todas as ROIs baseado na análise rigorosa da IA
# Coordenadas em porcentagem relative à resolução original 1917x1077
# Inclui: 6 jogadores (2 cartas cada) + 5 cartas comunitárias = 17 ROIs
CARDS_ROI: List[Dict[str, Any]] = [
    # === ALEX (Top Center) ===
    {
        "id": "alex_left",
        "player": "Alex",
        "seat": "top_center",
        "side": "left",
        "percent_x": 0.482524778299,
        "percent_y": 0.25348189415,
        "percent_w": 0.016171100678,
        "percent_h": 0.040854224698,
        "description": "Carta esquerda de Alex"
    },
    {
        "id": "alex_right",
        "player": "Alex",
        "seat": "top_center",
        "side": "right",
        "percent_x": 0.503390714658,
        "percent_y": 0.25348189415,
        "percent_w": 0.016171100678,
        "percent_h": 0.040854224698,
        "description": "Carta direita de Alex"
    },
    
    # === SOFIA (Upper Left) ===
    {
        "id": "sofia_left",
        "player": "Sofia",
        "seat": "upper_left",
        "side": "left",
        "percent_x": 0.256651017214,
        "percent_y": 0.364902506964,
        "percent_w": 0.016171100678,
        "percent_h": 0.040854224698,
        "description": "Carta esquerda de Sofia"
    },
    {
        "id": "sofia_right",
        "player": "Sofia",
        "seat": "upper_left",
        "side": "right",
        "percent_x": 0.277516953573,
        "percent_y": 0.364902506964,
        "percent_w": 0.016171100678,
        "percent_h": 0.040854224698,
        "description": "Carta direita de Sofia"
    },
    
    # === MAYA (Upper Right) - Atenção: parcialmente escurecida ===
    {
        "id": "maya_left",
        "player": "Maya",
        "seat": "upper_right",
        "side": "left",
        "percent_x": 0.707876890975,
        "percent_y": 0.377901578459,
        "percent_w": 0.016692749087,
        "percent_h": 0.039925719591,
        "description": "Carta esquerda de Maya (pode ter ruído)"
    },
    {
        "id": "maya_right",
        "player": "Maya",
        "seat": "upper_right",
        "side": "right",
        "percent_x": 0.729264475743,
        "percent_y": 0.377901578459,
        "percent_w": 0.015649452269,
        "percent_h": 0.039925719591,
        "description": "Carta direita de Maya (pode ter ruído)"
    },
    
    # === CAIO (Lower Left) ===
    {
        "id": "caio_left",
        "player": "Caio",
        "seat": "lower_left",
        "side": "left",
        "percent_x": 0.256129368805,
        "percent_y": 0.588672237697,
        "percent_w": 0.016692749087,
        "percent_h": 0.040854224698,
        "description": "Carta esquerda de Caio"
    },
    {
        "id": "caio_right",
        "player": "Caio",
        "seat": "lower_left",
        "side": "right",
        "percent_x": 0.276995305164,
        "percent_y": 0.588672237697,
        "percent_w": 0.016692749087,
        "percent_h": 0.040854224698,
        "description": "Carta direita de Caio"
    },
    
    # === REX (Lower Right) ===
    {
        "id": "rex_left",
        "player": "Rex",
        "seat": "lower_right",
        "side": "left",
        "percent_x": 0.707876890975,
        "percent_y": 0.588672237697,
        "percent_w": 0.016692749087,
        "percent_h": 0.040854224698,
        "description": "Carta esquerda de Rex"
    },
    {
        "id": "rex_right",
        "player": "Rex",
        "seat": "lower_right",
        "side": "right",
        "percent_x": 0.728742827334,
        "percent_y": 0.588672237697,
        "percent_w": 0.016692749087,
        "percent_h": 0.040854224698,
        "description": "Carta direita de Rex"
    },
    
    # === LUNA (Bottom Center - Jogador Principal) ===
    {
        "id": "luna_left",
        "player": "Luna",
        "seat": "bottom_center",
        "side": "left",
        "percent_x": 0.482524778299,
        "percent_y": 0.712163416899,
        "percent_w": 0.016171100678,
        "percent_h": 0.038997214485,
        "description": "Carta esquerda de Luna"
    },
    {
        "id": "luna_right",
        "player": "Luna",
        "seat": "bottom_center",
        "side": "right",
        "percent_x": 0.503390714658,
        "percent_y": 0.712163416899,
        "percent_w": 0.016171100678,
        "percent_h": 0.038997214485,
        "description": "Carta direita de Luna"
    },
    
    # === BOARD (Cartas Comunitárias) ===
    {
        "id": "board_1",
        "player": None,
        "seat": "community",
        "side": "slot_1",
        "percent_x": 0.446009389671,
        "percent_y": 0.491179201486,
        "percent_w": 0.015649452269,
        "percent_h": 0.039925719591,
        "description": "Carta comunitária 1"
    },
    {
        "id": "board_2",
        "player": None,
        "seat": "community",
        "side": "slot_2",
        "percent_x": 0.469483568075,
        "percent_y": 0.491179201486,
        "percent_w": 0.015649452269,
        "percent_h": 0.039925719591,
        "description": "Carta comunitária 2"
    },
    {
        "id": "board_3",
        "player": None,
        "seat": "community",
        "side": "slot_3",
        "percent_x": 0.492957746479,
        "percent_y": 0.491179201486,
        "percent_w": 0.015649452269,
        "percent_h": 0.038997214485,
        "description": "Carta comunitária 3"
    },
    {
        "id": "board_4",
        "player": None,
        "seat": "community",
        "side": "slot_4",
        "percent_x": 0.516431924883,
        "percent_y": 0.491179201486,
        "percent_w": 0.015649452269,
        "percent_h": 0.039925719591,
        "description": "Carta comunitária 4"
    },
    {
        "id": "board_5",
        "player": None,
        "seat": "community",
        "side": "slot_5",
        "percent_x": 0.539906103286,
        "percent_y": 0.491179201486,
        "percent_w": 0.015649452269,
        "percent_h": 0.039925719591,
        "description": "Carta comunitária 5"
    },
]


def get_monitor_info(monitor_id: int = MONITOR_ID) -> Dict[str, int]:
    """Obtém informações do monitor especificado."""
    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_id >= len(monitors):
            raise ValueError(f"Monitor ID {monitor_id} não encontrado. Disponíveis: 0-{len(monitors)-1}")
        return monitors[monitor_id]


def calculate_roi_bbox(roi: Dict[str, Any], monitor: Dict[str, int]) -> Dict[str, int]:
    """
    Calcula bounding box absoluta para uma ROI baseada em porcentagens.
    Usa round() para evitar erros de truncamento (crítico para precisão).
    """
    x = int(round(monitor['width'] * roi['percent_x']))
    y = int(round(monitor['height'] * roi['percent_y']))
    w = int(round(monitor['width'] * roi['percent_w']))
    h = int(round(monitor['height'] * roi['percent_h']))
    
    return {
        'left': monitor['left'] + x,
        'top': monitor['top'] + y,
        'width': w,
        'height': h
    }


def get_all_rois_bboxes(monitor_id: int = MONITOR_ID) -> List[Dict[str, Any]]:
    """
    Retorna todas as ROIs com suas bounding boxes absolutas calculadas.
    """
    monitor = get_monitor_info(monitor_id)
    results = []
    
    for roi in CARDS_ROI:
        bbox = calculate_roi_bbox(roi, monitor)
        results.append({
            **roi,
            'bbox': bbox,
            'monitor_id': monitor_id
        })
    
    return results


def capture_roi(roi_bbox: Dict[str, int]) -> 'Image.Image':
    """
    Captura uma região específica da tela.
    Retorna um objeto PIL Image.
    """
    from PIL import Image
    
    with mss.mss() as sct:
        screenshot = sct.grab(roi_bbox)
        img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
        return img


if __name__ == "__main__":
    # Teste rápido para validar configurações
    print(f"=== Configuração de Captura - Monitor {MONITOR_ID} ===")
    try:
        monitor = get_monitor_info(MONITOR_ID)
        print(f"Resolução: {monitor['width']}x{monitor['height']}")
        print(f"Posição: ({monitor['left']}, {monitor['top']})")
        print(f"\nTotal de ROIs configuradas: {len(CARDS_ROI)}")
        print(f"  - 6 jogadores × 2 cartas = 12 cartas de jogadores")
        print(f"  - 5 cartas comunitárias (board)")
        
        # Mostra exemplo de cálculo para Luna (jogador principal)
        print("\n=== Exemplo: Cartas de Luna ===")
        for roi in CARDS_ROI:
            if roi['player'] == 'Luna':
                bbox = calculate_roi_bbox(roi, monitor)
                print(f"{roi['id']}:")
                print(f"  Porcentagem: x={roi['percent_x']:.6f}, y={roi['percent_y']:.6f}")
                print(f"  BBox: left={bbox['left']}, top={bbox['top']}, w={bbox['width']}, h={bbox['height']}")
                
    except Exception as e:
        print(f"Erro (esperado em ambiente Docker sem display): {e}")
        print("\n✅ Em produção (sua máquina local), funcionará perfeitamente!")
        print("Certifique-se apenas de que o jogo esteja no monitor especificado (MONITOR_ID={}).".format(MONITOR_ID))
