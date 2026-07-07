"""
Config Loader - Carrega configurações do arquivo config.json
Permite parametrização completa sem modificar o código Python.
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

CONFIG_FILE = "config.json"

class ConfigLoader:
    """Carregador de configurações parametrizáveis."""
    
    def __init__(self, config_path: str = CONFIG_FILE):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega o arquivo JSON de configuração."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_system_config(self) -> Dict[str, Any]:
        """Retorna configurações gerais do sistema."""
        return self.config.get("system_config", {})
    
    def get_monitor_profiles(self) -> List[Dict[str, Any]]:
        """Retorna todos os perfis de monitor disponíveis."""
        return self.config.get("monitor_profiles", [])
    
    def get_active_profile(self) -> Dict[str, Any]:
        """Retorna o perfil de monitor ativo."""
        active_profile_id = self.config.get("active_profile")
        profiles = self.get_monitor_profiles()
        
        for profile in profiles:
            if profile.get("profile_id") == active_profile_id:
                return profile
        
        # Retorna o primeiro perfil se o ativo não for encontrado
        return profiles[0] if profiles else {}
    
    def get_cards_roi(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """
        Retorna todas as ROIs de cartas configuradas.
        
        Args:
            enabled_only: Se True, retorna apenas ROIs habilitadas
        """
        cards_roi = self.config.get("cards_roi", [])
        
        if enabled_only:
            return [roi for roi in cards_roi if roi.get("enabled", True)]
        
        return cards_roi
    
    def get_roi_by_id(self, roi_id: str) -> Optional[Dict[str, Any]]:
        """Retorna uma ROI específica pelo ID."""
        cards_roi = self.get_cards_roi(enabled_only=False)
        
        for roi in cards_roi:
            if roi.get("id") == roi_id:
                return roi
        
        return None
    
    def get_tolerance(self) -> int:
        """Retorna a tolerância para identificação de cartas."""
        return self.config.get("system_config", {}).get("identification_tolerance", 15)
    
    def use_round_for_coords(self) -> bool:
        """Verifica se deve usar round() para cálculo de coordenadas."""
        return self.config.get("system_config", {}).get("use_round_for_coords", True)
    
    def get_external_api_url(self) -> str:
        """Retorna URL da API externa."""
        return self.config.get("system_config", {}).get("api_external_url", "http://localhost:8001/validate")
    
    def get_dataset_file(self) -> str:
        """Retorna caminho do arquivo de dataset."""
        return self.config.get("system_config", {}).get("dataset_file", "dataset/dataset_mestrado.jsonl")
    
    def get_screenshot_dir(self) -> str:
        """Retorna diretório de screenshots."""
        return self.config.get("system_config", {}).get("screenshot_dir", "screenshots")


# Instância global para uso direto
config_loader = ConfigLoader()


def load_config_from_file(config_path: str = CONFIG_FILE) -> ConfigLoader:
    """Função utilitária para carregar configuração."""
    return ConfigLoader(config_path)


if __name__ == "__main__":
    # Teste rápido do carregador
    print("=== Teste do Config Loader ===\n")
    
    try:
        loader = ConfigLoader()
        
        print("Configurações do Sistema:")
        sys_config = loader.get_system_config()
        for key, value in sys_config.items():
            print(f"  {key}: {value}")
        
        print(f"\nPerfil Ativo: {loader.get_active_profile().get('profile_id')}")
        
        print(f"\nTotal de ROIs configuradas: {len(loader.get_cards_roi())}")
        print(f"ROIs habilitadas: {len(loader.get_cards_roi(enabled_only=True))}")
        
        print("\nJogadores configurados:")
        players = set()
        for roi in loader.get_cards_roi():
            if roi.get("player"):
                players.add(roi["player"])
        
        for player in sorted(players):
            print(f"  - {player}")
        
        print("\n✅ Configuração carregada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
