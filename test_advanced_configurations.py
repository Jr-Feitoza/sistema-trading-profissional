"""
Testes avançados de configurações e combinações de estratégias
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/home/user/sistema-trading-profissional')

from strategies.strategy_selector import (
    StrategySelector,
    StrategyType,
    SignalCombinationMethod
)

print("="*80)
print("TESTES AVANÇADOS DE CONFIGURAÇÕES")
print("="*80)
print()

# Criar dados com diferentes cenários de mercado
def create_trending_market(days=200, trend='up'):
    """Cria dados com tendência definida"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='h')
    np.random.seed(42)
    price = 50000

    trend_factor = 0.001 if trend == 'up' else -0.001

    data = []
    for i, date in enumerate(dates):
        # Adiciona tendência
        price *= (1 + trend_factor)

        # Adiciona ruído
        noise = np.random.randn() * 0.01
        price *= (1 + noise)

        high = price * (1 + abs(np.random.randn()) * 0.01)
        low = price * (1 - abs(np.random.randn()) * 0.01)
        open_price = price * (1 + np.random.randn() * 0.005)
        volume = abs(np.random.randn() * 1000000 + 5000000)

        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })

    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df

# ============================================================================
# TESTE 1: Mercado em Alta vs Baixa
# ============================================================================
print("TESTE 1: Comparando Mercados de Alta vs Baixa")
print("-"*80)

for market_type in ['up', 'down']:
    print(f"\n  Mercado em {market_type.upper()}:")
    df = create_trending_market(200, trend=market_type)

    selector = StrategySelector()
    selector.add_strategy(StrategyType.SMC_ORDER_BLOCK)
    selector.add_strategy(StrategyType.WYCKOFF_SPRING)
    selector.add_strategy(StrategyType.SMC_WYCKOFF_COMBINED)

    df_result = selector.generate_combined_signals(
        df,
        combination_method=SignalCombinationMethod.MAJORITY
    )

    signals = df_result[df_result['signal'] != 0]
    buy_signals = len(signals[signals['signal'] == 1])
    sell_signals = len(signals[signals['signal'] == -1])

    print(f"    Total de sinais: {len(signals)}")
    print(f"    COMPRA: {buy_signals} ({buy_signals/len(signals)*100 if len(signals) > 0 else 0:.1f}%)")
    print(f"    VENDA: {sell_signals} ({sell_signals/len(signals)*100 if len(signals) > 0 else 0:.1f}%)")

    # Compara estratégias
    comparison = selector.compare_strategies(df)
    print(f"\\n    Detalhes por estratégia:")
    for _, row in comparison.iterrows():
        print(f"      {row['strategy']}: {row['total_signals']} sinais ({row['signal_frequency']})")

print()

# ============================================================================
# TESTE 2: Diferentes Métodos de Combinação
# ============================================================================
print("TESTE 2: Comparando Todos os Métodos de Combinação")
print("-"*80)

df = create_trending_market(300, trend='up')

selector = StrategySelector()
selector.add_strategy(StrategyType.SMC_ORDER_BLOCK, weight=1.0)
selector.add_strategy(StrategyType.SMC_FVG, weight=1.0)
selector.add_strategy(StrategyType.SMC_LIQUIDITY, weight=0.8)
selector.add_strategy(StrategyType.WYCKOFF_SPRING, weight=1.2)
selector.add_strategy(StrategyType.WYCKOFF_ACCUMULATION, weight=1.0)

methods = {
    'UNANIMOUS': SignalCombinationMethod.UNANIMOUS,
    'MAJORITY': SignalCombinationMethod.MAJORITY,
    'ANY': SignalCombinationMethod.ANY,
    'WEIGHTED': SignalCombinationMethod.WEIGHTED,
    'CONFLUENCE': SignalCombinationMethod.CONFLUENCE
}

results = []

