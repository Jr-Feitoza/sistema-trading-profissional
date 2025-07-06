# 📊 Sistema Profissional de Trading

Um sistema completo e profissional de trading desenvolvido em Python, focado em testes de estratégias, emissão de sinais e análise técnica para traders de varejo.

## 🎯 Características Principais

- **Backtesting Avançado**: Engine robusto com suporte a slippage e custos de corretagem
- **Múltiplas Estratégias**: RSI, Médias Móveis, IRF2 (Rompimento) e mais
- **Indicadores Técnicos**: EMA, RSI, MACD, Bollinger Bands, ATR, VWAP, Volume
- **Interface Moderna**: Interface web com Streamlit e gráficos TradingView
- **Modo Headless**: Execução via linha de comando para automação
- **Sistema de Alertas**: Notificações por e-mail e Telegram
- **Gerenciamento de Perfis**: Salve e carregue configurações personalizadas

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação
```bash
# Clone o repositório
git clone <seu-repositorio>
cd sistema-trading

# Instale as dependências
pip install -r requirements.txt

# Execute o sistema
python main.py
```

## 📖 Guia de Uso

### 1. Interface Web (Recomendado)
```bash
python main.py
# Escolha opção 1 para interface web
# Acesse: http://localhost:8501
```

### 2. Modo Headless (Linha de Comando)
```bash
python main.py
# Escolha opção 2 para modo headless
```

### 3. Execução Direta
```bash
# Interface web
streamlit run visualization/ui.py

# Modo headless
python visualization/ui_headless.py
```

## 🏗️ Arquitetura do Sistema

```
sistema-trading/
├── config/                 # Configurações do sistema
├── connectors/             # Conectores para exchanges
├── engine/                 # Motor de backtesting
├── indicators/             # Indicadores técnicos
├── strategies/             # Estratégias de trading
├── utils/                  # Utilitários e helpers
├── visualization/          # Interfaces de usuário
├── live_trading/           # Trading ao vivo
├── tests/                  # Testes unitários
└── docs/                   # Documentação
```

## 📊 Estratégias Disponíveis

### 1. RSI (Relative Strength Index)
- **Descrição**: Estratégia baseada em sobrecompra/sobrevenda
- **Parâmetros**: Período, níveis de sobrecompra e sobrevenda
- **Uso**: Ideal para mercados laterais

### 2. Médias Móveis
- **Descrição**: Cruzamento de médias móveis simples
- **Parâmetros**: Período da média curta e longa
- **Uso**: Eficaz em tendências definidas

### 3. IRF2 (Rompimento)
- **Descrição**: Estratégia de rompimento de máximas/mínimas
- **Parâmetros**: Margem de rompimento
- **Uso**: Captura movimentos de breakout

## 🔧 Configuração Avançada

### Conectores de Exchange
O sistema suporta múltiplas exchanges através de conectores modulares:

```python
from connectors.binance_connector import BinanceConnector

# Configurar conector
connector = BinanceConnector()
data = connector.load_historical_data("BTCUSDT", "1h")
```

### Criando Estratégias Personalizadas
```python
from strategies.base_strategy import BaseStrategy

class MinhaEstrategia(BaseStrategy):
    def generate_signals(self, df):
        df["signal"] = 0
        # Sua lógica aqui
        return df
```

### Adicionando Indicadores
```python
from indicators.base_indicator import BaseIndicator

class MeuIndicador(BaseIndicator):
    def calculate(self, df):
        # Sua lógica de cálculo
        return resultado
```

## 📈 Métricas de Performance

O sistema calcula automaticamente:

- **ROI (Return on Investment)**: Retorno sobre investimento
- **Taxa de Acerto**: Percentual de trades vencedores
- **Fator de Lucro**: Razão entre lucros e perdas
- **Máximo Drawdown**: Maior perda consecutiva
- **Lucro/Prejuízo Médio**: Médias de ganhos e perdas

## 🔔 Sistema de Alertas

### Configuração de E-mail
```python
email_config = {
    "sender_email": "seu@email.com",
    "sender_password": "sua_senha",
    "receiver_email": "destino@email.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}
```

### Alertas em Tempo Real
O sistema pode enviar alertas quando:
- Novos sinais são gerados
- Metas de lucro são atingidas
- Stop-loss é acionado

## 🧪 Testes

Execute os testes unitários:
```bash
python -m unittest discover tests/ -v
```

Testes disponíveis:
- Estratégias de trading
- Indicadores técnicos
- Engine de backtesting
- Conectores de dados

## 📊 Gráficos e Visualização

### TradingView Charts
O sistema utiliza a biblioteca `lightweight-charts-python` para gráficos profissionais:
- Candlesticks interativos
- Indicadores sobrepostos
- Marcadores de sinais
- Zoom e navegação

### Exportação de Resultados
- **CSV**: Dados tabulares para análise
- **PDF**: Relatórios formatados
- **ZIP**: Pacote completo de resultados

## 🔒 Segurança e Boas Práticas

- **Nunca** commite chaves de API
- Use variáveis de ambiente para credenciais
- Teste sempre em ambiente de simulação primeiro
- Mantenha backups de configurações importantes

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação em `docs/`
- Verifique os exemplos em `examples/`

## 🔄 Atualizações

### Versão 1.0.0
- Sistema base de backtesting
- Estratégias RSI, MA e IRF2
- Interface web com Streamlit
- Gráficos TradingView
- Sistema de perfis

### Próximas Versões
- Mais estratégias de trading
- Suporte a mais exchanges
- Trading ao vivo automatizado
- Machine Learning integrado
- API REST para integração

---

**Desenvolvido com ❤️ para a comunidade de traders**

