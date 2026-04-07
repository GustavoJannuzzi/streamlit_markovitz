# CLAUDE.md — Projeto: Análise de Portfólio Markowitz (Streamlit)

## 🎯 Visão Geral do Projeto

Desenvolver uma **aplicação Streamlit completa** para análise de portfólios de investimento com base na **Teoria Moderna de Portfólio de Markowitz**, voltada para ativos da B3. A aplicação replica e expande a lógica de uma planilha Excel didática desenvolvida em disciplina de mestrado (Análise de Investimentos), adicionando screening fundamentalista via Fundamentus, otimização computacional e visualizações interativas.

---

## 🗂️ Estrutura de Arquivos do Projeto

```
markowitz-app/
├── app.py                     # Entrypoint principal do Streamlit
├── requirements.txt
├── .streamlit/
│   └── config.toml            # Tema visual da aplicação
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py          # Download de preços via yfinance
│   │   └── fundamentus.py     # Scraping do Fundamentus
│   ├── finance/
│   │   ├── __init__.py
│   │   ├── returns.py         # Cálculo de retornos
│   │   ├── statistics.py      # Métricas estatísticas por ativo
│   │   ├── portfolio.py       # Retorno/risco da carteira
│   │   ├── covariance.py      # Matriz de covariância/correlação
│   │   ├── optimization.py    # Otimização (scipy) + Fronteira Eficiente
│   │   └── beta.py            # Regressão linear para Beta
│   └── ui/
│       ├── __init__.py
│       ├── tab_selecao.py     # Aba: Seleção de Ativos (manual)
│       ├── tab_screening.py   # Aba: Screening Fundamentalista
│       ├── tab_estatisticas.py
│       ├── tab_carteira.py
│       ├── tab_fronteira.py
│       ├── tab_beta.py
│       └── tab_teoria.py      # Aba: Teoria, Fórmulas e Interpretação
└── CLAUDE.md
```

---

## 📦 Dependências (`requirements.txt`)

```
streamlit>=1.35.0
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.26.0
scipy>=1.13.0
plotly>=5.22.0
requests>=2.31.0
lxml>=5.2.0
html5lib>=1.1
scikit-learn>=1.4.0
statsmodels>=0.14.0
```

---

## ⚙️ Configuração Streamlit (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#0066CC"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1E2130"
textColor = "#FAFAFA"
font = "sans serif"

[server]
maxUploadSize = 50
```

---

## 🧭 Navegação — Abas da Aplicação

A aplicação usa `st.tabs()` com **7 abas**:

```python
tabs = st.tabs([
    "📋 Seleção de Ativos",
    "🔍 Screening Fundamentalista",
    "📊 Estatísticas dos Ativos",
    "🧮 Construção da Carteira",
    "📈 Fronteira Eficiente",
    "📉 Risco Sistemático (Beta)",
    "📚 Teoria & Fórmulas"
])
```

---

## 🔧 Detalhamento por Módulo

---

### `src/data/loader.py`

**Responsabilidade:** baixar séries históricas de preços ajustados via `yfinance`.

```python
import yfinance as yf
import pandas as pd

def download_prices(tickers: list[str], period: str = "3y") -> pd.DataFrame:
    """
    Baixa preços ajustados de fechamento para os tickers fornecidos.
    - Adiciona sufixo '.SA' automaticamente se o ticker não tiver ponto
    - Retorna DataFrame com datas no índice e tickers nas colunas
    - Remove colunas com mais de 10% de NaN
    - Faz forward fill seguido de backward fill
    """

def get_market_index(period: str = "3y") -> pd.Series:
    """
    Baixa o IBOVESPA (^BVSP) como proxy do mercado para cálculo de Beta.
    Retorna série de preços ajustados.
    """
```

**Parâmetros de período disponíveis para o usuário:**
- `"1y"`, `"2y"`, `"3y"`, `"5y"` (via `st.selectbox`)

---

### `src/data/fundamentus.py`

**Responsabilidade:** coletar e processar dados fundamentalistas da B3 via Fundamentus.

```python
import requests
import pandas as pd
import io

