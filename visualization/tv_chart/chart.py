from lightweight_charts import Chart
import streamlit.components.v1 as components
import pandas as pd
import ta
import sys
import os

# Adicionar o diretório pai ao path para importar os indicadores
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from indicators.ema_indicator import EMAIndicator
from indicators.rsi_indicator import RSIIndicator
from indicators.macd_indicator import MACDIndicator
from indicators.bbands_indicator import BBANDSIndicator
from indicators.volume_indicator import VolumeIndicator
from indicators.atr_indicator import ATRIndicator
from indicators.vwap_indicator import VWAPIndicator

def df_to_candles(df: pd.DataFrame) -> list:
    """Converte DataFrame para formato de candlesticks do lightweight-charts"""
    candles = []
    for idx, row in df.iterrows():
        # Converter timestamp para formato Unix
        if isinstance(idx, pd.Timestamp):
            timestamp = int(idx.timestamp())
        else:
            timestamp = int(pd.to_datetime(idx).timestamp())
        
        candles.append({
            "time": timestamp,
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
        })
    return candles

def trades_to_markers(trades: list[dict]) -> list:
    """Converte trades para marcadores no gráfico"""
    markers = []
    for trade in trades:
        timestamp = trade["timestamp"]
        if isinstance(timestamp, pd.Timestamp):
            time_unix = int(timestamp.timestamp())
        else:
            time_unix = int(pd.to_datetime(timestamp).timestamp())
        
        action = trade["action"]
        price = float(trade["price"])
        
        # Definir cor e posição baseado na ação
        if action in ["buy", "cover"]:
            color = "#00ff00"  # Verde para compra
            position = "belowBar"
            shape = "arrowUp"
        else:  # sell, short
            color = "#ff0000"  # Vermelho para venda
            position = "aboveBar"
            shape = "arrowDown"
        
        markers.append({
            "time": time_unix,
            "position": position,
            "color": color,
            "shape": shape,
            "text": f"{action.upper()} @{price:.2f}"
        })
    return markers

def compute_indicators(df: pd.DataFrame, selected: list) -> dict:
    """Calcula indicadores selecionados"""
    df = df.copy()
    indicators = {}

    if "EMA20" in selected:
        ema_indicator = EMAIndicator(window=20)
        df["EMA20"] = ema_indicator.calculate(df)
        indicators["EMA20"] = {"data": df[["EMA20"]], "color": "#00bcd4"}

    if "RSI14" in selected:
        rsi_indicator = RSIIndicator(window=14)
        df["RSI14"] = rsi_indicator.calculate(df)
        indicators["RSI14"] = {"data": df[["RSI14"]], "color": "#ff9900"}

    if "MACD" in selected:
        macd_indicator = MACDIndicator()
        df["MACD"] = macd_indicator.calculate(df)
        indicators["MACD"] = {"data": df[["MACD"]], "color": "#66ffcc"}

    if "BBANDS" in selected:
        bbands_indicator = BBANDSIndicator(window=20)
        bb_df = bbands_indicator.calculate(df)
        df["BB_H"] = bb_df["BB_H"]
        df["BB_L"] = bb_df["BB_L"]
        indicators["BB_H"] = {"data": df[["BB_H"]], "color": "#9999ff"}
        indicators["BB_L"] = {"data": df[["BB_L"]], "color": "#9999ff"}

    if "VOLUME" in selected and "volume" in df.columns:
        volume_indicator = VolumeIndicator()
        df["VOLUME"] = volume_indicator.calculate(df)
        indicators["VOLUME"] = {"data": df[["VOLUME"]], "color": "#cccc00"}

    if "ATR" in selected:
        atr_indicator = ATRIndicator(window=14)
        df["ATR"] = atr_indicator.calculate(df)
        indicators["ATR"] = {"data": df[["ATR"]], "color": "#cc66ff"}

    if "VWAP" in selected:
        vwap_indicator = VWAPIndicator()
        df["VWAP"] = vwap_indicator.calculate(df)
        indicators["VWAP"] = {"data": df[["VWAP"]], "color": "#ffcc00"}

    return indicators

def add_indicator_line(chart: Chart, df: pd.DataFrame, indicator_name: str, color: str = "#888"):
    """Adiciona uma linha de indicador ao gráfico"""
    line_data = []
    for idx, row in df.iterrows():
        if pd.notna(row[indicator_name]):
            if isinstance(idx, pd.Timestamp):
                timestamp = int(idx.timestamp())
            else:
                timestamp = int(pd.to_datetime(idx).timestamp())
            
            line_data.append({
                "time": timestamp,
                "value": float(row[indicator_name])
            })
    
    if line_data:
        line = chart.create_line(color=color, width=2)
        line.set(line_data)

def render_tv_chart(df: pd.DataFrame, trades: list = None, overlays: list = None, timeframe: str = "15m"):
    """Renderiza o gráfico TradingView usando lightweight-charts"""
    try:
        # Criar o gráfico
        chart = Chart(
            width=800,
            height=600,
            toolbox=True,
            debug=False
        )
        
        # Configurar título
        chart.topbar.textbox('symbol', f'Trading Chart - {timeframe}')
        
        # Adicionar dados de candlestick
        candles = df_to_candles(df)
        chart.set(candles)
        
        # Adicionar marcadores de trades se existirem
        if trades and len(trades) > 0:
            markers = trades_to_markers(trades)
            chart.marker(markers)
        
        # Adicionar indicadores se selecionados
        if overlays:
            indicators = compute_indicators(df, overlays)
            for name, info in indicators.items():
                indicator_df = info["data"]
                color = info.get("color", "#888")
                
                # Criar dados para a linha do indicador
                line_data = []
                for idx, row in indicator_df.iterrows():
                    if pd.notna(row.iloc[0]):  # Primeira coluna do DataFrame do indicador
                        if isinstance(idx, pd.Timestamp):
                            timestamp = int(idx.timestamp())
                        else:
                            timestamp = int(pd.to_datetime(idx).timestamp())
                        
                        line_data.append({
                            "time": timestamp,
                            "value": float(row.iloc[0])
                        })
                
                if line_data:
                    line = chart.create_line(color=color, width=2)
                    line.set(line_data)
        
        # Renderizar no Streamlit
        chart_html = chart.render()
        components.html(chart_html, height=650)
        
    except Exception as e:
        st.error(f"Erro ao renderizar gráfico: {str(e)}")
        # Fallback para gráfico simples usando plotly
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        )])
        
        fig.update_layout(
            title=f'Candlestick Chart - {timeframe}',
            xaxis_title='Time',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)

