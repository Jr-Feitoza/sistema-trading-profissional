# 🌐 Web Demo Interface - Prévia Visual

## Como Acessar

```bash
# Instalar dependências
pip install streamlit pandas numpy eth-account

# Executar o web demo
streamlit run web_demo.py
```

O Streamlit abrirá automaticamente no navegador em: `http://localhost:8501`

---

## 📱 Interface do Usuário

### 🎯 Tela Principal: Position Size Calculator

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    🚀 Sistema Trading Profissional                       ║
║           Calculadora de Position Size com Risk Management Avançado      ║
╚══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│  SIDEBAR (Esquerda)                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ⚙️ Configurações                                                       │
│                                                                          │
│  Modo: ● 🎯 Position Size Calculator                                   │
│        ○ 📊 Leverage Calculator                                         │
│        ○ 📖 Sobre                                                       │
│                                                                          │
│  ─────────────────────────────────                                      │
│                                                                          │
│  ### Parâmetros da Posição                                             │
│                                                                          │
│  💵 Preço de Entrada (USDT)                                            │
│  [    50000.00    ] ▲▼                                                 │
│                                                                          │
│  💰 Saldo da Conta (USDT)                                              │
│  [    10000.00    ] ▲▼                                                 │
│                                                                          │
│  📈 Lado da Operação                                                    │
│  [ LONG (Compra) ▼ ]                                                   │
│                                                                          │
│  ⚠️ Quanto Arriscar (USDT)                                             │
│  [     10.00      ] ▲▼                                                 │
│  ℹ️ Quanto você está disposto a perder                                │
│                                                                          │
│  🎯 Objetivo de Lucro (USDT)                                           │
│  [     30.00      ] ▲▼                                                 │
│  ℹ️ Quanto você quer lucrar                                            │
│                                                                          │
│  ⏱️ Timeframe                                                           │
│  [     15m      ▼  ]                                                   │
│                                                                          │
│  ☐ Definir Stop Loss Manualmente                                       │
│                                                                          │
│  ☐ Usar Alavancagem                                                    │
│                                                                          │
│  ─────────────────────────────────                                      │
│                                                                          │
│  [ 🔥 Calcular Position Size ]                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  ÁREA PRINCIPAL (Direita)                                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ✅ Posição Calculada com Sucesso!                                     │
│                                                                          │
│  ┌────────────┬────────────┬────────────┬────────────┐                 │
│  │ 📦 Position│ 💵 Valor da│ 💳 Margem  │ ⚖️ Risk/   │                 │
│  │    Size    │  Posição   │ Necessária │  Reward    │                 │
│  │            │            │            │            │                 │
│  │  0.020000  │  $1,000.00 │  $1,000.00 │   1:3.00   │                 │
│  │            │            │            │            │                 │
│  │ Quantidade │ Valor total│ Margem p/  │ Ratio entre│                 │
│  │ de ativos  │ da posição │ abrir a    │ risco e    │                 │
│  │            │            │ posição    │ recompensa │                 │
│  └────────────┴────────────┴────────────┴────────────┘                 │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  ### 📉 Stop Loss         │   ### 📈 Take Profit                       │
│                            │                                             │
│  Preço: $49,500.00        │   Preço: $51,500.00                        │
│  Distância: 1.00%         │   Distância: 3.00%                         │
│  Risco: $10.00            │   Lucro Potencial: $30.00                  │
│  Risco % da Conta: 0.10%  │                                             │
│                            │                                             │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  ### 📊 Níveis de Preço                                                │
│                                                                          │
│  Take Profit  ████████████████████▌ $51,500                            │
│  Entry        ██████████████████▌ $50,000                              │
│  Stop Loss    ████████████████▌ $49,500                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 📊 Tela 2: Leverage Calculator

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ### 📊 Calculadora de Leverage Ótima                                  │
│                                                                          │
│  Esta ferramenta calcula a leverage ideal baseada na distância do       │
│  seu stop loss.                                                         │
│                                                                          │
│  Objetivo: Garantir que se o stop loss for atingido, você perca        │
│  exatamente a % de risco planejada.                                     │
│                                                                          │
│  ┌──────────────────────┬──────────────────────┐                       │
│  │ Preço de Entrada     │ Preço do Stop Loss   │                       │
│  │ [    50000.00    ]▲▼ │ [    49500.00    ]▲▼ │                       │
│  │                      │                      │                       │
│  │ Perda Máxima (%)     │                      │                       │
│  │ [      2.0       ]▲▼ │                      │                       │
│  └──────────────────────┴──────────────────────┘                       │
│                                                                          │
│  [  Calcular Leverage Ótima  ]                                         │
│                                                                          │
│  ✅ ### ⚡ Leverage Ótima: 2x                                          │
│                                                                          │
│  ┌──────────────────┬──────────────────┬──────────────────┐            │
│  │ Distância do Stop│ Perda Máxima     │ Leverage         │            │
│  │                  │                  │                  │            │
│  │     1.00%        │      2.00%       │       2x         │            │
│  └──────────────────┴──────────────────┴──────────────────┘            │
│                                                                          │
│  ℹ️ Explicação:                                                         │
│                                                                          │
│  Com leverage de 2x, se o preço se mover 1.00% até o stop loss,       │
│  você perderá exatamente 2.00% do seu capital.                         │
│                                                                          │
│  Fórmula: Leverage = Perda Máxima / Distância do Stop                 │
│  2 = 2.00% / 1.00%                                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Funcionalidades Interativas

