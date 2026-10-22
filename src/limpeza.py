import pandas as pd


def limpar(df):
    resumo = {"linhas_lidas": len(df)}

    df = df.drop_duplicates().copy()
    resumo["duplicadas_removidas"] = resumo["linhas_lidas"] - len(df)

    produto_antes = df["produto"].copy()
    df["produto"] = df["produto"].str.strip().str.capitalize()
    nomes_padronizados = int((produto_antes != df["produto"]).sum())

    df["data"] = pd.to_datetime(df["data"])

    clientes_vazios = int(df["cliente"].isna().sum())
    df["cliente"] = df["cliente"].fillna("Não informado")

    preco_unitario = (
        (df["valor"] / df["quantidade"]).groupby(df["produto"]).transform("median")
    )
    valores_vazios = int(df["valor"].isna().sum())
    df["valor"] = df["valor"].fillna((df["quantidade"] * preco_unitario).round(2))

    resumo["campos_corrigidos"] = nomes_padronizados + clientes_vazios + valores_vazios
    return df.reset_index(drop=True), resumo