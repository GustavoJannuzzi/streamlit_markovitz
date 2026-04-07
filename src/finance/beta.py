import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def calculate_beta(asset_returns: pd.Series, market_returns: pd.Series) -> dict:
    """
    Regressão linear: Ri = α + β * Rm + ε
    Alinha as séries temporais antes de calcular.
    Retorna: {'beta': float, 'alpha': float, 'r_squared': float}
    """
    # Alinha séries
    df = pd.concat([asset_returns, market_returns], axis=1).dropna()
    if len(df) < 30:
        return {"beta": np.nan, "alpha": np.nan, "r_squared": np.nan}

    X = df.iloc[:, 1].values.reshape(-1, 1)  # mercado
    y = df.iloc[:, 0].values  # ativo

    model = LinearRegression()
    model.fit(X, y)

    beta = float(model.coef_[0])
    alpha = float(model.intercept_)
    r_squared = float(model.score(X, y))

    return {"beta": beta, "alpha": alpha, "r_squared": r_squared}


def all_betas(returns: pd.DataFrame, market_returns: pd.Series) -> pd.DataFrame:
    """
    Calcula beta, alpha e R² para todos os ativos.
    Alinha as séries temporais antes de calcular.
    Retorna DataFrame com ativos nas linhas.
    """
    results = {}
    for col in returns.columns:
        res = calculate_beta(returns[col], market_returns)
        beta = res["beta"]

        if np.isnan(beta):
            classification = "N/D"
        elif beta < 0.8:
            classification = "Defensivo"
        elif beta <= 1.2:
            classification = "Neutro"
        else:
            classification = "Agressivo"

        results[col] = {
            "Alpha (α)": res["alpha"],
            "Beta (β)": beta,
            "R²": res["r_squared"],
            "Classificação": classification,
        }

    return pd.DataFrame(results).T
