import logging
from db.database import consultar_aliquota
from sped.difa import calcular_difa
from planilha.leitor_planilha import buscar_aliquota_na_planilha

def extrair_ncm(linha_c170):
    campos = linha_c170.split('|')
    return campos[12]  # Ajuste conforme a posição do NCM

def extrair_base_calculo_icms(linha_c170):
    campos = linha_c170.split('|')
    return float(campos[13]) if campos[13] else 0.0, float(campos[14]) if campos[14] else 0.0  # Ajuste conforme a posição da base de cálculo

def extrair_identificacao_nota(linha_c170):
    campos = linha_c170.split('|')
    return campos[2]  # Ajuste conforme a posição da identificação da nota

def alterar_registro_c197(linha_c170, difa):
    campos = linha_c170.split('|')
    registro_c197 = [
        "C197",            # Código do registro
        "MS70000001",      # COD_AJ - Código do ajuste (DIFAL)
        "",                # Descrição
        "",                # Código ICMS
        str(campos[13]),   # VL_BC_ICMS - Valor da base de cálculo
        "12.00",           # ALIQ_ICMS - Alíquota de ICMS aplicada (exemplo)
        str(difa),         # VL_ICMS - Valor do DIFAL calculado
    ]
    return '|'.join(campos) + '\n' + '|'.join(registro_c197)

def log_alteracoes(notas_alteradas):
    logging.basicConfig(filename='alteracoes_notas.log', level=logging.INFO)
    for nota, difa_value in notas_alteradas.items():
        logging.info(f"Nota Fiscal Alterada: {nota}, Valor DIFAL Calculado: {difa_value}")
        print(f"Nota Fiscal Alterada: {nota}, Valor DIFAL Calculado: {difa_value}")

def gerar_arquivo_sped_alterado(arquivo_sped_original, notas_alteradas, arquivo_saida):
    with open(arquivo_saida, 'w') as novo_sped:
        with open(arquivo_sped_original, 'r') as arquivo_sped:
            for linha in arquivo_sped:
                novo_sped.write(linha)
                for nota, difa_value in notas_alteradas.items():
                    if verificar_nota_alterada(linha, nota):
                        novo_sped.write(f"|0460|{gerar_cod_obs(nota)}|Observação referente ao ajuste de DIFAL|\n")
                        novo_sped.write(f"|C195|{gerar_cod_obs(nota)}|Ajuste de diferencial de alíquota|\n")
                        novo_sped.write(f"|C197|MS70000001|DIFAL ICMS|{difa_value}|...\n")
    print(f"Arquivo SPED atualizado e salvo em {arquivo_saida}")

def verificar_nota_alterada(linha, nota):
    """
    Verifica se a linha do SPED corresponde à nota fiscal alterada.
    """
    campos = linha.split('|')
    identificacao_nota = extrair_identificacao_nota(linha)
    return identificacao_nota == nota

def gerar_cod_obs(nota):
    """
    Gera um código de observação para o registro 0460 relacionado à nota fiscal.
    """
    return f"OBS_{nota}"

def cfop_uso_consumo(linha_c170):
    """
    Verifica se o CFOP da linha corresponde aos códigos 1556 ou 2556 (uso e consumo).
    """
    campos = linha_c170.split('|')
    cfop = campos[11]  # Ajuste o índice conforme a posição correta do CFOP
    return cfop in ['1556', '2556']

def processar_arquivo_sped(caminho_arquivo_sped, caminho_novo_arquivo_sped, planilha):
    notas_alteradas = {}

    with open(caminho_arquivo_sped, 'r') as arquivo_sped, open(caminho_novo_arquivo_sped, 'w') as novo_arquivo:
        for linha in arquivo_sped:
            if linha.startswith('C170'):
                ncm = extrair_ncm(linha)
                icms_aliquota = consultar_aliquota(ncm)

                if cfop_uso_consumo(linha):
                    if not icms_aliquota:
                        icms_aliquota = buscar_aliquota_na_planilha(linha, planilha)

                    if icms_aliquota and icms_aliquota < 17:
                        base_calculo_icms, aliquota = extrair_base_calculo_icms(linha)
                        difa = calcular_difa(base_calculo_icms, icms_aliquota)
                        linha_modificada = alterar_registro_c197(linha, difa)
                        notas_alteradas[extrair_identificacao_nota(linha)] = difa
                        novo_arquivo.write(linha_modificada + '\n')
                    else:
                        novo_arquivo.write(linha + '\n')
            else:
                novo_arquivo.write(linha + '\n')

    log_alteracoes(notas_alteradas)
    gerar_arquivo_sped_alterado(caminho_novo_arquivo_sped, notas_alteradas, 'sped_arquivo_final.txt')
