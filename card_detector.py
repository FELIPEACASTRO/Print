"""
Módulo de Detecção Automática de Cartas por Visão Computacional

Detecta cartas de baralho em qualquer posição da tela usando:
1. Pré-processamento adaptativo
2. Detecção de contornos
3. Filtragem geométrica (formato retangular de carta)
4. Correção de perspectiva e rotação
5. Identificação via hashing
"""

import cv2
import numpy as np
from PIL import Image
import mss
from typing import List, Dict, Tuple, Optional
import base64
from io import BytesIO

# Importa configurações
from config_loader import config_loader
from deck_config import DeckDatabase


class CardDetector:
    """Detector de cartas baseado em visão computacional"""
    
    def __init__(self):
        self.deck_db = DeckDatabase()
        # Usa o loader global diretamente
        self.config_data = config_loader._load_config() if hasattr(config_loader, '_load_config') else {}
        
        # Parâmetros de detecção (ajustáveis via config)
        detection_params = self.config_data.get('detection_params', {})
        self.min_card_area = detection_params.get('min_card_area', 500)
        self.max_card_area = detection_params.get('max_card_area', 50000)
        self.card_aspect_ratio_min = detection_params.get('card_aspect_ratio_min', 1.2)
        self.card_aspect_ratio_max = detection_params.get('card_aspect_ratio_max', 1.8)
        self.contour_approx_epsilon = detection_params.get('contour_approx_epsilon', 0.02)
        
    def capture_screen(self, monitor_id: int = 1) -> np.ndarray:
        """Captura a tela inteira do monitor especificado"""
        with mss.mss() as sct:
            monitors = sct.monitors
            if monitor_id >= len(monitors):
                monitor_id = 1  # Fallback para monitor principal
            
            monitor = monitors[monitor_id]
            screenshot = sct.grab(monitor)
            
            # Converte para numpy array (RGB)
            img = np.array(screenshot)
            return img[:, :, :3]  # Remove canal alpha se existir
    
    def preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Pré-processa a imagem para destacar cartas
        Retorna: (imagem processada, máscara de cartas)
        """
        # Converte para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Aplica blur para reduzir ruído
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detecta bordas usando Canny
        edges = cv2.Canny(blurred, 50, 150)
        
        # Threshold adaptativo para destacar regiões claras (cartas)
        # Cartas geralmente são mais claras que o fundo da mesa
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Combina edges e threshold
        mask = cv2.bitwise_or(edges, thresh)
        
        # Operações morfológicas para conectar regiões
        kernel = np.ones((5, 5), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=2)
        eroded_mask = cv2.erode(dilated_mask, kernel, iterations=1)
        
        return eroded_mask, gray
    
    def find_card_contours(self, mask: np.ndarray, original_image: np.ndarray) -> List[Dict]:
        """
        Encontra contornos que correspondem a cartas
        Retorna lista de dicionários com informações de cada carta detectada
        """
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_cards = []
        
        for contour in contours:
            # Aproxima o contorno para um polígono
            epsilon = self.contour_approx_epsilon * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Filtra por número de vértices (retângulo tem 4)
            if len(approx) != 4:
                continue
            
            # Calcula área
            area = cv2.contourArea(contour)
            if not (self.min_card_area <= area <= self.max_card_area):
                continue
            
            # Calcula proporção (aspect ratio)
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            if not (self.card_aspect_ratio_min <= aspect_ratio <= self.card_aspect_ratio_max):
                continue
            
            # Verifica convexidade (cartas são convexas)
            if not cv2.isContourConvex(approx):
                continue
            
            # Calcula centro
            M = cv2.moments(contour)
            if M['m00'] == 0:
                continue
            center_x = int(M['m10'] / M['m00'])
            center_y = int(M['m01'] / M['m00'])
            
            detected_cards.append({
                'contour': contour,
                'approx': approx,
                'bbox': (x, y, w, h),
                'area': area,
                'aspect_ratio': aspect_ratio,
                'center': (center_x, center_y),
                'screen_position': {
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                }
            })
        
        # Ordena por área (maiores primeiro - provavelmente mais próximas/importantes)
        detected_cards.sort(key=lambda k: k['area'], reverse=True)
        
        return detected_cards
    
    def correct_perspective(self, image: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """
        Corrige perspectiva e rotação da carta
        Retorna a carta "retificada" (vista de frente)
        """
        # Ordena os pontos do contorno: topo-esquerdo, topo-direito, baixo-direito, baixo-esquerdo
        pts = contour.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        
        # Soma dos coordenadas (topo-esquerdo tem menor soma, baixo-direito tem maior)
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # Topo-esquerdo
        rect[2] = pts[np.argmax(s)]  # Baixo-direito
        
        # Diferença (topo-direito tem menor diferença, baixo-esquerdo tem maior)
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # Topo-direito
        rect[3] = pts[np.argmax(diff)]  # Baixo-esquerdo
        
        # Calcula dimensões da nova imagem
        (tl, tr, br, bl) = rect
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))
        
        # Pontos de destino para perspectiva "frontal"
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")
        
        # Aplica transformação de perspectiva
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
    
    def identify_card(self, card_image: np.ndarray) -> Optional[Dict]:
        """
        Identifica a carta usando o sistema de hashing existente
        """
        # Converte para PIL
        pil_image = Image.fromarray(card_image)
        
        # Salva temporariamente para usar o método existente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            pil_image.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Usa o método de identificação existente
            result = self.deck_db.identify_card(temp_path, tolerance=20)
            
            if result and result.get('card'):
                return {
                    'identified': True,
                    'card_code': result['card'].get('code'),
                    'card_name': result['card'].get('name'),
                    'rank': result['card'].get('rank'),
                    'suit': result['card'].get('suit'),
                    'confidence': result.get('confidence', 0.0),
                    'hamming_distance': result.get('hamming_distance', 999)
                }
        finally:
            # Limpa arquivo temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return {'identified': False, 'card_code': None, 'card_name': 'Desconhecida'}
    
    def detect_all_cards(self, monitor_id: int = 1) -> Dict:
        """
        Detecta e identifica TODAS as cartas visíveis na tela
        Retorna estrutura completa compatível com a API
        """
        import time
        start_time = time.time()
        
        # Captura tela
        capture_start = time.time()
        screen_image = self.capture_screen(monitor_id)
        capture_time = (time.time() - capture_start) * 1000
        
        # Pré-processa
        mask, gray = self.preprocess_image(screen_image)
        
        # Encontra contornos de cartas
        card_contours = self.find_card_contours(mask, screen_image)
        
        results = []
        processing_times = []
        
        for idx, card_info in enumerate(card_contours):
            proc_start = time.time()
            
            x, y, w, h = card_info['bbox']
            
            # Recorta região da carta (com margem)
            margin = 5
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(screen_image.shape[1], x + w + margin)
            y2 = min(screen_image.shape[0], y + h + margin)
            
            card_roi = screen_image[y1:y2, x1:x2].copy()
            
            # Corrige perspectiva
            try:
                corrected_card = self.correct_perspective(card_roi, card_info['approx'])
            except Exception as e:
                corrected_card = card_roi  # Fallback para não corrigido
            
            # Identifica carta
            identification = self.identify_card(corrected_card)
            
            proc_time = (time.time() - proc_start) * 1000
            processing_times.append(proc_time)
            
            # Converte para base64
            pil_img = Image.fromarray(corrected_card)
            buffered = BytesIO()
            pil_img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            results.append({
                'roi_id': f'auto_detected_{idx}',
                'player_name': None,  # Não sabemos qual jogador é
                'position': 'auto_detected',
                'screen_coordinates': card_info['screen_position'],
                'identified_card': {
                    'code': identification.get('card_code') or 'UNKNOWN',
                    'rank': identification.get('rank') or '?',
                    'suit': identification.get('suit') or 'UNKNOWN',
                    'name': identification.get('card_name') or 'Desconhecida',
                    'is_coringa': False
                },
                'confidence': {
                    'score': identification.get('confidence', 0.0),
                    'hamming_distance': identification.get('hamming_distance', 999),
                    'algorithm_used': 'pHash+dHash+perspective_correction'
                },
                'validation': {
                    'external_status': 'not_validated',
                    'api_latency_ms': 0,
                    'message': 'Detecção automática - sem validação externa'
                },
                'screenshot_base64': f'data:image/png;base64,{img_base64}',
                'processing_details': {
                    'hash_calculation_ms': proc_time,
                    'perspective_correction_applied': True
                }
            })
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            'status': 'success' if results else 'no_cards_found',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'monitor_id': monitor_id,
            'resolution': {
                'width': screen_image.shape[1],
                'height': screen_image.shape[0]
            },
            'metrics': {
                'total_time_ms': total_time,
                'capture_time_ms': capture_time,
                'processing_time_ms': sum(processing_times),
                'cards_detected': len(results),
                'detection_method': 'computer_vision_contours'
            },
            'cards': results,
            'detection_info': {
                'total_contours_analyzed': len(card_contours),
                'min_area_threshold': self.min_card_area,
                'aspect_ratio_range': [self.card_aspect_ratio_min, self.card_aspect_ratio_max]
            }
        }


# Instância singleton
detector = CardDetector()


def detect_cards_on_screen(monitor_id: int = 1) -> Dict:
    """Função convenience para detectar cartas"""
    return detector.detect_all_cards(monitor_id)
