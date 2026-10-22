import pandas as pd

from src.limpeza import limpar


def _base():
    return pd.DataFrame({
        "data": ["2026-01-01", "2026-01-01", "2026-01-02"],
        "produto": [" CAMISETA ", " CAMISETA ", "Camiseta"],
        "cliente": ["Cliente 001", "Cliente 001", None],
        "quantidade": [2, 2, 1],
        "valor": [99.8, 99.8, None],
    })


def test_remove_duplicadas():
    df, resumo = limpar(_base())
    assert resumo["duplicadas_removidas"] == 1
    assert len(df) == 2


def test_padroniza_produto():
    df, _ = limpar(_base())
    assert set(df["produto"]) == {"Camiseta"}


def test_preenche_vazios():
    df, _ = limpar(_base())
    assert df["cliente"].isna().sum() == 0
    assert df["valor"].isna().sum() == 0
    assert df["valor"].iloc[1] == 49.9