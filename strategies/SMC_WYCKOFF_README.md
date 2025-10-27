# Estratégias SMC (Smart Money Concepts) e Wyckoff

Sistema completo de estratégias de trading baseadas em Smart Money Concepts e Método Wyckoff, com sistema de seleção e combinação de múltiplas estratégias.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estratégias Disponíveis](#estratégias-disponíveis)
- [Como Usar](#como-usar)
- [Exemplos Práticos](#exemplos-práticos)
- [Sistema de Seleção](#sistema-de-seleção)
- [Integração com Backtest](#integração-com-backtest)
- [Configuração Avançada](#configuração-avançada)

---

## 🎯 Visão Geral

Este sistema implementa **6 estratégias profissionais** baseadas nos conceitos mais avançados de análise técnica institucional:

### Smart Money Concepts (SMC)
Metodologia que identifica onde instituições e "smart money" operam no mercado.

### Método Wyckoff
Análise de acumulação e distribuição institucional com mais de 100 anos de comprovação.

---

## 📊 Estratégias Disponíveis

### 1. **SMC Order Blocks** (`SMCOrderBlockStrategy`)

**Descrição:** Identifica blocos de ordens institucionais - o último candle antes de um movimento significativo onde grandes players colocaram ordens.

**Conceitos:**
- Order Block Bullish: Último candle bearish antes de impulso de alta
- Order Block Bearish: Último candle bullish antes de impulso de baixa
- Reteste: Preço retorna ao order block para dar entrada

**Sinais:**
- 🟢 **COMPRA:** Preço retorna a Order Block bullish (suporte institucional)
- 🔴 **VENDA:** Preço retorna a Order Block bearish (resistência institucional)

**Melhor Para:** Mercados com tendência clara, todos os timeframes

**Parâmetros:**
```python
swing_length: int = 5          # Período para detectar swing points
min_impulse_pct: float = 0.02  # 2% movimento mínimo para validar
ob_validity_bars: int = 20     # Validade do order block em barras
```

---

### 2. **SMC Fair Value Gaps (FVG)** (`SMCFVGStrategy`)

**Descrição:** Negocia desequilíbrios de preço (imbalances) onde o preço se moveu tão rápido que deixou "gaps" no mercado.

**Conceitos:**
- FVG ocorre quando candles não se sobrepõem
- Preço tende a retornar ao gap ~70% das vezes
- Gap bullish: zona de compra agressiva
- Gap bearish: zona de venda agressiva

**Sinais:**
- 🟢 **COMPRA:** Preço retorna a FVG bullish
- 🔴 **VENDA:** Preço retorna a FVG bearish

**Melhor Para:** Mercados voláteis, intraday e swing trading

**Parâmetros:**
```python
min_fvg_size_pct: float = 0.005    # 0.5% tamanho mínimo do gap
fvg_validity_bars: int = 50        # Validade do FVG
require_fill_pct: float = 0.5      # % de preenchimento para invalidar
```

---

### 3. **SMC Liquidity Sweeps** (`SMCLiquidityStrategy`)

**Descrição:** Captura varreduras de liquidez onde smart money "caça" stops de traders retail.

**Conceitos:**
- Liquidez está acima de máximas óbvias e abaixo de mínimas
- Sweep = rompe nível + reverte rapidamente
- Stop hunt seguido de movimento contrário

**Sinais:**
- 🟢 **COMPRA:** Após sweep de liquidez baixa (bear trap)
- 🔴 **VENDA:** Após sweep de liquidez alta (bull trap)

**Melhor Para:** Mercados líquidos, todos os timeframes

**Parâmetros:**
```python
lookback_highs: int = 20               # Período para identificar máximas
lookback_lows: int = 20                # Período para identificar mínimas
sweep_threshold_pct: float = 0.001     # 0.1% além do nível
reversal_threshold_pct: float = 0.005  # 0.5% reversão mínima
```

---

### 4. **Wyckoff Accumulation** (`WyckoffAccumulationStrategy`)

**Descrição:** Identifica e negocia as fases de acumulação institucional do método Wyckoff.

**Fases:**
- **Fase A:** Stopping (PS, SC, AR) - Para a queda
- **Fase B:** Building (ST) - Consolida em range
- **Fase C:** Testing (Spring) - Testa o suporte com falso rompimento
- **Fase D:** Dominance (LPS, SOS) - Demanda domina
- **Fase E:** Markup - Tendência de alta

**Sinais:**
- 🟢 **COMPRA:**
  - Após Spring confirmado (bear trap)
  - Em Last Point of Support (LPS)
  - No Sign of Strength (SOS)

**Melhor Para:** Fim de downtrends, consolidações, swing e position trading

**Parâmetros:**
```python
volume_threshold: float = 1.5      # Volume do SC 1.5x média
range_lookback: int = 30           # Período para definir range
spring_penetration_pct: float = 0.02  # 2% abaixo do suporte
```

---

### 5. **Wyckoff Spring Pattern** (`WyckoffSpringStrategy`)

**Descrição:** Especializada em detectar e negociar o padrão Spring - o falso rompimento mais poderoso do Wyckoff.

**Conceitos:**
- Spring = Bear Trap intencional
- Preço penetra suporte → stops são capturados → reversão rápida
- Volume geralmente decresce no spring
- Reversão pode ter volume aumentado

**Sinais:**
- 🟢 **COMPRA:** Logo após confirmação do Spring
- 🔴 **VENDA:** Ao detectar Upthrust (spring reverso no topo)

**Qualidade do Spring (score 0-100):**
- **Alta (70+):** Reversão rápida, volume correto, fechamento forte
- **Média (40-69):** Boas características mas menos ideal
- **Baixa (<40):** Fraca confirmação

**Melhor Para:** Consolidações e ranges, todos os timeframes

**Parâmetros:**
```python
support_lookback: int = 20            # Período para identificar suporte
spring_penetration_pct: float = 0.015 # 1.5% abaixo do suporte
max_spring_duration: int = 5          # Máximo de barras para spring
volume_confirmation: bool = True      # Requer confirmação de volume
```

---

### 6. **SMC + Wyckoff Combined** (`SMCWyckoffCombinedStrategy`)

**Descrição:** Combina os melhores aspectos de SMC e Wyckoff para confluência máxima.

**Lógica de Confluência:**
- **Score 3:** Confluência de múltiplos conceitos (SINAL FORTE)
- **Score 2:** Dois conceitos concordam (SINAL MÉDIO)
- **Score 1:** Apenas um conceito (SINAL FRACO)

**Confluências Bullish Poderosas:**
- Spring (Wyckoff) + Order Block Bullish (SMC)
- Liquidity Sweep Low + FVG Bullish
- Accumulation Phase D + Order Block retest

**Confluências Bearish Poderosas:**
- Upthrust (Wyckoff) + Order Block Bearish (SMC)
- Liquidity Sweep High + FVG Bearish
- Distribution Phase + Bearish patterns

**Melhor Para:** Trading de alta probabilidade, todos os timeframes

**Parâmetros:**
```python
min_confluence_score: int = 2      # Score mínimo para gerar sinal (1-3)
use_weighted_signals: bool = True  # Usar pesos diferentes
```

---

## 🚀 Como Usar

### Uso Básico - Estratégia Única

```python
from strategies.smc_order_block_strategy import SMCOrderBlockStrategy
import pandas as pd

# Cria estratégia
strategy = SMCOrderBlockStrategy()

# Carrega dados (OHLCV)
df = pd.read_csv('seu_arquivo.csv')

# Gera sinais
df_with_signals = strategy.generate_signals(df)

# Verifica sinais
buy_signals = df_with_signals[df_with_signals['signal'] == 1]
sell_signals = df_with_signals[df_with_signals['signal'] == -1]

print(f"Sinais de compra: {len(buy_signals)}")
print(f"Sinais de venda: {len(sell_signals)}")
```

### Sistema de Seleção - Múltiplas Estratégias

```python
from strategies.strategy_selector import (
    StrategySelector,
    StrategyType,
    SignalCombinationMethod
)

# Cria seletor
selector = StrategySelector()

# Adiciona estratégias
selector.add_strategy(StrategyType.SMC_ORDER_BLOCK, weight=1.0)
selector.add_strategy(StrategyType.SMC_FVG, weight=1.0)
selector.add_strategy(StrategyType.WYCKOFF_SPRING, weight=1.2)

# Gera sinais combinados
df_result = selector.generate_combined_signals(
    df,
    combination_method=SignalCombinationMethod.MAJORITY
)

# Compara estratégias
comparison = selector.compare_strategies(df)
print(comparison)
```

---

## 📚 Exemplos Práticos

Execute o arquivo de exemplos:

```bash
cd strategies
python smc_wyckoff_examples.py
```

### Exemplos Disponíveis:

1. **Estratégia Única** - Como usar Order Blocks sozinho
2. **Múltiplas SMC** - Combinar Order Blocks + FVG + Liquidity
3. **Wyckoff** - Accumulation e Spring patterns
4. **Combinada** - SMC + Wyckoff com confluência
5. **Comparação** - Teste todas as estratégias
6. **Configuração Custom** - Parâmetros personalizados
7. **Métodos de Combinação** - UNANIMOUS, MAJORITY, ANY, CONFLUENCE
8. **Integração Backtest** - Preparar para backtest

---

## 🎛️ Sistema de Seleção

### StrategySelector

Gerencia múltiplas estratégias e combina seus sinais.

#### Métodos de Combinação

**1. UNANIMOUS**
```python
combination_method=SignalCombinationMethod.UNANIMOUS
```
- Todas as estratégias devem concordar
- Sinais mais raros mas de altíssima confiança
- Ideal para: Posições grandes, risk-averse trading

**2. MAJORITY**
```python
combination_method=SignalCombinationMethod.MAJORITY
```
- Maioria das estratégias deve concordar
- Equilíbrio entre qualidade e frequência
- Ideal para: Trading geral, swing trading

**3. ANY**
```python
combination_method=SignalCombinationMethod.ANY
```
- Qualquer estratégia pode gerar sinal
- Máxima frequência de sinais
- Ideal para: Scalping, trading ativo

**4. WEIGHTED**
```python
combination_method=SignalCombinationMethod.WEIGHTED
```
- Combina sinais ponderados por peso de cada estratégia
- Prioriza estratégias com maior peso
- Ideal para: Portfólios customizados

**5. CONFLUENCE**
```python
combination_method=SignalCombinationMethod.CONFLUENCE
```
- Score baseado em quantas estratégias concordam
- Fornece `confluence_score` no DataFrame
- Ideal para: Filtrar sinais por nível de confluência

#### Lista Estratégias Disponíveis

```python
selector = StrategySelector()

# Lista todas
strategies = selector.list_available_strategies()
print(strategies)

# Info de uma estratégia
info = selector.get_strategy_info(StrategyType.SMC_ORDER_BLOCK)
print(info['description'])
print(info['best_for'])
```

#### Comparação de Estratégias

```python
# Compara performance
comparison_df = selector.compare_strategies(df)
print(comparison_df)

# Resultado:
# strategy              | total_signals | buy_signals | sell_signals | frequency
# SMC Order Blocks      | 45            | 25          | 20           | 4.5%
# SMC FVG               | 67            | 38          | 29           | 6.7%
# Wyckoff Spring        | 23            | 15          | 8            | 2.3%
```

---

## 🔄 Integração com Backtest

### Método 1: Usar StrategySelector diretamente

```python
from engine.backtest_engine import BacktestEngine
from strategies.strategy_selector import StrategySelector, StrategyType

# Configura estratégias
selector = StrategySelector()
selector.add_strategy(StrategyType.SMC_WYCKOFF_COMBINED)

# Gera sinais
df_with_signals = selector.generate_combined_signals(df)

# Cria classe wrapper para BacktestEngine
class CombinedStrategy:
    def __init__(self, selector):
        self.selector = selector

    def generate_signals(self, df):
        return self.selector.generate_combined_signals(df)

# Executa backtest
strategy = CombinedStrategy(selector)
engine = BacktestEngine(
    strategy=strategy,
    initial_capital=10000,
    commission=0.001
)

result = engine.run_backtest(df)
print(result.metrics)
```

### Método 2: Estratégia individual

```python
from strategies.smc_wyckoff_combined_strategy import SMCWyckoffCombinedStrategy

strategy = SMCWyckoffCombinedStrategy(min_confluence_score=2)

engine = BacktestEngine(
    strategy=strategy,
    initial_capital=10000
)

result = engine.run_backtest(df)
```

---

## ⚙️ Configuração Avançada

### Configurar Parâmetros Individuais

```python
# Order Blocks mais conservadores
ob_config = {
    'swing_length': 10,           # Swing maior = menos sinais, mais fortes
    'min_impulse_pct': 0.03,      # 3% impulso mínimo (vs 2% padrão)
    'ob_validity_bars': 40        # OB válido por mais tempo
}

selector.add_strategy(
    StrategyType.SMC_ORDER_BLOCK,
    config=ob_config,
    weight=1.5
)

# Spring mais agressivo
spring_config = {
    'spring_penetration_pct': 0.01,   # Aceita springs menores
    'require_volume_decrease': False   # Não exige volume baixo
}

selector.add_strategy(
    StrategyType.WYCKOFF_SPRING,
    config=spring_config,
    weight=1.0
)
```

### Pesos Customizados

```python
# Prioriza estratégias Wyckoff
selector.add_strategy(StrategyType.WYCKOFF_SPRING, weight=2.0)
selector.add_strategy(StrategyType.WYCKOFF_ACCUMULATION, weight=1.5)
selector.add_strategy(StrategyType.SMC_ORDER_BLOCK, weight=1.0)

# Usa método WEIGHTED para respeitar os pesos
df_result = selector.generate_combined_signals(
    df,
    combination_method=SignalCombinationMethod.WEIGHTED
)
```

---

## 📖 Conceitos Teóricos

### Smart Money Concepts (SMC)

**Origem:** Inner Circle Traders (ICT), Michael J. Huddleston

**Premissa:** Seguir o dinheiro institucional, não o varejo

**Principais Conceitos:**
- **Order Blocks:** Zonas de ordens institucionais
- **Fair Value Gaps:** Desequilíbrios que precisam ser preenchidos
- **Liquidity:** Smart money caça liquidez (stops) antes de mover preço
- **BOS/CHOCH:** Break of Structure / Change of Character
- **Displacement:** Movimento impulsivo agressivo

### Método Wyckoff

**Origem:** Richard D. Wyckoff (1930s)

**Premissa:** Preço é movido por lei de oferta/demanda controlada por "Composite Man"

**Leis de Wyckoff:**
1. Lei da Oferta e Demanda
2. Lei do Esforço vs Resultado (volume vs movimento)
3. Lei da Causa e Efeito (acumulação causa markup)

**Fases de Acumulação:**
- **PS:** Preliminary Support (suporte preliminar)
- **SC:** Selling Climax (clímax de venda)
- **AR:** Automatic Rally (rally automático)
- **ST:** Secondary Test (teste secundário)
- **Spring:** Falso rompimento (bear trap)
- **LPS:** Last Point of Support (último suporte)
- **SOS:** Sign of Strength (sinal de força)
- **Backup:** Reteste após SOS

---

## 🎓 Melhores Práticas

### 1. Combine SMC + Wyckoff
Máxima confluência = maiores probabilidades

### 2. Use Timeframe Múltiplo
- Timeframe maior: Direção (onde está no ciclo Wyckoff?)
- Timeframe menor: Entrada precisa (Order Blocks, FVG)

### 3. Gestão de Risco
- Stop loss abaixo do Order Block (compra) ou acima (venda)
- Stop abaixo do Spring low
- Take profit em próximo Order Block contrário

### 4. Filtre Sinais por Confluência
```python
# Use apenas sinais com score >= 2
high_quality = df_result[abs(df_result['confluence_score']) >= 2]
```

### 5. Backteste Sempre
Teste configurações antes de usar em live:
```python
results = []
for config in [config1, config2, config3]:
    result = backtest_with_config(config)
    results.append(result)
# Compare e escolha o melhor
```

---

## 📊 Estrutura de Arquivos

```
strategies/
├── base_strategy.py                      # Classe base
├── smc_order_block_strategy.py          # SMC Order Blocks
├── smc_fvg_strategy.py                  # SMC Fair Value Gaps
├── smc_liquidity_strategy.py            # SMC Liquidity Sweeps
├── wyckoff_accumulation_strategy.py     # Wyckoff Accumulation
├── wyckoff_spring_strategy.py           # Wyckoff Spring
├── smc_wyckoff_combined_strategy.py     # Combinada
├── strategy_selector.py                 # Sistema de seleção
├── smc_wyckoff_examples.py              # Exemplos práticos
└── SMC_WYCKOFF_README.md                # Esta documentação
```

---

## 🚨 Avisos Importantes

1. **Backteste antes de usar em live trading**
2. **Nenhuma estratégia é 100% confiável**
3. **Use gestão de risco apropriada**
4. **Combine com análise fundamentalista quando aplicável**
5. **Considere contexto de mercado (bull/bear/range)**

---

## 📞 Suporte

Para dúvidas sobre as estratégias:
1. Leia a documentação completa
2. Execute os exemplos (`smc_wyckoff_examples.py`)
3. Teste com dados históricos
4. Ajuste parâmetros conforme seu estilo

---

**Desenvolvido com Claude Code** 🤖

*"Follow the Smart Money, Don't Fight It"*
