import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.finance.statistics import asset_statistics
from src.finance.covariance import covariance_matrix, correlation_matrix


def _color_sharpe(val):
    """Coloração condicional para Sharpe."""
    try:
        v = float(val)
        if v >= 1.0:
            return "color: #00C48C; font-weight: bold"
        elif v >= 0.5:
            return "color: #FFD166"
        else:
            return "color: #FF6B6B"
    except Exception:
        return ""


def _color_ret(val):
    try:
        v = float(str(val).replace("%", ""))
        return "color: #00C48C" if v > 0 else "color: #FF6B6B"
    except Exception:
        return ""


def render(tab):
    with tab:
        st.markdown("## 📊 Estatísticas dos Ativos")

        if "returns" not in st.session_state or st.session_state["returns"] is None:
            st.info("⬅️ Carregue os dados na aba **📋 Seleção de Ativos** primeiro.")
            return

        returns = st.session_state["returns"]
        prices  = st.session_state.get("prices")
        rf      = st.session_state.get("rf", 0.1075)

        # ── Tabela de estatísticas ─────────────────────────────────────────
        st.markdown("### 📋 Resumo Estatístico")
        stats = asset_statistics(returns, rf=rf)

        # Formata para exibição
        stats_fmt = pd.DataFrame(index=stats.index)
        stats_fmt["Ret. Médio Diário"] = stats["Retorno Médio Diário"].apply(lambda x: f"{x:.4f}")
        stats_fmt["Retorno Anual"]     = stats["Retorno Anual"].apply(lambda x: f"{x:.2%}")
        stats_fmt["Vol. Diária"]       = stats["Vol. Diária"].apply(lambda x: f"{x:.4f}")
        stats_fmt["Vol. Anual"]        = stats["Vol. Anual"].apply(lambda x: f"{x:.2%}")
        stats_fmt["Sharpe"]            = stats["Sharpe"].apply(lambda x: f"{x:.3f}")
        stats_fmt["Assimetria"]        = stats["Assimetria"].apply(lambda x: f"{x:.3f}")
        stats_fmt["Curtose"]           = stats["Curtose"].apply(lambda x: f"{x:.3f}")

        styled = (
            stats_fmt.style
            .applymap(_color_ret, subset=["Retorno Anual"])
            .applymap(_color_sharpe, subset=["Sharpe"])
            .set_properties(**{"text-align": "right"})
            .set_table_styles([
                {"selector": "th", "props": [("text-align", "center"), ("font-weight", "bold")]}
            ])
        )
        st.dataframe(styled, use_container_width=True)

        csv_stats = stats.to_csv().encode("utf-8")
        st.download_button("💾 Baixar estatísticas (CSV)", csv_stats, "estatisticas_ativos.csv", "text/csv")

        st.divider()

        # ── Cards de destaques ─────────────────────────────────────────────
        st.markdown("### 🏅 Destaques")
        best_ret   = stats["Retorno Anual"].idxmax()
        best_sharpe = stats["Sharpe"].idxmax()
        low_vol    = stats["Vol. Anual"].idxmin()

        c1, c2, c3 = st.columns(3)
        c1.metric("🚀 Maior Retorno Anual", best_ret,
                  f"{stats.loc[best_ret, 'Retorno Anual']:.2%}")
        c2.metric("⭐ Melhor Sharpe", best_sharpe,
                  f"{stats.loc[best_sharpe, 'Sharpe']:.3f}")
        c3.metric("🛡️ Menor Volatilidade", low_vol,
                  f"{stats.loc[low_vol, 'Vol. Anual']:.2%}")

        st.divider()

        # ── Gráfico 0: Preços normalizados (base 100)  ─────────────────────
        if prices is not None and not prices.empty:
            st.markdown("### 📈 Performance Normalizada (Base 100)")
            prices_norm = prices / prices.iloc[0] * 100
            colors = px.colors.qualitative.Plotly
            fig0 = go.Figure()
            for i, col in enumerate(prices_norm.columns):
                fig0.add_trace(go.Scatter(
                    x=prices_norm.index,
                    y=prices_norm[col],
                    name=col,
                    mode="lines",
                    line=dict(color=colors[i % len(colors)], width=2),
                    hovertemplate="%{x|%d/%m/%Y}<br>%{y:.1f}<extra>" + col + "</extra>",
                ))
            fig0.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                           annotation_text="Base 100")
            fig0.update_layout(
                template="plotly_dark",
                yaxis_title="Valor (Base 100 = início do período)",
                xaxis_title="Data",
                height=500,
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig0, use_container_width=True)
            st.divider()

        # ── Gráfico 1: Retorno Anual vs Volatilidade Anual ─────────────────
        st.markdown("### 📊 Risco × Retorno por Ativo")
        # Scatter mais informativo
        fig1 = go.Figure()
        colors = px.colors.qualitative.Plotly
        for i, ticker in enumerate(stats.index):
            fig1.add_trace(go.Scatter(
                x=[stats.loc[ticker, "Vol. Anual"] * 100],
                y=[stats.loc[ticker, "Retorno Anual"] * 100],
                mode="markers+text",
                name=ticker,
                text=[ticker],
                textposition="top center",
                marker=dict(
                    size=max(14, stats.loc[ticker, "Sharpe"] * 12),
                    color=colors[i % len(colors)],
                    line=dict(color="white", width=1.5),
                    symbol="circle",
                ),
                hovertemplate=(
                    f"<b>{ticker}</b><br>"
                    "Volatilidade: %{x:.2f}%<br>"
                    "Retorno: %{y:.2f}%<br>"
                    f"Sharpe: {stats.loc[ticker, 'Sharpe']:.3f}<extra></extra>"
                ),
            ))
        fig1.add_hline(y=rf * 100, line_dash="dot", line_color="#FFD166",
                       annotation_text=f"Rf = {rf:.2%}", annotation_position="right")
        fig1.update_layout(
            template="plotly_dark",
            xaxis_title="Volatilidade Anual (%)",
            yaxis_title="Retorno Anual (%)",
            height=500,
            showlegend=False,
            title="Tamanho do círculo proporcional ao Sharpe Ratio",
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.divider()

        # ── Gráfico 2: Matriz de correlação ────────────────────────────────
        st.markdown("### 🔗 Matriz de Correlação")
        corr = correlation_matrix(returns)
        fig2 = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdYlGn",
            zmin=-1,
            zmax=1,
            template="plotly_dark",
            title="Correlação entre Ativos (−1 = diversificação máxima, +1 = sem diversificação)",
        )
        fig2.update_layout(height=500)
        fig2.update_traces(textfont=dict(size=14))
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # ── Gráfico 3: Retorno cumulativo ─────────────────────────────────
        st.markdown("### 📈 Retorno Acumulado (%)")
        cumulative = (1 + returns).cumprod() - 1
        fig3 = go.Figure()
        for i, col in enumerate(cumulative.columns):
            fig3.add_trace(go.Scatter(
                x=cumulative.index,
                y=cumulative[col] * 100,
                name=col,
                mode="lines",
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate="%{x|%d/%m/%Y}<br>%{y:.2f}%<extra>" + col + "</extra>",
            ))
        fig3.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig3.update_layout(
            template="plotly_dark",
            yaxis_title="Retorno Acumulado (%)",
            xaxis_title="Data",
            height=500,
            hovermode="x unified",
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # ── Gráfico 4: Box plot dos retornos diários ────────────────────────
        st.markdown("### 📦 Distribuição dos Retornos Diários")
        fig4 = go.Figure()
        for i, col in enumerate(returns.columns):
            fig4.add_trace(go.Box(
                y=returns[col] * 100,
                name=col,
                marker_color=colors[i % len(colors)],
                boxmean="sd",
                hovertemplate=f"<b>{col}</b><br>%{{y:.3f}}%<extra></extra>",
            ))
        fig4.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig4.update_layout(
            template="plotly_dark",
            yaxis_title="Retorno Diário (%)",
            height=500,
            showlegend=False,
            title="Mediana, IQR e outliers dos retornos diários",
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        # ── Gráfico 5: Barras Retorno vs Vol ───────────────────────────────
        st.markdown("### 📊 Retorno vs Volatilidade Anual (Comparativo)")
        fig5 = go.Figure()
        tickers_list = list(stats.index)
        fig5.add_trace(go.Bar(
            name="Retorno Anual",
            x=tickers_list,
            y=stats["Retorno Anual"].values * 100,
            marker_color="#0066CC",
            text=[f"{v:.1%}" for v in stats["Retorno Anual"].values],
            textposition="outside",
        ))
        fig5.add_trace(go.Bar(
            name="Vol. Anual",
            x=tickers_list,
            y=stats["Vol. Anual"].values * 100,
            marker_color="#FF6B35",
            text=[f"{v:.1%}" for v in stats["Vol. Anual"].values],
            textposition="outside",
        ))
        fig5.update_layout(
            template="plotly_dark",
            barmode="group",
            yaxis_title="(%)",
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig5, use_container_width=True)
