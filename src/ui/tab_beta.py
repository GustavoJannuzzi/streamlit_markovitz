import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from src.finance.beta import all_betas


def render(tab):
    with tab:
        st.markdown("## 📉 Risco Sistemático (Beta)")
        st.markdown(
            "Análise do risco de mercado de cada ativo em relação ao IBOVESPA "
            "via regressão linear."
        )

        if "returns" not in st.session_state or st.session_state["returns"] is None:
            st.info("⬅️ Carregue os dados na aba **📋 Seleção de Ativos** primeiro.")
            return

        returns = st.session_state["returns"]
        market_returns = st.session_state.get("market_returns", pd.Series(dtype=float))

        if market_returns is None or market_returns.empty:
            st.warning("Dados do IBOVESPA não disponíveis. Recarregue os dados na aba **📋 Seleção de Ativos**.")
            return

        st.markdown("### 📋 Beta por Ativo")
        with st.spinner("Calculando regressões..."):
            df_betas = all_betas(returns, market_returns)

        df_show = df_betas.copy()
        for col in ["Alpha (α)", "Beta (β)", "R²"]:
            if col in df_show.columns:
                df_show[col] = pd.to_numeric(df_show[col], errors="coerce")

        styled = df_show.style.format(
            {"Alpha (α)": "{:.6f}", "Beta (β)": "{:.4f}", "R²": "{:.4f}"}
        ).background_gradient(cmap="RdYlGn_r", subset=["Beta (β)"])
        st.dataframe(styled, use_container_width=True)

        st.markdown("### 📊 Beta dos Ativos vs Mercado")
        betas_num = pd.to_numeric(df_betas["Beta (β)"], errors="coerce")
        tickers = list(df_betas.index)

        colors = [
            "#00B4D8" if b < 0.8 else ("#95D5B2" if b <= 1.2 else "#FF6B35")
            for b in betas_num
        ]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=tickers, y=betas_num.values, marker_color=colors,
            hovertemplate="%{x}<br>Beta: %{y:.4f}<extra></extra>", name="Beta",
        ))
        fig_bar.add_hline(y=1.0, line_dash="dash", line_color="white",
                          annotation_text="β = 1 (Mercado)", annotation_position="right")
        fig_bar.add_hline(y=0.8, line_dash="dot", line_color="#00B4D8", annotation_text="β = 0.8")
        fig_bar.add_hline(y=1.2, line_dash="dot", line_color="#FF6B35", annotation_text="β = 1.2")
        fig_bar.update_layout(template="plotly_dark", yaxis_title="Beta (β)", height=450,
                               title="Beta de cada ativo em relação ao IBOVESPA")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()
        st.markdown("### 💬 Interpretação Automática")
        for ticker in tickers:
            beta = float(df_betas.loc[ticker, "Beta (β)"])
            r2 = float(df_betas.loc[ticker, "R²"])
            alpha_val = float(df_betas.loc[ticker, "Alpha (α)"])
            classif = df_betas.loc[ticker, "Classificação"]
            if np.isnan(beta):
                continue
            if beta < 0.8:
                amp = "atenuar"
            elif beta <= 1.2:
                amp = "acompanhar de forma neutra"
            else:
                amp = f"amplificar em {(beta-1)*100:.0f}%"

            st.info(
                f"**{ticker}** | Beta: **{beta:.4f}** | Classif.: **{classif}** | R²: **{r2:.4f}**\n\n"
                f"Este ativo tende a **{amp}** os movimentos do mercado. "
                f"{r2:.0%} da variação é explicada pelo IBOVESPA."
            )

        st.divider()
        st.markdown("### 🔬 Regressão Detalhada por Ativo")
        for ticker in tickers:
            beta = float(df_betas.loc[ticker, "Beta (β)"])
            alpha_val = float(df_betas.loc[ticker, "Alpha (α)"])
            r2 = float(df_betas.loc[ticker, "R²"])
            if np.isnan(beta):
                continue
            with st.expander(f"📈 {ticker} — β={beta:.4f} | α={alpha_val:.6f} | R²={r2:.4f}"):
                df_reg = pd.concat([returns[ticker], market_returns], axis=1).dropna()
                df_reg.columns = [ticker, "IBOVESPA"]
                x_vals = df_reg["IBOVESPA"].values * 100
                y_vals = df_reg[ticker].values * 100
                x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                y_line = alpha_val * 100 + beta * x_line

                fig_sc = go.Figure()
                fig_sc.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, mode="markers",
                    marker=dict(size=4, color="#0066CC", opacity=0.5),
                    name="Observações",
                    hovertemplate="Mercado: %{x:.2f}%<br>Ativo: %{y:.2f}%<extra></extra>",
                ))
                fig_sc.add_trace(go.Scatter(
                    x=x_line, y=y_line, mode="lines",
                    line=dict(color="#FF6B35", width=2),
                    name=f"Ri = {alpha_val:.4f} + {beta:.4f}·Rm",
                ))
                fig_sc.update_layout(
                    template="plotly_dark",
                    xaxis_title="Retorno IBOVESPA (%)",
                    yaxis_title=f"Retorno {ticker} (%)",
                    height=400,
                )
                st.plotly_chart(fig_sc, use_container_width=True)
