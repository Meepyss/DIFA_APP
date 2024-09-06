from sped.processador_sped import processar_arquivo_sped
from planilha.leitor_planilha import carregar_planilha
from db.carregar_html import carregar_dados_html
from interface.interface_usuario import *


# Caminho dos arquivos de entrada e saída
caminho_arquivo_sped = 'data/arquivo_sped.txt'
caminho_novo_arquivo_sped = 'data/arquivo_sped_mod.txt'
caminho_planilha_entradas = 'data/entradas.xlsx'
caminho_arquivo_html = 'data/dados.html'

if __name__ == '__main__':
    # Carregar as informações do arquivo HTML no banco de dados
    carregar_dados_html(caminho_arquivo_html)
    
    # Carrega a planilha de entradas
    planilha = carregar_planilha(caminho_planilha_entradas)
    
    # Inicia o processamento do arquivo SPED
    processar_arquivo_sped(caminho_arquivo_sped, caminho_novo_arquivo_sped, planilha)
