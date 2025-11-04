# 🌐 Como Testar o Sistema Online (Sem Baixar)

## Opções Disponíveis

### 1. 🚀 **GitHub Codespaces** (RECOMENDADO)

O GitHub Codespaces permite executar todo o projeto direto no navegador!

**Vantagens:**
- ✅ VS Code completo no navegador
- ✅ Ambiente Linux com Python pré-instalado
- ✅ 60 horas grátis por mês (usuários gratuitos)
- ✅ 120 horas grátis por mês (GitHub Pro)
- ✅ Acesso total ao terminal
- ✅ Instala dependências automaticamente

**Como usar:**

```bash
1. Acesse o repositório no GitHub:
   https://github.com/Jr-Feitoza/sistema-trading-profissional

2. Clique no botão verde "Code"

3. Selecione a aba "Codespaces"

4. Clique em "Create codespace on [branch]"

5. Aguarde alguns segundos... VS Code abrirá no navegador!

6. No terminal integrado, execute:
   pip install -r requirements.txt
   python examples/position_size_calculator_examples.py
```

**Custo:** GRÁTIS (60h/mês)

---

### 2. 🔧 **Gitpod**

Alternativa ao Codespaces, também muito boa!

**Como usar:**

```bash
1. Acesse:
   https://gitpod.io/#https://github.com/Jr-Feitoza/sistema-trading-profissional

2. Faça login com GitHub

3. Workspace será criado automaticamente

4. Execute os comandos normalmente
```

**Custo:** GRÁTIS (50h/mês)

---

### 3. 🎮 **Replit**

Plataforma interativa, ótima para demonstrações!

**Como usar:**

```bash
1. Acesse: https://replit.com/

2. Clique em "Create Repl"

3. Selecione "Import from GitHub"

4. Cole o URL: https://github.com/Jr-Feitoza/sistema-trading-profissional

5. Clique em "Import from GitHub"

6. Execute os scripts pelo botão "Run"
```

**Custo:** GRÁTIS (com algumas limitações)

---

### 4. 📱 **Google Colab** (Para Notebooks)

Se criar versões Jupyter Notebook dos exemplos:

**Como usar:**

```bash
1. Acesse: https://colab.research.google.com/

2. File → Open Notebook → GitHub

3. Cole o URL do repositório

4. Selecione o notebook (.ipynb)

5. Execute célula por célula
```

**Custo:** GRÁTIS

---

## 🎯 Guia Rápido: Testar no GitHub Codespaces

### Passo 1: Criar o Codespace

```
1. Vá em: https://github.com/Jr-Feitoza/sistema-trading-profissional
2. Botão "Code" (verde) → Codespaces → Create codespace
3. Aguarde ~30 segundos
```

### Passo 2: Instalar Dependências

No terminal que aparece no VS Code online:

```bash
# Instalar dependências
pip install pandas numpy eth-account requests

# Ou se tiver requirements.txt
pip install -r requirements.txt
```

### Passo 3: Testar os Exemplos

```bash
# Exemplo 1: Calculadora de Position Size
python examples/position_size_calculator_examples.py

# Exemplo 2: Comparação de Estratégias de Stop
python compare_stop_strategies.py

# Exemplo 3: Backtest Histórico
python run_historical_backtest.py
```

### Passo 4: Testar Integração HyperLiquid (Modo Leitura)

```bash
# Criar script de teste rápido
cat > test_hyperliquid.py << 'EOF'
from connectors.hyperliquid_connector import HyperLiquidConnector

# Modo leitura (sem private key)
connector = HyperLiquidConnector(testnet=True)

# Buscar preço do BTC
ticker = connector.get_ticker('BTC')
print(f"BTC Price: ${ticker.get('price', 0):,.2f}")

# Buscar símbolos disponíveis
info = connector.get_exchange_info()
print(f"Símbolos disponíveis: {len(info['symbols'])}")

# Calcular position size (simulação)
if connector.position_calculator:
    calc = connector.calculate_position_size_only(
        symbol='BTC',
        side='buy',
        entry_price=50000,
        stop_loss_price=49500
    )
    print(f"\nSimulação de Position Size:")
    print(f"  Quantidade: {calc['position_size']:.6f} BTC")
    print(f"  Leverage: {calc.get('leverage', 1)}x")
    print(f"  Margem: ${calc['margin_required']:,.2f}")
EOF

# Executar
python test_hyperliquid.py
```

---

## 📦 Criar Setup Automático para Codespaces

Vou criar arquivos de configuração para setup automático:

### `.devcontainer/devcontainer.json`

```json
{
  "name": "Sistema Trading Profissional",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",

  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.11"
    }
  },

  "postCreateCommand": "pip install pandas numpy eth-account requests",

  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black"
      }
    }
  },

  "forwardPorts": [8000],

  "remoteUser": "vscode"
}
```

### `requirements.txt`

```txt
pandas>=2.0.0
numpy>=1.24.0
eth-account>=0.10.0
requests>=2.31.0
```

### `.gitpod.yml`

```yaml
tasks:
  - name: Setup
    init: |
      pip install -r requirements.txt
    command: |
      echo "Sistema Trading Profissional"
      echo "=========================="
      echo ""
      echo "Exemplos disponíveis:"
      echo "1. python examples/position_size_calculator_examples.py"
      echo "2. python compare_stop_strategies.py"
      echo "3. python run_historical_backtest.py"
      echo ""

vscode:
  extensions:
    - ms-python.python
    - ms-python.vscode-pylance
```

---

## 🎮 Interface Web Interativa (Opcional)

Se quiser criar uma interface web para testar mais facilmente:

### `web_demo.py` (com Streamlit)

