"""
Estratégia SMC - Liquidity Sweeps
Identifica varreduras de liquidez onde smart money captura stops
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class SMCLiquidityStrategy(BaseStrategy):
    """
    Smart Money Concepts - Liquidity Sweep Strategy

    Smart Money procura liquidez acima de máximas óbvias e abaixo de mínimas
    limpas - exatamente onde traders retail colocam stops.

    Um liquidity sweep ocorre quando:
    - Preço rompe uma máxima/mínima significativa
    - Rapidamente reverte na direção oposta
    - Isso indica que stops foram capturados

    Sinais:
    - BUY: Após sweep de liquidez em baixa (captura stops de venda)
    - SELL: Após sweep de liquidez em alta (captura stops de compra)
    """

    def __init__(
        self,
        lookback_highs: int = 20,
        lookback_lows: int = 20,
        sweep_threshold_pct: float = 0.001,  # 0.1% além do nível
        reversal_threshold_pct: float = 0.005,  # 0.5% reversão mínima
        max_sweep_bars: int = 3  # Barras máximas para sweep + reversão
    ):
        """
        Args:
            lookback_highs: Período para identificar máximas significativas
            lookback_lows: Período para identificar mínimas significativas
            sweep_threshold_pct: Percentual além do nível para considerar sweep
            reversal_threshold_pct: Percentual de reversão para confirmar
            max_sweep_bars: Número máximo de barras entre sweep e reversão
        """
        self.lookback_highs = lookback_highs
        self.lookback_lows = lookback_lows
        self.sweep_threshold_pct = sweep_threshold_pct
        self.reversal_threshold_pct = reversal_threshold_pct
        self.max_sweep_bars = max_sweep_bars

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais baseados em Liquidity Sweeps"""
        df = df.copy()
        df['signal'] = 0

        # Identifica níveis de liquidez (highs e lows significativos)
        df = self._identify_liquidity_levels(df)

        # Detecta sweeps de liquidez
        df = self._detect_liquidity_sweeps(df)

        return df

    def _identify_liquidity_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica níveis de liquidez (máximas e mínimas significativas)"""
        df['liquidity_high'] = df['high'].rolling(
            window=self.lookback_highs,
            center=True
        ).max()

        df['liquidity_low'] = df['low'].rolling(
            window=self.lookback_lows,
            center=True
        ).min()

        # Marca apenas máximas/mínimas que são iguais ao rolling max/min
        # (ou seja, pontos pivot reais)
        df['is_liquidity_high'] = df['high'] == df['liquidity_high']
        df['is_liquidity_low'] = df['low'] == df['liquidity_low']

        return df

    def _detect_liquidity_sweeps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta sweeps de liquidez e gera sinais"""
        # Armazena últimos níveis de liquidez
        recent_highs = []
        recent_lows = []

        for i in range(self.lookback_highs, len(df)):
            current_idx = df.index[i]

            # Atualiza lista de máximas recentes
            if df['is_liquidity_high'].iloc[i]:
                recent_highs.append({
                    'price': df['high'].iloc[i],
                    'index': i
                })
                # Mantém apenas as últimas N máximas
                recent_highs = recent_highs[-5:]

            # Atualiza lista de mínimas recentes
            if df['is_liquidity_low'].iloc[i]:
                recent_lows.append({
                    'price': df['low'].iloc[i],
                    'index': i
                })
                # Mantém apenas as últimas N mínimas
                recent_lows = recent_lows[-5:]

            # Detecta sweep de liquidez ALTA (potencial SELL)
            for liq_high in recent_highs:
                # Verifica se está dentro da janela de tempo
                if i - liq_high['index'] > self.max_sweep_bars:
                    continue

                sweep_level = liq_high['price'] * (1 + self.sweep_threshold_pct)

                # Verifica se houve sweep (preço ultrapassou)
                if df['high'].iloc[i] >= sweep_level:
                    # Verifica reversão bearish
                    reversal_target = df['high'].iloc[i] * (1 - self.reversal_threshold_pct)

                    if df['close'].iloc[i] <= reversal_target:
                        # Sweep confirmado com reversão
                        # Verifica se é um candle bearish engulfing ou forte rejeição
                        if (df['close'].iloc[i] < df['open'].iloc[i] and
                            df['open'].iloc[i] >= df['high'].iloc[i] * 0.95):
                            # Sinal de VENDA
                            df.loc[current_idx, 'signal'] = -1
                            df.loc[current_idx, 'sweep_type'] = 'high_sweep'

            # Detecta sweep de liquidez BAIXA (potencial BUY)
            for liq_low in recent_lows:
                # Verifica se está dentro da janela de tempo
                if i - liq_low['index'] > self.max_sweep_bars:
                    continue

                sweep_level = liq_low['price'] * (1 - self.sweep_threshold_pct)

                # Verifica se houve sweep (preço ultrapassou)
                if df['low'].iloc[i] <= sweep_level:
                    # Verifica reversão bullish
                    reversal_target = df['low'].iloc[i] * (1 + self.reversal_threshold_pct)

                    if df['close'].iloc[i] >= reversal_target:
                        # Sweep confirmado com reversão
                        # Verifica se é um candle bullish engulfing ou forte rejeição
                        if (df['close'].iloc[i] > df['open'].iloc[i] and
                            df['open'].iloc[i] <= df['low'].iloc[i] * 1.05):
                            # Sinal de COMPRA
                            df.loc[current_idx, 'signal'] = 1
                            df.loc[current_idx, 'sweep_type'] = 'low_sweep'

        return df
