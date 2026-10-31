import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = BASE_DIR / "data" / "dataflow.db"


def conectar():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row

    return conexao


def inicializar_banco():
    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS processamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                arquivo TEXT NOT NULL,

                criado_em TEXT NOT NULL,

                status TEXT NOT NULL,

                periodo_inicio TEXT,
                periodo_fim TEXT,

                filtros TEXT,

                indicadores TEXT,

                resumo_limpeza TEXT,

                erro TEXT
            )
            """
        )


def salvar_processamento(
    arquivo: str,
    status: str,
    periodo_inicio: str | None = None,
    periodo_fim: str | None = None,
    filtros: dict[str, Any] | None = None,
    indicadores: dict[str, Any] | None = None,
    resumo_limpeza: dict[str, Any] | None = None,
    erro: str | None = None,
) -> int:

    criado_em = datetime.now().isoformat(timespec="seconds")

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO processamentos (
                arquivo,
                criado_em,
                status,
                periodo_inicio,
                periodo_fim,
                filtros,
                indicadores,
                resumo_limpeza,
                erro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                arquivo,
                criado_em,
                status,
                periodo_inicio,
                periodo_fim,
                json.dumps(filtros, ensure_ascii=False)
                if filtros is not None
                else None,
                json.dumps(indicadores, ensure_ascii=False)
                if indicadores is not None
                else None,
                json.dumps(resumo_limpeza, ensure_ascii=False)
                if resumo_limpeza is not None
                else None,
                erro,
            ),
        )

        return int(cursor.lastrowid)


def listar_processamentos(limite: int = 50) -> list[dict]:

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                id,
                arquivo,
                criado_em,
                status,
                periodo_inicio,
                periodo_fim,
                indicadores,
                erro
            FROM processamentos
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()

    resultado = []

    for linha in linhas:
        item = dict(linha)

        if item["indicadores"]:
            item["indicadores"] = json.loads(
                item["indicadores"]
            )

        resultado.append(item)

    return resultado


def buscar_processamento(
    processamento_id: int,
) -> dict | None:

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT *
            FROM processamentos
            WHERE id = ?
            """,
            (processamento_id,),
        ).fetchone()

    if linha is None:
        return None

    item = dict(linha)

    for campo in [
        "filtros",
        "indicadores",
        "resumo_limpeza",
    ]:
        if item[campo]:
            item[campo] = json.loads(item[campo])

    return item