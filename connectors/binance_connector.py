from binance.client import Client
import pandas as pd
import random
from datetime import datetime

class BinanceConnector:
    def __init__(self, api_key=None, api_secret=None):
        """
        Inicializa o conector da Binance.
        Se nenhuma chave for fornecida, opera em modo simulação.
        """
        if api_key and api_secret:
            self.client = Client(api_key, api_secret)
        else:
            self.client = None  # Modo simulação / backtest

    def load_historical_data(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1h",
        start_time: datetime = None,
        end_time: datetime = None
    ) -> pd.DataFrame:
        """
        Simula o carregamento de dados históricos para um determinado ativo e intervalo.
        """
        print(
            f"Simulando carregamento de dados históricos para {symbol} - "
            f"intervalo: {interval}"
        )

        if start_time is None:
            start_time = datetime.now()

        freq_map = {
            "1m": "T", "5m": "5T", "15m": "15T", "30m": "30T",
            "1h": "H", "4h": "4H", "1d": "D"
        }

        pandas_freq = freq_map.get(interval)
        if not pandas_freq:
            raise ValueError(f"Intervalo '{interval}' não suportado.")

        if end_time:
            dates = pd.date_range(end=end_time, periods=100, freq=pandas_freq)
        else:
            dates = pd.date_range(start=start_time, periods=100, freq=pandas_freq)

        base_price = 30000
        data = {
            "open": [base_price + random.uniform(-1000, 1000) for _ in range(100)],
            "high": [base_price + random.uniform(0, 1500) for _ in range(100)],
            "low": [base_price + random.uniform(-1500, 0) for _ in range(100)],
            "close": [base_price + random.uniform(-1000, 1000) for _ in range(100)],
            "volume": [random.uniform(100, 1000) for _ in range(100)],
        }

        df = pd.DataFrame(data, index=dates)
        df.index.name = "timestamp"
        return df

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> dict:
        """
        Simula a colocação de uma ordem de compra ou venda.
        """
        print(f"Simulando ordem: {side} {quantity} {symbol} a {price}")
        return {
            "orderId": "simulated_order_123",
            "status": "FILLED"
        }

    def get_account_balance(self) -> dict:
        """
        Retorna saldo simulado da conta.
        """
        print("Simulando saldo da conta")
        return {
            "USDT": 10000,
            "BTC": 0.5
        }

    def get_current_price(self, symbol: str) -> float:
        """
        Retorna o preço atual simulado do ativo.
        """
        print(f"Simulando preço atual para {symbol}")
        return random.uniform(30000, 35000)
