import random
from datetime import date, timedelta

import pandas as pd

random.seed(42)

PRODUTOS = {
    "Camiseta": 49.90,
    "Calça jeans": 129.90,
    "Tênis": 219.90,
    "Boné": 39.90,
    "Jaqueta": 249.90,
    "Meia": 14.90,
}
CLIENTES = [f"Cliente {i:03d}" for i in range(1, 81)]

linhas = []
inicio = date(2026, 1, 1)
for _ in range(1200):
    produto = random.choice(list(PRODUTOS))
    qtd = random.randint(1, 5)
    linhas.append({
        "data": (inicio + timedelta(days=random.randint(0, 288))).isoformat(),
        "produto": produto,
        "cliente": random.choice(CLIENTES),
        "quantidade": qtd,
        "valor": round(qtd * PRODUTOS[produto], 2),
    })

df = pd.DataFrame(linhas)

vazios = df.sample(12, random_state=2).index
df.loc[vazios[:6], "cliente"] = None
df.loc[vazios[6:], "valor"] = None

nomes = df.sample(30, random_state=3).index
df.loc[nomes, "produto"] = df.loc[nomes, "produto"].str.upper().apply(lambda s: f" {s} ")

duplicadas = df.sample(37, random_state=1)
df = pd.concat([df, duplicadas], ignore_index=True)
df = df.sample(frac=1, random_state=4).reset_index(drop=True)

df.to_csv("data/vendas.csv", index=False)
print(f"{len(df)} linhas salvas em data/vendas.csv")