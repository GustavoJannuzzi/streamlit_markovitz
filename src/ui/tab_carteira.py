import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.finance.portfolio import portfolio_return, portfolio_volatility, portfolio_sharpe
from src.finance.covariance import covariance_matrix
from src.finance.optimization import min_variance_portfolio, max_sharpe_portfolio


def render(tab):
    with tab:
        st.markdown("## 🧮 Construção da Carteira")

        if "returns" not in st.session_state or st.session_state["returns"] is None:
            st.info("⬅️ Carregue os dados na aba **📋 Seleção de Ativos** primeiro.")
            return

        returns = st.session_state["returns"]
        tickers = st.session_state["tickers"]
        rf = st.session_state.get("rf", 0.1075)
        n = len(tickers)

        mean_returns_annual = returns.mean().values * 252
        cov = covariance_matrix(returns).values

        # ══════════════════════════════════════════════════════════════════
        # Seção 4A — Carteira Manual
        # ══════════════════════════════════════════════════════════════════
        st.markdown("### 🎛️ Carteira Manual")
        st.markdown("Ajuste os pesos de cada ativo (devem somar 100%).")

        weights_pct = []
        cols = st.columns(min(n, 5))
        for i, ticker in enumerate(tickers):
            default_w = round(100 / n)
            w = cols[i % 5].slider(
                f"{ticker}",
                min_value=0,
                max_value=100,
                value=default_w,
                step=1,
                key=f"peso_{ticker}",
            )
            weights_pct.append(w)

        soma = sum(weights_pct)
        if abs(soma - 100) > 0.1:
            st.warning(f"⚠️ Os pesos somam **{soma}%** — ajuste para totalizarem **100%**.")
        else:
            st.success("✅ Os pesos somam 100%.")

        # Métricas da carteira manual
        w_arr = np.array(weights_pct) / 100.0
        if abs(soma - 100) <= 0.1:
            ret_manual = portfolio_return(w_arr, mean_returns_annual)
            vol_manual = portfolio_volatility(w_arr, cov)
            sharpe_manual = portfolio_sharpe(w_arr, mean_returns_annual, cov, rf)

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("📈 Retorno Esperado", f"{ret_manual:.2%}")
            col_m2.metric("📉 Volatilidade", f"{vol_manual:.2%}")
            col_m3.metric("⭐ Sharpe Ratio", f"{sharpe_manual:.3f}")

            # Gráfico pizza
            fig_pie = px.pie(
                names=tickers,
                values=weights_pct,
                title="Composição da Carteira Manual",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                template="plotly_dark",
            )
            fig_pie.update_traces(textinfo="percent+label", hole=0.3)
            fig_pie.update_layout(height=450)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()

        # ══════════════════════════════════════════════════════════════════
        # Seção 4B — Carteiras Otimizadas
        # ══════════════════════════════════════════════════════════════════
        st.markdown("### 🤖 Carteiras Otimizadas")

        with st.spinner("Calculando otimizações..."):
            min_var = min_variance_portfolio(mean_returns_annual, cov)
            max_sh = max_sharpe_portfolio(mean_returns_annual, cov, rf)
            eq_weights = np.ones(n) / n
            ret_eq = portfolio_return(eq_weights, mean_returns_annual)
            vol_eq = portfolio_volatility(eq_weights, cov)
            sharpe_eq = portfolio_sharpe(eq_weights, mean_returns_annual, cov, rf)

        # ── Três colunas ───────────────────────────────────────────────
        col_mv, col_ms, col_eq = st.columns(3)

        def _bar_weights(weights_arr, ticker_list, title, color):
            fig = go.Figure(
                go.Bar(
                    x=ticker_list,
                    y=weights_arr * 100,
                    marker_color=color,
                )
            )
            fig.update_layout(
                template="plotly_dark",
                title=title,
                yaxis_title="Peso (%)",
                height=350,
                margin=dict(t=50, b=30),
            )
            return fig

        benchmark_sharpe = sharpe_eq  # para delta

        for col, result, label, color in [
            (col_mv, min_var, "Mínima Variância", "#00B4D8"),
            (col_ms, max_sh, "Máximo Sharpe", "#FFD166"),
        ]:
            with col:
                st.markdown(f"**{label}**")
                if result is None:
                    st.warning("Otimização não convergiu.")
                else:
                    st.metric("Retorno", f"{result['return']:.2%}")
                    st.metric("Volatilidade", f"{result['volatility']:.2%}")
                    st.metric(
                        "Sharpe",
                        f"{result['sharpe']:.3f}",
                        delta=f"{result['sharpe'] - benchmark_sharpe:+.3f} vs 1/N",
                    )
                    fig = _bar_weights(result["weights"], tickers, f"Pesos — {label}", color)
                    st.plotly_chart(fig, use_container_width=True)

        with col_eq:
            st.markdown("**Igual (1/N)**")
            st.metric("Retorno", f"{ret_eq:.2%}")
            st.metric("Volatilidade", f"{vol_eq:.2%}")
            st.metric("Sharpe", f"{sharpe_eq:.3f}")
            fig_eq = _bar_weights(eq_weights, tickers, "Pesos — Igual (1/N)", "#95D5B2")
            st.plotly_chart(fig_eq, use_container_width=True)

        # ── Tabela comparativa ─────────────────────────────────────────
        st.divider()
        st.markdown("### 📊 Comparativo de Estratégias")

        strategies_data = {
            "Estratégia": ["Mínima Variância", "Máximo Sharpe", "Igual (1/N)"],
            "Retorno": [
                f"{min_var['return']:.2%}" if min_var else "N/D",
                f"{max_sh['return']:.2%}" if max_sh else "N/D",
                f"{ret_eq:.2%}",
            ],
            "Volatilidade": [
                f"{min_var['volatility']:.2%}" if min_var else "N/D",
                f"{max_sh['volatility']:.2%}" if max_sh else "N/D",
                f"{vol_eq:.2%}",
            ],
            "Sharpe": [
                f"{min_var['sharpe']:.3f}" if min_var else "N/D",
                f"{max_sh['sharpe']:.3f}" if max_sh else "N/D",
                f"{sharpe_eq:.3f}",
            ],
        }
        df_comp = pd.DataFrame(strategies_data)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

        # ── Download dos pesos ─────────────────────────────────────────
        weights_df = pd.DataFrame({"Ativo": tickers})
        if min_var:
            weights_df["Min. Variância (%)"] = (min_var["weights"] * 100).round(2)
        if max_sh:
            weights_df["Máx. Sharpe (%)"] = (max_sh["weights"] * 100).round(2)
        weights_df["Igual 1/N (%)"] = (eq_weights * 100).round(2)

        csv_w = weights_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "💾 Baixar pesos (CSV)",
            csv_w,
            "pesos_carteiras.csv",
            "text/csv",
        )