### 1. **Inputs Dinâmicos**
- ✅ Number inputs com incremento/decremento (▲▼)
- ✅ Selectboxes para escolhas
- ✅ Checkboxes para opções
- ✅ Validação em tempo real

### 2. **Cálculo Instantâneo**
- ✅ Clique no botão → cálculo imediato
- ✅ Sem reload de página
- ✅ Feedback visual instantâneo

### 3. **Visualizações**
- ✅ Métricas em cards coloridos
- ✅ Gráfico de barras (níveis de preço)
- ✅ Ícones visuais para cada seção
- ✅ Cores: verde (válido), vermelho (inválido), amarelo (warning)

### 4. **Validações**
- ✅ Avisos em tempo real
- ✅ Status de validação (válido/inválido)
- ✅ Tooltips explicativos
- ✅ Mensagens de erro claras

### 5. **Responsividade**
- ✅ Layout adaptável
- ✅ Sidebar colapsável
- ✅ Funciona em desktop e tablet

---

## 🎨 Temas de Cores

### Tema Claro (padrão)
- Background: Branco
- Sidebar: Cinza claro
- Botão primário: Azul
- Sucesso: Verde
- Warning: Amarelo
- Erro: Vermelho

### Tema Escuro (settings)
- Background: Preto
- Sidebar: Cinza escuro
- Botão primário: Azul claro
- Cores mantêm contraste

---

## 🔧 Controles Disponíveis

### Position Size Calculator
| Campo | Tipo | Default | Range |
|-------|------|---------|-------|
| Preço de Entrada | Number | 50,000 | 0 - ∞ |
| Saldo da Conta | Number | 10,000 | 0 - ∞ |
| Lado | Select | LONG | LONG/SHORT |
| Risco (USDT) | Number | 10 | 0 - ∞ |
| Objetivo (USDT) | Number | 30 | 0 - ∞ |
| Timeframe | Select | 15m | 1m-1d |
| Stop Manual | Checkbox | ☐ | - |
| Usar Leverage | Checkbox | ☐ | - |
| Alavancagem Máx | Slider | 10 | 1-50 |

### Leverage Calculator
| Campo | Tipo | Default | Range |
|-------|------|---------|-------|
| Preço Entrada | Number | 50,000 | 0 - ∞ |
| Preço Stop | Number | 49,500 | 0 - ∞ |
| Perda Máxima (%) | Number | 2.0 | 0-100 |

---

## 📱 Screenshots Simuladas

### Exemplo 1: Trade Conservador

