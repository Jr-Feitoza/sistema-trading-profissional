"""
Sistema de Seleção de Estratégias
Permite escolher e combinar múltiplas estratégias SMC e Wyckoff
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from enum import Enum

# Importa todas as estratégias
from strategies.base_strategy import BaseStrategy
from strategies.smc_order_block_strategy import SMCOrderBlockStrategy
from strategies.smc_fvg_strategy import SMCFVGStrategy
from strategies.smc_liquidity_strategy import SMCLiquidityStrategy
from strategies.wyckoff_accumulation_strategy import WyckoffAccumulationStrategy
from strategies.wyckoff_spring_strategy import WyckoffSpringStrategy
from strategies.smc_wyckoff_combined_strategy import SMCWyckoffCombinedStrategy


class StrategyType(Enum):
    """Tipos de estratégias disponíveis"""
    # SMC Strategies
    SMC_ORDER_BLOCK = "smc_order_block"
    SMC_FVG = "smc_fvg"
    SMC_LIQUIDITY = "smc_liquidity"

    # Wyckoff Strategies
    WYCKOFF_ACCUMULATION = "wyckoff_accumulation"
    WYCKOFF_SPRING = "wyckoff_spring"

    # Combined Strategies
    SMC_WYCKOFF_COMBINED = "smc_wyckoff_combined"


class SignalCombinationMethod(Enum):
    """Métodos de combinação de sinais"""
    UNANIMOUS = "unanimous"  # Todas as estratégias devem concordar
    MAJORITY = "majority"  # Maioria das estratégias deve concordar
    ANY = "any"  # Qualquer estratégia pode gerar sinal
    WEIGHTED = "weighted"  # Sinais ponderados por confiança
    CONFLUENCE = "confluence"  # Score de confluência


class StrategySelector:
    """
    Seletor e Combinador de Estratégias

    Permite:
    - Selecionar múltiplas estratégias para usar
    - Combinar sinais de diferentes estratégias
    - Configurar parâmetros individuais
    - Avaliar performance de cada estratégia
    """

    def __init__(self):
        self.available_strategies = {
            StrategyType.SMC_ORDER_BLOCK: SMCOrderBlockStrategy,
            StrategyType.SMC_FVG: SMCFVGStrategy,
            StrategyType.SMC_LIQUIDITY: SMCLiquidityStrategy,
            StrategyType.WYCKOFF_ACCUMULATION: WyckoffAccumulationStrategy,
            StrategyType.WYCKOFF_SPRING: WyckoffSpringStrategy,
            StrategyType.SMC_WYCKOFF_COMBINED: SMCWyckoffCombinedStrategy,
        }

        self.selected_strategies: Dict[StrategyType, BaseStrategy] = {}
        self.strategy_weights: Dict[StrategyType, float] = {}

    def list_available_strategies(self) -> List[str]:
        """Lista todas as estratégias disponíveis"""
        return [strategy.value for strategy in StrategyType]

    def get_strategy_info(self, strategy_type: StrategyType) -> Dict[str, str]:
        """Retorna informações sobre uma estratégia"""
        info = {
            StrategyType.SMC_ORDER_BLOCK: {
                'name': 'SMC Order Blocks',
                'description': 'Identifica blocos de ordens institucionais',
                'best_for': 'Mercados com tendência clara',
                'timeframe': 'Todos os timeframes'
            },
            StrategyType.SMC_FVG: {
                'name': 'SMC Fair Value Gaps',
                'description': 'Negocia desequilíbrios de preço',
                'best_for': 'Mercados voláteis',
                'timeframe': 'Intraday e swing'
            },
            StrategyType.SMC_LIQUIDITY: {
                'name': 'SMC Liquidity Sweeps',
                'description': 'Captura varreduras de liquidez',
                'best_for': 'Mercados com liquidez alta',
                'timeframe': 'Todos os timeframes'
            },
            StrategyType.WYCKOFF_ACCUMULATION: {
                'name': 'Wyckoff Accumulation',
                'description': 'Identifica fases de acumulação',
                'best_for': 'Fim de downtrends, consolidações',
                'timeframe': 'Swing e position trading'
            },
            StrategyType.WYCKOFF_SPRING: {
                'name': 'Wyckoff Spring Pattern',
                'description': 'Negocia falsos rompimentos (Bear Traps)',
                'best_for': 'Consolidações e ranges',
                'timeframe': 'Todos os timeframes'
            },
            StrategyType.SMC_WYCKOFF_COMBINED: {
                'name': 'SMC + Wyckoff Combined',
                'description': 'Combina múltiplos conceitos para confluência',
                'best_for': 'Trading com alta probabilidade',
                'timeframe': 'Todos os timeframes'
            }
        }

        return info.get(strategy_type, {})

    def add_strategy(
        self,
        strategy_type: StrategyType,
        config: Optional[Dict[str, Any]] = None,
        weight: float = 1.0
    ):
        """
        Adiciona uma estratégia ao seletor

        Args:
            strategy_type: Tipo da estratégia
            config: Configuração customizada (opcional)
            weight: Peso da estratégia na combinação (0-1)
        """
        strategy_class = self.available_strategies[strategy_type]

        # Instancia estratégia com config
        if config:
            strategy = strategy_class(**config)
        else:
            strategy = strategy_class()

        self.selected_strategies[strategy_type] = strategy
        self.strategy_weights[strategy_type] = weight

        print(f"✓ Estratégia adicionada: {self.get_strategy_info(strategy_type)['name']}")

    def remove_strategy(self, strategy_type: StrategyType):
        """Remove uma estratégia"""
        if strategy_type in self.selected_strategies:
            del self.selected_strategies[strategy_type]
            del self.strategy_weights[strategy_type]
            print(f"✓ Estratégia removida: {strategy_type.value}")

    def clear_strategies(self):
        """Remove todas as estratégias"""
        self.selected_strategies.clear()
        self.strategy_weights.clear()
        print("✓ Todas as estratégias removidas")

    def generate_combined_signals(
        self,
        df: pd.DataFrame,
        combination_method: SignalCombinationMethod = SignalCombinationMethod.MAJORITY
    ) -> pd.DataFrame:
        """
        Gera sinais combinando todas as estratégias selecionadas

        Args:
            df: DataFrame com dados de preço
            combination_method: Método para combinar sinais

        Returns:
            DataFrame com sinal combinado
        """
        if not self.selected_strategies:
            raise ValueError("Nenhuma estratégia selecionada! Use add_strategy() primeiro.")

        # Gera sinais de cada estratégia
        strategy_signals = {}

        for strategy_type, strategy in self.selected_strategies.items():
            # Cria cópia do DataFrame
            df_strategy = df.copy()

            # Gera sinais
            df_strategy = strategy.generate_signals(df_strategy)

            # Armazena sinais
            strategy_signals[strategy_type.value] = df_strategy['signal']

        # Combina sinais baseado no método
        df = self._combine_signals(
            df,
            strategy_signals,
            combination_method
        )

        return df

    def _combine_signals(
        self,
        df: pd.DataFrame,
        strategy_signals: Dict[str, pd.Series],
        method: SignalCombinationMethod
    ) -> pd.DataFrame:
        """Combina sinais de múltiplas estratégias"""
        df = df.copy()

        if method == SignalCombinationMethod.UNANIMOUS:
            # Todas devem concordar
            df['signal'] = self._unanimous_combination(strategy_signals)

        elif method == SignalCombinationMethod.MAJORITY:
            # Maioria vence
            df['signal'] = self._majority_combination(strategy_signals)

        elif method == SignalCombinationMethod.ANY:
            # Qualquer sinal positivo é aceito
            df['signal'] = self._any_combination(strategy_signals)

        elif method == SignalCombinationMethod.WEIGHTED:
            # Combinação ponderada
            df['signal'] = self._weighted_combination(strategy_signals)

        elif method == SignalCombinationMethod.CONFLUENCE:
            # Score de confluência
            df['signal'] = self._confluence_combination(strategy_signals, df)

        # Adiciona sinais individuais ao DataFrame
        for strategy_name, signals in strategy_signals.items():
            df[f'signal_{strategy_name}'] = signals

        return df

    def _unanimous_combination(self, strategy_signals: Dict[str, pd.Series]) -> pd.Series:
        """Todas as estratégias devem concordar"""
        combined = pd.Series(0, index=list(strategy_signals.values())[0].index)

        for i in combined.index:
            signals = [sig[i] for sig in strategy_signals.values()]

            # Todas bullish
            if all(s == 1 for s in signals):
                combined[i] = 1
            # Todas bearish
            elif all(s == -1 for s in signals):
                combined[i] = -1
            # Não há acordo
            else:
                combined[i] = 0

        return combined

    def _majority_combination(self, strategy_signals: Dict[str, pd.Series]) -> pd.Series:
        """Maioria das estratégias vence"""
        combined = pd.Series(0, index=list(strategy_signals.values())[0].index)

        for i in combined.index:
            signals = [sig[i] for sig in strategy_signals.values()]

            bullish_count = sum(1 for s in signals if s == 1)
            bearish_count = sum(1 for s in signals if s == -1)

            # Maioria bullish
            if bullish_count > len(signals) / 2:
                combined[i] = 1
            # Maioria bearish
            elif bearish_count > len(signals) / 2:
                combined[i] = -1
            else:
                combined[i] = 0

        return combined

    def _any_combination(self, strategy_signals: Dict[str, pd.Series]) -> pd.Series:
        """Qualquer sinal é aceito"""
        combined = pd.Series(0, index=list(strategy_signals.values())[0].index)

        for i in combined.index:
            signals = [sig[i] for sig in strategy_signals.values()]

            # Prioriza sinais mais fortes
            if any(s == 1 for s in signals):
                combined[i] = 1
            elif any(s == -1 for s in signals):
                combined[i] = -1

        return combined

    def _weighted_combination(self, strategy_signals: Dict[str, pd.Series]) -> pd.Series:
        """Combinação ponderada por pesos"""
        combined = pd.Series(0, index=list(strategy_signals.values())[0].index)

        for i in combined.index:
            weighted_sum = 0.0

            for strategy_name, signals in strategy_signals.items():
                # Encontra StrategyType correspondente
                strategy_type = next(
                    (st for st in StrategyType if st.value == strategy_name),
                    None
                )

                if strategy_type:
                    weight = self.strategy_weights.get(strategy_type, 1.0)
                    weighted_sum += signals[i] * weight

            # Normaliza
            total_weight = sum(self.strategy_weights.values())

            if total_weight > 0:
                avg_signal = weighted_sum / total_weight

                if avg_signal > 0.3:
                    combined[i] = 1
                elif avg_signal < -0.3:
                    combined[i] = -1

        return combined

    def _confluence_combination(
        self,
        strategy_signals: Dict[str, pd.Series],
        df: pd.DataFrame
    ) -> pd.Series:
        """Score de confluência (quantos concordam)"""
        combined = pd.Series(0, index=list(strategy_signals.values())[0].index)
        df['confluence_score'] = 0

        for i in combined.index:
            signals = [sig[i] for sig in strategy_signals.values()]

            bullish_count = sum(1 for s in signals if s == 1)
            bearish_count = sum(1 for s in signals if s == -1)

            # Armazena score
            if bullish_count > bearish_count:
                df.loc[i, 'confluence_score'] = bullish_count
                if bullish_count >= 2:  # Pelo menos 2 estratégias
                    combined[i] = 1
            elif bearish_count > bullish_count:
                df.loc[i, 'confluence_score'] = -bearish_count
                if bearish_count >= 2:
                    combined[i] = -1

        return combined

    def compare_strategies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compara performance de todas as estratégias selecionadas

        Returns:
            DataFrame com estatísticas de cada estratégia
        """
        results = []

        for strategy_type, strategy in self.selected_strategies.items():
            df_test = df.copy()
            df_test = strategy.generate_signals(df_test)

            # Calcula estatísticas básicas
            total_signals = (df_test['signal'] != 0).sum()
            buy_signals = (df_test['signal'] == 1).sum()
            sell_signals = (df_test['signal'] == -1).sum()

            results.append({
                'strategy': self.get_strategy_info(strategy_type)['name'],
                'type': strategy_type.value,
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'signal_frequency': f"{(total_signals / len(df) * 100):.2f}%"
            })

        return pd.DataFrame(results)

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Retorna resumo da configuração atual"""
        return {
            'total_strategies': len(self.selected_strategies),
            'strategies': [
                {
                    'name': self.get_strategy_info(st)['name'],
                    'type': st.value,
                    'weight': self.strategy_weights[st]
                }
                for st in self.selected_strategies.keys()
            ]
        }
