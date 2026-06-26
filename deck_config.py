"""
Configuração do Baralho e Cache de Hashes (pHash + dHash)
Pré-processa as imagens das cartas para identificação ultrarrápida.
Usa combinação de múltiplos hashes para máxima precisão.
"""
import os
import imagehash
from PIL import Image
from typing import Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeckDatabase:
    def __init__(self, cards_dir: str = "cards"):
        self.cards_dir = cards_dir
        self.hash_map: Dict[str, dict] = {}  # combined_hash -> metadata
        self.load_deck()
    
    def _compute_combined_hash(self, img: Image.Image) -> str:
        """Calcula hash combinado (pHash + dHash + aHash) para máxima precisão."""
        phash = imagehash.phash(img, hash_size=8)
        dhash = imagehash.dhash(img, hash_size=8)
        ahash = imagehash.average_hash(img, hash_size=8)
        # Combina os três hashes em uma string única
        return f"{str(phash)}_{str(dhash)}_{str(ahash)}"
    
    def _compute_distance(self, hash1: str, hash2: str) -> int:
        """Calcula distância de Hamming entre dois hashes combinados."""
        try:
            h1_parts = hash1.split('_')
            h2_parts = hash2.split('_')
            
            total_distance = 0
            for i in range(3):
                hash_a = imagehash.hex_to_hash(h1_parts[i])
                hash_b = imagehash.hex_to_hash(h2_parts[i])
                total_distance += (hash_a - hash_b)
            
            return total_distance
        except:
            return float('inf')
    
    def load_deck(self):
        """Carrega todas as cartas da pasta e calcula seus hashes combinados."""
        if not os.path.exists(self.cards_dir):
            logger.warning(f"Diretório {self.cards_dir} não encontrado. Crie-o e adicione as imagens das cartas.")
            return
        
        files = [f for f in os.listdir(self.cards_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not files:
            logger.warning(f"Nenhuma imagem de carta encontrada em {self.cards_dir}")
            return
            
        logger.info(f"Processando {len(files)} cartas...")
        
        for filename in sorted(files):
            filepath = os.path.join(self.cards_dir, filename)
            try:
                # Extrair metadados do nome do arquivo (ex: AS_COPAS.png -> valor=AS, naipe=COPAS)
                name_without_ext = os.path.splitext(filename)[0]
                parts = name_without_ext.split('_')
                
                if len(parts) >= 2:
                    valor = parts[0]
                    # Caso especial para CORINGA
                    if valor == "CORINGA":
                        naipe = "CORINGA"
                    else:
                        naipe = '_'.join(parts[1:])
                else:
                    valor = name_without_ext
                    naipe = "DESCONHECIDO"
                
                # Carregar imagem e calcular hash combinado
                img = Image.open(filepath).convert('L')  # Escala de cinza
                combined_hash = self._compute_combined_hash(img)
                
                # Armazenar no mapa
                self.hash_map[combined_hash] = {
                    "id": name_without_ext,
                    "filename": filename,
                    "valor": valor,
                    "naipe": naipe,
                    "path": filepath,
                    "hash": combined_hash
                }
                
                logger.debug(f"Carta carregada: {filename} -> Hash: {combined_hash[:30]}...")
                
            except Exception as e:
                logger.error(f"Erro ao processar {filename}: {str(e)}")
        
        logger.info(f"Baralho carregado com sucesso: {len(self.hash_map)} cartas registradas.")
    
    def identify_card(self, image_path: str, tolerance: int = 15) -> Optional[dict]:
        """
        Identifica uma carta comparando seu hash combinado com o banco de dados.
        tolerance: diferença máxima de bits aceita (soma das 3 distâncias)
        """
        try:
            # Carregar e processar imagem de entrada
            img = Image.open(image_path).convert('L')
            query_hash = self._compute_combined_hash(img)
            
            # Busca exata primeiro
            if query_hash in self.hash_map:
                return self.hash_map[query_hash]
            
            # Busca aproximada (tolerante a pequenas variações)
            best_match = None
            min_distance = float('inf')
            
            for stored_hash, metadata in self.hash_map.items():
                distance = self._compute_distance(query_hash, stored_hash)
                if distance <= tolerance and distance < min_distance:
                    min_distance = distance
                    best_match = metadata
            
            if best_match:
                logger.info(f"Carta identificada: {best_match['id']} (distância: {min_distance})")
                return best_match
            
            logger.warning("Nenhuma carta correspondente encontrada.")
            return None
            
        except Exception as e:
            logger.error(f"Erro na identificação: {str(e)}")
            return None

# Instância global para uso no servidor
deck_db = DeckDatabase()
