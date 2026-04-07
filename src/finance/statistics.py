import pandas as pd
import numpy as np

TRADING_DAYS = 252


def asset_statistics(returns: pd.DataFrame, rf: float = 0.0) -> pd.DataFrame:
    """
    Para cada ativo, calcula:
    - Retorno médio diário (μ)
    - Retorno médio anualizado (μ * 252)
    - Variância diária (σ²)
    - Desvio padrão diário (σ)
    - Desvio padrão anualizado (σ * sqrt(252))
    - Sharpe individual (rf anualizado)
    - Assimetria (skewness)
    - Curtose (kurtosis)

    Retorna DataFrame com ativos nas linhas e métricas nas colunas.
    """
    stats = {}
    rf_daily = rf / TRADING_DAYS

    for col in returns.columns:
        r = returns[col].dropna()
        mu_daily = r.mean()
        sigma_daily = r.std()
        mu_annual = mu_daily * TRADING_DAYS
        sigma_annual = sigma_daily * np.sqrt(TRADING_DAYS)
        sharpe = (mu_annual - rf) / sigma_annual if sigma_annual > 0 else np.nan

        stats[col] = {
            "Retorno Médio Diário": mu_daily,
            "Retorno Anual": mu_annual,
            "Variância Diária": r.var(),
            "Vol. Diária": sigma_daily,
            "Vol. Anual": sigma_annual,
            "Sharpe": sharpe,
            "Assimetria": r.skew(),
            "Curtose": r.kurtosis(),
        }

    return pd.DataFrame(stats).T