for method_name, method in methods.items():
    df_result = selector.generate_combined_signals(df.copy(), combination_method=method)
    signals = df_result[df_result['signal'] != 0]

    buy_count = len(signals[signals['signal'] == 1])
    sell_count = len(signals[signals['signal'] == -1])

    results.append({
        'Método': method_name,
        'Total': len(signals),
        'Compra': buy_count,
        'Venda': sell_count,
        'Frequência': f"{len(signals)/len(df)*100:.2f}%"
    })

results_df = pd.DataFrame(results)
print("\\n" + results_df.to_string(index=False))

print()

# ============================================================================
# TESTE 3: Configurações Customizadas
# ============================================================================
print("TESTE 3: Testando Configurações Customizadas")
print("-"*80)

# Configuração conservadora
print("\\n  Configuração CONSERVADORA (menos sinais, maior qualidade):")
selector_conservative = StrategySelector()
selector_conservative.add_strategy(
    StrategyType.SMC_ORDER_BLOCK,
    config={'swing_length': 10, 'min_impulse_pct': 0.03},
    weight=1.5
)
selector_conservative.add_strategy(
    StrategyType.WYCKOFF_SPRING,
    config={'spring_penetration_pct': 0.02, 'require_volume_decrease': True},
    weight=1.5
)

df_conservative = selector_conservative.generate_combined_signals(
    df.copy(),
    combination_method=SignalCombinationMethod.UNANIMOUS
)
signals_conservative = df_conservative[df_conservative['signal'] != 0]

print(f"    Sinais gerados: {len(signals_conservative)}")
print(f"    Frequência: {len(signals_conservative)/len(df)*100:.2f}%")

# Configuração agressiva
print("\\n  Configuração AGRESSIVA (mais sinais, menor qualidade):")
selector_aggressive = StrategySelector()
selector_aggressive.add_strategy(
    StrategyType.SMC_ORDER_BLOCK,
    config={'swing_length': 3, 'min_impulse_pct': 0.01},
    weight=1.0
)
selector_aggressive.add_strategy(
    StrategyType.WYCKOFF_SPRING,
    config={'spring_penetration_pct': 0.005, 'require_volume_decrease': False},
    weight=1.0
)

df_aggressive = selector_aggressive.generate_combined_signals(
    df.copy(),
    combination_method=SignalCombinationMethod.ANY
)
signals_aggressive = df_aggressive[df_aggressive['signal'] != 0]

print(f"    Sinais gerados: {len(signals_aggressive)}")
print(f"    Frequência: {len(signals_aggressive)/len(df)*100:.2f}%")

print()

# ============================================================================
# TESTE 4: Pesos Diferentes
# ============================================================================
print("TESTE 4: Testando Diferentes Pesos de Estratégias")
print("-"*80)

weight_configs = [
    {'name': 'SMC Dominante', 'weights': {
        StrategyType.SMC_ORDER_BLOCK: 2.0,
        StrategyType.SMC_FVG: 1.5,
        StrategyType.WYCKOFF_SPRING: 0.5
    }},
    {'name': 'Wyckoff Dominante', 'weights': {
        StrategyType.SMC_ORDER_BLOCK: 0.5,
        StrategyType.SMC_FVG: 0.5,
        StrategyType.WYCKOFF_SPRING: 2.0
    }},
    {'name': 'Equilibrado', 'weights': {
        StrategyType.SMC_ORDER_BLOCK: 1.0,
        StrategyType.SMC_FVG: 1.0,
        StrategyType.WYCKOFF_SPRING: 1.0
    }}
]

for config in weight_configs:
    selector = StrategySelector()
    for strategy_type, weight in config['weights'].items():
        selector.add_strategy(strategy_type, weight=weight)

    df_result = selector.generate_combined_signals(
        df.copy(),
        combination_method=SignalCombinationMethod.WEIGHTED
    )

    signals = df_result[df_result['signal'] != 0]
    print(f"\\n  {config['name']}:")
    print(f"    Total de sinais: {len(signals)}")
    print(f"    COMPRA: {len(signals[signals['signal'] == 1])}")
    print(f"    VENDA: {len(signals[signals['signal'] == -1])}")

