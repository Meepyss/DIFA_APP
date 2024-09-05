def calcular_difa(base_calculo, aliquota):
    """
    Calcula a DIFA com base na fórmula:
    DIFA = Base de cálculo do ICMS / (1 - alíquota de ICMS)
    """
    return base_calculo / (1 - aliquota / 100)
