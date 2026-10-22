import pandas as pd

from src.indicadores import (
    faturamento_mensal_dashboard,
    ranking_produtos_dashboard
)
from src.qualidade import diagnosticar
from src.limpeza import limpar
from src.relatorio import gerar_relatorio

df = pd.read_csv("data/vendas.csv")
diagnostico = diagnosticar(df)

print("\n=== QUALIDADE DOS DADOS ===")
print(f"Registros recebidos: {diagnostico['registros_recebidos']}")
print(f"Duplicatas exatas: {diagnostico['duplicatas_exatas']}")
print(f"Valores ausentes: {diagnostico['valores_ausentes']}")
limpo, resumo = limpar(df)

print("\n=== INDICADORES DO DASHBOARD ===")

mensal = faturamento_mensal_dashboard(limpo)
produtos = ranking_produtos_dashboard(limpo)

print("\nFaturamento mensal:")
for item in mensal:
    print(item)

print("\nRanking de produtos:")
for item in produtos:
    print(item)

print("\nConferência dos totais:")
print(f"Faturamento original: R$ {limpo['valor'].sum():.2f}")
print(f"Soma dos meses: R$ {sum(i['faturamento'] for i in mensal):.2f}")
print(f"Soma dos produtos: R$ {sum(i['faturamento'] for i in produtos):.2f}")

print("\n=== DADOS APÓS A LIMPEZA ===")

print("\nColunas disponíveis:")
print(limpo.columns.tolist())

print("\nTipos de dados:")
print(limpo.dtypes)

print("\nPrimeiras 5 linhas:")
print(limpo.head(5).to_string(index=False))

print("\nTotal de registros limpos:")
print(len(limpo))

print("\nResumo da limpeza:")
print(resumo)

caminho = gerar_relatorio(limpo, resumo)
print(f"Relatório gerado em {caminho}")