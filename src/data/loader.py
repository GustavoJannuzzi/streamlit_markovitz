import yfinance as yf
import pandas as pd
import streamlit as st


def normalize_ticker(t: str) -> str:
    """Auto-append '.SA' se o ticker B3 não tiver ponto."""
    t = t.strip().upper()
    return t if "." in t else f"{t}.SA"


@st.cache_data(ttl=3600, show_spinner=False)
def download_prices(tickers: list, period: str = "3y") -> pd.DataFrame:
    """
    Baixa preços ajustados de fechamento para os tickers fornecidos.
    - Adiciona sufixo '.SA' automaticamente se o ticker não tiver ponto
    - Retorna DataFrame com datas no índice e tickers (sem sufixo) nas colunas
    - Remove colunas com mais de 10% de NaN
    - Faz forward fill seguido de backward fill
    """
    normalized = [normalize_ticker(t) for t in tickers]

    try:
        raw = yf.download(
            normalized,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        st.error(f"Erro ao baixar dados do yfinance: {e}")
        return pd.DataFrame()

    # Seleciona coluna "Close"
    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            prices = raw["Close"].copy()
        else:
            prices = raw.iloc[:, :len(normalized)].copy()
            prices.columns = normalized
    else:
        prices = raw[["Close"]].copy() if "Close" in raw.columns else raw.copy()
        prices.columns = normalized

    # Garante que as colunas correspondam aos tickers normalizados
    prices.columns = [str(c) for c in prices.columns]

    # Remove colunas com >10% de NaN
    threshold = 0.10 * len(prices)
    prices = prices.dropna(axis=1, thresh=int(len(prices) - threshold))

    # Forward fill + backward fill
    prices = prices.ffill().bfill()

    # Remove linhas totalmente nulas
    prices = prices.dropna(how="all")

    # Renomeia colunas removendo sufixo .SA para exibição
    rename_map = {col: col.replace(".SA", "") for col in prices.columns}
    prices = prices.rename(columns=rename_map)

    return prices


@st.cache_data(ttl=3600, show_spinner=False)
def get_market_index(period: str = "3y") -> pd.Series:
    """
    Baixa o IBOVESPA (^BVSP) como proxy do mercado para cálculo de Beta.
    Retorna série de preços ajustados com nome 'IBOVESPA'.
    """
    try:
        raw = yf.download("^BVSP", period=period, auto_adjust=True, progress=False)
        if raw.empty:
            return pd.Series(dtype=float, name="IBOVESPA")

        if isinstance(raw.columns, pd.MultiIndex):
            close = raw["Close"].iloc[:, 0]
        else:
            close = raw["Close"] if "Close" in raw.columns else raw.iloc[:, 0]

        close = close.ffill().bfill()
        close.name = "IBOVESPA"
        return close
    except Exception as e:
        st.error(f"Erro ao baixar IBOVESPA: {e}")
        return pd.Series(dtype=float, name="IBOVESPA")
