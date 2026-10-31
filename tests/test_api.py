
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api import app


client = TestClient(app)

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO_CSV = RAIZ / "data" / "vendas.csv"


def test_servidor_online():
    resposta = client.get("/api/health")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "online"


def test_upload_csv():
    with ARQUIVO_CSV.open("rb") as arquivo:
        resposta = client.post(
            "/api/relatorios/processar",
            files={"arquivo": ("vendas.csv", arquivo, "text/csv")}
        )

    assert resposta.status_code == 200, resposta.text

    dados = resposta.json()
    indicadores = dados["indicadores"]

    assert indicadores["faturamento"] == pytest.approx(426074.60)
    assert indicadores["vendas"] == 1200
    assert indicadores["ticket_medio"] == pytest.approx(355.06)
    assert indicadores["clientes_unicos"] == 80

    assert dados["resumo_limpeza"]["duplicadas_removidas"] == 37


def test_faturamento_graficos():
    with ARQUIVO_CSV.open("rb") as arquivo:
        resposta = client.post(
            "/api/relatorios/processar",
            files={"arquivo": ("vendas.csv", arquivo, "text/csv")}
        )

    assert resposta.status_code == 200, resposta.text

    dados = resposta.json()
    total = dados["indicadores"]["faturamento"]

    soma_meses = sum(
        item["faturamento"]
        for item in dados["faturamento_mensal"]
    )

    soma_produtos = sum(
        item["faturamento"]
        for item in dados["ranking_produtos"]
    )

    assert soma_meses == pytest.approx(total, abs=0.01)
    assert soma_produtos == pytest.approx(total, abs=0.01)


def test_arquivo_invalido():
    resposta = client.post(
        "/api/relatorios/processar",
        files={"arquivo": ("teste.txt", b"teste", "text/plain")}
    )

    assert resposta.status_code == 400


def test_arquivo_vazio():
    resposta = client.post(
        "/api/relatorios/processar",
        files={"arquivo": ("vazio.csv", b"", "text/csv")}
    )

    assert resposta.status_code == 400


def test_colunas_ausentes():
    conteudo = b"data,produto\n2026-01-01,Jaqueta\n"

    resposta = client.post(
        "/api/relatorios/processar",
        files={"arquivo": ("incompleto.csv", conteudo, "text/csv")}
    )

    assert resposta.status_code == 422


def test_filtro_jaqueta_julho():
    with ARQUIVO_CSV.open("rb") as arquivo:
        resposta = client.post(
            "/api/relatorios/processar",
            params={
                "data_inicio": "2026-07-01",
                "data_fim": "2026-07-31",
                "produto": "Jaqueta",
            },
            files={
                "arquivo": ("vendas.csv", arquivo, "text/csv")
            },
        )

    assert resposta.status_code == 200, resposta.text

    dados = resposta.json()

    assert dados["indicadores"]["faturamento"] == pytest.approx(18492.60)
    assert dados["indicadores"]["vendas"] == 24

    assert len(dados["faturamento_mensal"]) == 1
    assert dados["faturamento_mensal"][0]["mes"] == "2026-07"

    assert len(dados["ranking_produtos"]) == 1
    assert dados["ranking_produtos"][0]["produto"] == "Jaqueta"
    assert dados["ranking_produtos"][0]["participacao"] == 100.0


def test_intervalo_invalido():
    with ARQUIVO_CSV.open("rb") as arquivo:
        resposta = client.post(
            "/api/relatorios/processar",
            params={
                "data_inicio": "2026-08-01",
                "data_fim": "2026-07-01",
            },
            files={
                "arquivo": ("vendas.csv", arquivo, "text/csv")
            },
        )

    assert resposta.status_code == 422
    assert "data inicial" in resposta.json()["detail"].lower()


def test_filtros_disponiveis():
    with ARQUIVO_CSV.open("rb") as arquivo:
        resposta = client.post(
            "/api/relatorios/processar",
            files={
                "arquivo": ("vendas.csv", arquivo, "text/csv")
            },
        )

    assert resposta.status_code == 200, resposta.text

    dados = resposta.json()

    assert "Jaqueta" in dados["filtros_disponiveis"]["produtos"]
    assert "Tênis" in dados["filtros_disponiveis"]["produtos"]

    assert dados["filtros_aplicados"]["produto"] is None
    assert dados["filtros_aplicados"]["data_inicio"] is None
    assert dados["filtros_aplicados"]["data_fim"] is None


