"""
Script para gerar imagens de teste (cartas de baralho simuladas)
Cria 52 cartas + 2 coringas com designs MAIS DISTINTOS para garantir hashes únicos.
"""
from PIL import Image, ImageDraw
import os

def create_card_image(valor, naipe, output_path):
    """Cria uma imagem representando uma carta com design único."""
    # Cores dos naipes
    colors = {
        "COPAS": "red",
        "OUROS": "darkorange",
        "ESPADAS": "darkblue",
        "PAUS": "darkgreen",
        "CORINGA": "purple"
    }
    
    symbols = {
        "COPAS": "♥",
        "OUROS": "♦",
        "ESPADAS": "♠",
        "PAUS": "♣",
        "CORINGA": "★"
    }
    
    # Criar imagem com fundo colorido baseado no naipe para maior distinção
    base_color = colors.get(naipe, "white")
    img = Image.new('RGB', (200, 300), 'white')
    draw = ImageDraw.Draw(img)
    
    # Borda com cor do naipe
    draw.rectangle([5, 5, 195, 295], outline=base_color, width=4)
    draw.rectangle([10, 10, 190, 290], outline='black', width=2)
    
    symbol = symbols.get(naipe, "?")
    color = colors.get(naipe, "black")
    
    # Desenhar símbolo GRANDE no centro baseado no valor
    # Quantidade de símbolos varia conforme o valor para distinção máxima
    num_symbols = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
        "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 1, "Q": 1, "K": 1, "AS": 1, "CORINGA": 3
    }.get(valor, 1)
    
    # Símbolo central grande
    font_size = 80 if valor in ["J", "Q", "K", "AS", "CORINGA"] else 50
    draw.text((75, 100), symbol, fill=color, font_size=font_size)
    
    # Texto do valor no topo (grande e claro)
    draw.text((15, 10), str(valor), fill=color, font_size=40)
    
    # Adicionar símbolos menores espalhados para valores numéricos
    if valor.isdigit() or valor == "10":
        positions = [
            (50, 80), (150, 80),
            (50, 150), (150, 150),
            (50, 220), (150, 220),
            (100, 120), (100, 180)
        ][:num_symbols]
        for pos in positions:
            draw.text(pos, symbol, fill=color, font_size=25)
    
    # Valor embaixo (invertido visualmente)
    draw.text((155, 250), str(valor), fill=color, font_size=40)
    
    # Salvar imagem
    img.save(output_path)
    print(f"Criada: {output_path}")

# Criar diretório se não existir
os.makedirs("cards", exist_ok=True)

# Limpar cartas antigas
for f in os.listdir("cards"):
    os.remove(os.path.join("cards", f))

# Valores e naipes do baralho convencional
valores = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "AS"]
naipes = ["COPAS", "OUROS", "ESPADAS", "PAUS"]

# Gerar 52 cartas
count = 0
for naipe in naipes:
    for valor in valores:
        filename = f"{valor}_{naipe}.png"
        filepath = os.path.join("cards", filename)
        create_card_image(valor, naipe, filepath)
        count += 1

# Adicionar 2 coringas
create_card_image("CORINGA", "CORINGA", "cards/CORINGA_1.png")
create_card_image("CORINGA", "CORINGA", "cards/CORINGA_2.png")
count += 2

print(f"\nTotal de {count} cartas criadas na pasta 'cards/'")
print("Pronto para iniciar o servidor!")
