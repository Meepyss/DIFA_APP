import mysql.connector

def conectar_banco():
    """
    Configura a conexão com o banco de dados.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="151322",
        database="meu_banco"
    )

def consultar_aliquota(ncm):
    """
    Consulta a alíquota de ICMS no banco de dados para um dado NCM.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    query = "SELECT aliquota FROM ncm_aliquotas WHERE ncm = %s"
    cursor.execute(query, (ncm,))
    
    resultado = cursor.fetchone()
    
    cursor.close()
    conexao.close()
    
    if resultado:
        return float(resultado[0])
    return None
