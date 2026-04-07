import requests
import pandas as pd
import io
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# NOTA TÉCNICA:
# O Fundamentus usa JavaScript para renderizar P/L, P/VP, EV/EBITDA e
# Liq.2meses no cliente. Via scraping estático (requests), esses campos
# chegam como placeholders '000'. Apenas ROE, ROIC, Mrg.Líq., Mrg.Ebit,
# Div.Yield e Cresc.Rec chegam como strings reais.
# Os filtros disponíveis refletem apenas os campos com dados reais.
# ─────────────────────────────────────────────────────────────────────────────


def _pct_br(val) -> float:
    """Converte string percentual BR ('32,15%' ou '-3,50%') para fração decimal."""
    if val is None:
        return float("nan")
    if isinstance(val, (int, float)):
        return float(val) / 100.0 if abs(float(val)) > 1.5 else float(val)
    s = str(val).strip().replace("%", "").strip()
    if s in ("", "-", "000", "0000", "0,00", "0.00"):
        return 0.0  # zero real, não placeholder
    s = s.replace(".", "").replace(",", ".")
    try:
        v = float(s)
        # Fundamentus retorna em escala 0-100, normalizar para 0-1
        return v / 100.0
    except ValueError:
        return float("nan")


def _num_br(val) -> float:
    """Converte número BR. Placeholders '000' → NaN."""
    if val is None:
        return float("nan")
    if isinstance(val, (int, float)):
        f = float(val)
        return float("nan") if f == 0.0 else f
    s = str(val).strip()
    if s in ("000", "0000", "00000", "", "-"):
        return float("nan")
    s = s.replace(",", ".") if "," in s and "." not in s else s.replace(".", "", s.count(".") - 1 if "," in s else 0).replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return float("nan")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fundamentus() -> pd.DataFrame:
    """
    Scraping do Fundamentus via sessão HTTP.
    Colunas com dados reais: ROE, ROIC, Div.Yield, Mrg.Líq., Mrg Ebit, Cresc.Rec.5a
    Colunas com dados ausentes por limitação do site: P/L, P/VP, EV/EBITDA, Liq.2meses
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": "https://www.fundamentus.com.br/",
    })

    try:
        session.get("https://www.fundamentus.com.br/", timeout=10)
        response = session.get(
            "https://www.fundamentus.com.br/resultado.php",
            timeout=20,
        )
        response.raise_for_status()
        response.encoding = "utf-8"
    except requests.exceptions.RequestException as e:
        st.warning(f"Não foi possível acessar o Fundamentus: {e}")
        return pd.DataFrame()

    try:
        tables = pd.read_html(io.StringIO(response.text), flavor="lxml", encoding="utf-8")
        if not tables:
            st.warning("Nenhuma tabela encontrada no Fundamentus.")
            return pd.DataFrame()
        df = tables[0].copy()
    except Exception as e:
        st.warning(f"Erro ao parsear HTML do Fundamentus: {e}")
        return pd.DataFrame()

    df.columns = [str(c).strip() for c in df.columns]

    # Campos percentuais com dados REAIS via scraping
    pct_real = ["ROE", "ROIC", "Mrg Ebit", "Mrg. Líq.", "Cresc. Rec.5a", "Div.Yield"]
    for col in pct_real:
        if col in df.columns:
            df[col] = df[col].apply(_pct_br)

    # Campos numéricos — chegam como '000', manter como NaN para indicar ausência
    num_cols = ["P/L", "P/VP", "EV/EBITDA", "Liq.2meses", "Liq. Corr.", "Dív.Brut/ Patrim."]
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].apply(_num_br)

    if "Papel" in df.columns:
        df = df[df["Papel"].notna() & (df["Papel"].astype(str).str.strip() != "")]

    return df.reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# Filtros — somente pelos campos com dados reais
# ─────────────────────────────────────────────────────────────────────────────

#: Campos que funcionam corretamente via scraping estático
FILTERABLE_FIELDS = {"ROE", "ROIC", "Div.Yield", "Mrg. Líq.", "Mrg Ebit"}


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Aplica filtros funcionais ao DataFrame.
    Filtros com valor 0 (ou ≤ limiar mínimo) são **ignorados**.
    """
    mask = pd.Series([True] * len(df), index=df.index)

    def col(name: str) -> pd.Series:
        return pd.to_numeric(df[name], errors="coerce")

    # ROE mínimo
    roe_min = filters.get("roe_min", 0)
    if roe_min > 0 and "ROE" in df.columns:
        mask &= col("ROE") >= roe_min

    # ROIC mínimo
    roic_min = filters.get("roic_min", 0)
    if roic_min > 0 and "ROIC" in df.columns:
        mask &= col("ROIC") >= roic_min

    # Div.Yield mínimo
    dy_min = filters.get("dy_min", 0)
    if dy_min > 0 and "Div.Yield" in df.columns:
        mask &= col("Div.Yield") >= dy_min

    # Margem líquida mínima (aceita negativos: -0.10 = até -10%)
    mrg_min = filters.get("margem_liq_min", None)
    if mrg_min is not None and mrg_min > -0.49 and "Mrg. Líq." in df.columns:
        mask &= col("Mrg. Líq.") >= mrg_min

    # Margem EBIT mínima
    ebit_min = filters.get("margem_ebit_min", None)
    if ebit_min is not None and ebit_min > -0.49 and "Mrg Ebit" in df.columns:
        mask &= col("Mrg Ebit") >= ebit_min

    # Crescimento receita mínimo
    cresc_min = filters.get("cresc_min", None)
    if cresc_min is not None and cresc_min > -0.49 and "Cresc. Rec.5a" in df.columns:
        mask &= col("Cresc. Rec.5a") >= cresc_min

    return df[mask].reset_index(drop=True)