def fetch_fundamentus() -> pd.DataFrame:
    """
    Faz scraping de https://www.fundamentus.com.br/resultado.php
    Retorna DataFrame limpo com os indicadores fundamentalistas.

    Colunas percentuais (converter com pct()):
        ['ROE', 'ROIC', 'Mrg Ebit', 'Mrg. Líq.', 'Cresc. Rec.5a', 'Div.Yield']

    Colunas numéricas (converter com pd.to_numeric):
        ['P/L', 'P/VP', 'EV/EBITDA', 'Liq.2meses', 'Liq. Corr.', 'Dív.Brut/ Patrim.']

    Headers obrigatórios:
        {'User-Agent': 'Mozilla/5.0'}

    Deve cachear o resultado com @st.cache_data(ttl=3600)
    """

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Aplica filtros do usuário ao DataFrame do Fundamentus.
    Parâmetros em `filters`:
        - pl_max: float           → P/L máximo
        - pvp_max: float          → P/VP máximo
        - roe_min: float          → ROE mínimo
        - dy_min: float           → Dividend Yield mínimo
        - roic_min: float         → ROIC mínimo
        - liq_min: float          → Liquidez mínima (Liq.2meses)
        - ev_ebitda_max: float    → EV/EBITDA máximo
        - margem_liq_min: float   → Margem Líquida mínima
    """
```

---

### `src/finance/returns.py`

```python
import pandas as pd
import numpy as np

def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Retorno simples: Rt = (Pt / Pt-1) - 1"""

def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Retorno logarítmico: Rt = ln(Pt / Pt-1)"""
```

---

### `src/finance/statistics.py`

```python
def asset_statistics(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Para cada ativo, calcula:
    - Retorno médio diário (μ)
    - Retorno médio anualizado (μ * 252)
    - Variância diária (σ²)
    - Desvio padrão diário (σ)
    - Desvio padrão anualizado (σ * sqrt(252))
    - Sharpe individual (assumindo rf=0 por padrão, ou parâmetro)
    - Assimetria (skewness)
    - Curtose (kurtosis)
    Retorna DataFrame com ativos nas linhas e métricas nas colunas.
    """
```

---

### `src/finance/covariance.py`

```python
def covariance_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Matriz de covariância anualizada (multiplica por 252)"""

def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Matriz de correlação (normalização da covariância)"""
```

---

### `src/finance/portfolio.py`

```python
import numpy as np
import pandas as pd

def portfolio_return(weights: np.ndarray, mean_returns: np.ndarray) -> float:
    """E(Rp) = w' * μ  (anualizado)"""

def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """σp = sqrt(w' Σ w)  (anualizado)"""

def portfolio_sharpe(weights, mean_returns, cov_matrix, rf=0.0) -> float:
    """Sharpe = (E(Rp) - rf) / σp"""

def build_random_portfolios(
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    n_portfolios: int = 5000
) -> pd.DataFrame:
    """
    Simula n_portfolios carteiras aleatórias.
    Retorna DataFrame com colunas: ['Return', 'Volatility', 'Sharpe', w1, w2, ..., wn]
    Pesos somam 1, sem shorts (w >= 0).
    """
```

---

### `src/finance/optimization.py`

```python
from scipy.optimize import minimize
import numpy as np
import pandas as pd

def min_variance_portfolio(mean_returns, cov_matrix) -> dict:
    """
    Minimiza σ²p = w' Σ w
    Restrições: sum(w) = 1, w >= 0
    Retorna: {'weights': array, 'return': float, 'volatility': float, 'sharpe': float}
    """

def max_sharpe_portfolio(mean_returns, cov_matrix, rf=0.0) -> dict:
    """
    Maximiza Sharpe Ratio.
    Mesmas restrições.
    """

def efficient_frontier_points(
    mean_returns, cov_matrix, n_points: int = 100
) -> pd.DataFrame:
    """
    Gera n_points pontos da fronteira eficiente.
    Para cada nível de retorno alvo entre min e max dos ativos,
    minimiza a variância.
    Retorna DataFrame com colunas: ['Return', 'Volatility']
    """
```

---

### `src/finance/beta.py`

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def calculate_beta(asset_returns: pd.Series, market_returns: pd.Series) -> dict:
    """
    Regressão linear: Ri = α + β * Rm + ε
    Retorna: {'beta': float, 'alpha': float, 'r_squared': float}
    """

def all_betas(returns: pd.DataFrame, market_returns: pd.Series) -> pd.DataFrame:
    """
    Calcula beta, alpha e R² para todos os ativos.
    Alinha as séries temporais antes de calcular.
    Retorna DataFrame com ativos nas linhas.
    """
```

