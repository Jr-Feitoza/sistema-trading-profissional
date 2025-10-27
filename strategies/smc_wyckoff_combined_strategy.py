"""
Estratégia Combinada SMC + Wyckoff
Combina os melhores aspectos de Smart Money Concepts e método Wyckoff
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class SMCWyckoffCombinedStrategy(BaseStrategy):
    """
    Combined SMC + Wyckoff Strategy

    Esta estratégia combina:
    - Order Blocks (SMC) com fases de acumulação (Wyckoff)
    - Fair Value Gaps (SMC) com Spring patterns (Wyckoff)
    - Liquidity Sweeps (SMC) com testes Wyckoff

    Lógica de Confluência:
    - Sinal FORTE (3 pontos): Quando múltiplos conceitos concordam
    - Sinal MÉDIO (2 pontos): Quando 2 conceitos concordam
    - Sinal FRACO (1 ponto): Apenas 1 conceito

    Sinais de COMPRA quando há confluência de:
    - Spring (Wyckoff) + Order Block Bullish (SMC)
    - Liquidity Sweep Low + FVG Bullish
    - Accumulation Phase D + Order Block retest

    Sinais de VENDA quando há confluência de:
    - Upthrust (Wyckoff) + Order Block Bearish (SMC)
    - Liquidity Sweep High + FVG Bearish
    - Distribution Phase + Bearish patterns
    """

    def __init__(
        self,
        # SMC Parameters
        swing_length: int = 5,
        min_fvg_size_pct: float = 0.005,
        min_impulse_pct: float = 0.02,

        # Wyckoff Parameters
        support_lookback: int = 20,
        spring_penetration_pct: float = 0.015,
        volume_threshold: float = 1.5,

        # Combined Parameters
        min_confluence_score: int = 2,  # Mínimo de confluências para sinal
        use_weighted_signals: bool = True
    ):
        """
        Args:
            Parâmetros SMC e Wyckoff individuais +
            min_confluence_score: Score mínimo para gerar sinal (1-3)
            use_weighted_signals: Usar pesos diferentes para cada sinal
        """
        self.swing_length = swing_length
        self.min_fvg_size_pct = min_fvg_size_pct
        self.min_impulse_pct = min_impulse_pct
        self.support_lookback = support_lookback
        self.spring_penetration_pct = spring_penetration_pct
        self.volume_threshold = volume_threshold
        self.min_confluence_score = min_confluence_score
        self.use_weighted_signals = use_weighted_signals

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais combinando SMC e Wyckoff"""
        df = df.copy()
        df['signal'] = 0

        # Calcula indicadores auxiliares
        df['volume_ma'] = df['volume'].rolling(window=20).mean()

        # ===== COMPONENTE SMC =====
        # 1. Order Blocks
        df = self._identify_smc_order_blocks(df)

        # 2. Fair Value Gaps
        df = self._identify_smc_fvgs(df)

        # 3. Liquidity Sweeps
        df = self._identify_smc_liquidity_sweeps(df)

        # ===== COMPONENTE WYCKOFF =====
        # 4. Springs
        df = self._identify_wyckoff_springs(df)

        # 5. Accumulation Phases
        df = self._identify_wyckoff_accumulation(df)

        # ===== COMBINAR SINAIS =====
        df = self._combine_signals(df)

        return df

    def _identify_smc_order_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica Order Blocks (versão simplificada)"""
        df['bullish_ob'] = False
        df['bearish_ob'] = False

        for i in range(self.swing_length + 2, len(df)):
            # Procura impulso bullish
            price_change = (df['high'].iloc[i] - df['low'].iloc[i - self.swing_length]) / df['low'].iloc[i - self.swing_length]

            if price_change > self.min_impulse_pct:
                # Encontra último candle bearish antes do impulso
                for j in range(1, self.swing_length + 1):
                    idx = i - j
                    if df['close'].iloc[idx] < df['open'].iloc[idx]:
                        df.loc[df.index[i], 'bullish_ob'] = True
                        df.loc[df.index[i], 'ob_price'] = (df['high'].iloc[idx] + df['low'].iloc[idx]) / 2
                        break

            # Procura impulso bearish
            price_change_down = (df['high'].iloc[i - self.swing_length] - df['low'].iloc[i]) / df['high'].iloc[i - self.swing_length]

            if price_change_down > self.min_impulse_pct:
                # Encontra último candle bullish antes do impulso
                for j in range(1, self.swing_length + 1):
                    idx = i - j
                    if df['close'].iloc[idx] > df['open'].iloc[idx]:
                        df.loc[df.index[i], 'bearish_ob'] = True
                        df.loc[df.index[i], 'ob_price'] = (df['high'].iloc[idx] + df['low'].iloc[idx]) / 2
                        break

        return df

    def _identify_smc_fvgs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica Fair Value Gaps"""
        df['bullish_fvg'] = False
        df['bearish_fvg'] = False

        for i in range(2, len(df)):
            # FVG Bullish
            if df['low'].iloc[i - 2] > df['high'].iloc[i]:
                gap_size = (df['low'].iloc[i - 2] - df['high'].iloc[i]) / df['high'].iloc[i]
                if gap_size >= self.min_fvg_size_pct:
                    df.loc[df.index[i], 'bullish_fvg'] = True

            # FVG Bearish
            if df['high'].iloc[i - 2] < df['low'].iloc[i]:
                gap_size = (df['low'].iloc[i] - df['high'].iloc[i - 2]) / df['high'].iloc[i - 2]
                if gap_size >= self.min_fvg_size_pct:
                    df.loc[df.index[i], 'bearish_fvg'] = True

        return df

    def _identify_smc_liquidity_sweeps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica Liquidity Sweeps"""
        df['sweep_low'] = False
        df['sweep_high'] = False

        for i in range(self.support_lookback, len(df)):
            lookback_high = df['high'].iloc[i - self.support_lookback:i].max()
            lookback_low = df['low'].iloc[i - self.support_lookback:i].min()

            # Sweep de baixa com reversão
            if df['low'].iloc[i] < lookback_low * 0.999:
                if df['close'].iloc[i] > df['low'].iloc[i] * 1.003:
                    df.loc[df.index[i], 'sweep_low'] = True

            # Sweep de alta com reversão
            if df['high'].iloc[i] > lookback_high * 1.001:
                if df['close'].iloc[i] < df['high'].iloc[i] * 0.997:
                    df.loc[df.index[i], 'sweep_high'] = True

        return df

    def _identify_wyckoff_springs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica Springs Wyckoff"""
        df['is_spring'] = False
        df['is_upthrust'] = False

        for i in range(self.support_lookback, len(df)):
            support = df['low'].iloc[i - self.support_lookback:i].min()
            resistance = df['high'].iloc[i - self.support_lookback:i].max()

            # Spring (falso rompimento em baixa)
            if df['low'].iloc[i] < support * (1 - self.spring_penetration_pct):
                if df['close'].iloc[i] > support:
                    df.loc[df.index[i], 'is_spring'] = True

            # Upthrust (falso rompimento em alta)
            if df['high'].iloc[i] > resistance * (1 + self.spring_penetration_pct):
                if df['close'].iloc[i] < resistance:
                    df.loc[df.index[i], 'is_upthrust'] = True

        return df

    def _identify_wyckoff_accumulation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica fases de acumulação"""
        df['in_accumulation'] = False
        df['selling_climax'] = False

        for i in range(20, len(df)):
            # Detecta Selling Climax
            if df['volume'].iloc[i] > df['volume_ma'].iloc[i] * self.volume_threshold:
                body_size = abs(df['close'].iloc[i] - df['open'].iloc[i])
                if body_size > abs(df['close'].iloc[i-5:i] - df['open'].iloc[i-5:i]).mean() * 1.5:
                    if df['close'].iloc[i] < df['open'].iloc[i]:
                        df.loc[df.index[i], 'selling_climax'] = True

                        # Marca próximas barras como em acumulação
                        for j in range(1, min(30, len(df) - i)):
                            df.loc[df.index[i + j], 'in_accumulation'] = True

        return df

    def _combine_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combina todos os sinais com sistema de confluência"""
        df['bullish_score'] = 0
        df['bearish_score'] = 0
        df['confluence_type'] = ''

        for i in range(1, len(df)):
            bullish_score = 0
            bearish_score = 0
            confluence_reasons = []

            # ===== CONFLUÊNCIAS BULLISH =====

            # Confluência 1: Spring + Order Block Bullish
            if df['is_spring'].iloc[i] and df['bullish_ob'].iloc[i]:
                bullish_score += 3
                confluence_reasons.append('Spring_OB')

            # Confluência 2: Sweep Low + FVG Bullish
            elif df['sweep_low'].iloc[i] and df['bullish_fvg'].iloc[i]:
                bullish_score += 3
                confluence_reasons.append('Sweep_FVG')

            # Confluência 3: Spring + Accumulation
            elif df['is_spring'].iloc[i] and df['in_accumulation'].iloc[i]:
                bullish_score += 2
                confluence_reasons.append('Spring_Accumulation')

            # Sinais individuais
            if df['is_spring'].iloc[i]:
                bullish_score += 1
                confluence_reasons.append('Spring')

            if df['bullish_ob'].iloc[i]:
                bullish_score += 1
                confluence_reasons.append('OrderBlock')

            if df['sweep_low'].iloc[i]:
                bullish_score += 1
                confluence_reasons.append('LiquiditySweep')

            if df['bullish_fvg'].iloc[i]:
                bullish_score += 1
                confluence_reasons.append('FVG')

            # ===== CONFLUÊNCIAS BEARISH =====

            # Confluência 1: Upthrust + Order Block Bearish
            if df['is_upthrust'].iloc[i] and df['bearish_ob'].iloc[i]:
                bearish_score += 3
                confluence_reasons.append('Upthrust_OB')

            # Confluência 2: Sweep High + FVG Bearish
            elif df['sweep_high'].iloc[i] and df['bearish_fvg'].iloc[i]:
                bearish_score += 3
                confluence_reasons.append('Sweep_FVG_Bear')

            # Sinais individuais bearish
            if df['is_upthrust'].iloc[i]:
                bearish_score += 1
                confluence_reasons.append('Upthrust')

            if df['bearish_ob'].iloc[i]:
                bearish_score += 1
                confluence_reasons.append('OrderBlock_Bear')

            if df['sweep_high'].iloc[i]:
                bearish_score += 1
                confluence_reasons.append('LiquiditySweep_Bear')

            if df['bearish_fvg'].iloc[i]:
                bearish_score += 1
                confluence_reasons.append('FVG_Bear')

            # Armazena scores
            df.loc[df.index[i], 'bullish_score'] = bullish_score
            df.loc[df.index[i], 'bearish_score'] = bearish_score

            # Gera sinal baseado em score
            if bullish_score >= self.min_confluence_score and bullish_score > bearish_score:
                df.loc[df.index[i], 'signal'] = 1
                df.loc[df.index[i], 'confluence_type'] = '_'.join(confluence_reasons[:3])

            elif bearish_score >= self.min_confluence_score and bearish_score > bullish_score:
                df.loc[df.index[i], 'signal'] = -1
                df.loc[df.index[i], 'confluence_type'] = '_'.join(confluence_reasons[:3])

        return df

    def get_signal_statistics(self, df: pd.DataFrame) -> dict:
        """Retorna estatísticas sobre os sinais gerados"""
        if 'bullish_score' not in df.columns:
            return {}

        return {
            'total_bullish_signals': len(df[df['signal'] == 1]),
            'total_bearish_signals': len(df[df['signal'] == -1]),
            'avg_bullish_score': df[df['signal'] == 1]['bullish_score'].mean() if len(df[df['signal'] == 1]) > 0 else 0,
            'avg_bearish_score': df[df['signal'] == -1]['bearish_score'].mean() if len(df[df['signal'] == -1]) > 0 else 0,
            'high_confluence_signals': len(df[(df['bullish_score'] >= 3) | (df['bearish_score'] >= 3)]),
        }
