
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
