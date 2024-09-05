from db.database import consultar_aliquota
from sped.difa import calcular_difa
from planilha.leitor_planilha import buscar_aliquota_na_planilha

def processar_arquivo_sped(caminho_arquivo_sped, caminho_novo_arquivo_sped, planilha):
    with open(caminho_arquivo_sped, 'r') as arquivo_sped, open(caminho_novo_arquivo_sped, 'w') as novo_arquivo:
        for linha in arquivo_sped:
            if linha.startswith('C170'):
                ncm = extrair_ncm(linha)
                icms_aliquota = consultar_aliquota(ncm)
                
                # Verifica CFOP 1556 ou 2556
                if cfop_uso_consumo(linha):
                    if not icms_aliquota:
                        # Busca a alíquota na planilha se estiver ausente no SPED
                        icms_aliquota = buscar_aliquota_na_planilha(linha, planilha)
                
                if icms_aliquota and icms_aliquota < 17:
                    base_calculo_icms = extrair_base_calculo(linha)
                    difa = calcular_difa(base_calculo_icms, icms_aliquota)
                    linha_modificada = alterar_registro_c197(linha, difa)
                    novo_arquivo.write(linha_modificada + '\n')
                else:
                    novo_arquivo.write(linha + '\n')
            else:
                novo_arquivo.write(linha + '\n')

def cfop_uso_consumo(linha_c170):
    campos = linha_c170.split('|')
    cfop = campos[11]  # Exemplo de índice para o CFOP
    return cfop in ['1556', '2556']

def extrair_ncm(linha_c170):
    campos = linha_c170.split('|')
    return campos[12]  # Exemplo de índice onde o NCM se encontra

def extrair_base_calculo(linha_c170):
    campos = linha_c170.split('|')
    return float(campos[13])  # Exemplo de índice onde a base de cálculo se encontra

def alterar_registro_c197(linha_c170, difa):
    campos = linha_c170.split('|')
    campos[9] = str(difa)  # Exemplo de alteração do campo da DIFA
    return '|'.join(campos)
