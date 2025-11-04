# 📊 Guia Completo: Cálculo de Alavancagem no Mercado Futuro

## Índice
1. [Conceito de Alavancagem](#conceito)
2. [Cálculo de Leverage Ótima](#calculo)
3. [Exemplos Práticos](#exemplos)
4. [Preço de Liquidação](#liquidacao)
5. [Riscos e Cuidados](#riscos)

---

## 1. Conceito de Alavancagem {#conceito}

### O que é Alavancagem?

Alavancagem permite controlar uma posição maior com menos capital (margem).

**Exemplo Simples:**
```
Capital: $1,000
Alavancagem: 10x
Posição Controlada: $10,000

Se o preço sobe 1%:
- Lucro na posição: $100 (1% de $10,000)
- Lucro no capital: $100 / $1,000 = 10%

Se o preço cai 1%:
- Perda na posição: $100
- Perda no capital: $100 / $1,000 = -10%

Leverage amplifica GANHOS e PERDAS!
```

### Fórmula Básica

```
Margem Necessária = Valor da Posição / Leverage

Exemplo:
- Posição: $10,000
- Leverage: 5x
- Margem: $10,000 / 5 = $2,000
```

---

## 2. Cálculo de Leverage Ótima {#calculo}

### A Fórmula do Sistema

O sistema calcula a leverage ideal baseado na distância do stop loss:

```python
def calculate_optimal_leverage(
    entry_price: float,
    stop_loss_price: float,
    max_loss_pct: float = 2.0  # Perda máxima permitida (%)
) -> int:
    """
    Calcula leverage ótima baseada no stop loss

    Lógica:
    - Se stop = 2% de distância e max_loss = 2%
      → Leverage = 1x (sem leverage)

    - Se stop = 1% de distância e max_loss = 2%
      → Leverage = 2x

    - Se stop = 0.5% de distância e max_loss = 2%
      → Leverage = 4x
    """

    # 1. Calcula distância do stop em %
    stop_distance_pct = abs(entry_price - stop_loss_price) / entry_price * 100

    # 2. Se distância >= perda máxima, não precisa leverage
    if stop_distance_pct >= max_loss_pct:
        return 1

    # 3. Calcula leverage necessária
    leverage = max_loss_pct / stop_distance_pct

    # 4. Arredonda e limita
    leverage = int(round(leverage))
    leverage = min(leverage, 20)  # Máximo 20x (limite típico)

    return leverage
```

### Por que essa Fórmula?

**Objetivo:** Garantir que se o stop loss for atingido, você perca **exatamente** a % de risco planejada.

**Exemplo:**
```
Entry: $50,000
Stop: $49,750 (0.5% de distância)
Max Loss: 2% do capital

Sem leverage:
- Stop bateu = perde 0.5% ❌ (menor que planejado)

Com leverage 4x:
- Stop bateu = perde 0.5% × 4 = 2% ✅ (exatamente o planejado!)
```

---

## 3. Exemplos Práticos {#exemplos}

### Exemplo 1: Stop Largo (sem leverage necessária)

```
📊 SETUP:
Entry: $50,000
Stop Loss: $49,000 (2% de distância)
Capital: $10,000
Max Loss Permitido: 2% = $200

CÁLCULO:
Distância do Stop: 2%
Max Loss: 2%

Leverage Ótima = 2% / 2% = 1x

✅ RESULTADO:
- Leverage: 1x (sem alavancagem)
- Margem necessária: $10,000
- Se stop bater: perde $200 (2%)
```

### Exemplo 2: Stop Médio (leverage moderada)

```
📊 SETUP:
Entry: $50,000
Stop Loss: $49,500 (1% de distância)
Capital: $10,000
Max Loss Permitido: 2% = $200

CÁLCULO:
Distância do Stop: 1%
Max Loss: 2%

Leverage Ótima = 2% / 1% = 2x

✅ RESULTADO:
- Leverage: 2x
- Position Size: 0.04 BTC ($2,000 de valor)
- Margem necessária: $2,000 / 2 = $1,000
- Se stop bater: perde 1% × 2 = 2% = $200 ✅
```

### Exemplo 3: Stop Apertado (leverage alta)

```
📊 SETUP:
Entry: $50,000
Stop Loss: $49,900 (0.2% de distância)
Capital: $10,000
Max Loss Permitido: 2% = $200

CÁLCULO:
Distância do Stop: 0.2%
Max Loss: 2%

Leverage Ótima = 2% / 0.2% = 10x

✅ RESULTADO:
- Leverage: 10x
- Position Size: 0.2 BTC ($10,000 de valor)
- Margem necessária: $10,000 / 10 = $1,000
- Se stop bater: perde 0.2% × 10 = 2% = $200 ✅

⚠️ ATENÇÃO: Leverage alta = risco de liquidação!
```

### Exemplo 4: Comparação Side-by-Side

```
┌─────────────────────────────────────────────────────────────────┐
│  Capital: $10,000 | Max Loss: 2% ($200) | Entry: $50,000       │
├──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│ Stop     │ Dist %   │ Leverage │ Margem   │ P&L se Stop Bater   │
├──────────┼──────────┼──────────┼──────────┼─────────────────────┤
│ $49,000  │ 2.0%     │ 1x       │ $10,000  │ -$200 (2%)         │
│ $49,500  │ 1.0%     │ 2x       │ $1,000   │ -$200 (2%)         │
│ $49,750  │ 0.5%     │ 4x       │ $500     │ -$200 (2%)         │
│ $49,900  │ 0.2%     │ 10x      │ $200     │ -$200 (2%)         │
└──────────┴──────────┴──────────┴──────────┴─────────────────────┘

💡 INSIGHT:
Independente da leverage, você sempre perde a mesma quantia ($200)
quando o stop é atingido!

A diferença está na MARGEM necessária:
- Stop largo = mais margem, menos leverage
- Stop apertado = menos margem, mais leverage
```

---

## 4. Preço de Liquidação {#liquidacao}

### O que é Liquidação?

Liquidação ocorre quando suas perdas consomem toda a margem disponível. A exchange fecha sua posição automaticamente.

### Cálculo de Liquidação

```python
def calculate_liquidation_price(
    entry_price: float,
    side: str,  # 'long' ou 'short'
    leverage: int
) -> float:
    """
    Fórmula aproximada de liquidação
    """
    maintenance_margin = 0.005  # 0.5% (varia por exchange)

    if side == 'long':
        # Long: liquidação abaixo do entry
        liq_price = entry_price * (1 - (1/leverage) + maintenance_margin)
    else:
        # Short: liquidação acima do entry
        liq_price = entry_price * (1 + (1/leverage) - maintenance_margin)

    return liq_price
```

### Exemplos de Liquidação

```
Entry: $50,000 (LONG)

Leverage 1x:
- Liquidação: ~$0 (sem liquidação prática)

Leverage 2x:
- Liquidação: $50,000 × (1 - 1/2) = $25,000
- Queda de 50% = liquidação

Leverage 5x:
- Liquidação: $50,000 × (1 - 1/5) = $40,000
- Queda de 20% = liquidação

Leverage 10x:
- Liquidação: $50,000 × (1 - 1/10) = $45,000
- Queda de 10% = liquidação

Leverage 20x:
- Liquidação: $50,000 × (1 - 1/20) = $47,500
- Queda de 5% = liquidação ⚠️
```

### Relação entre Stop Loss e Liquidação

**REGRA DE OURO:** Seu stop loss deve estar **SEMPRE** antes da liquidação!

```
✅ BOM:
Entry: $50,000
Stop: $49,500 (1% de distância)
Leverage: 2x
Liquidação: $25,000

Stop está MUITO antes da liquidação → Seguro!

❌ PERIGOSO:
Entry: $50,000
Stop: $49,000 (2% de distância)
Leverage: 20x
Liquidação: $47,500

Stop está DEPOIS da liquidação → Você será liquidado antes do stop!
```

### Sistema de Validação

O Position Size Calculator verifica automaticamente:

```python
# Verifica distância entre stop e liquidação
if position_side == 'LONG':
    distance_to_liq = (stop_loss_price - liquidation_price) / liquidation_price * 100
else:
    distance_to_liq = (liquidation_price - stop_loss_price) / liquidation_price * 100

if distance_to_liq < 10:  # Menos de 10% de margem
    warnings.append(
        f"⚠️ Stop muito próximo da liquidação: {distance_to_liq:.2f}% de margem"
    )
```

---

## 5. Riscos e Cuidados {#riscos}

### ⚠️ Riscos da Alavancagem

1. **Liquidação Rápida**
   - Quanto maior a leverage, mais rápido pode ser liquidado
   - Volatilidade extrema pode liquidar antes do stop

2. **Custos de Funding**
   - Posições alavancadas pagam funding rate
   - Em mercados de tendência forte, pode ser caro manter posição

3. **Slippage Amplificado**
   - Slippage em posições grandes pode ser significativo
   - Especialmente em mercados ilíquidos

4. **Gap de Preço**
   - Se mercado abre com gap, pode ser liquidado sem tocar no stop
   - Mais comum em fins de semana ou eventos extremos

### ✅ Boas Práticas

1. **Comece com Leverage Baixa**
   ```
   Iniciante: Máximo 2-3x
   Intermediário: Máximo 5x
   Avançado: Máximo 10x
   Profissional: Máximo 20x (com muito cuidado!)
   ```

2. **Sempre Use Stop Loss**
   - NUNCA opere com leverage sem stop loss
   - Configure o stop ANTES de entrar na posição

3. **Margem de Segurança**
   ```
   Stop Loss: $49,500
   Liquidação: $47,500

   Margem de Segurança: $49,500 - $47,500 = $2,000
   % de Margem: 4%

   Recomendado: Mínimo 10% de margem entre stop e liquidação
   ```

4. **Teste no Papel Primeiro**
   - Use o sistema de cálculo para simular
   - Entenda os riscos antes de operar real

5. **Monitore Constantemente**
   - Posições alavancadas precisam de monitoramento
   - Considere usar trailing stops

### 📋 Checklist Antes de Usar Leverage

```
□ Calculei a leverage ótima para meu stop loss?
□ Verifiquei o preço de liquidação?
□ Tenho margem suficiente na conta?
□ Meu stop está ANTES da liquidação (mínimo 10%)?
□ Entendo que posso perder todo o capital investido?
□ Tenho experiência suficiente para usar esta leverage?
□ O risco está dentro do meu limite (máximo 2% da conta)?
□ Configurei stop loss antes de entrar?
```

---

## 6. Como o Sistema Implementa

### No Position Size Calculator

```python
# 1. Sistema calcula distância do stop
stop_distance_pct = abs(entry_price - stop_loss_price) / entry_price * 100

# 2. Determina leverage baseado no risco
if use_leverage:
    leverage = calculate_optimal_leverage(
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        max_loss_pct=2.0  # Máximo 2% de perda
    )
else:
    leverage = 1

# 3. Calcula preço de liquidação
liquidation_price = calculate_liquidation_price(
    entry_price, side, leverage
)

# 4. Valida segurança
if stop is too close to liquidation:
    warnings.append("⚠️ Risco de liquidação alto!")

# 5. Calcula margem necessária
margin_required = position_value / leverage
```

### No HyperLiquid Connector

```python
# Ao colocar ordem inteligente
def place_smart_order(self, ...):
    # 1. Calcula position size ideal
    result = self.position_calculator.calculate_position_size(params)

    # 2. Se usar leverage, ajusta na exchange
    if use_leverage and result.leverage > 1:
        self.set_leverage(symbol, result.leverage)

    # 3. Coloca ordem com margem calculada
    order = self.place_order(...)

    # 4. Configura stop loss (proteção)
    self.set_stop_loss(symbol, result.stop_loss_price)

    return result
```

---

## 7. Exemplos de Código

### Exemplo 1: Calcular Leverage Manualmente

```python
from risk_management.position_size_calculator import calculate_optimal_leverage

# Cenário: Stop apertado
entry = 50000
stop = 49750  # 0.5% de distância
max_loss = 2.0  # 2% do capital

leverage = calculate_optimal_leverage(entry, stop, max_loss)
print(f"Leverage ótima: {leverage}x")
# Output: Leverage ótima: 4x

# Explicação:
# Stop = 0.5% de distância
# Max Loss = 2%
# Leverage = 2% / 0.5% = 4x
```

### Exemplo 2: Simular Diferentes Stops

```python
from risk_management.position_size_calculator import calculate_optimal_leverage

entry = 50000
max_loss = 2.0

stops = [49000, 49500, 49750, 49900]

print("Stop\t\tDist%\tLeverage")
print("-" * 40)

for stop in stops:
    distance = ((entry - stop) / entry) * 100
    leverage = calculate_optimal_leverage(entry, stop, max_loss)
    print(f"${stop}\t{distance:.2f}%\t{leverage}x")

# Output:
# Stop          Dist%   Leverage
# ----------------------------------------
# $49000        2.00%   1x
# $49500        1.00%   2x
# $49750        0.50%   4x
# $49900        0.20%   10x
```

### Exemplo 3: Validar Segurança

```python
from risk_management.position_size_calculator import (
    calculate_optimal_leverage,
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe
)

entry = 50000
stop = 49900  # Stop apertado: 0.2%

# Calcula leverage
leverage = calculate_optimal_leverage(entry, stop, 2.0)
print(f"Leverage sugerida: {leverage}x")

# Calcula liquidação
if leverage > 1:
    liq_price = entry * (1 - (1/leverage) + 0.005)
    print(f"Preço de liquidação: ${liq_price:,.2f}")

    # Verifica margem de segurança
    margin = ((stop - liq_price) / liq_price) * 100
    print(f"Margem de segurança: {margin:.2f}%")

    if margin < 10:
        print("⚠️ ATENÇÃO: Margem muito pequena!")
    else:
        print("✅ Margem adequada")

# Output:
# Leverage sugerida: 10x
# Preço de liquidação: $45,250.00
# Margem de segurança: 10.30%
# ✅ Margem adequada
```

---

## 8. Resumo Visual

```
┌────────────────────────────────────────────────────────────────────┐
│                    FLUXO DE CÁLCULO DE LEVERAGE                    │
└────────────────────────────────────────────────────────────────────┘

1. ENTRADA DO TRADER
   ↓
   Entry: $50,000
   Stop: $49,500
   Risk: $10 (0.1% da conta de $10,000)
   Max Loss: 2%

2. SISTEMA CALCULA
   ↓
   Distância Stop: 1%
   Leverage Ótima: 2% / 1% = 2x

3. CÁLCULOS DERIVADOS
   ↓
   Position Size: 0.02 BTC
   Position Value: $1,000
   Margem Necessária: $1,000 / 2 = $500
   Liquidação: ~$25,000

4. VALIDAÇÕES
   ↓
   ✓ Margem disponível? SIM ($10,000 > $500)
   ✓ Stop antes liquidação? SIM ($49,500 > $25,000)
   ✓ Risk dentro limite? SIM (0.1% < 2%)

5. RESULTADO
   ↓
   ✅ POSIÇÃO APROVADA
   Comprar 0.02 BTC com 2x leverage
   Margem: $500
   Stop: $49,500
   Target: $51,500
```

---

## 💡 Dica Final

**Use a função de simulação antes de operar:**

```python
# Simule ANTES de executar
result = connector.calculate_position_size_only(
    symbol='BTC',
    side='buy',
    entry_price=50000,
    stop_loss_price=49500
)

print(f"Leverage: {result.leverage}x")
print(f"Liquidação: ${result.liquidation_price:,.2f}")
print(f"Margem: ${result.margin_required:,.2f}")

# Só execute se estiver confortável
if input("Executar? (s/n): ") == 's':
    connector.place_smart_order(...)
```

---

**Lembre-se:** Alavancagem é uma ferramenta poderosa, mas deve ser usada com responsabilidade e sempre com gestão de risco adequada! 🎯
