import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategies.irf2_strategy import IRF2Strategy
from strategies.rsi_strategy import RSIStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from connectors.binance_connector import BinanceConnector
from engine.backtest_engine import BacktestEngine
from engine.order_manager import OrderManager
from engine.execution_result import ExecutionResult
from visualization.tv_chart.chart import render_tv_chart
from config.config import INDICATOR_PRESETS, TIMEFRAME_OPTIONS, INDICADORES_DISPONIVEIS
from utils.profile_manager import salvar_perfil, carregar_perfil, listar_perfis
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import pandas as pd
import zipfile
from live_trading.live_launcher import run_in_background, stop_live_process

st.set_page_config(page_title="Backtest de Estratégias", layout="wide")
st.title("📊 Plataforma de Backtest com Perfis Personalizados")

# ========== Perfis de Setup ==========
with st.sidebar:
    st.subheader("💾 Perfis de Configuração")
    nome_novo_perfil = st.text_input("🔖 Nome do Novo Perfil")
    perfis_disponiveis = listar_perfis()
    perfil_selecionado = st.selectbox("📁 Carregar Perfil Existente", perfis_disponiveis if perfis_disponiveis else ["Nenhum"])
    col_salvar, col_carregar = st.columns(2)

# ========== Parâmetros Gerais ==========
with st.sidebar:
    st.header("⚙️ Parâmetros Gerais")
    symbol = st.text_input("Ativo (ex: BTCUSDT)", value="BTCUSDT")
    timeframe = st.selectbox("Intervalo de Tempo", TIMEFRAME_OPTIONS, index=2)

    estrategia_nome = st.selectbox("📈 Estratégia", [
        "IRF2 (Rompimento)",
        "RSI (Sobrecompra/venda)",
        "Médias Móveis"
    ])

    parametros = {}

    if estrategia_nome == "IRF2 (Rompimento)":
        margin = st.slider("Margem de rompimento (USD)", 0.1, 10.0, 1.0, 0.1)
        strategy = IRF2Strategy(breakout_margin=margin)
        parametros = {"margin": margin}

    elif estrategia_nome == "RSI (Sobrecompra/venda)":
        period = st.slider("Período do RSI", 5, 30, 14)
        overbought = st.slider("Sobrecompra (%)", 60, 90, 70)
        oversold = st.slider("Sobrevenda (%)", 10, 40, 30)
        strategy = RSIStrategy(period=period, overbought=overbought, oversold=oversold)
        parametros = {"period": period, "overbought": overbought, "oversold": oversold}

    elif estrategia_nome == "Médias Móveis":
        short = st.slider("Média Curta", 5, 50, 10)
        long = st.slider("Média Longa", 10, 200, 50)
        strategy = MovingAverageStrategy(short_window=short, long_window=long)
        parametros = {"short_window": short, "long_window": long}

    preset = st.selectbox("🎛️ Preset de Indicadores", list(INDICATOR_PRESETS.keys()), index=0)
    overlays = st.multiselect("📊 Indicadores no Gráfico", INDICADORES_DISPONIVEIS, default=INDICATOR_PRESETS[preset])

    # 🔘 Ações de perfil
    if col_salvar.button("💾 Salvar Perfil") and nome_novo_perfil:
        dados_perfil = {
            "symbol": symbol,
            "timeframe": timeframe,
            "estrategia": estrategia_nome,
            "parametros": parametros,
            "overlays": overlays
        }
        salvar_perfil(nome_novo_perfil, dados_perfil)
        st.success(f"Perfil '{nome_novo_perfil}' salvo com sucesso.")

    if col_carregar.button("🔁 Carregar Perfil") and perfil_selecionado and perfil_selecionado != "Nenhum":
        perfil = carregar_perfil(perfil_selecionado)
        if perfil:
            st.rerun()

    executar = st.button("🚀 Executar Backtest")

# ==============================
# EXECUÇÃO DO BACKTEST
# ==============================
trades = []
metricas = {}
df = pd.DataFrame()
data_loader = BinanceConnector()

if executar:
    order_manager = OrderManager(mode="backtest")
    engine = BacktestEngine(strategy, data_loader, order_manager)
    with st.spinner("Executando estratégia e preparando gráfico..."):
        df = data_loader.load_historical_data(symbol=symbol, interval=timeframe)
        engine.data_loader.load_historical_data = lambda: df
        resultado = engine.run()
        trades = resultado.trades
        metricas = resultado.calculate_metrics()

# ==============================
# RENDERIZAÇÃO NO TV Chart
# ==============================
if not df.empty:
    st.subheader("📉 Gráfico Candlestick com Sinais (TV Chart)")
    render_tv_chart(df=df, trades=trades, overlays=overlays, timeframe=timeframe)

# ==============================
# MÉTRICAS DO BACKTEST
# ==============================
if metricas:
    st.subheader("📊 Indicadores de Desempenho")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Operações", f"{metricas['total_trades']}")
    col2.metric("ROI", f"{metricas['roi'] * 100:.2f}%")
    col3.metric("Taxa de Acerto", f"{metricas['win_rate']:.2f}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("Lucro Médio", f"${metricas['average_gain']:.2f}")
    col5.metric("Prejuízo Médio", f"${metricas['average_loss']:.2f}")
    col6.metric("Fator de Lucro", f"{metricas['profit_factor']:.2f}")

    st.metric("Máximo Rebaixamento", f"{metricas['max_drawdown'] * 100:.2f}%")

    st.divider()
    st.subheader("📤 Exportar Resultados")
    df_csv = pd.DataFrame([metricas])
    csv_bytes = df_csv.to_csv(index=False).encode()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=f"Relatório de Backtest - {estrategia_nome}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    nomes_pt = {
        "total_trades": "Total de Operações",
        "roi": "Retorno sobre Investimento",
        "win_rate": "Taxa de Acerto",
        "average_gain": "Lucro Médio",
        "average_loss": "Prejuízo Médio",
        "profit_factor": "Fator de Lucro",
        "max_drawdown": "Máximo Rebaixamento"
    }
    for key, value in metricas.items():
        if key in nomes_pt:
            pdf.cell(80, 10, txt=nomes_pt[key], border=1)
            pdf.cell(110, 10, txt=str(value), border=1, ln=1)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("resultado.csv", csv_bytes)
        zf.writestr("relatorio.pdf", pdf_bytes)
    st.download_button("📁 Baixar Resultados (.zip)", data=zip_buffer.getvalue(), file_name="backtest_resultado.zip")

# ==============================
# LIVE TRADING (opcional)
# ==============================
with st.sidebar:
    st.markdown("---")
    st.subheader("🟢 Operação ao Vivo (Beta)")
    if st.button("Iniciar Modo ao Vivo"):
        p = run_in_background()
        st.success("Modo ao vivo iniciado em segundo plano!")

with st.expander("📡 Monitor Ao Vivo (Simulação de Ordens)", expanded=False):
    log_path = "live_logs/orders.csv"
    if os.path.exists(log_path):
        df_orders = pd.read_csv(log_path)
        st.dataframe(df_orders.tail(20), use_container_width=True)
    else:
        st.info("Nenhuma ordem executada ainda.")
    if st.button("⛔ Parar Modo Ao Vivo"):
        sucesso = stop_live_process()
        if sucesso:
            st.success("Modo ao vivo encerrado com sucesso.")
        else:
            st.error("Falha ao encerrar o modo ao vivo.")


