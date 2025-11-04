# 🚀 Sistema Trading Profissional

Sistema completo de trading automatizado com **AI Agents**, **Smart Money Concepts (SMC)**, **Wyckoff**, **position sizing automático** e integração com **HyperLiquid**.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main)

## ✨ Principais Funcionalidades

### 1. 🤖 AI Agents para Desenvolvimento
Sistema multi-agente para automação de desenvolvimento:
- **Planner Agent**: Cria planos de execução
- **Developer Agent**: Implementa código
- **Reviewer Agent**: Revisa qualidade
- **Tester Agent**: Executa testes
- **Documenter Agent**: Gera documentação
- **Analyst Agent**: Analisa performance

### 2. 📊 Estratégias de Trading Avançadas
- **SMC (Smart Money Concepts)**:
  - Order Blocks
  - Fair Value Gaps (FVG)
  - Liquidity Sweeps
  - Break of Structure (BOS)

- **Wyckoff Method**:
  - Accumulation/Distribution Phases
  - Spring Patterns
  - Volume Analysis

- **Combinações**: Sistema de confluência para combinar múltiplas estratégias

### 3. 💰 Position Sizing Automático
Cálculo inteligente de tamanho de posição:
- ✅ Baseado em risk/reward (ex: arriscar $10 para lucrar $30)
- ✅ Ajusta por timeframe (5m, 15m, 1h, 4h)
- ✅ Usa ATR para volatilidade
- ✅ Calcula leverage ótima automaticamente
- ✅ Valida preço de liquidação
- ✅ Gestão de breakeven e trailing stop

### 4. 🔄 Backtest Avançado
Sistema de backtesting profissional:
- Stop loss e take profit automáticos
- Breakeven stop (move para entry após lucro)
- Trailing stop (segue o preço)
- Suporte a leverage
- Métricas detalhadas (Sharpe, PF, Max DD, R:R)

### 5. 🌐 Integração HyperLiquid
Conector completo para HyperLiquid DEX:
- Trading de futuros perpétuos
- Ordem inteligente com position sizing
- Suporte a leverage até 50x
- Stop loss e take profit automáticos
- Cálculo de liquidação

## 🚀 Como Começar

### Opção 1: GitHub Codespaces (Recomendado)

1. Clique em [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main)
2. Aguarde o ambiente carregar
3. Execute os exemplos:

```bash
python examples/position_size_calculator_examples.py
```

### Opção 2: Instalação Local

```bash
# Clone o repositório
git clone https://github.com/Jr-Feitoza/sistema-trading-profissional.git
cd sistema-trading-profissional

# Instale as dependências
pip install -r requirements.txt

# Execute exemplos
python examples/position_size_calculator_examples.py
```

### Opção 3: Gitpod

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Jr-Feitoza/sistema-trading-profissional)

## 📚 Exemplos de Uso

### Position Size Calculator

```python
from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe
)

# Cria calculadora
calculator = PositionSizeCalculator()

# Define parâmetros
params = PositionSizeParams(
    entry_price=50000,           # BTC a $50k
    account_balance=10000,        # Conta de $10k
    side=PositionSide.LONG,      # Compra
    risk_amount_usdt=10,         # Arriscar $10
    profit_target_usdt=30,       # Lucrar $30 (1:3)
    timeframe=Timeframe.M15      # Timeframe 15min
)

# Calcula position size
result = calculator.calculate_position_size(params)

print(f"Position Size: {result.position_size:.6f} BTC")
print(f"Stop Loss: ${result.stop_loss_price:,.2f}")
print(f"Take Profit: ${result.take_profit_price:,.2f}")
print(f"Risk/Reward: 1:{result.risk_reward_ratio:.2f}")
```

**Saída:**
```
Position Size: 0.020000 BTC
Stop Loss: $49,500.00
Take Profit: $51,500.00
Risk/Reward: 1:3.00
```

### Backtest com Position Sizing

```python
from backtest.enhanced_backtest_runner import EnhancedBacktestRunner, Timeframe

# Cria runner com position sizing
runner = EnhancedBacktestRunner(
    initial_capital=10000,
    risk_per_trade_usdt=10,      # Risk $10 por trade
    profit_target_usdt=30,       # Target $30
    use_breakeven=True,          # Move stop para BE
    use_trailing_stop=True,      # Ativa trailing
    timeframe=Timeframe.M15
)

# Executa backtest
metrics = runner.run_backtest(df_with_signals)

# Resultados
print(f"Total Trades: {metrics['total_trades']}")
print(f"Win Rate: {metrics['win_rate']:.1f}%")
print(f"Profit Factor: {metrics['profit_factor']:.2f}")
print(f"Return: {metrics['total_return_pct']:.2f}%")
```

### HyperLiquid - Ordem Inteligente

