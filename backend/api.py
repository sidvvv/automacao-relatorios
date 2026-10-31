from fastapi.responses import StreamingResponse, FileResponse
from src.relatorio import gerar_relatorio

from backend.historico import (
    inicializar_banco,
    salvar_processamento,
    listar_processamentos,
    buscar_processamento,
)
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
from datetime import date
from fastapi import FastAPI, File, UploadFile, HTTPException, Query

from src.limpeza import limpar
from src.qualidade import diagnosticar
from src.validacao import validar_estrutura, ErroValidacao

app = FastAPI(
    title="Automação de Relatórios API",
    description="API para limpeza, análise e geração de relatórios.",
    version="1.0.0"
)

inicializar_banco()

TAMANHO_MAXIMO = 10 * 1024 * 1024  # 10 MB

COLUNAS_OBRIGATORIAS = [
    "data", "produto", "cliente", "quantidade", "valor"
]

async def preparar_exportacao(
    arquivo: UploadFile,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    produto: str | None = None,
):
    nome = arquivo.filename or "dados"
    extensao = Path(nome).suffix.lower()

    if extensao not in {".csv", ".xlsx"}:
        raise HTTPException(
            status_code=422,
            detail="Formato não suportado. Use CSV ou XLSX."
        )

    conteudo = await arquivo.read()

    try:
        if extensao == ".csv":
            df = pd.read_csv(BytesIO(conteudo))
        else:
            df = pd.read_excel(
                BytesIO(conteudo),
                engine="openpyxl"
            )

        validar_estrutura(df, COLUNAS_OBRIGATORIAS)

        limpo, resumo = limpar(df)

        if data_inicio:
            limpo = limpo[
                limpo["data"].dt.date >= data_inicio
            ].copy()

        if data_fim:
            limpo = limpo[
                limpo["data"].dt.date <= data_fim
            ].copy()

        if produto and produto.strip():
            limpo = limpo[
                limpo["produto"]
                .astype("string")
                .str.strip()
                .str.casefold()
                == produto.strip().casefold()
            ].copy()

        if limpo.empty:
            raise HTTPException(
                status_code=422,
                detail="Nenhum dado encontrado para exportar."
            )

        return limpo, resumo

    except HTTPException:
        raise

    except Exception as erro:
        raise HTTPException(
            status_code=422,
            detail=f"Não foi possível preparar a exportação: {erro}"
        ) from erro

@app.get("/api/health")
def verificar_saude():
    return {
        "status": "online",
        "mensagem": "API de relatórios funcionando!"
    }


@app.post("/api/relatorios/processar")
async def processar_relatorio(
    arquivo: UploadFile = File(...),
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    produto: str | None = Query(default=None),
):
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

                    
        # ==========================================
        # FILTROS INTERATIVOS
        # ==========================================

        # Guardar as opções disponíveis antes de filtrar
        produtos_disponiveis = sorted(
            limpo["produto"].dropna().astype(str).unique().tolist()
        )

        periodo_disponivel = {
            "inicio": limpo["data"].min().date().isoformat(),
            "fim": limpo["data"].max().date().isoformat()
        }

        # Validar intervalo de datas
        if data_inicio and data_fim and data_inicio > data_fim:
            raise HTTPException(
                status_code=422,
                detail="A data inicial não pode ser maior que a data final."
            )

        # Aplicar data inicial
        if data_inicio:
            limpo = limpo[
                limpo["data"].dt.date >= data_inicio
            ].copy()

        # Aplicar data final
        if data_fim:
            limpo = limpo[
                limpo["data"].dt.date <= data_fim
            ].copy()

        # Aplicar filtro de produto
        if produto and produto.strip():
            limpo = limpo[
                limpo["produto"]
                .astype("string")
                .str.strip()
                .str.casefold()
                == produto.strip().casefold()
            ].copy()

        # 4. Calcular indicadores
        faturamento = float(limpo["valor"].sum())
        vendas = int(len(limpo))
        ticket_medio = faturamento / vendas if vendas else 0.0
        clientes = int(clientes_unicos(limpo))

        # 5. Preparar dados dos gráficos
        mensal = faturamento_mensal_dashboard(limpo)
        produtos = ranking_produtos_dashboard(limpo)

        # 6. Retornar JSON para o dashboard
        resposta = {
            "arquivo": nome,
            
            "filtros_disponiveis": {
                "produtos": produtos_disponiveis,
                "periodo": periodo_disponivel,
            },

            "filtros_aplicados": {
                "data_inicio": (
                    data_inicio.isoformat() if data_inicio else None
                ),
                "data_fim": (
                    data_fim.isoformat() if data_fim else None
                ),
                "produto": produto.strip() if produto else None,
            },

            "sem_resultados": limpo.empty,
            # Limites consultados não dependem das vendas do produto filtrado.
            "periodo_selecionado": {
                "inicio": (
                    data_inicio.isoformat()
                    if data_inicio else periodo_disponivel["inicio"]
                ),
                "fim": (
                    data_fim.isoformat()
                    if data_fim else periodo_disponivel["fim"]
                ),
            },
            "periodo": {
                "inicio": limpo["data"].min().date().isoformat(),
                "fim": limpo["data"].max().date().isoformat()
            } if not limpo.empty else None,
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

        processamento_id = salvar_processamento(
        arquivo=nome,
        status="sucesso",

        periodo_inicio=(
            resposta["periodo"]["inicio"]
            if resposta["periodo"]
            else None
        ),

        periodo_fim=(
            resposta["periodo"]["fim"]
            if resposta["periodo"]
            else None
        ),

        filtros=resposta["filtros_aplicados"],

        indicadores=resposta["indicadores"],

        resumo_limpeza=resposta["resumo_limpeza"],
    )

        resposta["processamento_id"] = processamento_id

        return resposta
        

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

@app.get("/api/historico")
def obter_historico(limite: int = 50):
    limite = max(1, min(limite, 200))

    return {
        "processamentos": listar_processamentos(limite)
    }


@app.get("/api/historico/{processamento_id}")
def obter_processamento(processamento_id: int):

    processamento = buscar_processamento(
        processamento_id
    )

    if processamento is None:
        raise HTTPException(
            status_code=404,
            detail="Processamento não encontrado."
        )

    return processamento

@app.post("/api/relatorios/exportar/dados")
async def exportar_dados_tratados(
    arquivo: UploadFile = File(...),
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    produto: str | None = Query(default=None),
):
    limpo, _ = await preparar_exportacao(
        arquivo,
        data_inicio,
        data_fim,
        produto,
    )

    limpo = limpo.copy()
    limpo["data"] = limpo["data"].dt.strftime("%d/%m/%Y")

    buffer = BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:
        limpo.to_excel(
            writer,
            index=False,
            sheet_name="Dados tratados"
        )

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="dados_tratados.xlsx"'
        },
    )

@app.post("/api/relatorios/exportar/relatorio")
async def exportar_relatorio_executivo(
    arquivo: UploadFile = File(...),
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    produto: str | None = Query(default=None),
):
    limpo, resumo = await preparar_exportacao(
        arquivo,
        data_inicio,
        data_fim,
        produto,
    )

    caminho = gerar_relatorio(
        limpo,
        resumo
    )

    return FileResponse(
        path=caminho,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        filename="relatorio_executivo.xlsx",
    )