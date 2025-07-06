import pandas as pd
from strategies.base_strategy import BaseStrategy

class IRF2Strategy(BaseStrategy):
    def __init__(self, breakout_margin=1.0):
        self.breakout_margin = breakout_margin

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df["signal"] = 0
        df["high_prev"] = df["high"].shift(1)
        df["low_prev"] = df["low"].shift(1)

        df.loc[df["close"] > (df["high_prev"] + self.breakout_margin), "signal"] = 1
        df.loc[df["close"] < (df["low_prev"] - self.breakout_margin), "signal"] = -1

        return df

