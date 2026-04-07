import streamlit as st
import pandas as pd
from src.data.fundamentus import fetch_fundamentus, apply_filters
from src.data.loader import download_prices
from src.finance.returns import simple_returns


DISPLAY_COLS = [
    "Papel", "ROE", "ROIC", "Div.Yield", "Mrg. Líq.", "Mrg Ebit",
    "Cresc. Rec.5a", "P/L", "P/VP", "EV/EBITDA", "Liq.2meses",
]

# Incrementar quando a lógica de conversão mudar, para invalidar cache automático
DATA_VERSION = "v3"

PRESETS = {
    "amplo":      dict(roe=0.0,  roic=0.0,  dy=0.0, mrg=-50.0, ebit=-50.0, cresc=-50.0),
    "lucrativo":  dict(roe=5.0,  roic=5.0,  dy=0.0, mrg=3.0,   ebit=3.0,   cresc=-50.0),
    "balanceado": dict(roe=10.0, roic=8.0,  dy=0.0, mrg=5.0,   ebit=5.0,   cresc=-50.0),
    "qualidade":  dict(roe=15.0, roic=12.0, dy=0.0, mrg=8.0,   ebit=8.0,   cresc=0.0),
    "dividendos": dict(roe=8.0,  roic=6.0,  dy=4.0, mrg=5.0,   ebit=5.0,   cresc=-50.0),
}

PRESET_KEYS = {
    "roe": "sc_roe", "roic": "sc_roic", "dy": "sc_dy",
    "mrg": "sc_mrg", "ebit": "sc_ebit", "cresc": "sc_cresc",
}


def _apply_preset(name: str):
    if name == "limpar":
        for v in PRESET_KEYS.values():
            st.session_state.pop(v, None)
    elif name in PRESETS:
        for field, ss_key in PRESET_KEYS.items():
            st.session_state[ss_key] = float(PRESETS[name][field])
    st.rerun()


def _fmt_pct(val):
    try:
        return f"{float(val):.1%}" if pd.notna(val) else "—"
    except Exception:
        return "—"


def _fmt_num(val):
    try:
        f = float(val)
        return f"{f:.2f}" if pd.notna(val) and f != 0.0 else "—"
    except Exception:
        return "—"


def _format_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pct_cols = ["ROE", "ROIC", "Div.Yield", "Mrg. Líq.", "Mrg Ebit", "Cresc. Rec.5a"]
    for col in pct_cols:
        if col in df.columns:
            df[col] = df[col].apply(_fmt_pct)
    num_cols = ["P/L", "P/VP", "EV/EBITDA"]
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].apply(_fmt_num)
    if "Liq.2meses" in df.columns:
        df["Liq.2meses"] = df["Liq.2meses"].apply(
            lambda x: f"R$ {float(x):,.0f}" if pd.notna(x) and str(x) not in ("nan", "") and float(x if x else 0) > 0 else "—"
        )
    return df


