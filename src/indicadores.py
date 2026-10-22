import pandas as pd

NAO_INFORMADO = "Não informado"


def faturamento_total(df):
    return round(float(df["valor"].sum()), 2)


def numero_vendas(df):
    return int(len(df))


def ticket_medio(df):
    if len(df) == 0:
        return 0.0
    return round(faturamento_total(df) / numero_vendas(df), 2)


def clientes_unicos(df):
    identificados = df.loc[df["cliente"] != NAO_INFORMADO, "cliente"]
    return int(identificados.nunique())


def top_produtos(df, n=5):
    return (
        df.groupby("produto")["valor"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .head(n)
    )


def vendas_por_mes(df):
    serie = df.groupby(df["data"].dt.to_period("M"))["valor"].sum().round(2)
    serie.index = serie.index.astype(str)
    return serie

def vendas_por_produto(df):
    return (
        df.groupby("produto")["valor"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
    )