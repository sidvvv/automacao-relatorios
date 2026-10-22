import pandas as pd

from src.relatorio import gerar_relatorio


def test_gera_arquivo(tmp_path):
    df = pd.DataFrame({
        "data": pd.to_datetime(["2026-01-10", "2026-02-05"]),
        "produto": ["A", "B"],
        "cliente": ["C1", "C2"],
        "quantidade": [1, 2],
        "valor": [100.0, 200.0],
    })
    resumo = {"linhas_lidas": 2, "duplicadas_removidas": 0, "campos_corrigidos": 0}
    gerar_relatorio(df, resumo, tmp_path / "r.xlsx")
    assert (tmp_path / "r.xlsx").exists()