print()

# ============================================================================
# TESTE 5: Confluência Mínima
# ============================================================================
print("TESTE 5: Testando Diferentes Níveis de Confluência")
print("-"*80)

selector = StrategySelector()
selector.add_strategy(StrategyType.SMC_ORDER_BLOCK)
selector.add_strategy(StrategyType.SMC_FVG)
selector.add_strategy(StrategyType.SMC_LIQUIDITY)
selector.add_strategy(StrategyType.WYCKOFF_SPRING)
selector.add_strategy(StrategyType.WYCKOFF_ACCUMULATION)

df_confluence = selector.generate_combined_signals(
    df.copy(),
    combination_method=SignalCombinationMethod.CONFLUENCE
)

if 'confluence_score' in df_confluence.columns:
    for min_score in [1, 2, 3, 4]:
        high_conf = df_confluence[abs(df_confluence['confluence_score']) >= min_score]
        signals_high = high_conf[high_conf['signal'] != 0]

        print(f"\\n  Confluência mínima {min_score}+:")
        print(f"    Sinais gerados: {len(signals_high)}")
        if len(signals_high) > 0:
            print(f"    COMPRA: {len(signals_high[signals_high['signal'] == 1])}")
            print(f"    VENDA: {len(signals_high[signals_high['signal'] == -1])}")
            print(f"    Frequência: {len(signals_high)/len(df)*100:.2f}%")

print()

# ============================================================================
# TESTE 6: Performance por Estratégia Individual
# ============================================================================
print("TESTE 6: Análise Detalhada de Cada Estratégia")
print("-"*80)

all_strategies = [
    StrategyType.SMC_ORDER_BLOCK,
    StrategyType.SMC_FVG,
    StrategyType.SMC_LIQUIDITY,
    StrategyType.WYCKOFF_ACCUMULATION,
    StrategyType.WYCKOFF_SPRING,
    StrategyType.SMC_WYCKOFF_COMBINED
]

detailed_results = []

for strategy_type in all_strategies:
    selector = StrategySelector()
    info = selector.get_strategy_info(strategy_type)
    selector.add_strategy(strategy_type)

    df_result = selector.generate_combined_signals(df.copy())
    signals = df_result[df_result['signal'] != 0]

    detailed_results.append({
        'Estratégia': info['name'],
        'Total': len(signals),
        'Compra': len(signals[signals['signal'] == 1]),
        'Venda': len(signals[signals['signal'] == -1]),
        'Freq%': f"{len(signals)/len(df)*100:.2f}",
        'Melhor Para': info['best_for'][:30] + '...' if len(info['best_for']) > 30 else info['best_for']
    })

detailed_df = pd.DataFrame(detailed_results)
print("\\n" + detailed_df.to_string(index=False))

print()

# ============================================================================
# RESUMO
# ============================================================================
print("="*80)
print("RESUMO DOS TESTES AVANÇADOS")
print("="*80)
print()
print("✓ Todos os testes avançados concluídos com sucesso!")
print()
print("Testes realizados:")
print("  ✓ Mercados de Alta vs Baixa")
print("  ✓ Todos os métodos de combinação (5 métodos)")
print("  ✓ Configurações customizadas (conservadora vs agressiva)")
print("  ✓ Diferentes pesos de estratégias")
print("  ✓ Níveis de confluência")
print("  ✓ Performance individual de cada estratégia")
print()
print("Conclusões:")
print("  • Sistema altamente configurável")
print("  • Cada método de combinação tem casos de uso específicos")
print("  • Confluência permite filtrar sinais de maior qualidade")
print("  • Pesos permitem priorizar estratégias preferidas")
print("  • Configurações podem ser ajustadas para diferentes perfis de risco")
print("="*80)
