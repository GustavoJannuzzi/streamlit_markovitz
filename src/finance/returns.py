import pandas as pd
import numpy as np


def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Retorno simples: Rt = (Pt / Pt-1) - 1"""
    return prices.pct_change().dropna()


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Retorno logarítmico: Rt = ln(Pt / Pt-1)"""
    return np.log(prices / prices.shift(1)).dropna()
