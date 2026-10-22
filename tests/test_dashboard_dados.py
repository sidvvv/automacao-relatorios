
import pandas as pd

from src.indicadores import (
    faturamento_mensal_dashboard,
    ranking_produtos_dashboard,
)


def criar_dados_teste():
    return pd.DataFrame({
        "data": pd.to_datetime([
            "2026-01-10",
            "2026-01-15",
            "2026-02-10"
        ]),
        "produto": ["Jaqueta", "Tênis", "Jaqueta"],
        "valor": [200.0, 100.0, 300.0]
    })


def test_faturamento_mensal():
    resultado = faturamento_mensal_dashboard(
        criar_dados_teste()
    )

    assert len(resultado) == 2
    assert resultado[0]["mes"] == "2026-01"
    assert resultado[0]["faturamento"] == 300.0
    assert resultado[1]["faturamento"] == 300.0


def test_ranking_produtos():
    resultado = ranking_produtos_dashboard(
        criar_dados_teste()
    )

    assert resultado[0]["produto"] == "Jaqueta"
    assert resultado[0]["faturamento"] == 500.0
    assert resultado[1]["produto"] == "Tênis"


def test_participacao():
    resultado = ranking_produtos_dashboard(
        criar_dados_teste()
    )

    participacao_total = sum(
        item["participacao"]
        for item in resultado
    )

    assert abs(participacao_total - 100.0) < 0.01