```python
import streamlit as st
import sys
sys.path.append('.')

from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe
)

st.title("🚀 Calculadora de Position Size")
st.markdown("### Sistema de Trading Profissional")

# Sidebar com inputs
st.sidebar.header("Parâmetros")

entry_price = st.sidebar.number_input(
    "Preço de Entrada",
    value=50000.0,
    step=100.0
)

account_balance = st.sidebar.number_input(
    "Saldo da Conta (USDT)",
    value=10000.0,
    step=100.0
)

risk_amount = st.sidebar.number_input(
    "Quanto Arriscar (USDT)",
    value=10.0,
    step=1.0
)

profit_target = st.sidebar.number_input(
    "Objetivo de Lucro (USDT)",
    value=30.0,
    step=1.0
)

side = st.sidebar.selectbox(
    "Lado",
    ["LONG", "SHORT"]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["5m", "15m", "1h", "4h"]
)

# Mapear timeframe
tf_map = {
    "5m": Timeframe.M5,
    "15m": Timeframe.M15,
    "1h": Timeframe.H1,
    "4h": Timeframe.H4
}

# Botão calcular
if st.sidebar.button("Calcular Position Size"):

    calculator = PositionSizeCalculator()

    params = PositionSizeParams(
        entry_price=entry_price,
        account_balance=account_balance,
        side=PositionSide.LONG if side == "LONG" else PositionSide.SHORT,
        risk_amount_usdt=risk_amount,
        profit_target_usdt=profit_target,
        timeframe=tf_map[timeframe]
    )

    result = calculator.calculate_position_size(params)

    # Mostrar resultados
    st.success("✅ Cálculo Completo!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Position Size",
            f"{result.position_size:.6f}",
            delta=None
        )

    with col2:
        st.metric(
            "Valor da Posição",
            f"${result.position_value_usdt:,.2f}",
            delta=None
        )

    with col3:
        st.metric(
            "Margem Necessária",
            f"${result.margin_required:,.2f}",
            delta=None
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📉 Stop Loss")
        st.markdown(f"**Preço:** ${result.stop_loss_price:,.2f}")
        st.markdown(f"**Distância:** {result.stop_loss_distance_pct:.2f}%")
        st.markdown(f"**Risco:** ${result.risk_amount:.2f}")

    with col2:
        st.markdown("### 📈 Take Profit")
        st.markdown(f"**Preço:** ${result.take_profit_price:,.2f}")
        st.markdown(f"**Distância:** {result.take_profit_distance_pct:.2f}%")
        st.markdown(f"**Lucro:** ${result.profit_potential:.2f}")

    st.markdown("---")

    st.markdown(f"### ⚖️ Risk/Reward: 1:{result.risk_reward_ratio:.2f}")

    # Warnings
    if result.warnings:
        st.warning("⚠️ Avisos:")
        for warning in result.warnings:
            st.write(f"- {warning}")

    # Validação
    if result.is_valid:
        st.success("✅ Posição válida e segura!")
    else:
        st.error("❌ Posição inválida! Revise os parâmetros.")
```

### Como rodar Streamlit no Codespaces:

```bash
# Instalar streamlit
pip install streamlit

# Rodar app
streamlit run web_demo.py

# Codespaces automaticamente abrirá o navegador na porta correta!
```

---

## 📱 Teste Rápido (1 Minuto)

**Forma mais rápida de testar AGORA:**

1. Abra: https://replit.com/new/python3

2. Cole este código:

```python
# Sistema de Position Sizing
class PositionCalculator:
    def calculate(self, entry, stop, risk_usd):
        distance = abs(entry - stop)
        position_size = risk_usd / distance
        position_value = position_size * entry

        stop_pct = (distance / entry) * 100

        return {
            'position_size': position_size,
            'position_value': position_value,
            'stop_distance_pct': stop_pct,
            'leverage_needed': 1 if position_value <= risk_usd * 100 else position_value / (risk_usd * 100)
        }

# Teste
calc = PositionCalculator()
result = calc.calculate(
    entry=50000,
    stop=49500,
    risk_usd=10
)

print("=== CALCULADORA DE POSITION SIZE ===")
print(f"Entry: $50,000")
print(f"Stop: $49,500")
print(f"Risk: $10")
print()
print(f"Position Size: {result['position_size']:.6f} BTC")
print(f"Position Value: ${result['position_value']:,.2f}")
print(f"Stop Distance: {result['stop_distance_pct']:.2f}%")
print(f"Leverage: {result['leverage_needed']:.1f}x")
```

3. Clique em "Run" ▶️

4. Veja o resultado instantaneamente!

---

## 🔗 Links Diretos

Quando o repositório estiver público, você pode usar estes links diretos:

```
GitHub Codespaces:
https://github.com/Jr-Feitoza/sistema-trading-profissional/codespaces

Gitpod:
https://gitpod.io/#https://github.com/Jr-Feitoza/sistema-trading-profissional

Replit (import):
https://replit.com/new/github/Jr-Feitoza/sistema-trading-profissional
```

---

## 💡 Recomendação

Para **melhor experiência** testando nosso sistema completo:

1. **Use GitHub Codespaces** (mais completo e gratuito)
2. **Ou Gitpod** (alternativa excelente)
3. **Para demos rápidas**: Replit

Para **demonstrações públicas**:
- Criar app Streamlit
- Hospedar no Streamlit Cloud (gratuito)
- Compartilhar link público

---

## 📊 Status das Funcionalidades

```
✅ Position Size Calculator - Funciona em todos
✅ Backtest System - Funciona em Codespaces/Gitpod
✅ Strategy Comparison - Funciona em Codespaces/Gitpod
✅ Examples - Funciona em todos
⚠️ HyperLiquid Live Trading - Apenas com private key
```

**Quer que eu crie os arquivos de configuração agora para facilitar o teste online?**
