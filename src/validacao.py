
import pandas as pd


class ErroValidacao(ValueError):
    """Erro encontrado na estrutura da planilha."""
    pass


def validar_estrutura(
    df: pd.DataFrame,
    colunas_obrigatorias: list
) -> pd.DataFrame:
    """Valida a estrutura da planilha antes da limpeza."""

    if not isinstance(df, pd.DataFrame):
        raise ErroValidacao(
            "O arquivo não contém uma tabela válida."
        )

    if df.empty:
        raise ErroValidacao(
            "A planilha está vazia."
        )

    duplicadas = df.columns[
        df.columns.duplicated()
    ].tolist()

    if duplicadas:
        raise ErroValidacao(
            f"Colunas duplicadas: {duplicadas}"
        )

    faltantes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ErroValidacao(
            f"Colunas obrigatórias ausentes: {faltantes}"
        )

    return df.copy()
