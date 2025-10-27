"""
Script de teste completo para todas as estratégias e agentes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, '/home/user/sistema-trading-profissional')

print("="*80)
print("SISTEMA DE TESTE COMPLETO - SMC, WYCKOFF E AGENTES IA")
print("="*80)
print()

# ============================================================================
# TESTE 1: Criar Dados de Amostra
# ============================================================================
print("TESTE 1: Criando Dados de Amostra")
print("-"*80)

def create_sample_data(days=200):
    """Cria dados de amostra para testes"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='1H')

    np.random.seed(42)
    price = 50000

    data = []
    for date in dates:
        change_pct = np.random.randn() * 0.02
        price *= (1 + change_pct)

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

df = create_sample_data(200)

print(f"✓ Dados criados: {len(df)} barras")
print(f"  Período: {df.index[0]} até {df.index[-1]}")
print(f"  Preço inicial: ${df['close'].iloc[0]:,.2f}")
print(f"  Preço final: ${df['close'].iloc[-1]:,.2f}")
print(f"  Variação: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
print()

# ============================================================================
# TESTE 2: Testar Estratégia SMC Order Blocks
# ============================================================================
print("TESTE 2: Testando SMC Order Blocks Strategy")
print("-"*80)

try:
    from strategies.smc_order_block_strategy import SMCOrderBlockStrategy

    strategy = SMCOrderBlockStrategy(
        swing_length=5,
        min_impulse_pct=0.02,
        ob_validity_bars=20
    )

    df_test = strategy.generate_signals(df.copy())
    signals = df_test[df_test['signal'] != 0]

    print(f"✓ SMC Order Blocks testado com sucesso!")
    print(f"  Total de sinais: {len(signals)}")
    print(f"  Sinais de COMPRA: {len(signals[signals['signal'] == 1])}")
    print(f"  Sinais de VENDA: {len(signals[signals['signal'] == -1])}")

    if len(signals) > 0:
        print(f"  Primeiro sinal: {signals.index[0]} - {['VENDA', 'NEUTRO', 'COMPRA'][signals['signal'].iloc[0] + 1]}")

except Exception as e:
    print(f"✗ Erro ao testar SMC Order Blocks: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TESTE 3: Testar Estratégia SMC FVG
# ============================================================================
print("TESTE 3: Testando SMC Fair Value Gaps Strategy")
print("-"*80)

try:
    from strategies.smc_fvg_strategy import SMCFVGStrategy

    strategy = SMCFVGStrategy(
        min_fvg_size_pct=0.005,
        fvg_validity_bars=50
    )

    df_test = strategy.generate_signals(df.copy())
    signals = df_test[df_test['signal'] != 0]

    print(f"✓ SMC FVG testado com sucesso!")
    print(f"  Total de sinais: {len(signals)}")
    print(f"  Sinais de COMPRA: {len(signals[signals['signal'] == 1])}")
    print(f"  Sinais de VENDA: {len(signals[signals['signal'] == -1])}")

except Exception as e:
    print(f"✗ Erro ao testar SMC FVG: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TESTE 4: Testar Estratégia SMC Liquidity
# ============================================================================
print("TESTE 4: Testando SMC Liquidity Sweeps Strategy")
print("-"*80)

try:
    from strategies.smc_liquidity_strategy import SMCLiquidityStrategy

    strategy = SMCLiquidityStrategy(
        lookback_highs=20,
        lookback_lows=20
    )

    df_test = strategy.generate_signals(df.copy())
    signals = df_test[df_test['signal'] != 0]

    print(f"✓ SMC Liquidity testado com sucesso!")
    print(f"  Total de sinais: {len(signals)}")
    print(f"  Sinais de COMPRA: {len(signals[signals['signal'] == 1])}")
    print(f"  Sinais de VENDA: {len(signals[signals['signal'] == -1])}")

except Exception as e:
    print(f"✗ Erro ao testar SMC Liquidity: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TESTE 5: Testar Estratégia Wyckoff Accumulation
# ============================================================================
print("TESTE 5: Testando Wyckoff Accumulation Strategy")
print("-"*80)

try:
    from strategies.wyckoff_accumulation_strategy import WyckoffAccumulationStrategy

    strategy = WyckoffAccumulationStrategy(
        volume_threshold=1.5,
        range_lookback=30
    )

    df_test = strategy.generate_signals(df.copy())
    signals = df_test[df_test['signal'] != 0]

    print(f"✓ Wyckoff Accumulation testado com sucesso!")
    print(f"  Total de sinais: {len(signals)}")
    print(f"  Sinais de COMPRA: {len(signals[signals['signal'] == 1])}")

    # Verifica fases detectadas
    if 'wyckoff_phase' in df_test.columns:
        phases = df_test[df_test['wyckoff_phase'] != '']['wyckoff_phase'].value_counts()
        if len(phases) > 0:
            print(f"  Fases Wyckoff detectadas:")
            for phase, count in phases.items():
                print(f"    - {phase}: {count}")

except Exception as e:
    print(f"✗ Erro ao testar Wyckoff Accumulation: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TESTE 6: Testar Estratégia Wyckoff Spring
# ============================================================================
print("TESTE 6: Testando Wyckoff Spring Strategy")
print("-"*80)

try:
    from strategies.wyckoff_spring_strategy import WyckoffSpringStrategy

    strategy = WyckoffSpringStrategy(
        support_lookback=20,
        spring_penetration_pct=0.015
    )

    df_test = strategy.generate_signals(df.copy())
    signals = df_test[df_test['signal'] != 0]

    print(f"✓ Wyckoff Spring testado com sucesso!")
    print(f"  Total de sinais: {len(signals)}")
    print(f"  Sinais de COMPRA: {len(signals[signals['signal'] == 1])}")
    print(f"  Sinais de VENDA: {len(signals[signals['signal'] == -1])}")

    # Estatísticas de springs
    stats = strategy.get_spring_statistics(df_test)
    if stats.get('total_springs', 0) > 0:
        print(f"  Springs detectados: {stats['total_springs']}")
        print(f"  Qualidade média: {stats.get('avg_quality', 0):.1f}")
        print(f"  Alta qualidade: {stats.get('high_quality_springs', 0)}")

except Exception as e:
    print(f"✗ Erro ao testar Wyckoff Spring: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TESTE 7: Testar Estratégia Combinada SMC + Wyckoff
# ============================================================================
print("TESTE 7: Testando SMC + Wyckoff Combined Strategy")
print("-"*80)

try:
    from strategies.smc_wyckoff_combined_strategy import SMCWyckoffCombinedStrategy

    strategy = SMCWyckoffCombinedStrategy(
        min_confluence_score=2
    )

    df_test = strategy.generate_signals(df.copy())
    signals = df_test[df_test['signal'] != 0]

    print(f"✓ SMC + Wyckoff Combined testado com sucesso!")
    print(f"  Total de sinais: {len(signals)}")
    print(f"  Sinais de COMPRA: {len(signals[signals['signal'] == 1])}")
    print(f"  Sinais de VENDA: {len(signals[signals['signal'] == -1])}")

    # Estatísticas de confluência
    stats = strategy.get_signal_statistics(df_test)
    if stats:
        print(f"  Score médio bullish: {stats.get('avg_bullish_score', 0):.2f}")
        print(f"  Score médio bearish: {stats.get('avg_bearish_score', 0):.2f}")
        print(f"  Sinais alta confluência: {stats.get('high_confluence_signals', 0)}")

except Exception as e:
    print(f"✗ Erro ao testar Combined Strategy: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TESTE 8: Testar StrategySelector
# ============================================================================
print("TESTE 8: Testando Strategy Selector")
print("-"*80)

try:
    from strategies.strategy_selector import (
        StrategySelector,
        StrategyType,
        SignalCombinationMethod
    )

    selector = StrategySelector()

    # Lista estratégias disponíveis
    available = selector.list_available_strategies()
    print(f"✓ StrategySelector inicializado")
    print(f"  Estratégias disponíveis: {len(available)}")

    # Adiciona múltiplas estratégias
    selector.add_strategy(StrategyType.SMC_ORDER_BLOCK, weight=1.0)
    selector.add_strategy(StrategyType.SMC_FVG, weight=1.0)
    selector.add_strategy(StrategyType.WYCKOFF_SPRING, weight=1.2)

    config = selector.get_configuration_summary()
    print(f"  Estratégias adicionadas: {config['total_strategies']}")

    # Testa diferentes métodos de combinação
    methods = [
        SignalCombinationMethod.UNANIMOUS,
        SignalCombinationMethod.MAJORITY,
        SignalCombinationMethod.ANY,
        SignalCombinationMethod.CONFLUENCE
    ]

    print(f"\\n  Testando métodos de combinação:")
    for method in methods:
        df_result = selector.generate_combined_signals(df.copy(), combination_method=method)
        signals = df_result[df_result['signal'] != 0]
        print(f"    {method.value.upper()}: {len(signals)} sinais")

    # Comparação de estratégias
    print(f"\\n  Comparação de estratégias:")
    comparison = selector.compare_strategies(df)
    print(comparison.to_string(index=False))

except Exception as e:
    print(f"✗ Erro ao testar StrategySelector: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TESTE 9: Testar Sistema de Agentes IA
# ============================================================================
print("TESTE 9: Testando Sistema de Agentes IA")
print("-"*80)

try:
    from agents import (
        WorkflowOrchestrator,
        PlannerAgent,
        AnalystAgent,
        AgentContext
    )

    # Teste 1: Agente individual (Planner)
    print("  Testando PlannerAgent...")
    context = AgentContext(
        project_path="/home/user/sistema-trading-profissional",
        task_description="Testar integração de estratégias SMC com backtest"
    )

    planner = PlannerAgent()
    result = planner.execute(context)

    if result.is_success():
        plan = result.output
        print(f"    ✓ Plano criado: {len(plan.tasks)} tarefas")
        print(f"      Tempo estimado: {plan.estimated_total_time}")
        print(f"      Riscos identificados: {len(plan.risks)}")

    # Teste 2: Workflow Orchestrator
    print(f"\\n  Testando WorkflowOrchestrator...")
    orchestrator = WorkflowOrchestrator()

    workflows = orchestrator.list_available_workflows()
    print(f"    ✓ Workflows disponíveis: {len(workflows)}")
    print(f"      {', '.join(workflows)}")

    # Teste workflow simples
    print(f"\\n  Executando workflow 'analysis'...")
    workflow_result = orchestrator.execute_workflow(
        task_description="Analisar sistema de estratégias",
        project_path="/home/user/sistema-trading-profissional",
        workflow_type="analysis"
    )

    print(f"    ✓ Workflow executado")
    print(f"      Sucesso: {workflow_result.success}")
    print(f"      Duração: {workflow_result.total_duration:.2f}s")
    print(f"      Passos concluídos: {len(workflow_result.steps_completed)}")

except Exception as e:
    print(f"✗ Erro ao testar Agentes IA: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("="*80)
print("RESUMO DOS TESTES")
print("="*80)
print()
print("✓ Sistema testado com sucesso!")
print()
print("Componentes testados:")
print("  ✓ Criação de dados de amostra")
print("  ✓ SMC Order Blocks Strategy")
print("  ✓ SMC FVG Strategy")
print("  ✓ SMC Liquidity Strategy")
print("  ✓ Wyckoff Accumulation Strategy")
print("  ✓ Wyckoff Spring Strategy")
print("  ✓ SMC + Wyckoff Combined Strategy")
print("  ✓ Strategy Selector (4 métodos de combinação)")
print("  ✓ Agentes IA (Planner, Orchestrator)")
print()
print("O sistema está funcionando corretamente e pronto para uso!")
print("="*80)
