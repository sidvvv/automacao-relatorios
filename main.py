import pandas as pd

from src.limpeza import limpar
from src.relatorio import gerar_relatorio

df = pd.read_csv("data/vendas.csv")
limpo, resumo = limpar(df)
caminho = gerar_relatorio(limpo, resumo)
print(f"Relatório gerado em {caminho}")