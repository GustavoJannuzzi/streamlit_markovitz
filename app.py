import streamlit as st

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Análise de Portfólio Markowitz",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Imports das abas ───────────────────────────────────────────────────────────
from src.ui import (
    tab_selecao,
    tab_screening,
    tab_estatisticas,
    tab_carteira,
    tab_fronteira,
    tab_beta,
    tab_teoria,
)

# ── Cabeçalho ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #0066CC 0%, #003380 50%, #001a4d 100%);
        padding: 2rem 2.5rem 1.5rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    ">
        <h1 style="margin: 0; font-size: 2rem; color: #FFFFFF; font-weight: 700;">
            📈 Análise de Portfólio Markowitz
        </h1>
        <p style="margin: 0.5rem 0 0 0; color: #A8C8F0; font-size: 1rem;">
            Teoria Moderna de Portfólio aplicada a ativos da B3 &nbsp;|&nbsp;
            Seleção, Otimização & Fronteira Eficiente
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Status da sessão (sidebar) ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Status da Sessão")
    if "tickers" in st.session_state and st.session_state["tickers"]:
        st.success(f"✅ {len(st.session_state['tickers'])} ativos carregados")
        st.markdown("**Ativos:** " + ", ".join(st.session_state["tickers"]))
        periodo = st.session_state.get("periodo", "—")
        rf = st.session_state.get("rf", 0.1075)
        tipo = st.session_state.get("tipo_retorno", "—")
        st.markdown(f"**Período:** {periodo}")
        st.markdown(f"**Retorno:** {tipo}")
        st.markdown(f"**Rf:** {rf:.2%} a.a.")

        if st.button("🗑️ Limpar sessão", key="btn_clear"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        st.info("⬅️ Nenhum dado carregado.\nVá para a aba **Seleção de Ativos**.")

    st.divider()
    st.markdown(
        "**ℹ️ Como usar:**\n"
        "1. Selecione ativos na aba 📋\n"
        "2. Ou filtre pelo 🔍 Screening\n"
        "3. Explore estatísticas 📊\n"
        "4. Monte carteiras 🧮\n"
        "5. Veja a fronteira 📈\n"
        "6. Analise o Beta 📉\n"
        "7. Consulte a teoria 📚"
    )

# ── Abas principais ────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📋 Seleção de Ativos",
    "🔍 Screening Fundamentalista",
    "📊 Estatísticas dos Ativos",
    "🧮 Construção da Carteira",
    "📈 Fronteira Eficiente",
    "📉 Risco Sistemático (Beta)",
    "📚 Teoria & Fórmulas",
])

tab_selecao.render(tabs[0])
tab_screening.render(tabs[1])
tab_estatisticas.render(tabs[2])
tab_carteira.render(tabs[3])
tab_fronteira.render(tabs[4])
tab_beta.render(tabs[5])
tab_teoria.render(tabs[6])
