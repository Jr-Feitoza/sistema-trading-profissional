import pandas as pd
import ta
from indicators.base_indicator import BaseIndicator

class EMAIndicator(BaseIndicator):
    def __init__(self, window=20):
        self.window = window

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return ta.trend.ema_indicator(df["close"], window=self.window).round(2)


