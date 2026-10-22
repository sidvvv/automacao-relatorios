import pandas as pd

from src import indicadores as ind
from src.limpeza import limpar

df = pd.read_csv("data/vendas.csv")
limpo, resumo = limpar(df)

print(resumo)
print("Faturamento:", ind.faturamento_total(limpo))
print("Vendas:", ind.numero_vendas(limpo))
print("Ticket médio:", ind.ticket_medio(limpo))
print("Clientes únicos:", ind.clientes_unicos(limpo))
print(ind.top_produtos(limpo))
print(ind.vendas_por_mes(limpo))