import pandas as pd
import ta
from indicators.base_indicator import BaseIndicator

class MACDIndicator(BaseIndicator):
    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return ta.trend.macd_diff(df["close"]).round(2)


