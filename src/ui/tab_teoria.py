import streamlit as st


def render(tab):
    with tab:
        st.markdown("## 📚 Teoria & Fórmulas")
        st.markdown(
            "Referência teórica completa da Teoria Moderna de Portfólio de Markowitz "
            "e métricas utilizadas nesta aplicação."
        )

        # ── 1. Markowitz ──────────────────────────────────────────────────
        with st.expander("1️⃣ Teoria Moderna de Portfólio (Markowitz, 1952)", expanded=True):
            st.markdown("""
A **Teoria Moderna de Portfólio** (TMP), desenvolvida por Harry Markowitz em 1952,
estabelece que um investidor pode construir uma carteira de ativos de forma a maximizar
o retorno esperado para um dado nível de risco, ou minimizar o risco para um dado nível
de retorno esperado.

O princípio fundamental é a **diversificação**: combinar ativos cujas variações de
preço não sejam perfeitamente correlacionadas reduz o risco total da carteira sem
necessariamente reduzir o retorno esperado.
            """)

        # ── 2. Retornos ───────────────────────────────────────────────────
        with st.expander("2️⃣ Retornos: Simples vs Logarítmico"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Retorno Simples**")
                st.latex(r"R_t = \frac{P_t - P_{t-1}}{P_{t-1}} = \frac{P_t}{P_{t-1}} - 1")
                st.markdown("Adequado para agregar retornos entre ativos em um mesmo período.")
            with col2:
                st.markdown("**Retorno Logarítmico**")
                st.latex(r"r_t = \ln\!\left(\frac{P_t}{P_{t-1}}\right)")
                st.markdown("Propriedades matemáticas mais convenientes; aditivo no tempo.")

        # ── 3. Métricas ───────────────────────────────────────────────────
        with st.expander("3️⃣ Métricas de Risco e Retorno"):
            st.markdown("**Retorno Esperado (anualizado)**")
            st.latex(r"\mu_{anual} = \bar{R}_{diário} \times 252")

            st.markdown("**Variância e Desvio Padrão (anualizado)**")
            st.latex(r"\sigma^2_{anual} = \sigma^2_{diário} \times 252")
            st.latex(r"\sigma_{anual} = \sigma_{diário} \times \sqrt{252}")

            st.markdown("**Assimetria (Skewness)**")
            st.latex(
                r"\text{Skew} = \frac{1}{n}\sum_{t=1}^n"
                r"\left(\frac{R_t - \bar{R}}{\sigma}\right)^3"
            )

            st.markdown("**Curtose (Kurtosis)**")
            st.latex(
                r"\text{Kurt} = \frac{1}{n}\sum_{t=1}^n"
                r"\left(\frac{R_t - \bar{R}}{\sigma}\right)^4 - 3"
            )

        # ── 4. Covariância e Correlação ───────────────────────────────────
        with st.expander("4️⃣ Matriz de Covariância e Correlação"):
            st.markdown("**Covariância entre ativos i e j**")
            st.latex(
                r"\sigma_{ij} = \frac{1}{T-1}\sum_{t=1}^T"
                r"(R_{i,t}-\bar{R}_i)(R_{j,t}-\bar{R}_j)"
            )
            st.markdown("**Coeficiente de Correlação**")
            st.latex(r"\rho_{ij} = \frac{\sigma_{ij}}{\sigma_i \cdot \sigma_j}")
            st.markdown(
                "- ρ = +1: movimentos perfeitamente iguais (sem diversificação)  \n"
                "- ρ = 0: independência  \n"
                "- ρ = -1: diversificação máxima"
            )

        # ── 5. Portfólio ──────────────────────────────────────────────────
        with st.expander("5️⃣ Retorno e Risco da Carteira"):
            st.markdown("**Retorno esperado da carteira**")
            st.latex(
                r"E(R_p) = \sum_{i=1}^{n} w_i \cdot \mu_i = \mathbf{w}^T \boldsymbol{\mu}"
            )
            st.markdown("**Variância da carteira**")
            st.latex(r"\sigma_p^2 = \mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}")
            st.markdown("**Volatilidade da carteira**")
            st.latex(r"\sigma_p = \sqrt{\mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}}")
            st.markdown(
                "Onde **w** é o vetor de pesos e **Σ** é a matriz de covariância anualizada."
            )

        # ── 6. Fronteira Eficiente ────────────────────────────────────────
        with st.expander("6️⃣ Fronteira Eficiente"):
            st.markdown("""
A **Fronteira Eficiente** é o conjunto de portfólios que oferecem o maior retorno
esperado para cada nível de risco (ou o menor risco para cada nível de retorno).

Matematicamente, cada ponto da fronteira resolve o problema de otimização:

**Minimizar:**
            """)
            st.latex(r"\min_{\mathbf{w}} \; \mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}")
            st.markdown("**Sujeito a:**")
            st.latex(
                r"\mathbf{w}^T \boldsymbol{\mu} = \mu^* \quad "
                r"\sum_i w_i = 1 \quad w_i \geq 0"
            )
            st.markdown("onde μ* é o retorno alvo para cada ponto da fronteira.")

        # ── 7. Capital Market Line ────────────────────────────────────────
        with st.expander("7️⃣ Capital Market Line (CML)"):
            st.latex(
                r"E(R_p) = R_f + \frac{E(R_m) - R_f}{\sigma_m} \cdot \sigma_p"
            )
            st.markdown(
                "A CML parte do ativo livre de risco (Rf) e é tangente à fronteira "
                "eficiente no ponto de **Máximo Sharpe**. Todo portfólio sobre a CML "
                "é mais eficiente do que qualquer portfólio apenas com ativos arriscados."
            )

        # ── 8. Beta e CAPM ────────────────────────────────────────────────
        with st.expander("8️⃣ Modelo de Mercado: Beta e CAPM"):
            st.markdown("**Modelo de Mercado (regressão)**")
            st.latex(r"R_i = \alpha_i + \beta_i \cdot R_m + \varepsilon_i")

            st.markdown("**Beta — definição**")
            st.latex(
                r"\beta_i = \frac{\text{Cov}(R_i, R_m)}{\sigma_m^2}"
            )

            st.markdown("**CAPM — retorno esperado**")
            st.latex(
                r"E(R_i) = R_f + \beta_i \cdot [E(R_m) - R_f]"
            )
            st.markdown(
                "Onde [E(Rm) − Rf] é o **prêmio de risco de mercado** (equity risk premium)."
            )

        # ── 9. Índice de Sharpe ───────────────────────────────────────────
        with st.expander("9️⃣ Índice de Sharpe"):
            st.latex(r"S = \frac{E(R_p) - R_f}{\sigma_p}")
            st.markdown(
                "Mede o retorno excedente por unidade de risco total. "
                "Quanto maior, melhor a relação risco-retorno."
            )

        # ── 10. Tabela de interpretação ───────────────────────────────────
        with st.expander("🔟 Tabela de Interpretação dos Indicadores"):
            st.markdown("""
| Indicador | Fórmula | Interpretação |
|---|---|---|
| **Beta > 1** | β = Cov(Ri, Rm) / σ²m | Mais volátil que o mercado (agressivo) |
| **Beta < 1** | β = Cov(Ri, Rm) / σ²m | Menos volátil que o mercado (defensivo) |
| **Sharpe > 1** | S = (Rp − Rf) / σp | Boa relação risco-retorno |
| **Sharpe < 0** | S = (Rp − Rf) / σp | Retorno abaixo do ativo livre de risco |
| **Correlação = −1** | ρ = Cov/σiσj | Diversificação máxima possível |
| **Correlação = +1** | ρ = Cov/σiσj | Sem benefício de diversificação |
| **Skewness > 0** | — | Distribuição assimétrica positiva (cauda direita) |
| **Curtose > 3** | — | Distribuição leptocúrtica (caudas pesadas) |
| **R² alto** | — | Ativo muito correlacionado com o mercado |
| **α > 0** | Ri = α + β·Rm | Retorno acima do explicado pelo mercado |
            """)

        st.markdown("---")
        st.markdown(
            "*Referências: Markowitz, H. (1952). Portfolio Selection. "
            "The Journal of Finance, 7(1), 77–91. | "
            "Sharpe, W.F. (1966). Mutual Fund Performance. "
            "The Journal of Business, 39(1), 119–138.*"
        )