```
Input:
  Entry: $50,000
  Balance: $10,000
  Risk: $5
  Target: $15
  Timeframe: 1h
  Leverage: Não

Output:
  Position Size: 0.010000 BTC
  Stop: $49,500 (-1.00%)
  TP: $51,500 (+3.00%)
  R:R: 1:3.00
  Status: ✅ VÁLIDO
```

### Exemplo 2: Trade Agressivo com Leverage

```
Input:
  Entry: $50,000
  Balance: $10,000
  Risk: $20
  Target: $80
  Timeframe: 5m
  Leverage: SIM (10x)

Output:
  Position Size: 0.057143 BTC
  Stop: $49,650 (-0.70%)
  TP: $51,400 (+2.80%)
  R:R: 1:4.00
  Leverage: 10x
  Liquidação: $45,500
  Status: ✅ VÁLIDO
  
  ⚠️ Warning:
  - Leverage alta (10x) = risco elevado
  - Margem até liquidação: 8.30%
```

### Exemplo 3: Trade Inválido

```
Input:
  Entry: $50,000
  Balance: $1,000
  Risk: $100
  Target: $300
  Timeframe: 15m
  Leverage: SIM (50x)

Output:
  ❌ POSIÇÃO INVÁLIDA
  
  Avisos:
  - ⚠️ Risk muito alto: 10.00% (máximo: 2%)
  - ⚠️ Margin insuficiente
  - ⚠️ Stop muito próximo da liquidação
```

---

## 🚀 Como Usar

1. **Abra o demo**: `streamlit run web_demo.py`
2. **Configure parâmetros** na sidebar esquerda
3. **Clique** em "Calcular Position Size"
4. **Veja resultados** instantaneamente
5. **Ajuste** parâmetros e recalcule
6. **Experimente** diferentes cenários

---

## 💡 Dicas de Uso

### Para Traders Iniciantes
- Comece com leverage desativada
- Use risk baixo ($5-10)
- Escolha timeframes maiores (1h, 4h)
- Observe os warnings

### Para Traders Intermediários
- Teste diferentes timeframes
- Compare risk/reward ratios
- Use stop loss manual
- Experimente leverage baixa (2-3x)

### Para Traders Avançados
- Optimize leverage baseado no stop
- Use calculadora de leverage
- Teste cenários extremos
- Analise preço de liquidação

---

## 🎯 Casos de Uso

### 1. Planejamento de Trade
```
Antes de entrar: Use o calculator para:
- Determinar position size ideal
- Validar se tem margem suficiente
- Calcular onde colocar stop/TP
- Ver risco real da operação
```

### 2. Educação
```
Para aprender: Teste diferentes cenários:
- O que acontece com leverage alta?
- Como o timeframe afeta o stop?
- Qual o impacto de riscar mais?
- Como funciona liquidação?
```

### 3. Comparação
```
Compare estratégias:
- Conservador vs Agressivo
- Com vs sem leverage
- Diferentes timeframes
- Vários risk/reward ratios
```

---

## 📊 Métricas Mostradas

### Principais
- Position Size (quantidade)
- Valor da Posição (USDT)
- Margem Necessária
- Risk/Reward Ratio

### Stop Loss
- Preço do stop
- Distância em %
- Risco em USDT
- Risco % da conta

### Take Profit
- Preço do TP
- Distância em %
- Lucro potencial

### Leverage (se ativado)
- Leverage utilizada
- Preço de liquidação
- Margem até liquidação

---

## ✅ Validações Automáticas

O sistema verifica automaticamente:
- ✅ Risk não excede limite (2%)
- ✅ Margem suficiente na conta
- ✅ Stop antes da liquidação (10% mínimo)
- ✅ Risk/reward mínimo (1.5:1)
- ✅ Position size dentro dos limites

---

## 🔗 Próximos Passos

Após testar a interface:
1. Experimente os exemplos Python
2. Leia a documentação completa
3. Teste com dados reais (API)
4. Integre com HyperLiquid

---

**💻 Para rodar agora:**
```bash
streamlit run web_demo.py
```

**🌐 Acesse:**
```
http://localhost:8501
```

---

© 2024 Sistema Trading Profissional
