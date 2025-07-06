import pandas as pd
import ta
from indicators.base_indicator import BaseIndicator

class RSIIndicator(BaseIndicator):
    def __init__(self, window=14):
        self.window = window

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return ta.momentum.rsi(df["close"], window=self.window).round(2)