# Fixture pequena: inclui duplicata para verificar os metadados de limpeza.
VENDAS_FILTROS = (
    "data,produto,cliente,quantidade,valor\n"
    "2026-01-10,Jaqueta,Ana,1,200\n"
    "2026-01-10,Jaqueta,Ana,1,200\n"
    "2026-01-20,Tenis,Beto,1,100\n"
    "2026-02-05,Jaqueta,Ana,1,300\n"
)


def processar_filtros(params=None):
    return client.post(
        "/api/relatorios/processar",
        params=params,
        files={"arquivo": ("filtros.csv", VENDAS_FILTROS.encode(), "text/csv")},
    )


@pytest.mark.parametrize("params", [
    {"produto": "Inexistente"},
    {"data_inicio": "2027-01-01", "data_fim": "2027-01-31"},
    {"data_inicio": "2026-02-01", "data_fim": "2026-02-28", "produto": "Tenis"},
])
def test_filtro_sem_vendas_retorna_estado_vazio(params):
    completo = processar_filtros().json()
    resposta = processar_filtros(params)
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["sem_resultados"] is True
    assert dados["periodo"] is None
    assert dados["indicadores"] == {
        "faturamento": 0, "vendas": 0, "ticket_medio": 0, "clientes_unicos": 0,
    }
    assert dados["faturamento_mensal"] == []
    assert dados["ranking_produtos"] == []
    for campo in ("filtros_disponiveis", "resumo_limpeza", "qualidade"):
        assert dados[campo] == completo[campo]
    assert dados["resumo_limpeza"]["duplicadas_removidas"] == 1
    assert dados["periodo_selecionado"] == {
        "inicio": params.get("data_inicio", "2026-01-10"),
        "fim": params.get("data_fim", "2026-02-05"),
    }


def test_periodo_selecionado_nao_encolhe_para_datas_com_vendas():
    resposta = processar_filtros({
        "data_inicio": "2026-01-01", "data_fim": "2026-01-31",
        "produto": "  jAqUeTa  ",
    })
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["sem_resultados"] is False
    assert dados["periodo_selecionado"] == {"inicio": "2026-01-01", "fim": "2026-01-31"}
    assert dados["periodo"] == {"inicio": "2026-01-10", "fim": "2026-01-10"}
    assert dados["indicadores"] == {
        "faturamento": 200, "vendas": 1, "ticket_medio": 200, "clientes_unicos": 1,
    }
    assert dados["faturamento_mensal"] == [{"mes": "2026-01", "faturamento": 200}]
    assert dados["filtros_aplicados"]["produto"] == "jAqUeTa"


@pytest.mark.parametrize("params,esperado", [
    ({}, {"inicio": "2026-01-10", "fim": "2026-02-05"}),
    ({"data_inicio": "2026-01-01"}, {"inicio": "2026-01-01", "fim": "2026-02-05"}),
    ({"data_fim": "2026-01-31"}, {"inicio": "2026-01-10", "fim": "2026-01-31"}),
])
def test_periodo_selecionado_com_limites_opcionais(params, esperado):
    resposta = processar_filtros(params)
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["periodo_selecionado"] == esperado


def test_remover_filtros_restaura_todos_os_dados():
    inicial = processar_filtros().json()
    processar_filtros({"produto": "Inexistente"})
    restaurado = processar_filtros().json()
    assert restaurado == inicial
    assert restaurado["sem_resultados"] is False
    assert restaurado["indicadores"]["vendas"] == 3
    assert len(restaurado["faturamento_mensal"]) == 2
    assert len(restaurado["ranking_produtos"]) == 2
    assert restaurado["periodo"] == restaurado["periodo_selecionado"]


@pytest.mark.parametrize("params", [
    {"data_inicio": "2026-02-01", "data_fim": "2026-01-01"},
    {"data_inicio": "data-invalida"},
])
def test_filtros_invalidos_continuam_retornando_422(params):
    assert processar_filtros(params).status_code == 422


def test_planilha_sem_vendas_validas_continua_retornando_422():
    resposta = client.post(
        "/api/relatorios/processar",
        files={"arquivo": ("vazio.csv", b"data,produto,cliente,quantidade,valor\n", "text/csv")},
    )
    assert resposta.status_code == 422
