import pandas as pd
import ta
from strategies.base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df["rsi"] = ta.momentum.rsi(df["close"], window=self.period)
        df["signal"] = 0

        df.loc[(df["rsi"].shift(1) < self.oversold) & (df["rsi"] >= self.oversold), "signal"] = 1
        df.loc[(df["rsi"].shift(1) > self.overbought) & (df["rsi"] <= self.overbought), "signal"] = -1

        return df

