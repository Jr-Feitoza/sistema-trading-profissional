import pandas as pd
import ta
from indicators.base_indicator import BaseIndicator

class VWAPIndicator(BaseIndicator):
    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return ta.volume.volume_weighted_average_price(df["high"], df["low"], df["close"], df["volume"]).round(2)


