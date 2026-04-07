import requests
import pandas as pd
import io
import streamlit as st


def _pct(s: pd.Series) -> pd.Series:
    """Converte strings percentuais no formato brasileiro (ex: '12,34%') para float."""
    return (
        s.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        / 100
    )


def _num(s: pd.Series) -> pd.Series:
    """Converte strings numéricas no formato brasileiro para float."""
    return (
        s.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fundamentus() -> pd.DataFrame:
    """
    Faz scraping de https://www.fundamentus.com.br/resultado.php
    Retorna DataFrame limpo com os indicadores fundamentalistas.
    """
    url = "https://www.fundamentus.com.br/resultado.php"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.warning(f"Não foi possível acessar o Fundamentus: {e}")
        return pd.DataFrame()

    try:
        tables = pd.read_html(
            io.StringIO(response.text),
            decimal=",",
            thousands=".",
            encoding="utf-8",
        )
        if not tables:
            st.warning("Nenhuma tabela encontrada no Fundamentus.")
            return pd.DataFrame()

        df = tables[0].copy()
    except Exception as e:
        st.warning(f"Erro ao parsear HTML do Fundamentus: {e}")
        return pd.DataFrame()

    # Padroniza nomes de colunas
    df.columns = [str(c).strip() for c in df.columns]

    # Colunas percentuais — converter de string %
    pct_cols = ["ROE", "ROIC", "Mrg Ebit", "Mrg. Líq.", "Cresc. Rec.5a", "Div.Yield"]
    for col in pct_cols:
        if col in df.columns:
            df[col] = _pct(df[col])

    # Colunas numéricas
    num_cols = ["P/L", "P/VP", "EV/EBITDA", "Liq.2meses", "Liq. Corr.", "Dív.Brut/ Patrim."]
    for col in num_cols:
        if col in df.columns:
            df[col] = _num(df[col])

    # Remove linhas onde o papel está vazio
    if "Papel" in df.columns:
        df = df[df["Papel"].notna() & (df["Papel"] != "")]

    df = df.reset_index(drop=True)
    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Aplica filtros do usuário ao DataFrame do Fundamentus.

    Parâmetros em `filters`:
        - pl_max: float           → P/L máximo
        - pvp_max: float          → P/VP máximo
        - roe_min: float          → ROE mínimo (como fração, ex: 0.10)
        - dy_min: float           → Dividend Yield mínimo (fração)
        - roic_min: float         → ROIC mínimo (fração)
        - liq_min: float          → Liquidez mínima (Liq.2meses em R$)
        - ev_ebitda_max: float    → EV/EBITDA máximo
        - margem_liq_min: float   → Margem Líquida mínima (fração)
    """
    mask = pd.Series([True] * len(df), index=df.index)

    if "pl_max" in filters and "P/L" in df.columns:
        mask &= (df["P/L"] > 0) & (df["P/L"] <= filters["pl_max"])

    if "pvp_max" in filters and "P/VP" in df.columns:
        mask &= (df["P/VP"] > 0) & (df["P/VP"] <= filters["pvp_max"])

    if "roe_min" in filters and "ROE" in df.columns:
        mask &= df["ROE"] >= filters["roe_min"]

    if "dy_min" in filters and "Div.Yield" in df.columns:
        mask &= df["Div.Yield"] >= filters["dy_min"]

    if "roic_min" in filters and "ROIC" in df.columns:
        mask &= df["ROIC"] >= filters["roic_min"]

    if "liq_min" in filters and "Liq.2meses" in df.columns:
        mask &= df["Liq.2meses"] >= filters["liq_min"]

    if "ev_ebitda_max" in filters and "EV/EBITDA" in df.columns:
        mask &= (df["EV/EBITDA"] > 0) & (df["EV/EBITDA"] <= filters["ev_ebitda_max"])

    if "margem_liq_min" in filters and "Mrg. Líq." in df.columns:
        mask &= df["Mrg. Líq."] >= filters["margem_liq_min"]

    return df[mask].reset_index(drop=True)
