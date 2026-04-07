import pandas as pd

TRADING_DAYS = 252


def covariance_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Matriz de covariância anualizada (multiplica por 252)."""
    return returns.cov() * TRADING_DAYS


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Matriz de correlação (normalização da covariância)."""
    return returns.corr()
