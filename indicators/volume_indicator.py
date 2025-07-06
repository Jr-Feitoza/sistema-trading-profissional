import pandas as pd
from indicators.base_indicator import BaseIndicator

class VolumeIndicator(BaseIndicator):
    def calculate(self, df: pd.DataFrame) -> pd.Series:
        if "volume" in df.columns:
            return df["volume"].round(2)
        return pd.Series()


