from src.indicadores import (
    faturamento_mensal_dashboard,
    ranking_produtos_dashboard,
    clientes_unicos,
)
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile
import logging

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException

from src.limpeza import limpar
from src.qualidade import diagnosticar
from src.validacao import validar_estrutura, ErroValidacao
from src.indicadores import (
    faturamento_mensal_dashboard,
    ranking_produtos_dashboard,
)

app = FastAPI(
    title="Automação de Relatórios API",
    description="API para limpeza, análise e geração de relatórios.",
    version="1.0.0"
)

TAMANHO_MAXIMO = 10 * 1024 * 1024  # 10 MB

COLUNAS_OBRIGATORIAS = [
    "data", "produto", "cliente", "quantidade", "valor"
]


@app.get("/api/health")
def verificar_saude():
    return {
        "status": "online",
        "mensagem": "API de relatórios funcionando!"
    }


@app.post("/api/relatorios/processar")
async def processar_relatorio(arquivo: UploadFile = File(...)):
    nome = arquivo.filename or ""
    extensao = Path(nome).suffix.lower()

    if extensao not in [".csv", ".xlsx"]:
        raise HTTPException(
            status_code=400,
            detail="Envie um arquivo CSV ou Excel (.xlsx)."
        )

    try:
        conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    finally:
        await arquivo.close()

    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(
            status_code=413,
            detail="O arquivo deve ter no máximo 10 MB."
        )

    if not conteudo:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio."
        )

    try:
        # 1. Ler a planilha
        if extensao == ".csv":
            df = pd.read_csv(
                BytesIO(conteudo),
                encoding="utf-8-sig"
            )
        else:
            df = pd.read_excel(
                BytesIO(conteudo),
                engine="openpyxl"
            )

        # 2. Validar e diagnosticar
        validar_estrutura(df, COLUNAS_OBRIGATORIAS)
        qualidade = diagnosticar(df)

        # 3. Aplicar limpeza existente
        limpo, resumo = limpar(df)

        if limpo.empty:
            raise HTTPException(
                status_code=422,
                detail="Nenhuma venda válida após a limpeza."
            )

        # 4. Calcular indicadores
        faturamento = float(limpo["valor"].sum())
        vendas = int(len(limpo))
        ticket_medio = faturamento / vendas
        clientes = int(clientes_unicos(limpo))

        # 5. Preparar dados dos gráficos
        mensal = faturamento_mensal_dashboard(limpo)
        produtos = ranking_produtos_dashboard(limpo)

        # 6. Retornar JSON para o dashboard
        return {
            "arquivo": nome,
            "periodo": {
                "inicio": limpo["data"].min().date().isoformat(),
                "fim": limpo["data"].max().date().isoformat()
            },
            "indicadores": {
                "faturamento": round(faturamento, 2),
                "vendas": vendas,
                "ticket_medio": round(ticket_medio, 2),
                "clientes_unicos": clientes
            },
            "faturamento_mensal": mensal,
            "ranking_produtos": produtos,
            "qualidade": qualidade,
            "resumo_limpeza": {
                "linhas_lidas": int(resumo["linhas_lidas"]),
                "duplicadas_removidas": int(
                    resumo["duplicadas_removidas"]
                ),
                "campos_corrigidos": int(
                    resumo["campos_corrigidos"]
                )
            }
        }

    except HTTPException:
        raise
    except (
        ErroValidacao, ValueError, KeyError,
        TypeError, UnicodeDecodeError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
        BadZipFile
    ) as erro:
        raise HTTPException(
            status_code=422,
            detail=f"Não foi possível processar: {erro}"
        ) from erro

    except Exception as erro:
        logging.exception("Erro ao processar a planilha")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a planilha."
        ) from erro
