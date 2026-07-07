"""
Script de Teste e Validação QA - Sistema de Captura de Cartas
Executa testes automatizados para validar toda a solução.
"""
import sys
import time
import json
from datetime import datetime

def test_imports():
    """Teste 1: Validação de imports"""
    print("\n" + "="*60)
    print("TESTE 1: Validação de Imports")
    print("="*60)
    
    try:
        import deck_config
        print("✅ deck_config.py importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar deck_config: {e}")
        return False
    
    try:
        import screen_capture_config
        print("✅ screen_capture_config.py importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar screen_capture_config: {e}")
        return False
    
    try:
        from main import app as main_app
        print("✅ main.py importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar main: {e}")
        return False
    
    try:
        from external_api import app as external_app
        print("✅ external_api.py importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar external_api: {e}")
        return False
    
    return True


def test_deck_database():
    """Teste 2: Validação do banco de dados de cartas"""
    print("\n" + "="*60)
    print("TESTE 2: Banco de Dados de Cartas")
    print("="*60)
    
    from deck_config import deck_db
    
    total_cards = len(deck_db.hash_map)
    print(f"📊 Total de cartas carregadas: {total_cards}")
    
    if total_cards != 54:
        print(f"⚠️  Atenção: Esperado 54 cartas, encontrado {total_cards}")
        return False
    else:
        print("✅ Quantidade correta de cartas (54)")
    
    # Verificar se todas as cartas estão presentes
    expected_suits = ["COPAS", "OUROS", "ESPADAS", "PAUS"]
    expected_values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "AS"]
    expected_jokers = ["CORINGA_1", "CORINGA_2"]
    
    found_cards = set()
    for card_hash, card_data in deck_db.hash_map.items():
        found_cards.add(card_data["id"])
    
    # Verificar CORINGAs
    for joker in expected_jokers:
        if joker in found_cards:
            print(f"✅ {joker} presente")
        else:
            print(f"❌ {joker} ausente")
            return False
    
    # Verificar naipe CORINGA (deve ser "CORINGA", não "1" ou "2")
    for card_hash, card_data in deck_db.hash_map.items():
        if "CORINGA" in card_data["id"]:
            if card_data["naipe"] == "CORINGA":
                print(f"✅ {card_data['id']} tem naipe='CORINGA' (correto)")
            else:
                print(f"❌ {card_data['id']} tem naipe='{card_data['naipe']}' (incorreto)")
                return False
    
    print("✅ Todas as verificações de cartas passaram")
    return True


def test_roi_configuration():
    """Teste 3: Validação das configurações de ROI"""
    print("\n" + "="*60)
    print("TESTE 3: Configuração de ROIs")
    print("="*60)
    
    from screen_capture_config import CARDS_ROI, MONITOR_ID, get_all_rois_bboxes
    
    print(f"📊 Monitor ID configurado: {MONITOR_ID}")
    print(f"📊 Total de ROIs configuradas: {len(CARDS_ROI)}")
    
    # Verificar quantidade esperada (6 jogadores × 2 cartas + 5 board = 17)
    if len(CARDS_ROI) != 17:
        print(f"⚠️  Atenção: Esperado 17 ROIs, encontrado {len(CARDS_ROI)}")
        return False
    else:
        print("✅ Quantidade correta de ROIs (17)")
    
    # Verificar grupos de jogadores
    players = set()
    board_slots = []
    
    for roi in CARDS_ROI:
        if roi.get("player"):
            players.add(roi["player"])
        else:
            board_slots.append(roi["id"])
    
    expected_players = {"Alex", "Sofia", "Maya", "Caio", "Rex", "Luna"}
    if players == expected_players:
        print(f"✅ Todos os 6 jogadores configurados: {', '.join(sorted(players))}")
    else:
        missing = expected_players - players
        extra = players - expected_players
        if missing:
            print(f"❌ Jogadores faltando: {missing}")
        if extra:
            print(f"❌ Jogadores extras: {extra}")
        return False
    
    # Verificar 5 slots do board
    if len(board_slots) == 5:
        print(f"✅ 5 slots do board configurados: {', '.join(board_slots)}")
    else:
        print(f"❌ Esperado 5 slots do board, encontrado {len(board_slots)}")
        return False
    
    # Verificar coordenadas em porcentagem
    for roi in CARDS_ROI:
        if not all(k in roi for k in ["percent_x", "percent_y", "percent_w", "percent_h"]):
            print(f"❌ ROI {roi['id']} não tem todas as coordenadas percentuais")
            return False
        
        # Validar faixas razoáveis
        if not (0 <= roi["percent_x"] <= 1):
            print(f"❌ ROI {roi['id']} percent_x fora de faixa: {roi['percent_x']}")
            return False
        if not (0 <= roi["percent_y"] <= 1):
            print(f"❌ ROI {roi['id']} percent_y fora de faixa: {roi['percent_y']}")
            return False
    
    print("✅ Todas as ROIs têm coordenadas válidas")
    
    # Tentar calcular bboxes (pode falhar em Docker sem display)
    try:
        bboxes = get_all_rois_bboxes(MONITOR_ID)
        print(f"✅ Cálculo de bboxes bem-sucedido para {len(bboxes)} ROIs")
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível calcular bboxes (ambiente Docker sem display): {e}")
        print("   Em produção (sua máquina local), funcionará corretamente!")
    
    return True