```python
from connectors.hyperliquid_connector import HyperLiquidConnector

# Inicializa connector
connector = HyperLiquidConnector(
    private_key="YOUR_PRIVATE_KEY",
    testnet=True,
    risk_per_trade_usdt=10,
    risk_reward_ratio=3.0
)

# Coloca ordem inteligente (calcula tudo automaticamente)
result = connector.place_smart_order(
    symbol='BTC',
    side='buy',
    stop_loss_price=49500  # Ou None para calcular automaticamente
)

# Sistema calcula:
# - Position size ideal
# - Leverage ótima
# - Take profit (baseado em R:R)
# - Preço de liquidação
# - Valida tudo antes de executar
```

## 📖 Documentação

### Guias Principais
- [📘 Cálculo de Alavancagem](docs/LEVERAGE_CALCULATION_GUIDE.md) - Guia completo sobre leverage
- [🌐 Sistema HyperLiquid](docs/HYPERLIQUID_LEVERAGE_SYSTEM.md) - Específico do HyperLiquid
- [💻 Como Testar Online](docs/COMO_TESTAR_ONLINE.md) - Teste sem baixar nada

### Componentes
- **AI Agents**: `agents/` - Sistema multi-agente
- **Estratégias**: `strategies/` - SMC, Wyckoff e combinações
- **Risk Management**: `risk_management/` - Position sizing
- **Backtest**: `backtest/` - Sistema de backtesting
- **Connectors**: `connectors/` - Integração HyperLiquid
- **Exemplos**: `examples/` - Código de exemplo

## 🎯 Scripts Prontos

### 1. Exemplos Interativos
```bash
python examples/position_size_calculator_examples.py
```
8 exemplos práticos de position sizing

### 2. Comparação de Estratégias de Stop
```bash
python compare_stop_strategies.py
```
Compara: Stop fixo vs Breakeven vs Trailing vs Combinado

### 3. Backtest Histórico
```bash
python run_historical_backtest.py
```
Backtest completo com todas as estratégias

### 4. Web Demo (Streamlit)
```bash
streamlit run web_demo.py
```
Interface web interativa para testar

## 🧪 Testes

```bash
# Instalar pytest
pip install pytest pytest-cov

# Rodar testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html
```

## 📊 Estrutura do Projeto

```
sistema-trading-profissional/
├── agents/                      # AI Agents system
│   ├── base_agent.py
│   ├── planner_agent.py
│   ├── developer_agent.py
│   └── workflow_orchestrator.py
├── strategies/                  # Trading strategies
│   ├── smc_order_block_strategy.py
│   ├── wyckoff_spring_strategy.py
│   ├── smc_wyckoff_combined_strategy.py
│   └── strategy_selector.py
├── risk_management/             # Position sizing
│   └── position_size_calculator.py
├── backtest/                    # Backtesting system
│   └── enhanced_backtest_runner.py
├── connectors/                  # Exchange connectors
│   └── hyperliquid_connector.py
├── examples/                    # Usage examples
│   └── position_size_calculator_examples.py
├── docs/                        # Documentation
│   ├── LEVERAGE_CALCULATION_GUIDE.md
│   ├── HYPERLIQUID_LEVERAGE_SYSTEM.md
│   └── COMO_TESTAR_ONLINE.md
├── compare_stop_strategies.py   # Stop strategy comparison
├── run_historical_backtest.py   # Historical backtest
├── web_demo.py                  # Streamlit web demo
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## 💡 Casos de Uso

### 1. Trader Conservador
```python
# Risk 1% para lucrar 3%
runner = EnhancedBacktestRunner(
    risk_per_trade_usdt=10,
    profit_target_usdt=30,
    use_breakeven=True,
    use_leverage=False  # Sem leverage
)
```

### 2. Trader Agressivo
```python
# Risk 2% com leverage
runner = EnhancedBacktestRunner(
    risk_per_trade_usdt=20,
    profit_target_usdt=80,  # 1:4
    use_leverage=True,
    max_leverage=10
)
```

### 3. Day Trader (Scalping)
```python
# Stops apertados, timeframe curto
runner = EnhancedBacktestRunner(
    risk_per_trade_usdt=5,
    profit_target_usdt=15,
    timeframe=Timeframe.M5,  # 5 minutos
    use_trailing_stop=True
)
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## ⚠️ Disclaimer

Este sistema é para fins educacionais e de pesquisa. Trading envolve riscos significativos de perda. Use por sua própria conta e risco. Os autores não se responsabilizam por perdas financeiras.

**IMPORTANTE:**
- Sempre teste em ambiente de teste (testnet) primeiro
- Nunca arrisque mais do que pode perder
- Entenda completamente o sistema antes de usar com dinheiro real
- Alavancagem amplifica ganhos E perdas
- Sempre use stop loss

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- **Jr Feitoza** - Idealizador e desenvolvedor principal
- **Claude (Anthropic)** - Assistente de desenvolvimento

## 🙏 Agradecimentos

- Comunidade SMC e Wyckoff
- HyperLiquid pela excelente API
- Todos os contribuidores

## 📞 Contato

- GitHub: [@Jr-Feitoza](https://github.com/Jr-Feitoza)
- Issues: [GitHub Issues](https://github.com/Jr-Feitoza/sistema-trading-profissional/issues)

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**

Made with ❤️ and Python
