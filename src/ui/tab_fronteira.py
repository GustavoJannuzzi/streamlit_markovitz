import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.finance.covariance import covariance_matrix
from src.finance.portfolio import build_random_portfolios
from src.finance.optimization import (
    efficient_frontier_points,
    max_sharpe_portfolio,
    min_variance_portfolio,
)


def render(tab):
    with tab:
        st.markdown("## 📈 Fronteira Eficiente")
        st.markdown(
            "Visualize o espaço de risco-retorno de carteiras possíveis e "
            "a curva da fronteira eficiente de Markowitz."
        )

        if "returns" not in st.session_state or st.session_state["returns"] is None:
            st.info("⬅️ Carregue os dados na aba **📋 Seleção de Ativos** primeiro.")
            return

        returns = st.session_state["returns"]
        tickers = st.session_state["tickers"]
        rf = st.session_state.get("rf", 0.1075)

        mean_returns = returns.mean().values * 252
        cov = covariance_matrix(returns).values

        # ── Controles ──────────────────────────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            n_sim = st.slider(
                "Nº de carteiras simuladas",
                min_value=1000,
                max_value=10000,
                value=5000,
                step=500,
                key="fe_n_sim",
            )
        with col2:
            show_random = st.checkbox("Mostrar carteiras aleatórias", value=True, key="fe_show_rand")
        col3, col4 = st.columns(2)
        with col3:
            show_cml = st.checkbox("Mostrar Capital Market Line (CML)", value=True, key="fe_show_cml")
        with col4:
            show_ativos = st.checkbox("Mostrar ativos individuais", value=True, key="fe_show_ativos")

        calcular = st.button("⚙️ Calcular Fronteira Eficiente", type="primary", key="btn_fronteira")

        if calcular:
            with st.spinner("Simulando carteiras e calculando fronteira eficiente..."):
                df_sim = build_random_portfolios(mean_returns, cov, n_portfolios=n_sim, rf=rf)
                df_fe = efficient_frontier_points(mean_returns, cov, n_points=100)
                opt_sharpe = max_sharpe_portfolio(mean_returns, cov, rf)
                opt_minvar = min_variance_portfolio(mean_returns, cov)

            st.session_state["fe_sim"] = df_sim
            st.session_state["fe_frontier"] = df_fe
            st.session_state["fe_optsh"] = opt_sharpe
            st.session_state["fe_optmv"] = opt_minvar

        # ── Gráfico principal ──────────────────────────────────────────────
        if "fe_sim" in st.session_state:
            df_sim = st.session_state["fe_sim"]
            df_fe = st.session_state["fe_frontier"]
            opt_sharpe = st.session_state["fe_optsh"]
            opt_minvar = st.session_state["fe_optmv"]

            n = len(tickers)
            weight_cols = [f"w{i}" for i in range(n)]

            fig = go.Figure()

            # Nuvem de pontos aleatórios
            if show_random:
                # Tooltip com pesos
                hover_texts = []
                for _, row in df_sim.iterrows():
                    text = "<br>".join(
                        [f"{tickers[i]}: {row[f'w{i}']:.1%}" for i in range(n)]
                    )
                    hover_texts.append(text)

                fig.add_trace(
                    go.Scatter(
                        x=df_sim["Volatility"] * 100,
                        y=df_sim["Return"] * 100,
                        mode="markers",
                        marker=dict(
                            size=4,
                            color=df_sim["Sharpe"],
                            colorscale="Viridis",
                            showscale=True,
                            colorbar=dict(title="Sharpe", x=1.02),
                            opacity=0.6,
                        ),
                        text=hover_texts,
                        hovertemplate=(
                            "<b>Carteira Aleatória</b><br>"
                            "Volatilidade: %{x:.2f}%<br>"
                            "Retorno: %{y:.2f}%<br>"
                            "Sharpe: %{marker.color:.3f}<br>"
                            "%{text}<extra></extra>"
                        ),
                        name="Carteiras Simuladas",
                    )
                )

            # Fronteira eficiente
            if not df_fe.empty:
                fig.add_trace(
                    go.Scatter(
                        x=df_fe["Volatility"] * 100,
                        y=df_fe["Return"] * 100,
                        mode="lines",
                        line=dict(color="#FF4560", width=3),
                        name="Fronteira Eficiente",
                        hovertemplate=(
                            "Fronteira Eficiente<br>"
                            "Volatilidade: %{x:.2f}%<br>"
                            "Retorno: %{y:.2f}%<extra></extra>"
                        ),
                    )
                )

            # Ponto Máximo Sharpe
            if opt_sharpe:
                tip = "<br>".join([f"{tickers[i]}: {opt_sharpe['weights'][i]:.1%}" for i in range(n)])
                fig.add_trace(
                    go.Scatter(
                        x=[opt_sharpe["volatility"] * 100],
                        y=[opt_sharpe["return"] * 100],
                        mode="markers",
                        marker=dict(symbol="star", size=18, color="gold", line=dict(color="white", width=1)),
                        name=f"Máx. Sharpe ({opt_sharpe['sharpe']:.3f})",
                        text=[tip],
                        hovertemplate=(
                            "<b>Máximo Sharpe</b><br>"
                            "Volatilidade: %{x:.2f}%<br>"
                            "Retorno: %{y:.2f}%<br>"
                            "%{text}<extra></extra>"
                        ),
                    )
                )

            # Ponto Mínima Variância
            if opt_minvar:
                tip = "<br>".join([f"{tickers[i]}: {opt_minvar['weights'][i]:.1%}" for i in range(n)])
                fig.add_trace(
                    go.Scatter(
                        x=[opt_minvar["volatility"] * 100],
                        y=[opt_minvar["return"] * 100],
                        mode="markers",
                        marker=dict(symbol="diamond", size=16, color="#00B4D8", line=dict(color="white", width=1)),
                        name="Mínima Variância",
                        text=[tip],
                        hovertemplate=(
                            "<b>Mínima Variância</b><br>"
                            "Volatilidade: %{x:.2f}%<br>"
                            "Retorno: %{y:.2f}%<br>"
                            "%{text}<extra></extra>"
                        ),
                    )
                )

            # Capital Market Line (CML)
            if show_cml and opt_sharpe:
                vol_ms = opt_sharpe["volatility"]
                ret_ms = opt_sharpe["return"]
                # CML vai de (0, rf) até um pouco além do ponto de máx. Sharpe
                x_cml = np.linspace(0, vol_ms * 1.8, 100)
                slope = (ret_ms - rf) / vol_ms
                y_cml = rf + slope * x_cml
                fig.add_trace(go.Scatter(
                    x=x_cml * 100,
                    y=y_cml * 100,
                    mode="lines",
                    line=dict(color="#FFD166", width=2, dash="dash"),
                    name=f"CML (Incl. = {slope:.2f})",
                    hovertemplate=(
                        "<b>Capital Market Line</b><br>"
                        "Volatilidade: %{x:.2f}%<br>"
                        "Retorno: %{y:.2f}%<extra></extra>"
                    ),
                ))
                # Ponto Rf
                fig.add_trace(go.Scatter(
                    x=[0], y=[rf * 100],
                    mode="markers+text",
                    marker=dict(symbol="square", size=10, color="#FFD166"),
                    text=[f"Rf={rf:.2%}"],
                    textposition="middle right",
                    showlegend=False,
                    hovertemplate=f"<b>Ativo Livre de Risco</b><br>Rf = {rf:.2%}<extra></extra>",
                ))

            # Ativos individuais
            if show_ativos:
                from src.finance.statistics import asset_statistics
                stats = asset_statistics(returns, rf=rf)
                asset_colors = px.colors.qualitative.Set2
                for i, ticker in enumerate(tickers):
                    fig.add_trace(go.Scatter(
                        x=[stats.loc[ticker, "Vol. Anual"] * 100],
                        y=[stats.loc[ticker, "Retorno Anual"] * 100],
                        mode="markers+text",
                        name=ticker,
                        text=[ticker],
                        textposition="top center",
                        marker=dict(
                            symbol="diamond-open",
                            size=12,
                            color=asset_colors[i % len(asset_colors)],
                            line=dict(width=2),
                        ),
                        hovertemplate=(
                            f"<b>{ticker}</b><br>"
                            "Vol: %{x:.2f}%<br>"
                            "Ret: %{y:.2f}%"
                            f"<br>Sharpe: {stats.loc[ticker, 'Sharpe']:.3f}<extra></extra>"
                        ),
                    ))

            fig.update_layout(
                template="plotly_dark",
                title="Fronteira Eficiente de Markowitz",
                xaxis_title="Volatilidade Anual (%)",
                yaxis_title="Retorno Anual (%)",
                height=620,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            )
            st.plotly_chart(fig, use_container_width=True)

            # ── Top 10 carteiras por Sharpe ─────────────────────────────────
            st.divider()
            st.markdown("### 🏆 Top 10 Carteiras por Sharpe Ratio")
            top10 = df_sim.nlargest(10, "Sharpe").reset_index(drop=True)

            display_top = pd.DataFrame()
            display_top["Retorno"] = top10["Return"].apply(lambda x: f"{x:.2%}")
            display_top["Volatilidade"] = top10["Volatility"].apply(lambda x: f"{x:.2%}")
            display_top["Sharpe"] = top10["Sharpe"].apply(lambda x: f"{x:.4f}")
            for i, t in enumerate(tickers):
                display_top[t] = top10[f"w{i}"].apply(lambda x: f"{x:.1%}")

            st.dataframe(display_top, use_container_width=True)

            csv_top = display_top.to_csv(index=False).encode("utf-8")
            st.download_button(
                "💾 Baixar top 10 carteiras (CSV)",
                csv_top, "top10_carteiras.csv", "text/csv"
            )
        else:
            st.info("Clique em **⚙️ Calcular Fronteira Eficiente** para visualizar o gráfico.")
