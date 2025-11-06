# Sistema de Validação de Segurança

**Versão:** 1.0
**Data:** 2025-11-06
**Status:** ✅ Completo e Testado

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Warnings em Tempo Real](#warnings-em-tempo-real)
3. [Verificação de Margem até Liquidação](#verificação-de-margem-até-liquidação)
4. [Validação de Posições](#validação-de-posições)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Como Usar](#como-usar)
7. [Referência de Validações](#referência-de-validações)

---

## 🎯 VISÃO GERAL

O Sistema de Trading Profissional possui **6 camadas de validação de segurança** que protegem contra:

- ❌ Risco excessivo por trade
- ❌ Margem insuficiente
- ❌ Liquidação prematura
- ❌ Stops muito apertados ou largos
- ❌ Risk/Reward desfavorável
- ❌ Posições muito grandes

### Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Position Size Calculator                  │
│                                                              │
│  1. Calcula position size baseado em risco                  │
│  2. Determina stop loss e take profit                       │
│  3. Calcula margem e liquidação                             │
│  4. VALIDA SEGURANÇA (6 validações)                         │
│  5. Retorna resultado OU rejeita posição                    │
└─────────────────────────────────────────────────────────────┘
```

### Tipos de Validação

| Tipo | Nível | Ação |
|------|-------|------|
| **✅ SUCCESS** | Info | Posição segura, pode executar |
| **⚠️ WARNING** | Alerta | Posição válida, mas requer atenção |
| **❌ ERROR** | Crítico | Posição rejeitada, NÃO executar |

---

## 🚨 WARNINGS EM TEMPO REAL

### 1. Risco Percentual

**O que valida:** Verifica se o risco por trade está dentro dos limites seguros.

```python
if risk_percentage > 2.0:
    ❌ ERRO: Risco muito alto (> 2%)
elif risk_percentage > 1.0:
    ⚠️  WARNING: Risco moderado (recomendado: < 1%)
else:
    ✅ Risco aceitável
```

**Exemplo:**
```
📊 PARÂMETROS:
   Account: $10,000
   Risk: $10

🔍 VALIDAÇÃO:
   ✅ Risco aceitável: 0.10%
```

**Por que importa:**
- Risco > 2% pode levar a drawdowns severos
- Com 10 perdas seguidas a 2%, perde 18.3% da conta
- Recomendação: < 1% para trading consistente

### 2. Margem Disponível

**O que valida:** Verifica se você tem margem livre suficiente para suportar volatilidade.

```python
margin_pct = (margin_required / account_balance) * 100

if margin_pct > 50:
    ❌ ERRO: Margem muito alta (> 50%)
elif margin_pct > 30:
    ⚠️  WARNING: Margem elevada (recomendado: < 30%)
else:
    ✅ Margem saudável
```

**Exemplo:**
```
💰 MARGEM:
   Required: $666.67
   Account: $10,000
   Usage: 6.7%

🔍 VALIDAÇÃO:
   ✅ Margem saudável: 6.7%
   💰 Margem Livre: $9,333.33 (93.3%)
```

**Por que importa:**
- Margem > 50% deixa pouca room para manter posições
- Em alta volatilidade, pode levar a liquidação
- Margem livre permite adicionar posições ou averaging

### 3. Distância até Liquidação

**O que valida:** Verifica se o stop loss está seguro em relação ao preço de liquidação.

```python
distance_stop_to_liq = ((stop_price - liquidation_price) / liquidation_price) * 100

if distance < 10:
    ❌ ERRO: Stop muito próximo da liquidação
elif distance < 20:
    ⚠️  WARNING: Stop relativamente próximo
else:
    ✅ Stop seguro
```

**Exemplo - SEGURO:**
```
📍 PREÇOS:
   Entry: $50,000
   Stop Loss: $49,500
   Liquidation: $33,583

📏 DISTÂNCIAS:
   Stop → Liquidação: 47.39%

🔍 VALIDAÇÃO:
   ✅ Stop seguro em relação à liquidação
```

**Exemplo - PERIGOSO:**
```
📍 PREÇOS:
   Entry: $50,000
   Stop Loss: $49,650
   Liquidation: $45,250
   Leverage: 10x

📏 DISTÂNCIAS:
   Stop → Liquidação: 9.72%

🔍 VALIDAÇÃO:
   ❌ ERRO: Stop muito próximo da liquidação!
```

**Por que importa:**
- Se stop < 10% da liquidação, volatilidade normal pode causar liquidação antes do stop
- Slippage ou gaps podem pular seu stop e liquidar a posição
- Liquidação = perda total da margem (maior que o stop loss planejado)

### 4. Distância do Stop Loss

**O que valida:** Verifica se o stop loss não está muito apertado (noise) ou muito largo (R:R ruim).

```python
if stop_distance < 0.3:
    ⚠️  WARNING: Stop muito apertado (< 0.3%)
elif stop_distance > 5.0:
    ⚠️  WARNING: Stop muito largo (> 5%)
else:
    ✅ Stop bem posicionado
```

**Exemplo:**
```
📏 STOP LOSS DISTANCE:
   Entry: $50,000
   Stop: $49,500
   Distance: 1.00%

🔍 VALIDAÇÃO:
   ✅ Stop bem posicionado: 1.00%
```

**Por que importa:**
- Stop < 0.3%: Pode ser hit por volatilidade normal (noise)
- Stop > 5%: R:R fica ruim, precisa ganhar muito para compensar
- Ideal: 0.5% - 3% dependendo do timeframe

### 5. Risk/Reward Ratio

**O que valida:** Verifica se o R:R é favorável para lucratividade de longo prazo.

```python
if risk_reward_ratio < 1.5:
    ⚠️  WARNING: R:R baixo (recomendado: > 1.5)
else:
    ✅ R:R favorável
```

**Exemplo:**
```
⚖️  RISK/REWARD:
   Risk: $10
   Profit Potential: $30
   Ratio: 1:3

🔍 VALIDAÇÃO:
   ✅ R:R favorável: 1:3.00
```

**Por que importa:**
- R:R 1:1 + 50% win rate = breakeven (sem lucro)
- R:R 1:2 + 40% win rate = breakeven
- R:R 1:3 + 33% win rate = breakeven
- Quanto maior o R:R, menor o win rate necessário

**Tabela de Win Rate Necessário:**

| R:R | Win Rate para Breakeven | Win Rate para +10% ROI |
|-----|------------------------|------------------------|
| 1:1 | 50% | 60% |
| 1:1.5 | 40% | 50% |
| 1:2 | 33% | 43% |
| 1:3 | 25% | 35% |
| 1:4 | 20% | 30% |

### 6. Tamanho da Posição

**O que valida:** Verifica se o tamanho da posição é proporcional à conta.

```python
position_pct = (position_value / account_balance) * 100

if position_pct > 100:
    ⚠️  WARNING: Posição maior que conta (usando leverage)
else:
    ℹ️  Position size: X% da conta
```

**Exemplo - Sem Leverage:**
```
💰 POSITION:
   Size: 0.02 BTC
   Value: $1,000
   Account: $10,000

🔍 VALIDAÇÃO:
   ℹ️  Position size: 10% da conta
```

**Exemplo - Com Leverage:**
```
💰 POSITION:
   Size: 0.04 BTC
   Value: $2,000
   Account: $10,000
   Leverage: 3x

🔍 VALIDAÇÃO:
   ⚠️  WARNING: Posição maior que conta: 200% (usando leverage 3x)
```

---

## 📊 VERIFICAÇÃO DE MARGEM ATÉ LIQUIDAÇÃO

### Cálculo de Liquidação (HyperLiquid Cross Margin)

**Fórmula:**
```python
# Para LONG:
liquidation_price = entry_price * (1 - (account_balance - margin_used) / (position_size * leverage))

# Para SHORT:
liquidation_price = entry_price * (1 + (account_balance - margin_used) / (position_size * leverage))
```

**Simplificado:**
```python
# Maintenance Margin (HyperLiquid)
maintenance_margin_rate = 0.005  # 0.5% para leverage baixo

# Para LONG:
liquidation_price = entry_price * (leverage - maintenance_margin_rate) / leverage

# Exemplo: Entry $50,000, Leverage 5x
liquidation_price = 50000 * (5 - 0.005) / 5 = $40,050
```

### Exemplo Completo - Verificação de Margem

```
╔══════════════════════════════════════════════════════════════╗
║              VERIFICAÇÃO DE MARGEM E LIQUIDAÇÃO              ║
╚══════════════════════════════════════════════════════════════╝

📊 SETUP:
   Entry Price: $50,000
   Position Size: 0.04 BTC
   Position Value: $2,000
   Account Balance: $10,000
   Leverage: 3x

💰 MARGEM:
   Margin Required: $666.67
   Margin Used %: 6.7%
   Free Margin: $9,333.33 (93.3%)

   ✅ Margem saudável - Suficiente para suportar volatilidade

⚠️  LIQUIDAÇÃO:
   Liquidation Price: $33,583.33
   Distance Entry → Liq: $16,416.67 (32.8%)

   Stop Loss: $49,500
   Distance Stop → Liq: $15,916.67 (47.4%)

   ✅ Stop seguro - 47.4% acima da liquidação

🔥 SIMULAÇÃO DE CENÁRIOS:

   Preço cai 10% ($45,000):
   • Perda: -$200 (2% da conta)
   • Margem disponível: $9,533.33
   • Status: ✅ Seguro

   Preço cai 20% ($40,000):
   • Perda: -$400 (4% da conta)
   • Margem disponível: $9,733.33
   • Status: ✅ Seguro

   Preço cai 32.8% ($33,583 - LIQUIDAÇÃO):
   • Perda: -$656 (6.6% da conta)
   • Margem disponível: $0
   • Status: ❌ LIQUIDADO

   MAS seu stop em $49,500 fecha a posição antes:
   • Perda no stop: -$20 (0.2% da conta)
   • ✅ Protegido
```

### Monitormento Real-Time

O sistema monitora constantemente:

1. **Distance to Liquidation** - Distância atual até preço de liquidação
2. **Margin Health** - % de margem livre
3. **Unrealized P&L** - Lucro/perda não realizado
4. **Stop Distance** - Distância até stop loss

**Alertas Automáticos:**
```python
if distance_to_liquidation < 20%:
    🚨 ALERTA CRÍTICO: Risco de liquidação alto!

if free_margin < 20%:
    ⚠️  ALERTA: Margem baixa - considere reduzir posições

if unrealized_loss > -1.5% of account:
    ⚠️  ALERTA: Perda aproximando do limite de risco
```

---

## ✅ VALIDAÇÃO DE POSIÇÕES

### Fluxo de Validação

```
┌─────────────────────────────┐
│  1. User Input Parameters   │
│  - Entry, Risk, Target      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  2. Calculate Position      │
│  - Size, Stop, TP           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  3. Run 6 Validations       │
│  - Risk, Margin, Liq, etc   │
└──────────┬──────────────────┘
           │
           ▼
      ╔═══════╗
      ║ Valid?║
      ╚═══╤═══╝
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌───────┐   ┌───────┐
│ ✅ YES │   │ ❌ NO  │
└───┬───┘   └───┬───┘
    │           │
    ▼           ▼
 Execute    Reject &
 Position   Show Errors
```

### Estados de Validação

#### Estado 1: ✅ POSIÇÃO TOTALMENTE SEGURA

**Critérios:**
- ✅ Risk ≤ 1%
- ✅ Margin ≤ 30%
- ✅ Stop → Liq > 20%
- ✅ Stop distance 0.5-3%
- ✅ R:R ≥ 1.5

**Exemplo:**
```
═══════════════════════════════════════════
✅ POSIÇÃO TOTALMENTE SEGURA
═══════════════════════════════════════════

Todas as validações passaram:
✅ Risco: 0.10% (muito seguro)
✅ Margem: 10% (excelente)
✅ Sem risco de liquidação
✅ Stop: 1.00% (ideal)
✅ R:R: 1:3 (favorável)

Recomendação: EXECUTAR
```

#### Estado 2: ⚠️ POSIÇÃO VÁLIDA COM WARNINGS

**Critérios:**
- 1 ou mais warnings
- 0 erros críticos
- Posição pode ser executada, mas requer atenção

**Exemplo:**
```
═══════════════════════════════════════════
⚠️  POSIÇÃO VÁLIDA COM WARNINGS (2 avisos)
═══════════════════════════════════════════

Validações:
✅ Risco: 0.50%
⚠️  Margem: 40% (elevada)
✅ Liquidação: 22.98%
✅ Stop: 1.00%
⚠️  R:R: 1:1.2 (baixo)

Warnings:
• Margem elevada (recomendado < 30%)
• R:R baixo (recomendado > 1.5)

Recomendação: EXECUTAR COM CAUTELA
Considere reduzir leverage ou melhorar R:R
```

#### Estado 3: ❌ POSIÇÃO REJEITADA

**Critérios:**
- 1 ou mais erros críticos
- Posição NÃO deve ser executada

**Exemplo:**
```
═══════════════════════════════════════════
❌ POSIÇÃO REJEITADA (1 erro crítico)
═══════════════════════════════════════════

Validações:
✅ Risco: 0.50%
✅ Margem: 7.2%
❌ Liquidação: 9.72% (MUITO PRÓXIMA)
✅ Stop: 0.70%
✅ R:R: 1:3

Erros Críticos:
• Stop muito próximo da liquidação (< 10%)
  Volatilidade normal pode causar liquidação
  antes do stop loss!

Recomendação: NÃO EXECUTAR
Reduza leverage de 10x para 3-5x
```

---

## 💻 EXEMPLOS PRÁTICOS

### Exemplo 1: Posição Conservadora - $10k Account

```python
from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe
)

calculator = PositionSizeCalculator()

# Setup conservador
params = PositionSizeParams(
    entry_price=50000,
    account_balance=10000,
    side=PositionSide.LONG,
    risk_amount_usdt=10,      # 0.1% apenas
    profit_target_usdt=30,    # R:R 1:3
    timeframe=Timeframe.M15,
    leverage=1                # Sem leverage
)

result = calculator.calculate_position_size(params)

print(f"Position: {result.position_size:.6f} BTC")
print(f"Stop Loss: ${result.stop_loss_price:,.2f}")
print(f"Take Profit: ${result.take_profit_price:,.2f}")
print(f"Risk: {result.risk_percentage_of_account:.2f}%")
print(f"Margin: ${result.margin_required:,.2f}")

# Validar manualmente
if result.risk_percentage_of_account > 2.0:
    print("❌ Risco muito alto!")
elif result.risk_percentage_of_account > 1.0:
    print("⚠️  Risco moderado")
else:
    print("✅ Risco aceitável")
```

**Output:**
```
Position: 0.020000 BTC
Stop Loss: $49,500.00
Take Profit: $51,500.00
Risk: 0.10%
Margin: $1,000.00
✅ Risco aceitável
```

### Exemplo 2: Validação Automática com Script

```bash
# Executar validação de segurança
python validate_security.py

# Escolher opção:
# 1 - Bateria completa (6 cenários)
# 2 - Demo tempo real
# 3 - Ambos
```

**Output Esperado:**
```
╔═════════════════════════════════════════════╗
║       VALIDAÇÃO DE SEGURANÇA                ║
╚═════════════════════════════════════════════╝

Escolha um teste:
1 - Bateria completa de validação (6 cenários)
2 - Demo de monitoramento em tempo real
3 - Executar ambos

> 1

🔒 TESTE 1: Posição SEGURA (Conservadora)
...
✅ POSIÇÃO TOTALMENTE SEGURA

🔒 TESTE 2: Posição MODERADA (3x Leverage)
...
✅ POSIÇÃO TOTALMENTE SEGURA

🔒 TESTE 3: Posição ARRISCADA (10x Leverage)
...
❌ POSIÇÃO REJEITADA - Stop muito próximo da liquidação

...

📊 RESUMO:
   Testes: 6
   Válidas: 3
   Com Warnings: 2
   Rejeitadas: 1
```

### Exemplo 3: Monitoring Real-Time

```python
# Simular monitoramento de posição aberta
from validate_security import SecurityValidator

validator = SecurityValidator()

# Parâmetros da posição aberta
entry = 50000
stop = 49500
tp = 51500
position_size = 0.04
leverage = 3
liquidation = 33583
account = 10000

# Preço atual
current_price = 50500

# Calcular métricas
pnl = (current_price - entry) * position_size
pnl_pct = ((current_price - entry) / entry) * 100 * leverage

dist_to_stop = abs(current_price - stop)
dist_to_liq = abs(current_price - liquidation)

print(f"💹 Preço: ${current_price:,.2f}")
print(f"📊 P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
print(f"📏 Até Stop: ${dist_to_stop:.2f}")
print(f"📏 Até Liquidação: ${dist_to_liq:.2f}")

# Validações em tempo real
if pnl_pct > 1.5:
    print("✅ Considere mover stop para breakeven")

if pnl_pct > 3.0:
    print("✅ Considere trailing stop")

if dist_to_liq < current_price * 0.25:
    print("🚨 ALERTA: Liquidação muito próxima!")
```

---

## 🔧 COMO USAR

### Método 1: Usar Position Calculator Diretamente

```python
from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe
)

calculator = PositionSizeCalculator()

params = PositionSizeParams(
    entry_price=50000,
    account_balance=10000,
    side=PositionSide.LONG,
    risk_amount_usdt=20,
    profit_target_usdt=60,
    timeframe=Timeframe.M15,
    leverage=3
)

# Calculator JÁ valida automaticamente
result = calculator.calculate_position_size(params)

# Verificar se é válido
if result.is_valid:
    print("✅ Posição válida")

    # Verificar warnings
    if result.warnings:
        print(f"⚠️  Warnings: {len(result.warnings)}")
        for warning in result.warnings:
            print(f"   • {warning}")
else:
    print("❌ Posição rejeitada")
```

### Método 2: Usar Script de Validação

```bash
# Executar testes pré-definidos
python validate_security.py

# Escolher opção 1 para ver 6 cenários diferentes
```

### Método 3: Usar Web Demo

```bash
# Iniciar interface web
streamlit run web_demo.py

# A interface mostra warnings automaticamente
# Seção "🚨 Avisos de Segurança" aparece se houver problemas
```

### Método 4: Integração com HyperLiquid

```python
from connectors.hyperliquid_connector import HyperLiquidConnector

# Connector valida automaticamente antes de executar
connector = HyperLiquidConnector(testnet=True)

result = connector.place_smart_order(
    symbol='BTC-USD',
    side='BUY',
    entry_price=50000,
    risk_amount_usdt=10,
    profit_target_usdt=30,
    use_leverage=True
)

# Se validação falhar, ordem não é executada
if result['status'] == 'rejected':
    print(f"❌ Ordem rejeitada: {result['reason']}")
else:
    print(f"✅ Ordem executada: {result}")
```

---

## 📖 REFERÊNCIA DE VALIDAÇÕES

### Tabela Completa de Limites

| Validação | Threshold Verde (✅) | Threshold Amarelo (⚠️) | Threshold Vermelho (❌) |
|-----------|---------------------|----------------------|------------------------|
| **Risco %** | ≤ 1.0% | 1.0% - 2.0% | > 2.0% |
| **Margem %** | ≤ 30% | 30% - 50% | > 50% |
| **Stop → Liq** | ≥ 20% | 10% - 20% | < 10% |
| **Stop Distance** | 0.5% - 3.0% | 0.3% - 5.0% | < 0.3% ou > 5.0% |
| **R:R Ratio** | ≥ 2.0 | 1.5 - 2.0 | < 1.5 |
| **Win Rate Mín** | Depende do R:R | Ver tabela abaixo | N/A |

### Win Rate Mínimo por R:R

| R:R | Breakeven WR | +5% ROI WR | +10% ROI WR | +20% ROI WR |
|-----|--------------|-----------|------------|------------|
| 1:1 | 50% | 55% | 60% | 70% |
| 1:1.5 | 40% | 45% | 50% | 60% |
| 1:2 | 33% | 38% | 43% | 53% |
| 1:2.5 | 29% | 34% | 39% | 49% |
| 1:3 | 25% | 30% | 35% | 45% |
| 1:4 | 20% | 25% | 30% | 40% |

### Leverage Recomendado por Experiência

| Nível | Max Leverage | Risco/Trade | Margem Max | Descrição |
|-------|-------------|-------------|-----------|-----------|
| **Iniciante** | 1-2x | 0.1-0.5% | 20% | Foco em aprender sem risco excessivo |
| **Intermediário** | 2-5x | 0.2-1.0% | 30% | Já tem consistência, pode aumentar |
| **Avançado** | 5-10x | 0.5-2.0% | 40% | Expertise comprovada, risk management sólido |
| **Profissional** | Variável | Depende | Depende | Ajusta conforme mercado e estratégia |

### Ações por Status

| Status | Ação Recomendada |
|--------|-----------------|
| ✅ **Totalmente Segura** | Executar imediatamente |
| ⚠️ **Válida com Warnings** | Revisar warnings → Executar com cautela |
| ❌ **Rejeitada** | NÃO executar → Ajustar parâmetros |

---

## 🎓 BEST PRACTICES

### 1. Sempre Validar Antes de Executar

```python
# ERRADO ❌
connector.execute_order(size, entry, stop, tp)

# CERTO ✅
result = calculator.calculate_position_size(params)
if result.is_valid and len(result.warnings) == 0:
    connector.execute_order(...)
else:
    print("Posição não passou nas validações")
```

### 2. Monitorar Posições Abertas

```python
# Configurar alertas
def check_position_health(position):
    current_price = get_current_price()

    dist_to_liq = abs(current_price - position.liquidation_price)

    if dist_to_liq < current_price * 0.15:
        send_alert("🚨 LIQUIDAÇÃO PRÓXIMA")

    if position.unrealized_loss > account * -0.015:
        send_alert("⚠️  Perda aproximando limite")
```

### 3. Testar em Paper Trading Primeiro

```python
# Usar testnet
connector = HyperLiquidConnector(testnet=True)

# Log todas as validações
for i in range(100):
    result = test_strategy()
    log_validation_results(result)

# Analisar taxa de rejeição
rejection_rate = rejected / total
if rejection_rate > 0.3:
    print("⚠️  30%+ das ordens sendo rejeitadas - ajustar parâmetros")
```

### 4. Revisar Warnings Regularmente

```bash
# Gerar relatório de warnings
python -c "
from analyze_trades import get_all_warnings
warnings = get_all_warnings(last_30_days=True)
print(f'Total warnings: {len(warnings)}')
print(f'Most common: {warnings.most_common(5)}')
"
```

---

## ⚠️ AVISOS IMPORTANTES

### O Sistema NÃO Protege Contra

1. **Mudanças súbitas de mercado** - Gaps ou movimentos extremos podem pular stops
2. **Falhas de exchange** - Liquidez, latência, downtime
3. **Eventos de cisne negro** - Crashes extremos, hacks, etc.
4. **Erros do usuário** - Executar manualmente sem validação
5. **Over-trading** - Sistema valida cada trade, mas não quantidade total de trades

### Use SEMPRE

- ✅ Stop loss em todas as posições
- ✅ Validação automática antes de executar
- ✅ Monitoramento de posições abertas
- ✅ Paper trading antes de real money
- ✅ Risk management rigoroso

### NUNCA

- ❌ Bypassar validações para "forçar" uma ordem
- ❌ Aumentar leverage após perdas (revenge trading)
- ❌ Remover stop loss de posição aberta
- ❌ Adicionar a posições perdedoras (averaging down sem plano)
- ❌ Arriscar mais de 2% por trade

---

## 📞 SUPORTE

### Arquivos Relacionados

- `risk_management/position_size_calculator.py` - Calculator com validações
- `validate_security.py` - Script de validação completo
- `web_demo.py` - Interface web com validações visuais
- `examples/position_size_calculator_examples.py` - 8 exemplos práticos

### Comandos Úteis

```bash
# Ver exemplos
python examples/position_size_calculator_examples.py

# Testar validações
python validate_security.py

# Web demo
streamlit run web_demo.py

# Rodar testes
pytest test_position_size_calculator.py -v
```

---

## 📝 CHANGELOG

### Versão 1.0 (2025-11-06)

**Adicionado:**
- ✅ Sistema completo de validação com 6 camadas
- ✅ Warnings em tempo real
- ✅ Verificação de margem até liquidação
- ✅ Script de validação interativo
- ✅ Documentação completa
- ✅ Exemplos práticos
- ✅ Integração com Position Calculator
- ✅ Testes automatizados

**Validações Implementadas:**
1. Risco percentual (< 1% ✅, < 2% ⚠️, > 2% ❌)
2. Margem disponível (< 30% ✅, < 50% ⚠️, > 50% ❌)
3. Distância até liquidação (> 20% ✅, > 10% ⚠️, < 10% ❌)
4. Distância do stop loss (0.5-3% ✅, 0.3-5% ⚠️, fora ❌)
5. Risk/Reward ratio (> 2 ✅, > 1.5 ⚠️, < 1.5 ❌)
6. Tamanho da posição (informativo)

---

**Desenvolvido por:** AI Agent System
**Licença:** MIT
**Status:** ✅ Produção

---

*Este sistema foi desenvolvido para maximizar segurança no trading. No entanto, trading sempre envolve risco de perda de capital. Use com responsabilidade.*
