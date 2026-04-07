<div align="center">

# 📈 Análise de Portfólio Markowitz

### Teoria Moderna de Portfólio aplicada a ativos da B3

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![yFinance](https://img.shields.io/badge/yFinance-0.2.40+-blueviolet?style=for-the-badge)](https://github.com/ranaroussi/yfinance)

Uma aplicação **Streamlit completa** para seleção, análise e otimização de portfólios de investimento com base na **Teoria Moderna de Portfólio de Markowitz** — voltada exclusivamente para ativos da **B3 (Bolsa Brasileira)**.

</div>

---

## ✨ Visão Geral

Esta aplicação replica e expande a lógica de uma **planilha Excel didática** desenvolvida em disciplina de mestrado em *Análise de Investimentos*, adicionando:

- 🔍 **Screening fundamentalista automático** via [Fundamentus](https://www.fundamentus.com.br)
- 🤖 **Otimização computacional** de portfólios (scipy)
- 📊 **Visualizações interativas** com Plotly
- 📉 **Análise de risco sistemático** via regressão linear (Beta/CAPM)
- 📚 **Referência teórica completa** com fórmulas LaTeX

---

## 🖥️ Screenshots

| Seleção de Ativos | Fronteira Eficiente |
|:-----------------:|:------------------:|
| Tickers B3, período histórico e taxa livre de risco | Monte Carlo + CML + pontos otimizados |

| Beta & CAPM | Screening Fundamentalista |
|:-----------:|:-------------------------:|
| Regressão por ativo vs IBOVESPA | Filtros com presets rápidos |

---

## 🗂️ Estrutura do Projeto

```
streamlit_markovitz/
│
├── app.py                          # 🚀 Entrypoint principal
├── requirements.txt                # 📦 Dependências
├── .streamlit/
│   └── config.toml                 # 🎨 Tema visual (dark mode)
│
└── src/
    ├── data/
    │   ├── loader.py               # 📥 Download de preços via yfinance
    │   └── fundamentus.py          # 🔍 Scraping do Fundamentus
    │
    ├── finance/
    │   ├── returns.py              # 📐 Retornos simples e logarítmicos
    │   ├── statistics.py           # 📊 Métricas por ativo
    │   ├── covariance.py           # 🔗 Matriz de covariância/correlação
    │   ├── portfolio.py            # 🧮 Retorno/risco + Monte Carlo
    │   ├── optimization.py         # ⚡ Otimização scipy (Máx Sharpe, Mín Var)
    │   └── beta.py                 # 📉 Regressão linear para Beta
    │
    └── ui/
        ├── tab_selecao.py          # Aba 1: Seleção de Ativos
        ├── tab_screening.py        # Aba 2: Screening Fundamentalista
        ├── tab_estatisticas.py     # Aba 3: Estatísticas dos Ativos
        ├── tab_carteira.py         # Aba 4: Construção da Carteira
        ├── tab_fronteira.py        # Aba 5: Fronteira Eficiente
        ├── tab_beta.py             # Aba 6: Risco Sistemático (Beta)
        └── tab_teoria.py           # Aba 7: Teoria & Fórmulas
```

---

## 🚀 Instalação e Execução

### Pré-requisitos

- Python **3.11+**
- pip

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/GustavoJannuzzi/streamlit_markovitz.git
cd streamlit_markovitz

# 2. (Opcional) Crie um ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`

---

## 📦 Dependências

| Pacote | Versão | Uso |
|--------|--------|-----|
| `streamlit` | ≥ 1.35 | Framework web |
| `yfinance` | ≥ 0.2.40 | Download de preços B3 |
| `pandas` | ≥ 2.0 | Manipulação de dados |
| `numpy` | ≥ 1.26 | Cálculos matriciais |
| `scipy` | ≥ 1.13 | Otimização de portfólios |
| `plotly` | ≥ 5.22 | Gráficos interativos |
| `scikit-learn` | ≥ 1.4 | Regressão linear (Beta) |
| `requests` + `lxml` | — | Scraping do Fundamentus |

---

## 🧭 Abas da Aplicação

### 📋 Aba 1 — Seleção de Ativos
Configure os parâmetros globais e informe os tickers da B3:

| Parâmetro | Opções | Default |
|-----------|--------|---------|
| Número de ativos | 2 – 15 | 5 |
| Período histórico | 1y, 2y, 3y, 5y | 3y |
| Tipo de retorno | Simples, Logarítmico | Simples |
| Taxa livre de risco | 0 – 50% a.a. | 10,75% (Selic) |

> **Dica:** Os tickers são normalizados automaticamente — basta digitar `PETR4`, e o sufixo `.SA` é adicionado para o yfinance.

---

### 🔍 Aba 2 — Screening Fundamentalista
Filtre os melhores ativos da B3 com dados em tempo real do **Fundamentus**:

**Filtros disponíveis:**
- P/L máximo, P/VP máximo, EV/EBITDA máximo
- ROE mínimo, ROIC mínimo, Div. Yield mínimo
- Liquidez 2 meses mínima (R$), Margem Líquida mínima

**🎯 Presets rápidos:**

| Preset | P/L | ROE | DY | Descrição |
|--------|-----|-----|----|-----------|
| 🔎 Amplo | ≤ 30 | ≥ 5% | ≥ 0% | Retorna muitos ativos |
| ⚖️ Balanceado | ≤ 20 | ≥ 8% | ≥ 2% | Equilíbrio qualidade/quantidade |
| ⭐ Qualidade | ≤ 15 | ≥ 15% | ≥ 3% | Ativos de alta qualidade |
| 🔄 Limpar | — | — | — | Remove todos os filtros |

---

### 📊 Aba 3 — Estatísticas dos Ativos
Análise estatística completa com **6 visualizações**:

- **Tabela resumo** com cores condicionais (Sharpe verde/amarelo/vermelho)
- **🏅 Cards de destaques** — maior retorno, melhor Sharpe, menor volatilidade
- **Performance Base 100** — evolução normalizada do preço no período
- **Scatter Risco × Retorno** — tamanho dos círculos proporcional ao Sharpe
- **Matriz de correlação** — heatmap RdYlGn
- **Box plot** dos retornos diários — distribuição e outliers

**Métricas calculadas:**
```
μ diário, μ anual (×252), σ diária, σ anual (×√252),
Sharpe Individual, Assimetria, Curtose
```

---

### 🧮 Aba 4 — Construção da Carteira

#### Carteira Manual
Ajuste os pesos de cada ativo com sliders (validação em tempo real da soma = 100%).

#### Carteiras Otimizadas

| Estratégia | Objetivo | Restrições |
|-----------|---------|-----------|
| **Mínima Variância** | Minimiza σ²p = **w**ᵀ**Σw** | Σw = 1, w ≥ 0 |
| **Máximo Sharpe** | Maximiza S = (Rp − Rf) / σp | Σw = 1, w ≥ 0 |
| **Igual (1/N)** | Benchmark ingênuo | wi = 1/n |

---

### 📈 Aba 5 — Fronteira Eficiente
**Visualização completa do espaço de risco-retorno:**

- 🔵 **Nuvem Monte Carlo** — até 10.000 carteiras aleatórias (coloridas pelo Sharpe)
- 🔴 **Fronteira Eficiente** — curva de Markowitz otimizada
- ⭐ **Máximo Sharpe** — carteira de ponto de tangência (estrela dourada)
- 💎 **Mínima Variância** — carteira de menor risco (diamante azul)
- 📏 **Capital Market Line** — CML partindo do Rf até além do ponto de tangência
- 🔶 **Ativos Individuais** — posição de cada ativo no espaço risco-retorno

---

### 📉 Aba 6 — Risco Sistemático (Beta)
Regressão linear de cada ativo contra o **IBOVESPA (^BVSP)**:

```
Ri = α + β · Rm + ε
```

| Classificação | Critério | Interpretação |
|--------------|---------|---------------|
| 🛡️ **Defensivo** | β < 0,8 | Oscila menos que o mercado |
| ⚖️ **Neutro** | 0,8 ≤ β ≤ 1,2 | Acompanha o mercado |
| ⚡ **Agressivo** | β > 1,2 | Amplifica movimentos do mercado |

Inclui gráfico de dispersão com linha de regressão para cada ativo.

---

### 📚 Aba 7 — Teoria & Fórmulas
Referência teórica completa com fórmulas **LaTeX renderizadas**:

1. Teoria Moderna de Portfólio (Markowitz, 1952)
2. Retornos: Simples vs Logarítmico
3. Métricas de Risco e Retorno
4. Matriz de Covariância e Correlação
5. Retorno e Risco da Carteira
6. Fronteira Eficiente
7. Capital Market Line (CML)
8. Modelo de Mercado: Beta e CAPM
9. Índice de Sharpe
10. Tabela de Interpretação dos Indicadores

---

## 📐 Fundamentos Matemáticos

**Retorno esperado da carteira:**
$$E(R_p) = \mathbf{w}^T \boldsymbol{\mu}$$

**Variância da carteira:**
$$\sigma_p^2 = \mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}$$

**Índice de Sharpe:**
$$S = \frac{E(R_p) - R_f}{\sigma_p}$$

**Beta:**
$$\beta_i = \frac{\text{Cov}(R_i, R_m)}{\sigma_m^2}$$

**Capital Market Line:**
$$E(R_p) = R_f + \frac{E(R_m) - R_f}{\sigma_m} \cdot \sigma_p$$

---

## 🎨 Design & Tecnologia

- **Tema escuro** configurado via `.streamlit/config.toml`
- **Gráficos Plotly** com template `plotly_dark`
- **Paleta Viridis** para mapas de cor (Sharpe na Fronteira)
- **Cache inteligente** — `@st.cache_data(ttl=3600)` para Fundamentus e yfinance
- **Simulação vetorizada** — Monte Carlo sem loops Python (`np.random.dirichlet` + `np.einsum`)

---

## 🔄 Fluxo de Dados

```
Aba 2 (Screening)
    └──→ st.session_state['tickers']
              └──→ Aba 1 (Seleção) → download_prices()
                        ├──→ st.session_state['prices']
                        └──→ st.session_state['returns']
                                  ├──→ Aba 3 (Estatísticas)
                                  ├──→ Aba 4 (Carteira)
                                  ├──→ Aba 5 (Fronteira)
                                  └──→ Aba 6 (Beta)
```

---

## 📝 Exemplo de Uso

```python
# Tickers sugeridos para começar
PETR4   # Petrobras — maior beta histórico (~0.7–1.3)
VALE3   # Vale — commodity global
ITUB4   # Itaú Unibanco — bancário de menor vol
BBDC4   # Bradesco — bancário
WEGE3   # WEG — industrial / crescimento
```

**Resultado esperado com esses 5 ativos (3 anos):**

| Estratégia | Retorno | Volatilidade | Sharpe |
|-----------|---------|-------------|--------|
| Máximo Sharpe | ~40% | ~17% | ~1.60 |
| Mínima Variância | ~28% | ~14% | ~1.20 |
| Igual (1/N) | ~27% | ~20% | ~0.82 |

> A carteira otimizada de Máx. Sharpe supera todos os ativos individuais — demonstrando o benefício da diversificação de Markowitz ✅

---

## 🤝 Contribuição

1. Fork o repositório
2. Crie sua branch: `git checkout -b feat/nova-feature`
3. Commit: `git commit -m "feat: descrição"`
4. Push: `git push origin feat/nova-feature`
5. Abra um **Pull Request**

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja `LICENSE` para mais informações.

---

## 👤 Autor

**Gustavo Jannuzzi**  
📧 Mestrado em Administração — Análise de Investimentos  
🔗 [github.com/GustavoJannuzzi](https://github.com/GustavoJannuzzi)

---

<div align="center">

Feito com ❤️ e muito Python 🐍

*"Diversification is the only free lunch in investing."* — Harry Markowitz

</div>