---

## 🖥️ Detalhamento das Abas da UI

---

### Aba 1 — `tab_selecao.py` — 📋 Seleção de Ativos

**Layout:**
```
[st.sidebar ou topo da aba]
  - Número de ativos: st.slider(2, 15, value=5)
  - Período histórico: st.selectbox(['1y','2y','3y','5y'])
  - Tipo de retorno: st.radio(['Simples','Logarítmico'])
  - Taxa livre de risco (% a.a.): st.number_input(0.0, value=10.75)

[Entrada de tickers]
  - Para cada i em range(n_ativos):
      st.text_input(f"Ativo {i+1}", placeholder="Ex: PETR4")

[Botão] "▶ Carregar Dados"

[Após carregamento]
  - st.success com período real dos dados
  - Tabela de preços (últimas 10 linhas)
  - Download CSV dos preços
```

**Estado global (st.session_state):**
```python
st.session_state['prices']        # pd.DataFrame
st.session_state['returns']       # pd.DataFrame
st.session_state['tickers']       # list[str]
st.session_state['rf']            # float
st.session_state['market_prices'] # pd.Series
st.session_state['market_returns']# pd.Series
```

---

### Aba 2 — `tab_screening.py` — 🔍 Screening Fundamentalista

**Propósito:** ajudar o usuário a descobrir ativos de qualidade via filtros fundamentalistas antes de montar a carteira.

**Layout:**
```
[Filtros em st.expander("⚙️ Filtros Fundamentalistas")]
  Coluna 1:
    - P/L máximo          (slider 0–50, default 15)
    - P/VP máximo         (slider 0–10, default 3)
    - EV/EBITDA máximo    (slider 0–20, default 10)
    - Dív.Brut/Patrim máx (slider 0–5, default 2)

  Coluna 2:
    - ROE mínimo (%)      (slider 0–50, default 10)
    - ROIC mínimo (%)     (slider 0–30, default 8)
    - Div.Yield mínimo (%)   (slider 0–20, default 3)
    - Liq.2meses mínima (R$) (number_input, default 1_000_000)
    - Mrg. Líq. mínima (%)   (slider -50–50, default 5)

[Botão] "🔍 Aplicar Filtros"

[Resultado]
  - st.metric: "Ativos encontrados: X de Y"
  - Tabela interativa (st.dataframe com highlight)
  - Colunas exibidas e formatadas:
      Papel | P/L | P/VP | EV/EBITDA | ROE | ROIC | Div.Yield | Mrg.Líq | Liq.2meses

[Ação]
  - st.multiselect: "Adicionar à carteira" (pré-seleciona top 5 por ROIC)
  - Botão: "➕ Usar estes ativos na Aba 1"
    → atualiza st.session_state['tickers'] e recarrega dados
```

---

### Aba 3 — `tab_estatisticas.py` — 📊 Estatísticas dos Ativos

**Requer:** `st.session_state['returns']` populado.

**Layout:**
```
[Tabela de estatísticas por ativo]
  Colunas formatadas:
    Ativo | Retorno Médio Diário | Retorno Anual | Vol Diária | Vol Anual | Sharpe | Skew | Curtose

[Gráfico 1 — Plotly]
  Bar chart: Retorno Anual vs Volatilidade Anual (grouped bars por ativo)

[Gráfico 2 — Plotly]
  Matriz de correlação como heatmap (px.imshow)
  Escala de cor: RdYlGn, centrada em 0

[Gráfico 3 — Plotly]
  Séries de retorno cumulativo (go.Scatter, linha) por ativo
  Eixo Y: retorno acumulado desde início do período

[Gráfico 4 — Plotly]
  Box plot dos retornos diários por ativo

[Download]
  - CSV com tabela de estatísticas
```

---

### Aba 4 — `tab_carteira.py` — 🧮 Construção da Carteira

**Layout — duas sub-seções:**

#### 4A — Carteira Manual
```
[Para cada ativo]
  st.slider: Peso do ativo (0–100%, step=1%)
[Validação em tempo real]
  st.warning se soma ≠ 100%
[Métricas da carteira atual]
  st.metric: Retorno Esperado | Volatilidade | Sharpe Ratio
[Gráfico]
  Pizza (px.pie) com pesos atuais
```

