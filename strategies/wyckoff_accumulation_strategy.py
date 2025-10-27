"""
Estratégia Wyckoff - Accumulation
Identifica fases de acumulação institucional baseadas no método Wyckoff
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class WyckoffAccumulationStrategy(BaseStrategy):
    """
    Wyckoff Accumulation Strategy

    Identifica e negocia baseado nas fases de acumulação Wyckoff:

    Fase A: Stopping the decline
        - PS (Preliminary Support): Primeiro sinal de demanda
        - SC (Selling Climax): Volume alto, queda dramática
        - AR (Automatic Rally): Recuperação automática

    Fase B: Building a cause
        - ST (Secondary Test): Testa o SC
        - Consolidação em trading range

    Fase C: Testing
        - Spring: Falso rompimento abaixo do suporte (Bear Trap)
        - Test: Re-teste do spring

    Fase D: Dominance of demand
        - LPS (Last Point of Support): Último ponto de suporte antes do rally
        - SOS (Sign of Strength): Sinal de força com volume

    Fase E: Markup
        - Uptrend confirmado

    Sinais:
    - BUY: Após Spring confirmado ou em LPS
    - SELL: Sai quando detecta distribuição ou fim de markup
    """

    def __init__(
        self,
        volume_threshold: float = 1.5,  # Volume do SC deve ser 1.5x média
        range_lookback: int = 30,
        spring_penetration_pct: float = 0.02,  # 2% abaixo do suporte
        sos_volume_mult: float = 1.3  # Volume do SOS 1.3x média
    ):
        """
        Args:
            volume_threshold: Multiplicador de volume para SC/PS
            range_lookback: Período para definir trading range
            spring_penetration_pct: Quanto o spring penetra o suporte
            sos_volume_mult: Multiplicador de volume para Sign of Strength
        """
        self.volume_threshold = volume_threshold
        self.range_lookback = range_lookback
        self.spring_penetration_pct = spring_penetration_pct
        self.sos_volume_mult = sos_volume_mult

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais baseados em Wyckoff Accumulation"""
        df = df.copy()
        df['signal'] = 0

        # Calcula volume médio
        df['volume_ma'] = df['volume'].rolling(window=20).mean()

        # Identifica fases de acumulação
        df = self._identify_accumulation_phases(df)

        # Gera sinais de trading
        df = self._generate_accumulation_signals(df)

        return df

    def _identify_accumulation_phases(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica fases da acumulação Wyckoff"""
        df['wyckoff_phase'] = ''
        df['is_selling_climax'] = False
        df['is_spring'] = False
        df['is_sos'] = False
        df['trading_range_high'] = np.nan
        df['trading_range_low'] = np.nan

        in_accumulation = False
        accumulation_start = None
        range_high = None
        range_low = None

        for i in range(self.range_lookback, len(df)):
            current_idx = df.index[i]

            # FASE A: Detecta Selling Climax (SC)
            # Alto volume + queda significativa + reversão
            if not in_accumulation:
                avg_volume = df['volume_ma'].iloc[i]
                current_volume = df['volume'].iloc[i]

                # Volume alto
                if current_volume > avg_volume * self.volume_threshold:
                    # Queda significativa (candle bearish grande)
                    body_size = abs(df['close'].iloc[i] - df['open'].iloc[i])
                    prev_body_avg = abs(
                        df['close'].iloc[i-5:i] - df['open'].iloc[i-5:i]
                    ).mean()

                    if (body_size > prev_body_avg * 1.5 and
                        df['close'].iloc[i] < df['open'].iloc[i]):

                        # Possível Selling Climax
                        df.loc[current_idx, 'is_selling_climax'] = True
                        df.loc[current_idx, 'wyckoff_phase'] = 'Phase_A_SC'

                        # Inicia acumulação
                        in_accumulation = True
                        accumulation_start = i
                        range_low = df['low'].iloc[i]
                        range_high = df['high'].iloc[max(i-10, 0):i].max()

            # FASE B & C: Dentro de acumulação
            elif in_accumulation:
                bars_in_accumulation = i - accumulation_start

                # Atualiza trading range
                if bars_in_accumulation < self.range_lookback:
                    range_high = df['high'].iloc[accumulation_start:i+1].max()
                    range_low = df['low'].iloc[accumulation_start:i+1].min()

                    df.loc[current_idx, 'trading_range_high'] = range_high
                    df.loc[current_idx, 'trading_range_low'] = range_low
                    df.loc[current_idx, 'wyckoff_phase'] = 'Phase_B_Consolidation'

                # FASE C: Detecta Spring
                # Spring é um falso rompimento abaixo do range_low
                if bars_in_accumulation >= 10:  # Pelo menos 10 barras em consolidação
                    spring_level = range_low * (1 - self.spring_penetration_pct)

                    # Verifica se rompeu abaixo
                    if df['low'].iloc[i] < spring_level:
                        # Verifica reversão rápida (fechamento dentro do range)
                        if df['close'].iloc[i] > range_low:
                            df.loc[current_idx, 'is_spring'] = True
                            df.loc[current_idx, 'wyckoff_phase'] = 'Phase_C_Spring'

                # FASE D: Detecta Sign of Strength (SOS)
                # Movimento forte para cima com volume
                if bars_in_accumulation >= 15:
                    # Verifica movimento forte acima do range
                    if df['close'].iloc[i] > range_high:
                        # Com volume acima da média
                        if df['volume'].iloc[i] > df['volume_ma'].iloc[i] * self.sos_volume_mult:
                            # Candle bullish
                            if df['close'].iloc[i] > df['open'].iloc[i]:
                                df.loc[current_idx, 'is_sos'] = True
                                df.loc[current_idx, 'wyckoff_phase'] = 'Phase_D_SOS'

                                # Sai da fase de acumulação após SOS
                                in_accumulation = False

                # Timeout: Sai de acumulação após muitas barras sem progresso
                if bars_in_accumulation > self.range_lookback * 2:
                    in_accumulation = False

        return df

    def _generate_accumulation_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais de trading baseados nas fases"""
        for i in range(1, len(df)):
            current_idx = df.index[i]

            # SINAL DE COMPRA 1: Após Spring confirmado
            if df['is_spring'].iloc[i]:
                df.loc[current_idx, 'signal'] = 1

            # SINAL DE COMPRA 2: Em Last Point of Support (LPS)
            # LPS é um pullback após SOS
            elif i > 1 and df['is_sos'].iloc[i-1]:
                # Próximas barras podem ser LPS (pullback)
                if (df['low'].iloc[i] > df['low'].iloc[i-1] and
                    df['close'].iloc[i] > df['open'].iloc[i]):
                    df.loc[current_idx, 'signal'] = 1
                    df.loc[current_idx, 'wyckoff_phase'] = 'Phase_D_LPS'

            # SINAL DE COMPRA 3: Breakout após SOS
            elif df['is_sos'].iloc[i]:
                df.loc[current_idx, 'signal'] = 1

        return df
