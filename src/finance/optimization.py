from scipy.optimize import minimize
import numpy as np
import pandas as pd
from src.finance.portfolio import portfolio_return, portfolio_volatility, portfolio_sharpe


def _equal_weights(n: int) -> np.ndarray:
    return np.ones(n) / n


def _bounds(n: int):
    return tuple((0.0, 1.0) for _ in range(n))


def _constraints_sum_one(n: int):
    return [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]


def min_variance_portfolio(mean_returns: np.ndarray, cov_matrix: np.ndarray) -> dict | None:
    """
    Minimiza σ²p = w' Σ w
    Restrições: sum(w) = 1, w >= 0
    Retorna: {'weights': array, 'return': float, 'volatility': float, 'sharpe': float}
    """
    n = len(mean_returns)
    w0 = _equal_weights(n)

    result = minimize(
        fun=lambda w: portfolio_volatility(w, cov_matrix) ** 2,
        x0=w0,
        method="SLSQP",
        bounds=_bounds(n),
        constraints=_constraints_sum_one(n),
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    if not result.success:
        return None

    w = result.x
    w = np.maximum(w, 0)
    w /= w.sum()
    return {
        "weights": w,
        "return": portfolio_return(w, mean_returns),
        "volatility": portfolio_volatility(w, cov_matrix),
        "sharpe": portfolio_sharpe(w, mean_returns, cov_matrix),
    }


def max_sharpe_portfolio(
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    rf: float = 0.0,
) -> dict | None:
    """
    Maximiza Sharpe Ratio.
    Mesmas restrições: sum(w)=1, w>=0.
    """
    n = len(mean_returns)
    w0 = _equal_weights(n)

    result = minimize(
        fun=lambda w: -portfolio_sharpe(w, mean_returns, cov_matrix, rf),
        x0=w0,
        method="SLSQP",
        bounds=_bounds(n),
        constraints=_constraints_sum_one(n),
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    if not result.success:
        return None

    w = result.x
    w = np.maximum(w, 0)
    w /= w.sum()
    return {
        "weights": w,
        "return": portfolio_return(w, mean_returns),
        "volatility": portfolio_volatility(w, cov_matrix),
        "sharpe": portfolio_sharpe(w, mean_returns, cov_matrix, rf),
    }


def efficient_frontier_points(
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    n_points: int = 100,
) -> pd.DataFrame:
    """
    Gera n_points pontos da fronteira eficiente.
    Para cada nível de retorno alvo entre min e max dos ativos,
    minimiza a variância.
    Retorna DataFrame com colunas: ['Return', 'Volatility']
    """
    n = len(mean_returns)
    r_min = mean_returns.min()
    r_max = mean_returns.max()
    target_returns = np.linspace(r_min, r_max, n_points)

    frontier = []
    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w, t=target: portfolio_return(w, mean_returns) - t},
        ]
        result = minimize(
            fun=lambda w: portfolio_volatility(w, cov_matrix) ** 2,
            x0=_equal_weights(n),
            method="SLSQP",
            bounds=_bounds(n),
            constraints=constraints,
            options={"ftol": 1e-12, "maxiter": 500},
        )
        if result.success:
            w = np.maximum(result.x, 0)
            w /= w.sum()
            frontier.append(
                {
                    "Return": portfolio_return(w, mean_returns),
                    "Volatility": portfolio_volatility(w, cov_matrix),
                }
            )

    return pd.DataFrame(frontier)