#### 4B — Carteiras Otimizadas
```
[st.columns(3)]
  Col 1: Carteira de Mínima Variância
    - Pesos como bar chart
    - Métricas: Retorno | Vol | Sharpe
  Col 2: Carteira de Máximo Sharpe
    - Idem
  Col 3: Carteira Igual (1/N como benchmark)
    - Idem

[Tabela comparativa]
  | Estratégia | Retorno | Volatilidade | Sharpe |

[Download]
  - CSV com pesos de cada estratégia
```

---

### Aba 5 — `tab_fronteira.py` — 📈 Fronteira Eficiente

**Layout:**
```
[Controles]
  - N° de carteiras simuladas: st.slider(1000, 10000, value=5000)
  - Mostrar carteiras aleatórias: st.checkbox (default True)

[Botão] "⚙️ Calcular Fronteira"

[Gráfico principal — Plotly Scatter]
  - Nuvem de pontos: carteiras aleatórias
    Color scale = Sharpe Ratio (Viridis)
  - Linha da fronteira eficiente (go.Scatter, linha vermelha espessa)
  - Ponto destacado: Máximo Sharpe (estrela dourada)
  - Ponto destacado: Mínima Variância (diamante azul)
  - Eixo X: Volatilidade Anual (%)
  - Eixo Y: Retorno Anual (%)
  - Hover: mostrar pesos dos ativos ao passar o mouse

[Tabela]
  Top 10 carteiras por Sharpe Ratio com seus pesos
```

---

### Aba 6 — `tab_beta.py` — 📉 Risco Sistemático (Beta)

**Layout:**
```
[Tabela de Betas]
  | Ativo | Alpha (α) | Beta (β) | R² | Classificação |
  Classificação: "Defensivo" (β<0.8), "Neutro" (0.8–1.2), "Agressivo" (β>1.2)

[Gráfico de barras — Plotly]
  Beta de cada ativo, linha pontilhada em β=1 (mercado)

[Para cada ativo — st.expander]
  Gráfico de dispersão: retorno ativo vs retorno mercado
  + linha de regressão
  + anotação com equação Ri = α + β*Rm

[Interpretação automática]
  Para cada ativo, texto gerado:
  "PETR4 possui Beta de 1.34, indicando que tende a amplificar
   os movimentos do mercado em 34%. R² de 0.68 indica que 68% da
   variação do ativo é explicada pelo IBOVESPA."
```

---

### Aba 7 — `tab_teoria.py` — 📚 Teoria & Fórmulas

**Conteúdo estático renderizado com `st.markdown` e `st.latex`:**

Seções:
1. **Teoria Moderna de Portfólio (Markowitz, 1952)**
2. **Retornos: Simples vs Logarítmico**
3. **Métricas de Risco e Retorno**
4. **Matriz de Covariância e Correlação**
5. **Fronteira Eficiente**
6. **Otimização de Portfólio**
7. **Capital Market Line (CML)**
8. **Modelo de Mercado: Beta e CAPM**
9. **Índice de Sharpe**
10. **Interpretação dos Resultados**

**Exemplo de renderização:**

```python
st.latex(r"E(R_p) = \sum_{i=1}^{n} w_i \cdot \mu_i = \mathbf{w}^T \boldsymbol{\mu}")

st.latex(r"\sigma_p^2 = \mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}")

st.latex(r"\beta_i = \frac{Cov(R_i, R_m)}{\sigma_m^2}")

st.latex(r"S = \frac{E(R_p) - R_f}{\sigma_p}")
```

Incluir tabela de interpretação:

| Indicador | Fórmula | Interpretação |
|-----------|---------|---------------|
| Beta > 1 | β = Cov(Ri, Rm) / σm² | Mais arriscado que mercado |
| Sharpe > 1 | S = (Rp - Rf) / σp | Bom risco-retorno |
| Correlação = -1 | ρ = Cov/σiσj | Diversificação máxima |

---

## 🔄 Fluxo de Dados entre Abas

```
Aba 2 (Screening)
    └──→ st.session_state['tickers']
              └──→ Aba 1 (Seleção) → download_prices()
                        └──→ st.session_state['prices']
                        └──→ st.session_state['returns']
                                  ├──→ Aba 3 (Estatísticas)
                                  ├──→ Aba 4 (Carteira)
                                  ├──→ Aba 5 (Fronteira)
                                  └──→ Aba 6 (Beta)
```

