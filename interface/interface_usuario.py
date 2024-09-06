import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
from tkinter.ttk import Progressbar
import time
from sped.processador_sped import processar_arquivo_sped  # Certifique-se de que a importação está correta

def validar_arquivo_sped(caminho_arquivo):
    return caminho_arquivo.endswith('.txt')

def validar_planilha_excel(caminho_arquivo):
    return caminho_arquivo.endswith('.xlsx')

def selecionar_arquivo_sped():
    caminho_arquivo_sped = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
    
    if caminho_arquivo_sped and validar_arquivo_sped(caminho_arquivo_sped):
        lbl_sped["text"] = f"Arquivo SPED Selecionado: {os.path.basename(caminho_arquivo_sped)}"
        root.caminho_sped = caminho_arquivo_sped
    else:
        messagebox.showerror("Erro", "Por favor, selecione um arquivo SPED válido (.txt).")

def selecionar_planilha_excel():
    caminho_planilha_excel = filedialog.askopenfilename(filetypes=[("Arquivos Excel", "*.xlsx")])
    
    if caminho_planilha_excel and validar_planilha_excel(caminho_planilha_excel):
        lbl_planilha["text"] = f"Planilha Excel Selecionada: {os.path.basename(caminho_planilha_excel)}"
        root.caminho_excel = caminho_planilha_excel
    else:
        messagebox.showerror("Erro", "Por favor, selecione um arquivo Excel válido (.xlsx).")

def processar_arquivos():
    if hasattr(root, 'caminho_sped') and hasattr(root, 'caminho_excel'):
        progress_bar["value"] = 0
        lbl_status["text"] = "Processando arquivos..."
        thread = threading.Thread(target=executar_processamento)
        thread.start()
    else:
        messagebox.showerror("Erro", "Selecione ambos os arquivos (SPED e Planilha Excel).")

def executar_processamento():
    """
    Executa o processamento chamando a função `processar_arquivo_sped`
    e atualiza a barra de progresso durante o processamento.
    """
    try:
        # Chama a função processar_arquivo_sped
        processar_arquivo_sped(root.caminho_sped, "arquivo_sped_modificado.txt", root.caminho_excel)

        # Simula uma barra de progresso durante o processamento
        for i in range(1, 101):
            time.sleep(0.05)  # Simula o tempo de processamento
            progress_bar["value"] = i
            root.update_idletasks()

        lbl_status["text"] = "Processamento Concluído!"
        messagebox.showinfo("Sucesso", "O processamento foi concluído com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante o processamento: {str(e)}")

# Criação da interface
root = tk.Tk()
root.title("Processador de Arquivos SPED")
root.geometry("500x300")

lbl_sped = tk.Label(root, text="Nenhum arquivo SPED selecionado")
lbl_sped.pack(pady=10)

btn_sped = tk.Button(root, text="Selecionar Arquivo SPED (.txt)", command=selecionar_arquivo_sped)
btn_sped.pack(pady=10)

lbl_planilha = tk.Label(root, text="Nenhuma planilha Excel selecionada")
lbl_planilha.pack(pady=10)

btn_excel = tk.Button(root, text="Selecionar Planilha Excel (.xlsx)", command=selecionar_planilha_excel)
btn_excel.pack(pady=10)

progress_bar = Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=20)

btn_processar = tk.Button(root, text="Processar Arquivos", command=processar_arquivos)
btn_processar.pack(pady=10)

lbl_status = tk.Label(root, text="")
lbl_status.pack(pady=10)

root.mainloop()