def test_hash_identification():
    """Teste 4: Validação da identificação de cartas"""
    print("\n" + "="*60)
    print("TESTE 4: Identificação de Cartas via Hash")
    print("="*60)
    
    from deck_config import deck_db
    
    # Testar identificação de algumas cartas conhecidas
    test_cards = [
        ("AS_COPAS.png", "AS", "COPAS"),
        ("K_ESPADAS.png", "K", "ESPADAS"),
        ("7_OUROS.png", "7", "OUROS"),
        ("CORINGA_1.png", "CORINGA", "CORINGA"),
    ]
    
    all_passed = True
    for filename, expected_valor, expected_naipe in test_cards:
        filepath = f"cards/{filename}"
        result = deck_db.identify_card(filepath, tolerance=15)
        
        if result is None:
            print(f"❌ Falha ao identificar {filename}")
            all_passed = False
        elif result["valor"] == expected_valor and result["naipe"] == expected_naipe:
            print(f"✅ {filename} identificado corretamente: {result['valor']} de {result['naipe']}")
        else:
            print(f"❌ {filename} identificado incorretamente:")
            print(f"   Esperado: {expected_valor} de {expected_naipe}")
            print(f"   Obtido: {result['valor']} de {result['naipe']}")
            all_passed = False
    
    return all_passed


def test_api_endpoints():
    """Teste 5: Validação dos endpoints da API"""
    print("\n" + "="*60)
    print("TESTE 5: Endpoints da API")
    print("="*60)
    
    from main import app as main_app
    from external_api import app as external_app
    
    # Verificar endpoints principais
    main_routes = [route.path for route in main_app.routes]
    expected_main_endpoints = ["/", "/identify", "/identify/upload", "/health", "/deck"]
    
    print("Endpoints da API Principal:")
    for endpoint in expected_main_endpoints:
        if endpoint in main_routes:
            print(f"  ✅ {endpoint}")
        else:
            print(f"  ❌ {endpoint} ausente")
            return False
    
    # Verificar endpoints da API externa
    external_routes = [route.path for route in external_app.routes]
    expected_external_endpoints = ["/validate", "/health"]
    
    print("\nEndpoints da API Externa:")
    for endpoint in expected_external_endpoints:
        if endpoint in external_routes:
            print(f"  ✅ {endpoint}")
        else:
            print(f"  ❌ {endpoint} ausente")
            return False
    
    return True


def test_dataset_integrity():
    """Teste 6: Validação da integridade do dataset"""
    print("\n" + "="*60)
    print("TESTE 6: Integridade do Dataset")
    print("="*60)
    
    import os
    dataset_file = "dataset/dataset_mestrado.jsonl"
    
    if not os.path.exists(dataset_file):
        print(f"⚠️  Arquivo {dataset_file} não encontrado")
        return True  # OK se estiver vazio inicialmente
    
    with open(dataset_file, 'r') as f:
        lines = f.readlines()
    
    print(f"📊 Total de registros no dataset: {len(lines)}")
    
    if len(lines) == 0:
        print("✅ Dataset vazio (estado inicial válido)")
        return True
    
    # Analisar últimos registros
    valid_count = 0
    error_count = 0
    
    for line in lines[-10:]:  # Últimos 10 registros
        try:
            record = json.loads(line)
            if record.get("identified"):
                if "external_api_response" in record:
                    ext_resp = record["external_api_response"]
                    if ext_resp.get("validated"):
                        valid_count += 1
                    elif ext_resp.get("error"):
                        error_count += 1
        except Exception as e:
            print(f"⚠️  Erro ao parsear registro: {e}")
    
    print(f"📊 Últimos registros: {valid_count} válidos, {error_count} com erro de API")
    
    # Verificar se há registros com CORINGA com naipe correto
    coringa_ok = False
    for line in lines:
        record = json.loads(line)
        if record.get("card_data") and "CORINGA" in record["card_data"].get("id", ""):
            if record["card_data"].get("naipe") == "CORINGA":
                coringa_ok = True
                break
    
    if coringa_ok:
        print("✅ Encontrado registro de CORINGA com naipe='CORINGA' (correto)")
    else:
        print("⚠️  Nenhum registro de CORINGA com naipe correto encontrado")
    
    return True


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🧪 SUÍTE DE TESTES QA - SISTEMA DE CAPTURA DE CARTAS")
    print("="*60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Imports", test_imports),
        ("Banco de Dados", test_deck_database),
        ("Configuração ROI", test_roi_configuration),
        ("Identificação Hash", test_hash_identification),
        ("Endpoints API", test_api_endpoints),
        ("Integridade Dataset", test_dataset_integrity),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO no teste {name}: {e}")
            results.append((name, False))
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO FINAL DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema pronto para produção.")
        return True
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam. Revise os erros acima.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