---

## ⚠️ Regras de Implementação

### Tratamento de Erros

```python
# Em loader.py — tickers inválidos
# Testar download; se retornar vazio, exibir st.error e remover ticker

# Em fundamentus.py — falha de rede
# Envolver em try/except; exibir st.warning com mensagem amigável

# Em optimization.py — scipy não convergir
# Retornar None e exibir st.warning na UI
```

### Performance

- `@st.cache_data(ttl=3600)` em `fetch_fundamentus()`
- `@st.cache_data` em `download_prices()` com hash dos tickers+período
- `build_random_portfolios` com `np.random` vetorizado (sem loop Python)
- Usar `@st.cache_resource` para objetos pesados reutilizados

### Formatação

```python
# Percentuais: f"{valor:.2%}"
# Decimais: f"{valor:.4f}"
# Reais: f"R$ {valor:,.0f}"
# Sempre usar locale pt-BR para separadores onde possível
```

### Tickers B3

```python
# Auto-append '.SA' se o ticker não contiver '.'
def normalize_ticker(t: str) -> str:
    t = t.strip().upper()
    return t if '.' in t else f"{t}.SA"
```

---

## 🎨 Estilo Visual

- Tema escuro (config.toml)
- Cores dos gráficos Plotly: usar paleta `Viridis` para mapas de calor, `Plasma` para dispersão
- Gráficos Plotly com `template="plotly_dark"`
- Sempre incluir `layout.update(height=500)` nos gráficos principais
- Tabelas: usar `st.dataframe` com `use_container_width=True`
- Métricas: `st.metric` com delta quando comparando com benchmark 1/N

---

## 🚀 Ordem de Desenvolvimento Sugerida

1. `requirements.txt` + `.streamlit/config.toml`
2. `src/data/loader.py` — download de preços + ibovespa
3. `src/finance/returns.py` + `statistics.py`
4. `src/ui/tab_selecao.py` — fluxo básico funcionando end-to-end
5. `src/finance/covariance.py` + `src/ui/tab_estatisticas.py`
6. `src/finance/portfolio.py` + `src/ui/tab_carteira.py`
7. `src/finance/optimization.py` + `src/ui/tab_fronteira.py`
8. `src/finance/beta.py` + `src/ui/tab_beta.py`
9. `src/data/fundamentus.py` + `src/ui/tab_screening.py`
10. `src/ui/tab_teoria.py` — conteúdo estático
11. `app.py` — integração final de todas as abas
12. Testes manuais com carteiras conhecidas (ex: PETR4, VALE3, ITUB4, BBDC4, WEGE3)

---

## ✅ Critérios de Aceite

- [ ] App inicia sem erros com `streamlit run app.py`
- [ ] Download de preços funciona para tickers B3 válidos
- [ ] Erro amigável para tickers inválidos (não quebra o app)
- [ ] Fronteira eficiente gera curva contínua com pontos destacados
- [ ] Otimização retorna pesos que somam exatamente 1.0
- [ ] Screening do Fundamentus filtra e exibe ativos corretamente
- [ ] Beta calculado corretamente (validar PETR4 ≈ 1.3–1.5 historicamente)
- [ ] Aba de teoria renderiza todas as fórmulas LaTeX sem erro
- [ ] Todos os gráficos têm título, eixos rotulados e tooltip informativo
- [ ] Downloads CSV funcionam em todas as abas que os oferecem

---

## 📝 Notas Finais para o Agente

- **Não usar `st.experimental_*`** — usar apenas APIs estáveis do Streamlit ≥ 1.35
- **Não usar loops Python para cálculos matriciais** — sempre vetorizar com NumPy
- **Anualização:** retornos × 252, volatilidade × √252
- **Dados do Fundamentus:** a tabela HTML tem formatação brasileira (vírgula decimal, ponto milhar) — usar o helper `pct()` fornecido na documentação
- **IBOVESPA no yfinance:** ticker é `"^BVSP"` (sem sufixo .SA)
- **Taxa Selic default:** inicializar `rf = 0.1075` (10,75% a.a.) mas deixar editável pelo usuário
- Organizar o código de forma modular — **cada função em seu módulo**, nunca colocar lógica financeira dentro dos arquivos de UI
