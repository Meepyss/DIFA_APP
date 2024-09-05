import logging
from db.database import consultar_aliquota
from sped.difa import calcular_difa
from planilha.leitor_planilha import buscar_aliquota_na_planilha

def extrair_ncm(linha_c170):
    """
    Extrai o NCM do registro C170 do arquivo SPED.
    O NCM está localizado no índice 12 do registro.
    """
    campos = linha_c170.split('|')
    return campos[12]

def extrair_base_calculo_icms(linha_c170):
    """
    Extrai a base de cálculo e a alíquota do ICMS da linha C170 do arquivo SPED.
    """
    campos = linha_c170.split('|')
    
    # Posição 13: Base de cálculo do ICMS (ajuste conforme o layout específico)
    base_calculo_icms = float(campos[13]) if campos[13] else 0.0

    # Posição 14: Alíquota do ICMS
    icms_aliquota = float(campos[14]) if campos[14] else 0.0

    return base_calculo_icms, icms_aliquota

def extrair_identificacao_nota(linha_c170):
    """
    Extrai a identificação da nota fiscal do registro C170 do arquivo SPED.
    O número da nota está no índice 2.
    """
    campos = linha_c170.split('|')
    return campos[2]

def alterar_registro_c197(linha_c170, difa):
    """
    Modifica ou cria um novo registro C197 com as informações do DIFAL calculado.
    """
    campos = linha_c170.split('|')

    # Exemplo de construção de um registro C197 com informações fictícias
    registro_c197 = [
        "C197",            # Código do registro
        "MS70000001",      # COD_AJ - Código do ajuste (DIFAL)
        "",                # Descrição
        "",                # Código ICMS
        str(campos[13]),   # VL_BC_ICMS - Valor da base de cálculo
        "12.00",           # ALIQ_ICMS - Alíquota de ICMS aplicada (exemplo)
        str(difa),         # VL_ICMS - Valor do DIFAL calculado
    ]
    
    # Adiciona o registro C197 logo após o registro C170
    return '|'.join(campos) + '\n' + '|'.join(registro_c197)

def log_alteracoes(notas_alteradas):
    """
    Loga e exibe detalhes das notas fiscais alteradas com os valores de DIFAL calculados.
    """
    logging.basicConfig(filename='alteracoes_notas.log', level=logging.INFO)
    for nota, difa_value in notas_alteradas.items():
        logging.info(f"Nota Fiscal Alterada: {nota}, Valor DIFAL Calculado: {difa_value}")
        print(f"Nota Fiscal Alterada: {nota}, Valor DIFAL Calculado: {difa_value}")

def gerar_arquivo_sped_alterado(arquivo_sped_original, notas_alteradas, arquivo_saida):
    """
    Gera um novo arquivo SPED com os registros C197, C195 e 0460 atualizados para cada nota fiscal alterada.
    """
    with open(arquivo_saida, 'w') as novo_sped:
        with open(arquivo_sped_original, 'r') as arquivo_sped:
            for linha in arquivo_sped:
                novo_sped.write(linha)
                # Inserir registros C197, C195 e 0460 para notas alteradas
                for nota, difa_value in notas_alteradas.items():
                    if verificar_nota_alterada(linha, nota):  # Função para verificar se essa linha corresponde a uma nota alterada
                        # Adiciona o Registro 0460
                        novo_sped.write(f"|0460|{gerar_cod_obs(nota)}|Observação referente ao ajuste de DIFAL|\n")
                        # Adiciona o Registro C195
                        novo_sped.write(f"|C195|{gerar_cod_obs(nota)}|Ajuste de diferencial de alíquota|\n")
                        # Adiciona o Registro C197
                        novo_sped.write(f"|C197|MS70000001|DIFAL ICMS|{difa_value}|...\n")
    print(f"Arquivo SPED atualizado e salvo em {arquivo_saida}")

def processar_arquivo_sped(caminho_arquivo_sped, caminho_novo_arquivo_sped, planilha):
    notas_alteradas = {}  # Usaremos um dicionário para armazenar notas e o valor do DIFAL

    with open(caminho_arquivo_sped, 'r') as arquivo_sped, open(caminho_novo_arquivo_sped, 'w') as novo_arquivo:
        for linha in arquivo_sped:
            if linha.startswith('C170'):  # Processa registros C170
                ncm = extrair_ncm(linha)  # Extrair o NCM usando a função extrair_ncm
                icms_aliquota = consultar_aliquota(ncm)

                # Verifica CFOP 1556 ou 2556
                if cfop_uso_consumo(linha):
                    if not icms_aliquota:
                        # Busca a alíquota na planilha se estiver ausente no SPED
                        icms_aliquota = buscar_aliquota_na_planilha(linha, planilha)

                if icms_aliquota and icms_aliquota < 17:
                    base_calculo_icms, aliquota = extrair_base_calculo_icms(linha)
                    difa = calcular_difa(base_calculo_icms, icms_aliquota)
                    linha_modificada = alterar_registro_c197(linha, difa)

                    # Armazenar os dados da nota fiscal e o valor do DIFAL calculado
                    notas_alteradas[extrair_identificacao_nota(linha)] = difa

                    novo_arquivo.write(linha_modificada + '\n')
                else:
                    novo_arquivo.write(linha + '\n')
            else:
                novo_arquivo.write(linha + '\n')

    # Logar e exibir as notas fiscais alteradas
    log_alteracoes(notas_alteradas)

    # Gerar um arquivo SPED com os registros C197, C195, e 0460
    gerar_arquivo_sped_alterado(caminho_novo_arquivo_sped, notas_alteradas, 'sped_arquivo_final.txt')

