import pandas as pd
import ta
from indicators.base_indicator import BaseIndicator

class ATRIndicator(BaseIndicator):
    def __init__(self, window=14):
        self.window = window

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=self.window).round(2)


