import pandas as pd

from src.limpeza import limpar

df = pd.read_csv("data/vendas.csv")
limpo, resumo = limpar(df)
print(resumo)