def render(tab):
    with tab:
        st.markdown("## 🔍 Screening Fundamentalista")
        st.markdown(
            "Filtre ações da B3 por indicadores de qualidade e rentabilidade. "
            "Dados obtidos em tempo real do [Fundamentus](https://www.fundamentus.com.br)."
        )

        # ── Aviso técnico ────────────────────────────────────────────────
        with st.expander("ℹ️ Sobre os dados disponíveis", expanded=False):
            st.info(
                "**Campos disponíveis para filtro:** ROE, ROIC, Div.Yield, Margem Líquida, "
                "Margem EBIT e Crescimento de Receita.\n\n"
                "**Campos exibidos mas não filtráveis:** P/L, P/VP, EV/EBITDA e Liquidez — "
                "esses dados são carregados via JavaScript no site do Fundamentus e não estão "
                "disponíveis no scraping estático. Eles aparecem na tabela quando disponíveis."
            )

        # ── Invalida cache se versoão mudar ou dados antigos ────────────
        if st.session_state.get("sc_data_version") != DATA_VERSION:
            st.cache_data.clear()
            for k in ["sc_df_full", "sc_df_total", "sc_df_filtered"]:
                st.session_state.pop(k, None)
            st.session_state["sc_data_version"] = DATA_VERSION

        # ── Carregamento de dados ────────────────────────────────────────
        if "sc_df_full" not in st.session_state:
            with st.spinner("📡 Carregando dados do Fundamentus (997 ações)..."):
                df_full = fetch_fundamentus()
            if df_full.empty:
                st.error("❌ Não foi possível obter dados. Verifique sua conexão e tente novamente.")
                if st.button("🔄 Tentar novamente"):
                    st.rerun()
                return
            st.session_state["sc_df_full"] = df_full
            st.session_state["sc_df_total"] = len(df_full)

        df_full = st.session_state["sc_df_full"]
        total = st.session_state.get("sc_df_total", len(df_full))

        col_btn, col_info = st.columns([1, 4])
        with col_btn:
            if st.button("🔄 Atualizar base", key="btn_refresh_fund"):
                st.cache_data.clear()
                for k in ["sc_df_full", "sc_df_total", "sc_df_filtered"]:
                    st.session_state.pop(k, None)
                st.rerun()
        with col_info:
            st.caption(f"📊 **{total}** ações na base. Filtros aplicados automaticamente.")

        st.divider()

        # ══════════════════════════════════════════════════════════════════
        # PRESETS
        # ══════════════════════════════════════════════════════════════════
        st.markdown("**🎯 Presets rápidos:**")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        if c1.button("🔎 Amplo",       key="p_amplo",  use_container_width=True): _apply_preset("amplo")
        if c2.button("💼 Lucrativo",   key="p_lucr",   use_container_width=True): _apply_preset("lucrativo")
        if c3.button("⚖️ Balanceado",  key="p_bal",    use_container_width=True): _apply_preset("balanceado")
        if c4.button("⭐ Qualidade",   key="p_qual",   use_container_width=True): _apply_preset("qualidade")
        if c5.button("💰 Dividendos",  key="p_div",    use_container_width=True): _apply_preset("dividendos")
        if c6.button("❌ Limpar",      key="p_clear",  use_container_width=True): _apply_preset("limpar")

        # ══════════════════════════════════════════════════════════════════
        # FILTROS (apenas campos com dados reais)
        # ══════════════════════════════════════════════════════════════════
        with st.expander("⚙️ Filtros", expanded=True):
            st.caption("**Dica:** Valor 0% (ou mínimo) = filtro ignorado para aquele campo.")
            col1, col2 = st.columns(2)
            with col1:
                roe_min  = st.slider("ROE mínimo (%)",             0.0,  50.0,
                                     float(st.session_state.get("sc_roe",  0.0)), 0.5, key="sc_roe",
                                     help="Retorno sobre Patrimônio. 0 = ignora esse filtro.")
                roic_min = st.slider("ROIC mínimo (%)",            0.0,  30.0,
                                     float(st.session_state.get("sc_roic", 0.0)), 0.5, key="sc_roic",
                                     help="Retorno sobre Capital Investido. 0 = ignora.")
                dy_min   = st.slider("Div.Yield mínimo (%)",       0.0,  20.0,
                                     float(st.session_state.get("sc_dy",   0.0)), 0.5, key="sc_dy",
                                     help="Dividend Yield anual. 0 = ignora.")
            with col2:
                mrg_min  = st.slider("Margem Líquida mínima (%)", -50.0, 50.0,
                                     float(st.session_state.get("sc_mrg",  -50.0)), 0.5, key="sc_mrg",
                                     help="-50% = ignora. Ex: 5 = só empresas com Mrg.Líq. ≥ 5%.")
                ebit_min = st.slider("Margem EBIT mínima (%)",    -50.0, 50.0,
                                     float(st.session_state.get("sc_ebit", -50.0)), 0.5, key="sc_ebit",
                                     help="-50% = ignora.")
                cresc_min= st.slider("Cresc. Receita 5a mínimo (%)", -50.0, 50.0,
                                     float(st.session_state.get("sc_cresc", -50.0)), 0.5, key="sc_cresc",
                                     help="-50% = ignora. Ex: 0 = só empresas com crescimento positivo.")

        # ── Aplica filtros automaticamente ───────────────────────────────
        filters = {
            "roe_min":         roe_min  / 100.0,
            "roic_min":        roic_min / 100.0,
            "dy_min":          dy_min   / 100.0,
            "margem_liq_min":  mrg_min  / 100.0,
            "margem_ebit_min": ebit_min / 100.0,
            "cresc_min":       cresc_min / 100.0,
        }
        df_filtered = apply_filters(df_full, filters)

        # ══════════════════════════════════════════════════════════════════
        # MÉTRICAS
        # ══════════════════════════════════════════════════════════════════
        m1, m2, m3 = st.columns(3)
        m1.metric("✅ Ações encontradas", len(df_filtered))
        m2.metric("📊 Total na base", total)
        m3.metric("🎯 Taxa de aprovação",
                  f"{len(df_filtered)/total:.1%}" if total > 0 else "—")

        if df_filtered.empty:
            st.warning(
                "⚠️ Nenhuma ação passou pelos filtros. "
                "Tente o preset **🔎 Amplo** ou diminua os critérios mínimos para 0."
            )
            return

        # ══════════════════════════════════════════════════════════════════
        # BUSCA + ORDENAÇÃO
        # ══════════════════════════════════════════════════════════════════
        bc, sc, oc = st.columns([2, 2, 1])
        with bc:
            busca = st.text_input("🔎 Buscar por ticker", value="",
                                  placeholder="Ex: PETR, VALE, ITUB…", key="sc_busca")
        with sc:
            sort_options = [c for c in ["ROIC", "ROE", "Div.Yield", "Mrg. Líq.", "Mrg Ebit", "Cresc. Rec.5a"]
                            if c in df_filtered.columns]
            sort_col = st.selectbox("Ordenar por:", sort_options, key="sc_sort")
        with oc:
            ordem = st.radio("Ordem:", ["⬇️ Maior", "⬆️ Menor"], horizontal=True, key="sc_ordem")

        # Aplica busca e ordenação
        df_view = df_filtered.copy()
        if busca.strip() and "Papel" in df_view.columns:
            df_view = df_view[df_view["Papel"].str.contains(busca.strip().upper(), na=False)]

        ascending = (ordem == "⬆️ Menor")
        if sort_col in df_view.columns:
            df_view = df_view.sort_values(sort_col, ascending=ascending, na_position="last")

        # ══════════════════════════════════════════════════════════════════
        # TABELA INTERATIVA
        # ══════════════════════════════════════════════════════════════════
        st.markdown(f"### 📋 {len(df_view)} ações encontradas")
        st.caption("💡 Clique no cabeçalho da coluna para reordenar. P/L, P/VP e Liq exibem '—' pois requerem JavaScript.")

        cols_show = [c for c in DISPLAY_COLS if c in df_view.columns]
        df_display = _format_table(df_view[cols_show])

        st.dataframe(
            df_display,
            use_container_width=True,
            height=450,
            hide_index=True,
        )

        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button("💾 Baixar CSV", csv, "screening.csv", "text/csv", key="sc_dl")

        st.divider()

        # ══════════════════════════════════════════════════════════════════
        # SELEÇÃO PARA CARTEIRA
        # ══════════════════════════════════════════════════════════════════
        st.markdown("### ➕ Adicionar à Carteira")

        papeis = list(df_view["Papel"].dropna().unique()) if "Papel" in df_view.columns else []

        # Top 5 por ROIC como sugestão
        default_sel = []
        if "ROIC" in df_filtered.columns and papeis:
            top5 = (
                df_filtered[["Papel", "ROIC"]].dropna()
                .sort_values("ROIC", ascending=False)
                .head(5)["Papel"].tolist()
            )
            default_sel = [p for p in top5 if p in papeis][:5]

        selecionados = st.multiselect(
            f"Selecione os ativos ({len(papeis)} disponíveis, sugestão: top 5 por ROIC)",
            options=papeis,
            default=default_sel,
            key="sc_selecionados",
        )

        if selecionados:
            # Preview visual dos selecionados
            df_prev = df_filtered[df_filtered["Papel"].isin(selecionados)]
            prev_cols = [c for c in ["Papel", "ROE", "ROIC", "Div.Yield", "Mrg. Líq."] if c in df_prev.columns]
            st.dataframe(_format_table(df_prev[prev_cols]), use_container_width=True, hide_index=True)

        col_b1, col_b2 = st.columns([2, 3])
        with col_b1:
            if st.button("📥 Carregar para análise", type="primary", key="btn_usar"):
                if not selecionados:
                    st.warning("Selecione pelo menos um ativo.")
                else:
                    periodo = st.session_state.get("periodo", "3y")
                    with st.spinner(f"Baixando cotações de {len(selecionados)} ativos…"):
                        prices = download_prices(selecionados, period=periodo)
                    if not prices.empty:
                        from src.finance.returns import simple_returns
                        returns = simple_returns(prices)
                        st.session_state.update({
                            "prices": prices,
                            "returns": returns,
                            "tickers": list(prices.columns),
                            "tickers_sugeridos": selecionados,
                        })
                        st.success(
                            f"✅ {len(prices.columns)} ativos carregados! "
                            "Explore **📊 Estatísticas** ou **📈 Fronteira Eficiente**."
                        )
                    else:
                        st.error("Falha ao baixar cotações. Verifique se os tickers existem na B3.")
        with col_b2:
            st.info("💡 Os ativos selecionados aqui substituem os da **Aba de Seleção**.")
