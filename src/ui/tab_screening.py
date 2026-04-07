import streamlit as st
import pandas as pd
from src.data.fundamentus import fetch_fundamentus, apply_filters
from src.data.loader import download_prices
from src.finance.returns import simple_returns


def render(tab):
    with tab:
        st.markdown("## 🔍 Screening Fundamentalista")
        st.markdown(
            "Descubra ativos de qualidade na B3 aplicando filtros fundamentalistas "
            "via Fundamentus. Após filtrar, envie os ativos escolhidos para a Aba de Seleção."
        )

        # ── Filtros ────────────────────────────────────────────────────────
        with st.expander("⚙️ Filtros Fundamentalistas", expanded=True):
            # Preset rápidos
            st.markdown("**🎯 Presets rápidos:**")
            preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)

            preset = None
            if preset_col1.button("🔎 Amplo (relaxado)", key="preset_amplo", use_container_width=True):
                preset = "amplo"
            if preset_col2.button("⚖️ Balanceado", key="preset_bal", use_container_width=True):
                preset = "balanceado"
            if preset_col3.button("⭐ Qualidade", key="preset_qual", use_container_width=True):
                preset = "qualidade"
            if preset_col4.button("🔄 Limpar filtros", key="preset_clear", use_container_width=True):
                preset = "limpar"

            # Valores default por preset
            PRESETS = {
                "amplo":       dict(pl=30.0,  pvp=5.0, ev=15.0, db=3.0, roe=5.0,  roic=5.0,  dy=0.0, liq=200_000.0,  mrg=-10.0),
                "balanceado":  dict(pl=20.0,  pvp=3.5, ev=12.0, db=2.5, roe=8.0,  roic=8.0,  dy=2.0, liq=500_000.0,  mrg=3.0),
                "qualidade":   dict(pl=15.0,  pvp=3.0, ev=10.0, db=2.0, roe=15.0, roic=12.0, dy=3.0, liq=1_000_000.0, mrg=8.0),
                "limpar":      dict(pl=50.0,  pvp=10.0, ev=20.0, db=5.0, roe=0.0, roic=0.0,  dy=0.0, liq=0.0,         mrg=-50.0),
            }

            if preset and preset in PRESETS:
                p = PRESETS[preset]
                st.session_state["sc_pl"]   = p["pl"]
                st.session_state["sc_pvp"]  = p["pvp"]
                st.session_state["sc_ev"]   = p["ev"]
                st.session_state["sc_db"]   = p["db"]
                st.session_state["sc_roe"]  = p["roe"]
                st.session_state["sc_roic"] = p["roic"]
                st.session_state["sc_dy"]   = p["dy"]
                st.session_state["sc_liq"]  = p["liq"]
                st.session_state["sc_mrg"]  = p["mrg"]

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                pl_max   = st.slider("P/L máximo",           0.0, 50.0, st.session_state.get("sc_pl", 20.0),  0.5, key="sc_pl")
                pvp_max  = st.slider("P/VP máximo",          0.0, 10.0, st.session_state.get("sc_pvp", 3.5),  0.1, key="sc_pvp")
                ev_max   = st.slider("EV/EBITDA máximo",     0.0, 20.0, st.session_state.get("sc_ev", 12.0),  0.5, key="sc_ev")
                div_brut_max = st.slider("Dív.Brut/Patrim. máx.", 0.0, 5.0, st.session_state.get("sc_db", 2.5), 0.1, key="sc_db")
            with col2:
                roe_min  = st.slider("ROE mínimo (%)",        0.0, 50.0, st.session_state.get("sc_roe", 8.0),  0.5, key="sc_roe")
                roic_min = st.slider("ROIC mínimo (%)",       0.0, 30.0, st.session_state.get("sc_roic", 8.0), 0.5, key="sc_roic")
                dy_min   = st.slider("Div.Yield mínimo (%)",  0.0, 20.0, st.session_state.get("sc_dy", 2.0),   0.5, key="sc_dy")
                liq_min  = st.number_input(
                    "Liq. 2 meses mínima (R$)",
                    min_value=0.0,
                    value=float(st.session_state.get("sc_liq", 500_000.0)),
                    step=100_000.0,
                    format="%.0f",
                    key="sc_liq",
                )
                mrg_liq_min = st.slider("Mrg. Líq. mínima (%)", -50.0, 50.0, st.session_state.get("sc_mrg", 3.0), 0.5, key="sc_mrg")

        aplicar = st.button("🔍 Aplicar Filtros", type="primary", key="btn_screening")

        if aplicar:
            with st.spinner("Buscando dados do Fundamentus..."):
                df_full = fetch_fundamentus()

            if df_full.empty:
                st.error("Não foi possível obter dados do Fundamentus. Verifique sua conexão.")
                return

            filters = {
                "pl_max":          pl_max,
                "pvp_max":         pvp_max,
                "roe_min":         roe_min  / 100,
                "dy_min":          dy_min   / 100,
                "roic_min":        roic_min / 100,
                "liq_min":         liq_min,
                "ev_ebitda_max":   ev_max,
                "margem_liq_min":  mrg_liq_min / 100,
            }

            df_filtered = apply_filters(df_full, filters)
            st.session_state["sc_df_filtered"] = df_filtered
            st.session_state["sc_df_total"]    = len(df_full)

        # ── Resultado ──────────────────────────────────────────────────────
        if "sc_df_filtered" in st.session_state:
            df_filtered = st.session_state["sc_df_filtered"]
            total = st.session_state.get("sc_df_total", "?")

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("✅ Ativos encontrados", len(df_filtered))
            col_m2.metric("📊 Total no Fundamentus", total)
            if total and len(df_filtered) > 0:
                col_m3.metric("🎯 Taxa de aprovação", f"{len(df_filtered)/total:.1%}")

            if df_filtered.empty:
                st.warning(
                    "Nenhum ativo passou pelos filtros. Tente os presets **🔎 Amplo** ou **⚖️ Balanceado**."
                )
                return

            # Colunas para exibição
            display_cols = [
                c for c in [
                    "Papel", "P/L", "P/VP", "EV/EBITDA", "ROE", "ROIC",
                    "Div.Yield", "Mrg. Líq.", "Liq.2meses",
                ]
                if c in df_filtered.columns
            ]
            df_display = df_filtered[display_cols].copy()

            # Formatação % e R$
            pct_cols_show = ["ROE", "ROIC", "Div.Yield", "Mrg. Líq."]
            for col in pct_cols_show:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(
                        lambda x: f"{x:.1%}" if pd.notna(x) else "—"
                    )
            if "Liq.2meses" in df_display.columns:
                df_display["Liq.2meses"] = df_display["Liq.2meses"].apply(
                    lambda x: f"R$ {x:,.0f}" if pd.notna(x) else "—"
                )

            st.dataframe(df_display, use_container_width=True)

            # Download
            csv_sc = df_display.to_csv(index=False).encode("utf-8")
            st.download_button(
                "💾 Baixar resultado (CSV)", csv_sc, "screening_resultado.csv", "text/csv"
            )

            # ── Seleção para carteira ──────────────────────────────────────
            st.divider()
            st.markdown("### ➕ Adicionar à Carteira")

            papeis = list(df_filtered["Papel"].dropna().unique()) if "Papel" in df_filtered.columns else []

            # Pré-seleciona top 5 por ROIC
            default_sel = []
            if "ROIC" in df_filtered.columns and papeis:
                top5 = (
                    df_filtered[["Papel", "ROIC"]]
                    .dropna()
                    .sort_values("ROIC", ascending=False)
                    .head(5)["Papel"]
                    .tolist()
                )
                default_sel = [p for p in top5 if p in papeis]

            selecionados = st.multiselect(
                "Selecione os ativos para usar na carteira (pré-selecionados: top 5 ROIC)",
                options=papeis,
                default=default_sel,
                key="sc_selecionados",
            )

            if st.button("➕ Usar estes ativos na Aba 1", key="btn_usar_screening"):
                if not selecionados:
                    st.warning("Selecione pelo menos um ativo.")
                else:
                    st.session_state["tickers_sugeridos"] = selecionados
                    periodo = st.session_state.get("periodo", "3y")
                    with st.spinner("Carregando dados dos ativos selecionados..."):
                        prices = download_prices(selecionados, period=periodo)
                        if not prices.empty:
                            returns = simple_returns(prices)
                            st.session_state["prices"]  = prices
                            st.session_state["returns"] = returns
                            st.session_state["tickers"] = list(prices.columns)
                    st.success(
                        f"✅ {len(selecionados)} ativos carregados! "
                        "Vá para outras abas para analisar."
                    )
