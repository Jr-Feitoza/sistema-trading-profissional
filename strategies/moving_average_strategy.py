import pandas as pd
import ta
from strategies.base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, short_window=10, long_window=50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df["short_ma"] = ta.trend.sma_indicator(df["close"], window=self.short_window)
        df["long_ma"] = ta.trend.sma_indicator(df["close"], window=self.long_window)
        df["signal"] = 0

        df.loc[(df["short_ma"].shift(1) < df["long_ma"].shift(1)) & (df["short_ma"] >= df["long_ma"]), "signal"] = 1
        df.loc[(df["short_ma"].shift(1) > df["long_ma"].shift(1)) & (df["short_ma"] <= df["long_ma"]), "signal"] = -1

        return df

