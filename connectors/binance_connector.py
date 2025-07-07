from binance.client import Client
import pandas as pd
import random
from datetime import datetime

class BinanceConnector:
    def __init__(self, api_key=None, api_secret=None):
        # Para backtest, as chaves não são necessárias
        if api_key and api_secret:
            self.client = Client(api_key, api_secret)
        else:
            self.client = None  # Modo simulação

    def load_historical_data(
        self,
        symbol="BTCUSDT",
        interval="1h",
        start_time=None,
        end_time=None
    ):
        # Simula o carregamento de dados históricos para backtest
        print(
            f"Simulando carregamento de dados históricos para {symbol} - "
            f"intervalo: {interval}"
        )

        # Define start_time padrão se não fornecido
        if start_time is None:
            start_time = datetime.now()

        # Traduz o intervalo para o formato compatível com pandas
        freq_map = {
            "1m": "T",    # minuto
            "5m": "5T",
            "15m": "15T",
            "30m": "30T",
            "1h": "H",
            "4h": "4H",
            "1d": "D"
        }

        pandas_freq = freq_map.get(interval, "H")  # Fallback = 1 hora

        # Gerar range de datas
        dates = pd.date_range(start=start_time, periods=100, freq=pandas_freq)

        # Gerar dados simulados
        data = {
            'open': [i + random.uniform(-5, 5) for i in range(100, 200)],
            'high': [i + random.uniform(0, 10) for i in range(100, 200)],
            'low': [i + random.uniform(-10, 0) for i in range(100, 200)],
            'close': [i + random.uniform(-5, 5) for i in range(100, 200)],
            'volume': [random.uniform(100, 1000) for _ in range(100)]
        }

        df = pd.DataFrame(data, index=dates)
        df.index.name = 'timestamp'
        return df

    def place_order(self, symbol, side, order_type, quantity, price=None):
        # Simula a colocação de uma ordem
        print(f"Simulando ordem: {side} {quantity} {symbol} a {price}")
        # Em ambiente real: self.client.create_order(...)
        return {"orderId": "simulated_order_123", "status": "FILLED"}

    def get_account_balance(self):
        # Simula o saldo da conta
        print("Simulando saldo da conta")
        return {"USDT": 10000, "BTC": 0.5}

    def get_current_price(self, symbol):
        # Simula o preço atual do ativo
        print(f"Simulando preço atual para {symbol}")
        return random.uniform(30000, 35000)
