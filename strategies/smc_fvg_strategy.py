"""
Estratégia SMC - Fair Value Gaps (FVG)
Identifica desequilíbrios no preço onde houve movimento muito rápido
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class SMCFVGStrategy(BaseStrategy):
    """
    Smart Money Concepts - Fair Value Gap Strategy

    Fair Value Gaps (FVG) ou Imbalance são gaps onde o preço se moveu
    tão rápido que deixou um desequilíbrio. O preço tende a retornar
    a esses gaps ~70% das vezes.

    Um FVG Bullish ocorre quando:
    - Low do candle anterior > High do candle seguinte ao atual
    - Indica compra agressiva

    Um FVG Bearish ocorre quando:
    - High do candle anterior < Low do candle seguinte ao atual
    - Indica venda agressiva

    Sinais:
    - BUY: Preço retorna a FVG bullish
    - SELL: Preço retorna a FVG bearish
    """

    def __init__(
        self,
        min_fvg_size_pct: float = 0.005,  # 0.5% mínimo
        fvg_validity_bars: int = 50,
        require_fill_pct: float = 0.5  # 50% do gap deve ser preenchido
    ):
        """
        Args:
            min_fvg_size_pct: Tamanho mínimo do FVG em percentual
            fvg_validity_bars: Número de barras que FVG permanece válido
            require_fill_pct: Percentual do gap que deve ser preenchido para sinal
        """
        self.min_fvg_size_pct = min_fvg_size_pct
        self.fvg_validity_bars = fvg_validity_bars
        self.require_fill_pct = require_fill_pct

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais baseados em Fair Value Gaps"""
        df = df.copy()
        df['signal'] = 0

        # Identifica FVGs
        df = self._identify_fvgs(df)

        # Gera sinais quando preço retorna aos FVGs
        df = self._generate_fvg_signals(df)

        return df

    def _identify_fvgs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica Fair Value Gaps bullish e bearish"""
        df['bullish_fvg_high'] = np.nan
        df['bullish_fvg_low'] = np.nan
        df['bearish_fvg_high'] = np.nan
        df['bearish_fvg_low'] = np.nan

        for i in range(2, len(df)):
            prev_candle = df.iloc[i - 2]
            current_candle = df.iloc[i - 1]
            next_candle = df.iloc[i]

            # FVG Bullish: gap entre low do candle anterior e high do próximo
            if prev_candle['low'] > next_candle['high']:
                gap_size = prev_candle['low'] - next_candle['high']
                gap_pct = gap_size / next_candle['high']

                if gap_pct >= self.min_fvg_size_pct:
                    # Verifica se foi movimento bullish forte
                    if current_candle['close'] > current_candle['open']:
                        df.loc[df.index[i], 'bullish_fvg_high'] = prev_candle['low']
                        df.loc[df.index[i], 'bullish_fvg_low'] = next_candle['high']

            # FVG Bearish: gap entre high do candle anterior e low do próximo
            if prev_candle['high'] < next_candle['low']:
                gap_size = next_candle['low'] - prev_candle['high']
                gap_pct = gap_size / prev_candle['high']

                if gap_pct >= self.min_fvg_size_pct:
                    # Verifica se foi movimento bearish forte
                    if current_candle['close'] < current_candle['open']:
                        df.loc[df.index[i], 'bearish_fvg_high'] = next_candle['low']
                        df.loc[df.index[i], 'bearish_fvg_low'] = prev_candle['high']

        # Forward fill os FVGs dentro do período de validade
        df = self._forward_fill_fvgs(df)

        return df

    def _forward_fill_fvgs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Propaga FVGs válidos e remove quando preenchidos"""
        for col_pair in [('bullish_fvg_high', 'bullish_fvg_low'),
                         ('bearish_fvg_high', 'bearish_fvg_low')]:
            high_col, low_col = col_pair
            last_high = np.nan
            last_low = np.nan
            bars_since_creation = self.fvg_validity_bars + 1

            for i in range(len(df)):
                # Novo FVG criado
                if not pd.isna(df[high_col].iloc[i]):
                    last_high = df[high_col].iloc[i]
                    last_low = df[low_col].iloc[i]
                    bars_since_creation = 0

                # FVG ainda válido
                elif bars_since_creation < self.fvg_validity_bars:
                    # Verifica se FVG foi significativamente preenchido
                    if not pd.isna(last_high) and not pd.isna(last_low):
                        fvg_range = abs(last_high - last_low)
                        required_fill = fvg_range * self.require_fill_pct

                        # Para bullish FVG, verifica se preço desceu suficiente
                        if 'bullish' in high_col:
                            if df['low'].iloc[i] <= (last_high - required_fill):
                                # FVG foi preenchido, invalida
                                last_high = np.nan
                                last_low = np.nan
                            else:
                                df.loc[df.index[i], high_col] = last_high
                                df.loc[df.index[i], low_col] = last_low
                                bars_since_creation += 1

                        # Para bearish FVG, verifica se preço subiu suficiente
                        else:
                            if df['high'].iloc[i] >= (last_low + required_fill):
                                # FVG foi preenchido, invalida
                                last_high = np.nan
                                last_low = np.nan
                            else:
                                df.loc[df.index[i], high_col] = last_high
                                df.loc[df.index[i], low_col] = last_low
                                bars_since_creation += 1
                    else:
                        bars_since_creation += 1

                # FVG expirou
                else:
                    df.loc[df.index[i], high_col] = np.nan
                    df.loc[df.index[i], low_col] = np.nan

        return df

    def _generate_fvg_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais quando preço retorna aos FVGs"""
        for i in range(1, len(df)):
            # Sinal de COMPRA - preço retorna a bullish FVG
            if (not pd.isna(df['bullish_fvg_low'].iloc[i]) and
                not pd.isna(df['bullish_fvg_high'].iloc[i])):

                fvg_mid = (df['bullish_fvg_high'].iloc[i] + df['bullish_fvg_low'].iloc[i]) / 2

                # Preço entrou no FVG
                if (df['low'].iloc[i] <= df['bullish_fvg_high'].iloc[i] and
                    df['high'].iloc[i] >= df['bullish_fvg_low'].iloc[i]):

                    # Confirma com rejeição (fechamento próximo ao meio ou acima)
                    if df['close'].iloc[i] >= fvg_mid:
                        # Adicional: verifica momentum bullish
                        if df['close'].iloc[i] > df['open'].iloc[i]:
                            df.loc[df.index[i], 'signal'] = 1

            # Sinal de VENDA - preço retorna a bearish FVG
            if (not pd.isna(df['bearish_fvg_low'].iloc[i]) and
                not pd.isna(df['bearish_fvg_high'].iloc[i])):

                fvg_mid = (df['bearish_fvg_high'].iloc[i] + df['bearish_fvg_low'].iloc[i]) / 2

                # Preço entrou no FVG
                if (df['high'].iloc[i] >= df['bearish_fvg_low'].iloc[i] and
                    df['low'].iloc[i] <= df['bearish_fvg_high'].iloc[i]):

                    # Confirma com rejeição (fechamento próximo ao meio ou abaixo)
                    if df['close'].iloc[i] <= fvg_mid:
                        # Adicional: verifica momentum bearish
                        if df['close'].iloc[i] < df['open'].iloc[i]:
                            df.loc[df.index[i], 'signal'] = -1

        return df
