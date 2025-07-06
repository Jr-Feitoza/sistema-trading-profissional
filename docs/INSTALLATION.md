# 🛠️ Guia de Instalação Detalhado

Este guia fornece instruções passo a passo para instalar e configurar o Sistema Profissional de Trading.

## 📋 Pré-requisitos

### Sistema Operacional
- **Windows**: 10 ou superior
- **macOS**: 10.14 ou superior  
- **Linux**: Ubuntu 18.04+ ou distribuições equivalentes

### Software Necessário
- **Python**: 3.8 ou superior (recomendado 3.9+)
- **pip**: Gerenciador de pacotes Python (incluído com Python)
- **Git**: Para clonagem do repositório (opcional)

## 🔧 Instalação do Python

### Windows
1. Baixe Python em [python.org](https://python.org)
2. Execute o instalador
3. ✅ **IMPORTANTE**: Marque "Add Python to PATH"
4. Verifique a instalação:
```cmd
python --version
pip --version
```

### macOS
```bash
# Usando Homebrew (recomendado)
brew install python

# Ou baixe diretamente de python.org
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## 📦 Instalação do Sistema

### Método 1: Download Direto
1. Baixe o código fonte
2. Extraia para uma pasta de sua escolha
3. Abra terminal/prompt na pasta

### Método 2: Git Clone
```bash
git clone <url-do-repositorio>
cd sistema-trading
```

## 🐍 Configuração do Ambiente Virtual (Recomendado)

### Criar Ambiente Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Verificar Ativação
Você deve ver `(venv)` no início da linha do terminal.

## 📚 Instalação de Dependências

### Instalação Automática
```bash
pip install -r requirements.txt
```

### Instalação Manual (se necessário)
```bash
pip install streamlit>=1.28.0
pip install pandas>=1.5.0
pip install ta>=0.10.2
pip install lightweight-charts>=1.0.0
pip install plotly>=5.15.0
pip install fpdf2>=2.7.0
pip install python-binance>=1.0.16
```

## ✅ Verificação da Instalação

### Teste Rápido
```bash
python main.py
```

Você deve ver o menu principal:
```
🚀 Sistema Profissional de Trading
==================================================
1. Interface Web (Streamlit)
2. Modo Headless (Linha de comando)
3. Instalar dependências
4. Sair
==================================================
```

### Teste dos Módulos
```bash
python -c "import streamlit, pandas, ta; print('✅ Módulos principais OK')"
```

### Executar Testes Unitários
```bash
python -m unittest discover tests/ -v
```

## 🔧 Configuração Inicial

### 1. Configurar Conectores de Exchange

Crie um arquivo `.env` na raiz do projeto:
```env
# Binance API (opcional - para dados ao vivo)
BINANCE_API_KEY=sua_chave_aqui
BINANCE_SECRET_KEY=sua_chave_secreta_aqui

# Configurações de E-mail (opcional - para alertas)
EMAIL_SENDER=seu@email.com
EMAIL_PASSWORD=sua_senha_app
EMAIL_RECEIVER=destino@email.com
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

### 2. Testar Interface Web
```bash
streamlit run visualization/ui.py
```

Acesse: http://localhost:8501

### 3. Testar Modo Headless
```bash
python visualization/ui_headless.py
```

## 🚨 Solução de Problemas

### Erro: "Module not found"
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt

# Verificar ambiente virtual ativo
which python  # Linux/macOS
where python  # Windows
```

### Erro: "Permission denied"
```bash
# Linux/macOS
sudo pip install -r requirements.txt

# Ou usar --user
pip install --user -r requirements.txt
```

### Erro: "Port already in use"
```bash
# Usar porta diferente
streamlit run visualization/ui.py --server.port 8502
```

### Erro: "SSL Certificate"
```bash
# Atualizar certificados
pip install --upgrade certifi

# Ou usar --trusted-host
pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
```

## 🔄 Atualizações

### Atualizar Sistema
```bash
git pull origin main  # Se usando Git
pip install --upgrade -r requirements.txt
```

### Verificar Versões
```bash
pip list | grep -E "(streamlit|pandas|ta)"
```

## 🐳 Instalação com Docker (Avançado)

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "visualization/ui.py", "--server.address", "0.0.0.0"]
```

### Comandos Docker
```bash
# Build
docker build -t sistema-trading .

# Run
docker run -p 8501:8501 sistema-trading
```

## 📱 Instalação em Diferentes Ambientes

### Google Colab
```python
!pip install streamlit ta lightweight-charts plotly fpdf2
!git clone <url-repositorio>
%cd sistema-trading
!python main.py
```

### Jupyter Notebook
```python
import sys
!{sys.executable} -m pip install -r requirements.txt
```

### Replit
1. Importe o repositório
2. Execute: `pip install -r requirements.txt`
3. Configure run command: `python main.py`

## 🔐 Configurações de Segurança

### Variáveis de Ambiente
```bash
# Linux/macOS
export BINANCE_API_KEY="sua_chave"

# Windows
set BINANCE_API_KEY=sua_chave
```

### Arquivo .gitignore
```
.env
*.pyc
__pycache__/
venv/
.vscode/
profiles.json
```

## 📊 Configuração de Performance

### Para Datasets Grandes
```bash
# Aumentar memória do Streamlit
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=1000

# Configurar pandas
export PANDAS_COMPUTE_BACKEND=threading
```

### Otimizações
```python
# No código Python
import pandas as pd
pd.set_option('compute.use_bottleneck', True)
pd.set_option('compute.use_numexpr', True)
```

## 🆘 Suporte Adicional

### Logs de Debug
```bash
# Executar com logs detalhados
python -v main.py

# Streamlit com debug
streamlit run visualization/ui.py --logger.level debug
```

### Verificação do Sistema
```bash
python -c "
import sys
print(f'Python: {sys.version}')
print(f'Platform: {sys.platform}')
import pandas as pd
print(f'Pandas: {pd.__version__}')
"
```

---

**✅ Instalação concluída com sucesso!**

Próximos passos:
1. Execute `python main.py`
2. Escolha a interface web (opção 1)
3. Crie seu primeiro perfil de trading
4. Execute seu primeiro backtest

Para dúvidas, consulte a documentação completa em `docs/` ou abra uma issue no repositório.

