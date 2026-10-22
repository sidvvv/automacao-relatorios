import pandas as pd

from src import indicadores as ind


def _df():
    return pd.DataFrame({
        "data": pd.to_datetime(["2026-01-10", "2026-01-20", "2026-02-05"]),
        "produto": ["A", "B", "A"],
        "cliente": ["C1", "C1", "Não informado"],
        "quantidade": [1, 1, 1],
        "valor": [100.0, 50.0, 150.0],
    })


def test_faturamento_vendas_ticket():
    df = _df()
    assert ind.faturamento_total(df) == 300.0
    assert ind.numero_vendas(df) == 3
    assert ind.ticket_medio(df) == 100.0


def test_clientes_unicos_ignora_nao_informado():
    assert ind.clientes_unicos(_df()) == 1


def test_top_produtos():
    top = ind.top_produtos(_df())
    assert list(top.index) == ["A", "B"]
    assert top["A"] == 250.0


def test_vendas_por_mes():
    serie = ind.vendas_por_mes(_df())
    assert serie["2026-01"] == 150.0
    assert serie["2026-02"] == 150.0