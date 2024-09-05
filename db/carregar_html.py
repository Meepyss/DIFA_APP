from bs4 import BeautifulSoup
from db.database import conectar_banco

def carregar_dados_html(caminho_html):
    """
    Lê o arquivo HTML e carrega as informações de NCM e alíquotas no banco de dados.
    """
    # Abrir o arquivo HTML com a codificação utf-8
    with open(caminho_html, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        
        # Tenta encontrar o corpo da tabela no HTML
        tabela = soup.find('tbody')  # Alterei para buscar o 'tbody', que contém as linhas de dados
        
        if tabela is None:
            print("Nenhuma tabela foi encontrada no arquivo HTML.")
            return
        
        # Agora vamos iterar pelas linhas da tabela
        linhas = tabela.find_all('tr')
        
        conexao = conectar_banco()
        cursor = conexao.cursor()
        
        for linha in linhas:
            colunas = linha.find_all('td')
            if len(colunas) >= 3:
                aliquota = colunas[0].text.strip().replace('%', '').strip()
                ncm = colunas[1].text.strip()
                descricao = colunas[2].text.strip()[:255]  # Limitar a descrição a 255 caracteres


                if ncm != '-':  # Ignora NCMs que são apenas "-"
                    try:
                        aliquota_float = float(aliquota)
                        # Insere os dados no banco de dados
                        cursor.execute("""
                            INSERT INTO ncm_aliquotas (ncm, descricao, aliquota)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE aliquota = VALUES(aliquota)
                        """, (ncm, descricao, aliquota_float))
                    except ValueError:
                        print(f"Erro ao converter a alíquota para número: {aliquota}")
        
        conexao.commit()
        cursor.close()
        conexao.close()
