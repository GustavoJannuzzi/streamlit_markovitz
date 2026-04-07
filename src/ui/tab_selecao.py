import streamlit as st
import pandas as pd
from src.data.loader import download_prices, get_market_index
from src.finance.returns import simple_returns, log_returns


DEFAULT_TICKERS = ["PETR4", "VALE3", "ITUB4", "BBDC4", "WEGE3"]


def render(tab):
    with tab:
        st.markdown("## 📋 Seleção de Ativos")
        st.markdown(
            "Configure os parâmetros e informe os tickers B3 para baixar os dados históricos."
        )

        # ── Parâmetros globais ────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            n_ativos = st.slider("Número de ativos", min_value=2, max_value=15, value=5, key="n_ativos")
        with col2:
            periodo = st.selectbox(
                "Período histórico",
                options=["1y", "2y", "3y", "5y"],
                index=2,
                key="periodo",
            )
        with col3:
            tipo_retorno = st.radio(
                "Tipo de retorno",
                options=["Simples", "Logarítmico"],
                horizontal=True,
                key="tipo_retorno",
            )
        with col4:
            rf_pct = st.number_input(
                "Taxa livre de risco (% a.a.)",
                min_value=0.0,
                max_value=50.0,
                value=10.75,
                step=0.25,
                format="%.2f",
                key="rf_pct",
            )
            rf = rf_pct / 100.0

        st.divider()

        # ── Entrada de tickers ────────────────────────────────────────────
        st.markdown("### Tickers dos Ativos")

        # Usa tickers do session_state se vieram do screening
        tickers_iniciais = st.session_state.get("tickers_sugeridos", DEFAULT_TICKERS[:])

        tickers = []
        cols = st.columns(min(n_ativos, 5))
        for i in range(n_ativos):
            col = cols[i % 5]
            default_val = tickers_iniciais[i] if i < len(tickers_iniciais) else ""
            ticker = col.text_input(
                f"Ativo {i + 1}",
                value=default_val,
                placeholder="Ex: PETR4",
                key=f"ticker_{i}",
            )
            if ticker.strip():
                tickers.append(ticker.strip().upper())

        # ── Botão de carregamento ─────────────────────────────────────────
        st.markdown("")
        carregar = st.button("▶ Carregar Dados", type="primary", key="btn_carregar")

        if carregar:
            if len(tickers) < 2:
                st.error("Informe pelo menos 2 tickers válidos.")
                return

            with st.spinner("Baixando dados históricos..."):
                prices = download_prices(tickers, period=periodo)
                market_prices = get_market_index(period=periodo)

            if prices.empty:
                st.error("Não foi possível baixar dados. Verifique os tickers informados.")
                return

            # Verifica quais tickers foram efetivamente baixados
            tickers_ok = list(prices.columns)
            tickers_invalidos = [t for t in tickers if t not in tickers_ok]
            if tickers_invalidos:
                st.warning(f"Tickers não encontrados e removidos: {', '.join(tickers_invalidos)}")

            if len(tickers_ok) < 2:
                st.error("São necessários pelo menos 2 ativos com dados válidos.")
                return

            # Calcula retornos
            if tipo_retorno == "Simples":
                returns = simple_returns(prices)
            else:
                returns = log_returns(prices)

            # Retornos do mercado
            market_returns = market_prices.pct_change().dropna() if not market_prices.empty else pd.Series(dtype=float)

            # Salva no session_state
            # NOTA: "periodo" e "tipo_retorno" já são gerenciados pelos
            # seus respectivos widgets (key=) — não atribuir manualmente.
            st.session_state["prices"] = prices
            st.session_state["returns"] = returns
            st.session_state["tickers"] = tickers_ok
            st.session_state["rf"] = rf
            st.session_state["market_prices"] = market_prices
            st.session_state["market_returns"] = market_returns

            st.success(
                f"✅ Dados carregados com sucesso! "
                f"{len(prices)} observações para {len(tickers_ok)} ativos | "
                f"Período: {str(prices.index[0].date())} → {str(prices.index[-1].date())}"
            )

        # ── Exibição dos dados carregados ──────────────────────────────────
        if "prices" in st.session_state and st.session_state["prices"] is not None:
            prices = st.session_state["prices"]

            st.markdown("### 📅 Últimas Observações de Preço")
            st.dataframe(
                prices.tail(10).style.format("{:.2f}"),
                use_container_width=True,
            )

            # Download CSV
            csv = prices.to_csv(index=True).encode("utf-8")
            st.download_button(
                label="💾 Baixar preços (CSV)",
                data=csv,
                file_name="precos_historicos.csv",
                mime="text/csv",
            )
