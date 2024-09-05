import pandas as pd

def carregar_planilha(caminho_planilha):
    """
    Carrega a planilha de entradas a partir de um arquivo Excel.
    """
    return pd.read_excel(caminho_planilha)

def buscar_aliquota_na_planilha(linha_sped, planilha):
    """
    Busca a alíquota de ICMS na planilha para uma determinada nota fiscal.
    """
    campos = linha_sped.split('|')
    chave_nota = campos[0]  # Exemplo de campo que representa o identificador da nota
    
    # Buscar na planilha por uma nota correspondente
    filtro = planilha[planilha['ChaveNota'] == chave_nota]
    
    if not filtro.empty:
        # Se houver correspondência, retorna a alíquota
        return filtro.iloc[0]['AliquotaICMS']
    
    return None
