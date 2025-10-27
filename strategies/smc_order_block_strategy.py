"""
Estratégia SMC - Order Blocks
Identifica blocos de ordens institucionais (último candle antes de movimento significativo)
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class SMCOrderBlockStrategy(BaseStrategy):
    """
    Smart Money Concepts - Order Block Strategy

    Order Blocks são zonas onde instituições colocaram grandes ordens.
    São identificados como o último candle bullish/bearish antes de um movimento forte.

    Sinais:
    - BUY: Preço retorna a order block bullish (suporte)
    - SELL: Preço retorna a order block bearish (resistência)
    """

    def __init__(
        self,
        swing_length: int = 5,
        min_impulse_pct: float = 0.02,  # 2% movimento mínimo
        ob_validity_bars: int = 20  # Validade do order block
    ):
        """
        Args:
            swing_length: Período para detectar swing highs/lows
            min_impulse_pct: Percentual mínimo de movimento para validar impulso
            ob_validity_bars: Número de barras que um order block permanece válido
        """
        self.swing_length = swing_length
        self.min_impulse_pct = min_impulse_pct
        self.ob_validity_bars = ob_validity_bars

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais baseados em Order Blocks"""
        df = df.copy()
        df['signal'] = 0

        # Identifica swing highs e lows
        df['swing_high'] = self._identify_swing_highs(df)
        df['swing_low'] = self._identify_swing_lows(df)

        # Identifica order blocks bullish e bearish
        df = self._identify_order_blocks(df)

        # Gera sinais quando preço retorna aos order blocks
        df = self._generate_ob_signals(df)

        return df

    def _identify_swing_highs(self, df: pd.DataFrame) -> pd.Series:
        """Identifica swing highs"""
        swing_highs = pd.Series(False, index=df.index)

        for i in range(self.swing_length, len(df) - self.swing_length):
            high = df['high'].iloc[i]
            is_swing_high = True

            # Verifica se é o ponto mais alto no período
            for j in range(1, self.swing_length + 1):
                if (df['high'].iloc[i - j] >= high or
                    df['high'].iloc[i + j] >= high):
                    is_swing_high = False
                    break

            swing_highs.iloc[i] = is_swing_high

        return swing_highs

    def _identify_swing_lows(self, df: pd.DataFrame) -> pd.Series:
        """Identifica swing lows"""
        swing_lows = pd.Series(False, index=df.index)

        for i in range(self.swing_length, len(df) - self.swing_length):
            low = df['low'].iloc[i]
            is_swing_low = True

            # Verifica se é o ponto mais baixo no período
            for j in range(1, self.swing_length + 1):
                if (df['low'].iloc[i - j] <= low or
                    df['low'].iloc[i + j] <= low):
                    is_swing_low = False
                    break

            swing_lows.iloc[i] = is_swing_low

        return swing_lows

    def _identify_order_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica Order Blocks bullish e bearish"""
        df['bullish_ob_high'] = np.nan
        df['bullish_ob_low'] = np.nan
        df['bearish_ob_high'] = np.nan
        df['bearish_ob_low'] = np.nan
        df['ob_created'] = 0

        for i in range(self.swing_length + 1, len(df)):
            # Procura impulso bullish após swing low
            if df['swing_low'].iloc[i - self.swing_length]:
                # Verifica se houve impulso forte para cima
                impulse_start = df['low'].iloc[i - self.swing_length]
                current_high = df['high'].iloc[i]
                impulse_pct = (current_high - impulse_start) / impulse_start

                if impulse_pct >= self.min_impulse_pct:
                    # Order block é o último candle bearish antes do impulso
                    for j in range(1, self.swing_length + 1):
                        ob_idx = i - self.swing_length - j
                        if ob_idx >= 0 and df['close'].iloc[ob_idx] < df['open'].iloc[ob_idx]:
                            # Encontrou candle bearish - este é o order block
                            df.loc[df.index[i], 'bullish_ob_high'] = df['high'].iloc[ob_idx]
                            df.loc[df.index[i], 'bullish_ob_low'] = df['low'].iloc[ob_idx]
                            df.loc[df.index[i], 'ob_created'] = 1
                            break

            # Procura impulso bearish após swing high
            if df['swing_high'].iloc[i - self.swing_length]:
                # Verifica se houve impulso forte para baixo
                impulse_start = df['high'].iloc[i - self.swing_length]
                current_low = df['low'].iloc[i]
                impulse_pct = (impulse_start - current_low) / impulse_start

                if impulse_pct >= self.min_impulse_pct:
                    # Order block é o último candle bullish antes do impulso
                    for j in range(1, self.swing_length + 1):
                        ob_idx = i - self.swing_length - j
                        if ob_idx >= 0 and df['close'].iloc[ob_idx] > df['open'].iloc[ob_idx]:
                            # Encontrou candle bullish - este é o order block
                            df.loc[df.index[i], 'bearish_ob_high'] = df['high'].iloc[ob_idx]
                            df.loc[df.index[i], 'bearish_ob_low'] = df['low'].iloc[ob_idx]
                            df.loc[df.index[i], 'ob_created'] = -1
                            break

        # Forward fill os order blocks dentro do período de validade
        df = self._forward_fill_order_blocks(df)

        return df

    def _forward_fill_order_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Propaga order blocks válidos"""
        for col in ['bullish_ob_high', 'bullish_ob_low', 'bearish_ob_high', 'bearish_ob_low']:
            last_valid_value = np.nan
            bars_since_creation = self.ob_validity_bars + 1

            for i in range(len(df)):
                if not pd.isna(df[col].iloc[i]):
                    last_valid_value = df[col].iloc[i]
                    bars_since_creation = 0
                elif bars_since_creation < self.ob_validity_bars:
                    df.loc[df.index[i], col] = last_valid_value
                    bars_since_creation += 1
                else:
                    df.loc[df.index[i], col] = np.nan

        return df

    def _generate_ob_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais quando preço retorna aos order blocks"""
        for i in range(1, len(df)):
            # Sinal de COMPRA - preço retorna a bullish order block
            if (not pd.isna(df['bullish_ob_low'].iloc[i]) and
                not pd.isna(df['bullish_ob_high'].iloc[i])):

                # Verifica se preço tocou o order block
                if (df['low'].iloc[i] <= df['bullish_ob_high'].iloc[i] and
                    df['high'].iloc[i] >= df['bullish_ob_low'].iloc[i]):

                    # Confirma com fechamento acima do order block
                    if df['close'].iloc[i] >= df['bullish_ob_low'].iloc[i]:
                        df.loc[df.index[i], 'signal'] = 1

            # Sinal de VENDA - preço retorna a bearish order block
            if (not pd.isna(df['bearish_ob_low'].iloc[i]) and
                not pd.isna(df['bearish_ob_high'].iloc[i])):

                # Verifica se preço tocou o order block
                if (df['high'].iloc[i] >= df['bearish_ob_low'].iloc[i] and
                    df['low'].iloc[i] <= df['bearish_ob_high'].iloc[i]):

                    # Confirma com fechamento abaixo do order block
                    if df['close'].iloc[i] <= df['bearish_ob_high'].iloc[i]:
                        df.loc[df.index[i], 'signal'] = -1

        return df
