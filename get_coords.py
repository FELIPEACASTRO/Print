import tkinter as tk
from tkinter import ttk, messagebox

class CoordinatePicker:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Seletor de Coordenadas - Captura de Tela")
        self.root.attributes('-topmost', True)
        self.root.geometry("500x300")
        
        # Instruções
        instructions = """
📋 INSTRUÇÕES DE USO:

1. MINIMIZE esta janela temporariamente
2. POSICIONE o mouse no CANTO SUPERIOR ESQUERDO da área onde está a carta
3. ANOTE as coordenadas X e Y que aparecem abaixo
4. MOVA o mouse para o CANTO INFERIOR DIREITO da mesma área
5. ANOTE novamente as coordenadas
6. DIGITE os 4 valores nos campos abaixo e clique em "Salvar Configuração"

💡 DICA: Deixe o navegador com o jogo/poker em tela cheia em UM monitor
         e use este outro monitor para trabalhar normalmente!
        """
        
        lbl = ttk.Label(root, text=instructions.strip(), justify='left', font=("Arial", 9))
        lbl.pack(pady=10)
        
        # Frame de coordenadas
        coord_frame = ttk.Frame(root)
        coord_frame.pack(pady=10)
        
        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, padx=5)
        self.x_entry = ttk.Entry(coord_frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(coord_frame, text="Y:").grid(row=0, column=2, padx=5)
        self.y_entry = ttk.Entry(coord_frame, width=10)
        self.y_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(coord_frame, text="Width:").grid(row=1, column=0, padx=5, pady=5)
        self.width_entry = ttk.Entry(coord_frame, width=10)
        self.width_entry.insert(0, "200")
        self.width_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(coord_frame, text="Height:").grid(row=1, column=2, padx=5, pady=5)
        self.height_entry = ttk.Entry(coord_frame, width=10)
        self.height_entry.insert(0, "300")
        self.height_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Label dinâmico
        self.coord_label = ttk.Label(root, text="Movimente o mouse para ver coordenadas...", 
                                     font=("Courier", 11), foreground="blue")
        self.coord_label.pack(pady=10)
        
        # Botões
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)
        
        self.btn_copy = ttk.Button(btn_frame, text="📋 Copiar JSON", command=self.copy_config)
        self.btn_copy.grid(row=0, column=0, padx=5)
        
        self.btn_save = ttk.Button(btn_frame, text="💾 Salvar em config.json", command=self.save_config)
        self.btn_save.grid(row=0, column=1, padx=5)
        
        self.last_x = 0
        self.last_y = 0
        
        root.bind('<Motion>', self.update_coords)
        
    def update_coords(self, event):
        # Pega coordenadas globais da tela
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.last_x = x
        self.last_y = y
        self.coord_label.config(text=f"📍 Posição atual: X={x}, Y={y}")

    def copy_config(self):
        try:
            left = int(self.x_entry.get()) if self.x_entry.get() else self.last_x
            top = int(self.y_entry.get()) if self.y_entry.get() else self.last_y
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            
            config = f'''# Configuração de Captura de Tela
# Cole isto no seu código ou arquivo de configuração

MONITOR_INDEX = 1  # Mude para 2 se for capturar do outro monitor

CAPTURE_REGION = {{
    "left": {left},
    "top": {top},
    "width": {width},
    "height": {height}
}}

# Exemplo de uso no endpoint /identify:
# screenshot = capture_screen(monitor_index=MONITOR_INDEX, region=CAPTURE_REGION)
'''
            self.root.clipboard_clear()
            self.root.clipboard_append(config)
            messagebox.showinfo("Sucesso!", "Configuração copiada para a área de transferência!\n\nAgora cole no seu código ou arquivo de configuração.")
            print(config)
        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos! Use apenas números.\nErro: {e}")

    def save_config(self):
        try:
            left = int(self.x_entry.get()) if self.x_entry.get() else self.last_x
            top = int(self.y_entry.get()) if self.y_entry.get() else self.last_y
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            
            import json
            config = {
                "monitor_index": 1,
                "region": {
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height
                },
                "description": "Coordenadas da área de captura da carta"
            }
            
            with open('capture_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso!", "Configuração salva em 'capture_config.json'!\n\nArquivo criado na pasta atual.")
            print(f"Config salva: {json.dumps(config, indent=2)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CoordinatePicker(root)
    root.mainloop()
