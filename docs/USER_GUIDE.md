# 📖 Guia do Usuário - Sistema de Trading

Este guia completo ensina como usar todas as funcionalidades do Sistema Profissional de Trading.

## 🚀 Primeiros Passos

### 1. Iniciando o Sistema
```bash
python main.py
```

Você verá o menu principal com 4 opções:
- **Opção 1**: Interface Web (recomendada para iniciantes)
- **Opção 2**: Modo Headless (para usuários avançados)
- **Opção 3**: Instalar dependências
- **Opção 4**: Sair

### 2. Acessando a Interface Web
Escolha a opção 1 e acesse: `http://localhost:8501`

## 🎛️ Interface Principal

### Barra Lateral - Configurações
A barra lateral contém todos os controles principais:

#### 💾 Perfis de Configuração
- **Nome do Novo Perfil**: Digite um nome para salvar suas configurações
- **Carregar Perfil Existente**: Selecione um perfil salvo anteriormente
- **Botões**: Salvar Perfil | Carregar Perfil

#### ⚙️ Parâmetros Gerais
- **Ativo**: Símbolo do par de trading (ex: BTCUSDT, ETHUSDT)
- **Intervalo de Tempo**: Timeframe dos candles (1m, 5m, 15m, 1h, 4h, 1d)
- **Estratégia**: Escolha entre as estratégias disponíveis

#### 📈 Configuração de Estratégias

**RSI (Sobrecompra/venda)**
- **Período do RSI**: Janela de cálculo (padrão: 14)
- **Sobrecompra (%)**: Nível superior (padrão: 70)
- **Sobrevenda (%)**: Nível inferior (padrão: 30)

**Médias Móveis**
- **Média Curta**: Período da média rápida (padrão: 10)
- **Média Longa**: Período da média lenta (padrão: 50)

**IRF2 (Rompimento)**
- **Margem de rompimento**: Valor em USD para confirmar breakout

#### 🎛️ Indicadores no Gráfico
- **Preset de Indicadores**: Configurações pré-definidas
- **Indicadores Personalizados**: Selecione individualmente

### Área Principal - Resultados

#### 📉 Gráfico Candlestick
- Gráfico interativo com dados históricos
- Indicadores técnicos sobrepostos
- Marcadores de sinais de compra/venda
- Zoom e navegação temporal

#### 📊 Métricas de Performance
Após executar um backtest, você verá:
- **Total de Operações**: Número de trades executados
- **ROI**: Retorno sobre investimento em %
- **Taxa de Acerto**: Percentual de trades vencedores
- **Lucro Médio**: Ganho médio por trade vencedor
- **Prejuízo Médio**: Perda média por trade perdedor
- **Fator de Lucro**: Razão lucro total / perda total
- **Máximo Rebaixamento**: Maior perda consecutiva

## 📊 Estratégias de Trading

### 1. RSI (Relative Strength Index)

**Como Funciona:**
O RSI mede a velocidade e magnitude das mudanças de preço, oscilando entre 0 e 100.

**Sinais:**
- **Compra**: RSI sai da zona de sobrevenda (< 30) e sobe
- **Venda**: RSI sai da zona de sobrecompra (> 70) e desce

**Melhores Condições:**
- Mercados laterais ou com correções
- Timeframes menores (1h, 4h)
- Combine com outros indicadores

**Configuração Recomendada:**
```
Período: 14
Sobrecompra: 70
Sobrevenda: 30
```

### 2. Médias Móveis

**Como Funciona:**
Compara duas médias móveis de períodos diferentes para identificar tendências.

**Sinais:**
- **Compra**: Média curta cruza acima da média longa
- **Venda**: Média curta cruza abaixo da média longa

**Melhores Condições:**
- Mercados em tendência definida
- Timeframes maiores (4h, 1d)
- Evite em mercados laterais

**Configuração Recomendada:**
```
Média Curta: 10
Média Longa: 50
```

