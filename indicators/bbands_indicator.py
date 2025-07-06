import pandas as pd
import ta
from indicators.base_indicator import BaseIndicator

class BBANDSIndicator(BaseIndicator):
    def __init__(self, window=20):
        self.window = window

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        bb = ta.volatility.BollingerBands(df["close"], window=self.window)
        df["BB_H"] = bb.bollinger_hband().round(2)
        df["BB_L"] = bb.bollinger_lband().round(2)
        return df[["BB_H", "BB_L"]]


