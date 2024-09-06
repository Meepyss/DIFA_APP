import logging
from db.database import consultar_aliquota
from sped.difa import calcular_difa
from planilha.leitor_planilha import buscar_aliquota_na_planilha

def extrair_ncm(linha_c170):
    campos = linha_c170.split('|')
    return campos[12]

def extrair_base_calculo_icms(linha_c170):
    campos = linha_c170.split('|')
    return float(campos[13]) if campos[13] else 0.0, float(campos[14]) if campos[14] else 0.0

def extrair_identificacao_nota(linha_c170):
    campos = linha_c170.split('|')
    return campos[2]  # Número da NF

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

def gerar_relatorio_alteracoes(notas_alteradas):
    """
    Gera um relatório claro e detalhado das notas fiscais alteradas e dos registros SPED modificados.
    O relatório é impresso no console e gravado em um arquivo de texto.
    """
    with open('relatorio_alteracoes.txt', 'w') as relatorio:
        print("\n### Relatório de Alterações ###\n")
        relatorio.write("### Relatório de Alterações ###\n\n")
        
        for nota, detalhes in notas_alteradas.items():
            nf = detalhes['nf']
            difal = detalhes['difa']
            registros = detalhes['registros']

            # Exibe no console
            print(f"Nota Fiscal: {nf}")
            print(f"Valor DIFAL Calculado: {difal}")
            print(f"Registros Alterados: {', '.join(registros)}")
            print("-" * 50)

            # Grava no arquivo
            relatorio.write(f"Nota Fiscal: {nf}\n")
            relatorio.write(f"Valor DIFAL Calculado: {difal}\n")
            relatorio.write(f"Registros Alterados: {', '.join(registros)}\n")
            relatorio.write("-" * 50 + "\n")

    print("\nRelatório gerado e salvo como 'relatorio_alteracoes.txt'")

def log_alteracoes(notas_alteradas):
    """
    Grava detalhes das notas alteradas em um arquivo de log.
    """
    logging.basicConfig(filename='alteracoes_notas.log', level=logging.INFO)
    for nota, detalhes in notas_alteradas.items():
        nf = detalhes['nf']
        difal = detalhes['difa']
        registros = detalhes['registros']
        logging.info(f"Nota Fiscal: {nf}, Valor DIFAL: {difal}, Registros Alterados: {', '.join(registros)}")

def gerar_arquivo_sped_alterado(arquivo_sped_original, notas_alteradas, arquivo_saida):
    with open(arquivo_saida, 'w') as novo_sped:
        with open(arquivo_sped_original, 'r') as arquivo_sped:
            for linha in arquivo_sped:
                novo_sped.write(linha)
                for nota, detalhes in notas_alteradas.items():
                    if verificar_nota_alterada(linha, nota):
                        novo_sped.write(f"|0460|{gerar_cod_obs(nota)}|Observação referente ao ajuste de DIFAL|\n")
                        novo_sped.write(f"|C195|{gerar_cod_obs(nota)}|Ajuste de diferencial de alíquota|\n")
                        novo_sped.write(f"|C197|MS70000001|DIFAL ICMS|{detalhes['difa']}|...\n")

    print(f"Arquivo SPED atualizado e salvo em {arquivo_saida}")

def verificar_nota_alterada(linha, nota):
    campos = linha.split('|')
    identificacao_nota = extrair_identificacao_nota(linha)
    return identificacao_nota == nota

def gerar_cod_obs(nota):
    return f"OBS_{nota}"

def cfop_uso_consumo(linha_c170):
    campos = linha_c170.split('|')
    cfop = campos[11]
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
                        
                        nf = extrair_identificacao_nota(linha)
                        
                        # Registre a nota fiscal alterada e o valor do DIFAL
                        notas_alteradas[nf] = {
                            'nf': nf,
                            'difa': difa,
                            'registros': ['C170', 'C197']  # Registros alterados
                        }
                        
                        novo_arquivo.write(linha_modificada + '\n')
                    else:
                        novo_arquivo.write(linha + '\n')
            else:
                novo_arquivo.write(linha + '\n')

    # Exibe e gera o relatório das notas alteradas
    gerar_relatorio_alteracoes(notas_alteradas)

    # Grava os dados no log
    log_alteracoes(notas_alteradas)

    # Gera o arquivo SPED final com as alterações
    gerar_arquivo_sped_alterado(caminho_novo_arquivo_sped, notas_alteradas, 'sped_arquivo_final.txt')