### 3. IRF2 (Rompimento)

**Como Funciona:**
Identifica rompimentos de máximas e mínimas anteriores com margem de segurança.

**Sinais:**
- **Compra**: Preço rompe máxima anterior + margem
- **Venda**: Preço rompe mínima anterior - margem

**Melhores Condições:**
- Mercados com volatilidade
- Breakouts de consolidações
- Timeframes médios (15m, 1h)

**Configuração Recomendada:**
```
Margem de rompimento: 1.0 USD
```

## 📈 Indicadores Técnicos

### EMA20 (Média Móvel Exponencial)
- **Uso**: Identificar direção da tendência
- **Cor**: Azul claro (#00bcd4)
- **Interpretação**: Preço acima = alta, abaixo = baixa

### RSI14 (Relative Strength Index)
- **Uso**: Identificar sobrecompra/sobrevenda
- **Cor**: Laranja (#ff9900)
- **Níveis**: 70 (sobrecompra), 30 (sobrevenda)

### MACD (Moving Average Convergence Divergence)
- **Uso**: Identificar mudanças de momentum
- **Cor**: Verde claro (#66ffcc)
- **Sinais**: Cruzamentos da linha zero

### Bollinger Bands
- **Uso**: Medir volatilidade e suporte/resistência
- **Cor**: Azul claro (#9999ff)
- **Componentes**: Banda superior e inferior

### ATR (Average True Range)
- **Uso**: Medir volatilidade do ativo
- **Cor**: Roxo (#cc66ff)
- **Aplicação**: Definir stop-loss e take-profit

### VWAP (Volume Weighted Average Price)
- **Uso**: Preço médio ponderado por volume
- **Cor**: Amarelo (#ffcc00)
- **Interpretação**: Referência de valor justo

### Volume
- **Uso**: Confirmar movimentos de preço
- **Cor**: Amarelo escuro (#cccc00)
- **Análise**: Volume alto = movimento forte

## 💾 Sistema de Perfis

### Criando um Perfil
1. Configure todos os parâmetros desejados
2. Digite um nome no campo "Nome do Novo Perfil"
3. Clique em "💾 Salvar Perfil"

### Carregando um Perfil
1. Selecione o perfil na lista "Carregar Perfil Existente"
2. Clique em "🔁 Carregar Perfil"
3. A página será recarregada com as configurações

### Exemplos de Perfis

**Perfil Conservador:**
```
Nome: Conservador_RSI
Estratégia: RSI
Período: 21
Sobrecompra: 75
Sobrevenda: 25
Timeframe: 4h
```

**Perfil Agressivo:**
```
Nome: Agressivo_MA
Estratégia: Médias Móveis
Média Curta: 5
Média Longa: 20
Timeframe: 15m
```

## 🚀 Executando Backtests

### Passo a Passo
1. **Configure os Parâmetros**: Escolha ativo, timeframe e estratégia
2. **Ajuste a Estratégia**: Defina os parâmetros específicos
3. **Selecione Indicadores**: Escolha quais indicadores exibir no gráfico
4. **Execute**: Clique em "🚀 Executar Backtest"
5. **Analise Resultados**: Examine gráfico e métricas

### Interpretando Resultados

**ROI (Return on Investment)**
- Positivo: Estratégia lucrativa
- Negativo: Estratégia com perdas
- Meta: > 10% anual

**Taxa de Acerto**
- > 60%: Excelente
- 50-60%: Boa
- < 50%: Revisar estratégia

**Fator de Lucro**
- > 2.0: Excelente
- 1.5-2.0: Bom
- < 1.0: Prejuízo

**Máximo Drawdown**
- < 10%: Baixo risco
- 10-20%: Risco moderado
- > 20%: Alto risco

## 📤 Exportando Resultados

### Formatos Disponíveis
Após executar um backtest, você pode baixar:

**Arquivo ZIP contendo:**
- **resultado.csv**: Dados tabulares das métricas
- **relatorio.pdf**: Relatório formatado em PDF

### Usando os Dados Exportados
- **CSV**: Abra no Excel ou Google Sheets para análise
- **PDF**: Compartilhe relatórios com outros traders
- **Backup**: Mantenha histórico de backtests

## 🟢 Trading ao Vivo (Beta)

### Ativando o Modo ao Vivo
1. Na barra lateral, encontre "🟢 Operação ao Vivo (Beta)"
2. Clique em "Iniciar Modo ao Vivo"
3. O sistema iniciará em segundo plano

### Monitoramento
- Expanda "📡 Monitor Ao Vivo"
- Visualize as últimas 20 operações simuladas
- Use "⛔ Parar Modo Ao Vivo" para encerrar

**⚠️ Aviso**: Esta é uma versão beta com operações simuladas.

## 🤖 Modo Headless

### Quando Usar
- Automação de backtests
- Execução em servidores
- Integração com outros sistemas
- Processamento em lote

### Como Usar
```bash
python main.py
# Escolha opção 2

# Ou diretamente:
python visualization/ui_headless.py
```

### Funcionalidades
- Lista perfis disponíveis
- Executa backtest automaticamente
- Exibe resultados no terminal
- Ideal para scripts automatizados

## 🔧 Configurações Avançadas

### Personalizando Timeframes
Edite `config/config.py`:
```python
TIMEFRAME_OPTIONS = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]
```

### Adicionando Novos Presets
```python
INDICATOR_PRESETS = {
    "Meu Setup": ["EMA20", "RSI14", "VOLUME"],
    "Scalping": ["EMA20", "MACD"],
    "Swing Trade": ["BBANDS", "ATR", "VWAP"]
}
```

### Configurando Alertas
Crie arquivo `.env`:
```env
EMAIL_SENDER=seu@email.com
EMAIL_PASSWORD=sua_senha_app
EMAIL_RECEIVER=destino@email.com
```

## 📊 Dicas de Uso

### Melhores Práticas
1. **Teste Múltiplos Timeframes**: Mesmo setup em diferentes períodos
2. **Combine Estratégias**: Use indicadores complementares
3. **Analise Drawdown**: Considere o risco máximo aceitável
4. **Backteste Períodos Diferentes**: Bull market, bear market, lateral
5. **Mantenha Registros**: Salve perfis de setups promissores

### Otimização de Estratégias
1. **Varie Parâmetros**: Teste diferentes configurações
2. **Analise Correlações**: Evite indicadores redundantes
3. **Considere Custos**: Inclua spread e taxas na análise
4. **Valide em Dados Recentes**: Teste em períodos não utilizados no desenvolvimento

### Gestão de Risco
1. **Defina Stop-Loss**: Use ATR para calcular
2. **Position Sizing**: Não arrisque mais que 2% por trade
3. **Diversificação**: Teste em múltiplos ativos
4. **Revisão Periódica**: Reavalie estratégias mensalmente

## 🆘 Solução de Problemas

### Gráfico Não Carrega
- Verifique conexão com internet
- Recarregue a página (F5)
- Teste com ativo diferente

### Dados Insuficientes
- Escolha timeframe menor
- Selecione período mais recente
- Verifique se o ativo existe

### Performance Lenta
- Reduza número de indicadores
- Use timeframes maiores
- Feche outras abas do navegador

### Erro de Conexão
- Verifique firewall
- Teste porta diferente: `--server.port 8502`
- Reinicie o sistema

---

**🎯 Parabéns! Você está pronto para usar o Sistema de Trading**

Lembre-se:
- Comece com backtests
- Teste em conta demo
- Nunca arrisque mais do que pode perder
- Trading envolve riscos significativos

Para suporte adicional, consulte a documentação técnica ou entre em contato através do repositório.

