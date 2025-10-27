"""
Estratégia Wyckoff - Spring Pattern
Especializada em detectar e negociar o padrão Spring (Bear Trap)
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class WyckoffSpringStrategy(BaseStrategy):
    """
    Wyckoff Spring Strategy

    O Spring é um dos padrões mais poderosos do método Wyckoff.
    É um falso rompimento (Bear Trap) que ocorre na Fase C da acumulação.

    Características do Spring:
    1. Preço penetra abaixo do suporte estabelecido
    2. Stop losses de traders retail são acionados
    3. Smart Money compra essa liquidez
    4. Preço rapidamente reverte acima do suporte
    5. Geralmente ocorre com volume decrescente no falso rompimento
    6. Reversão pode ter volume aumentado

    Sinais:
    - BUY: Logo após confirmação do Spring
    - SELL: Quando detecta topo ou spring reverso (Upthrust)
    """

    def __init__(
        self,
        support_lookback: int = 20,
        spring_penetration_pct: float = 0.015,  # 1.5% abaixo suporte
        max_spring_duration: int = 5,  # Máximo de barras para spring
        volume_confirmation: bool = True,
        require_volume_decrease: bool = True
    ):
        """
        Args:
            support_lookback: Período para identificar níveis de suporte
            spring_penetration_pct: Percentual de penetração do suporte
            max_spring_duration: Número máximo de barras para o spring
            volume_confirmation: Requer confirmação de volume
            require_volume_decrease: Volume deve diminuir no spring
        """
        self.support_lookback = support_lookback
        self.spring_penetration_pct = spring_penetration_pct
        self.max_spring_duration = max_spring_duration
        self.volume_confirmation = volume_confirmation
        self.require_volume_decrease = require_volume_decrease

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais baseados em Spring Pattern"""
        df = df.copy()
        df['signal'] = 0

        # Calcula médias de volume
        df['volume_ma'] = df['volume'].rolling(window=20).mean()

        # Identifica níveis de suporte
        df = self._identify_support_levels(df)

        # Detecta springs
        df = self._detect_springs(df)

        # Gera sinais
        df = self._generate_spring_signals(df)

        return df

    def _identify_support_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica níveis de suporte significativos"""
        df['support_level'] = df['low'].rolling(
            window=self.support_lookback,
            center=False
        ).min()

        # Identifica quando preço está próximo ao suporte
        df['near_support'] = (
            df['low'] <= df['support_level'] * 1.01  # Dentro de 1% do suporte
        )

        return df

    def _detect_springs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta padrões Spring"""
        df['is_spring'] = False
        df['spring_quality'] = 0  # 0-100 score de qualidade

        for i in range(self.support_lookback + 5, len(df)):
            # Identifica suporte dos últimos N barras
            lookback_start = max(0, i - self.support_lookback)
            support_level = df['low'].iloc[lookback_start:i].min()

            # Nível de spring (abaixo do suporte)
            spring_level = support_level * (1 - self.spring_penetration_pct)

            # Verifica se houve penetração do suporte
            if df['low'].iloc[i] < spring_level:
                # Verifica reversão rápida
                spring_detected = False
                quality_score = 0

                # Procura reversão nas próximas barras
                for j in range(1, min(self.max_spring_duration + 1, len(df) - i)):
                    future_idx = i + j

                    # Verificações para spring válido
                    reversal_checks = []

                    # 1. Fechamento acima do suporte original
                    if df['close'].iloc[future_idx] > support_level:
                        reversal_checks.append(True)
                        quality_score += 30
                    else:
                        reversal_checks.append(False)

                    # 2. Candle de reversão bullish
                    if df['close'].iloc[future_idx] > df['open'].iloc[future_idx]:
                        reversal_checks.append(True)
                        quality_score += 20
                    else:
                        reversal_checks.append(False)

                    # 3. Velocidade da reversão (quanto mais rápido, melhor)
                    if j <= 2:  # Reversão em 1-2 barras
                        quality_score += 30
                    elif j <= 4:
                        quality_score += 15

                    # 4. Análise de volume (se habilitado)
                    if self.volume_confirmation:
                        # Volume do spring deve ser menor
                        if self.require_volume_decrease:
                            if df['volume'].iloc[i] < df['volume_ma'].iloc[i]:
                                quality_score += 10
                                reversal_checks.append(True)
                            else:
                                reversal_checks.append(False)

                        # Volume da reversão deve aumentar
                        if df['volume'].iloc[future_idx] > df['volume_ma'].iloc[future_idx]:
                            quality_score += 10

                    # Se tem confirmações suficientes, marca como spring
                    if sum(reversal_checks) >= 2:
                        spring_detected = True
                        df.loc[df.index[future_idx], 'is_spring'] = True
                        df.loc[df.index[future_idx], 'spring_quality'] = min(quality_score, 100)
                        break

                if spring_detected:
                    # Marca o candle do spring também
                    df.loc[df.index[i], 'spring_low'] = df['low'].iloc[i]

        return df

    def _generate_spring_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera sinais de trading baseados em Springs"""
        for i in range(1, len(df)):
            current_idx = df.index[i]

            # SINAL DE COMPRA: Spring confirmado
            if df['is_spring'].iloc[i]:
                # Qualidade do spring
                quality = df['spring_quality'].iloc[i]

                # Apenas sinais de qualidade alta/média
                if quality >= 50:
                    df.loc[current_idx, 'signal'] = 1

                    # Informações adicionais para gestão de risco
                    df.loc[current_idx, 'entry_type'] = 'spring_high_quality'

                elif quality >= 30:
                    # Spring de qualidade média - sinal mais fraco
                    df.loc[current_idx, 'signal'] = 1
                    df.loc[current_idx, 'entry_type'] = 'spring_medium_quality'

            # SINAL DE SAÍDA: Detecção de Upthrust (spring reverso no topo)
            # Upthrust é o oposto do spring - falso rompimento no topo
            elif i >= self.support_lookback:
                lookback_start = max(0, i - self.support_lookback)
                resistance_level = df['high'].iloc[lookback_start:i].max()
                upthrust_level = resistance_level * (1 + self.spring_penetration_pct)

                # Verifica upthrust
                if df['high'].iloc[i] > upthrust_level:
                    # Verifica reversão bearish
                    if df['close'].iloc[i] < resistance_level:
                        if df['close'].iloc[i] < df['open'].iloc[i]:
                            # Sinal de VENDA (ou saída)
                            df.loc[current_idx, 'signal'] = -1
                            df.loc[current_idx, 'entry_type'] = 'upthrust'

        return df

    def get_spring_statistics(self, df: pd.DataFrame) -> dict:
        """Retorna estatísticas sobre springs detectados"""
        if 'is_spring' not in df.columns:
            return {}

        springs = df[df['is_spring'] == True]

        if len(springs) == 0:
            return {'total_springs': 0}

        return {
            'total_springs': len(springs),
            'avg_quality': springs['spring_quality'].mean(),
            'high_quality_springs': len(springs[springs['spring_quality'] >= 70]),
            'medium_quality_springs': len(springs[springs['spring_quality'].between(40, 69)]),
            'low_quality_springs': len(springs[springs['spring_quality'] < 40])
        }
