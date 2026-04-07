import numpy as np
import pandas as pd

TRADING_DAYS = 252


def portfolio_return(weights: np.ndarray, mean_returns: np.ndarray) -> float:
    """E(Rp) = w' * μ  (anualizado)"""
    return float(np.dot(weights, mean_returns))


def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """σp = sqrt(w' Σ w)  (anualizado — cov_matrix já anualizada)"""
    return float(np.sqrt(weights @ cov_matrix @ weights))


def portfolio_sharpe(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    rf: float = 0.0,
) -> float:
    """Sharpe = (E(Rp) - rf) / σp"""
    ret = portfolio_return(weights, mean_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    return (ret - rf) / vol if vol > 0 else 0.0


def build_random_portfolios(
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    n_portfolios: int = 5000,
    rf: float = 0.0,
) -> pd.DataFrame:
    """
    Simula n_portfolios carteiras aleatórias usando operações vetorizadas NumPy.
    Retorna DataFrame com colunas: ['Return', 'Volatility', 'Sharpe', w0, w1, ..., wn-1]
    Pesos somam 1, sem shorts (w >= 0).
    """
    n = len(mean_returns)

    # Gera pesos aleatórios vetorizado (sem loop Python)
    raw_weights = np.random.dirichlet(np.ones(n), size=n_portfolios)  # (n_portfolios, n)

    # Retornos vetorizados
    returns_vec = raw_weights @ mean_returns  # (n_portfolios,)

    # Volatilidades vetorizadas: sqrt(diag(W @ Sigma @ W'))
    # (n_portfolios, n) @ (n, n) = (n_portfolios, n), então dot com raw_weights
    cov_contrib = raw_weights @ cov_matrix  # (n_portfolios, n)
    variances = np.einsum("ij,ij->i", cov_contrib, raw_weights)  # (n_portfolios,)
    vols_vec = np.sqrt(np.maximum(variances, 0))

    sharpes_vec = np.where(vols_vec > 0, (returns_vec - rf) / vols_vec, 0.0)

    # Monta DataFrame
    weight_cols = {f"w{i}": raw_weights[:, i] for i in range(n)}
    df = pd.DataFrame(
        {
            "Return": returns_vec,
            "Volatility": vols_vec,
            "Sharpe": sharpes_vec,
            **weight_cols,
        }
    )
    return df
