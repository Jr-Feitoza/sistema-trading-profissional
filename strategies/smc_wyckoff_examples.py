"""
Exemplos práticos de uso das estratégias SMC e Wyckoff
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Importa o sistema de seleção
from strategies.strategy_selector import StrategySelector, StrategyType, SignalCombinationMethod


def create_sample_data(days: int = 100) -> pd.DataFrame:
    """Cria dados de amostra para testes"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='1H')

    # Simula movimento de preço
    np.random.seed(42)
    price = 50000  # Preço inicial

    data = []
    for date in dates:
        # Movimento aleatório com tendência
        change_pct = np.random.randn() * 0.02
        price *= (1 + change_pct)

        # OHLC
        high = price * (1 + abs(np.random.randn()) * 0.01)
        low = price * (1 - abs(np.random.randn()) * 0.01)
        open_price = price * (1 + np.random.randn() * 0.005)
        close = price

        volume = abs(np.random.randn() * 1000000 + 5000000)

        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })

    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)

    return df


def example_1_single_strategy():
    """Exemplo 1: Usando uma única estratégia"""
    print("\n" + "="*80)
    print("EXEMPLO 1: Usando Estratégia Única - SMC Order Blocks")
    print("="*80 + "\n")

    # Cria dados
    df = create_sample_data(200)

    # Cria seletor
    selector = StrategySelector()

    # Adiciona apenas Order Blocks
    selector.add_strategy(StrategyType.SMC_ORDER_BLOCK)

    # Gera sinais
    df_result = selector.generate_combined_signals(df)

    # Mostra resultados
    signals = df_result[df_result['signal'] != 0]
    print(f"Total de sinais: {len(signals)}")
    print(f"Sinais de COMPRA: {len(signals[signals['signal'] == 1])}")
    print(f"Sinais de VENDA: {len(signals[signals['signal'] == -1])}")

    print("\nPrimeiros 5 sinais:")
    print(signals[['signal']].head())


def example_2_multiple_strategies():
    """Exemplo 2: Combinando múltiplas estratégias"""
    print("\n" + "="*80)
    print("EXEMPLO 2: Combinando Múltiplas Estratégias SMC")
    print("="*80 + "\n")

    df = create_sample_data(200)
    selector = StrategySelector()

    # Adiciona várias estratégias SMC
    selector.add_strategy(StrategyType.SMC_ORDER_BLOCK, weight=1.0)
    selector.add_strategy(StrategyType.SMC_FVG, weight=1.0)
    selector.add_strategy(StrategyType.SMC_LIQUIDITY, weight=0.8)

    # Mostra configuração
    config = selector.get_configuration_summary()
    print("Estratégias configuradas:")
    for strat in config['strategies']:
        print(f"  - {strat['name']} (peso: {strat['weight']})")

    # Gera sinais com MAJORITY method
    print("\nUsando método: MAJORITY")
    df_result = selector.generate_combined_signals(
        df,
        combination_method=SignalCombinationMethod.MAJORITY
    )

    signals = df_result[df_result['signal'] != 0]
    print(f"\nTotal de sinais: {len(signals)}")

    # Compara estratégias
    print("\nComparação de estratégias:")
    comparison = selector.compare_strategies(df)
    print(comparison.to_string(index=False))


def example_3_wyckoff_strategies():
    """Exemplo 3: Estratégias Wyckoff"""
    print("\n" + "="*80)
    print("EXEMPLO 3: Estratégias Wyckoff")
    print("="*80 + "\n")

    df = create_sample_data(300)  # Mais dados para Wyckoff
    selector = StrategySelector()

    # Adiciona estratégias Wyckoff
    selector.add_strategy(StrategyType.WYCKOFF_ACCUMULATION, weight=1.2)
    selector.add_strategy(StrategyType.WYCKOFF_SPRING, weight=1.0)

    print("Estratégias Wyckoff ativas:")
    config = selector.get_configuration_summary()
    for strat in config['strategies']:
        info = selector.get_strategy_info(
            StrategyType(strat['type'])
        )
        print(f"\n  {strat['name']}:")
        print(f"    Melhor para: {info['best_for']}")
        print(f"    Timeframe: {info['timeframe']}")

    # Gera sinais
    df_result = selector.generate_combined_signals(
        df,
        combination_method=SignalCombinationMethod.CONFLUENCE
    )

    # Mostra sinais de alta confluência
    if 'confluence_score' in df_result.columns:
        high_confluence = df_result[abs(df_result['confluence_score']) >= 2]
        print(f"\nSinais de alta confluência (2+ estratégias): {len(high_confluence)}")


def example_4_combined_smc_wyckoff():
    """Exemplo 4: Estratégia Combinada SMC + Wyckoff"""
    print("\n" + "="*80)
    print("EXEMPLO 4: Estratégia Combinada SMC + Wyckoff")
    print("="*80 + "\n")

    df = create_sample_data(250)
    selector = StrategySelector()

    # Usa a estratégia combinada
    selector.add_strategy(
        StrategyType.SMC_WYCKOFF_COMBINED,
        config={'min_confluence_score': 2}  # Requer confluência de 2 conceitos
    )

    print("Usando estratégia SMC + Wyckoff Combinada")
    print("Requer confluência de múltiplos conceitos (Order Blocks, FVG, Springs, etc.)\n")

    df_result = selector.generate_combined_signals(df)

    # Mostra estatísticas
    signals = df_result[df_result['signal'] != 0]
    print(f"Total de sinais gerados: {len(signals)}")

    # Se a estratégia fornece scores de confluência
    if 'bullish_score' in df_result.columns:
        avg_bullish_score = df_result[df_result['signal'] == 1]['bullish_score'].mean()
        avg_bearish_score = df_result[df_result['signal'] == -1]['bearish_score'].mean()

        print(f"Score médio de sinais bullish: {avg_bullish_score:.2f}")
        print(f"Score médio de sinais bearish: {abs(avg_bearish_score):.2f}")


def example_5_all_strategies_comparison():
    """Exemplo 5: Compara todas as estratégias"""
    print("\n" + "="*80)
    print("EXEMPLO 5: Comparação de Todas as Estratégias")
    print("="*80 + "\n")

    df = create_sample_data(300)

    # Lista todas as estratégias
    selector = StrategySelector()
    print("Estratégias disponíveis:\n")

    for strategy_type in StrategyType:
        info = selector.get_strategy_info(strategy_type)
        print(f"{info['name']}:")
        print(f"  Descrição: {info['description']}")
        print(f"  Melhor para: {info['best_for']}")
        print()

    # Adiciona todas
    print("\nAdicionando todas as estratégias...\n")
    for strategy_type in StrategyType:
        selector.add_strategy(strategy_type)

    # Compara
    print("Comparação de performance:")
    comparison = selector.compare_strategies(df)
    print(comparison.to_string(index=False))


def example_6_custom_configuration():
    """Exemplo 6: Configuração customizada"""
    print("\n" + "="*80)
    print("EXEMPLO 6: Configuração Customizada com Parâmetros")
    print("="*80 + "\n")

    df = create_sample_data(200)
    selector = StrategySelector()

    # Adiciona estratégia com configuração customizada
    print("Configurando SMC Order Blocks com parâmetros personalizados:\n")

    custom_config = {
        'swing_length': 10,  # Aumenta período de swing
        'min_impulse_pct': 0.03,  # 3% de impulso mínimo (mais rigoroso)
        'ob_validity_bars': 30  # Order blocks válidos por mais tempo
    }

    print(f"Configuração customizada:")
    for key, value in custom_config.items():
        print(f"  {key}: {value}")

    selector.add_strategy(
        StrategyType.SMC_ORDER_BLOCK,
        config=custom_config,
        weight=1.0
    )

    # Gera sinais
    df_result = selector.generate_combined_signals(df)
    signals = df_result[df_result['signal'] != 0]

    print(f"\nSinais gerados com configuração customizada: {len(signals)}")


def example_7_different_combination_methods():
    """Exemplo 7: Diferentes métodos de combinação"""
    print("\n" + "="*80)
    print("EXEMPLO 7: Comparando Métodos de Combinação de Sinais")
    print("="*80 + "\n")

    df = create_sample_data(200)
    selector = StrategySelector()

    # Adiciona 3 estratégias
    selector.add_strategy(StrategyType.SMC_ORDER_BLOCK)
    selector.add_strategy(StrategyType.SMC_FVG)
    selector.add_strategy(StrategyType.WYCKOFF_SPRING)

    methods = [
        SignalCombinationMethod.UNANIMOUS,
        SignalCombinationMethod.MAJORITY,
        SignalCombinationMethod.ANY,
        SignalCombinationMethod.CONFLUENCE
    ]

    print("Testando diferentes métodos de combinação:\n")

    for method in methods:
        df_result = selector.generate_combined_signals(df, combination_method=method)
        signals = df_result[df_result['signal'] != 0]

        print(f"{method.value.upper()}: {len(signals)} sinais")

    print("\nDescrição dos métodos:")
    print("  UNANIMOUS: Todas as estratégias devem concordar")
    print("  MAJORITY: Maioria das estratégias deve concordar")
    print("  ANY: Qualquer estratégia pode gerar sinal")
    print("  CONFLUENCE: Score baseado em quantas concordam")


def example_8_backtest_integration():
    """Exemplo 8: Integração com Backtest"""
    print("\n" + "="*80)
    print("EXEMPLO 8: Preparando para Backtest")
    print("="*80 + "\n")

    df = create_sample_data(500)
    selector = StrategySelector()

    # Configura estratégia para backtest
    print("Configurando portfólio de estratégias para backtest:\n")

    # Adiciona estratégias com pesos diferentes
    selector.add_strategy(StrategyType.SMC_WYCKOFF_COMBINED, weight=1.5)
    selector.add_strategy(StrategyType.WYCKOFF_SPRING, weight=1.0)
    selector.add_strategy(StrategyType.SMC_LIQUIDITY, weight=0.8)

    config = selector.get_configuration_summary()
    print(f"Total de estratégias: {config['total_strategies']}")
    print("\nEstratégias no portfólio:")
    for strat in config['strategies']:
        print(f"  - {strat['name']} (peso: {strat['weight']})")

    # Gera sinais para backtest
    df_result = selector.generate_combined_signals(
        df,
        combination_method=SignalCombinationMethod.WEIGHTED
    )

    # Salva resultados
    print("\nDados preparados para backtest:")
    print(f"  Período: {df_result.index[0]} até {df_result.index[-1]}")
    print(f"  Total de barras: {len(df_result)}")
    print(f"  Sinais gerados: {len(df_result[df_result['signal'] != 0])}")

    # Mostra colunas disponíveis
    signal_columns = [col for col in df_result.columns if 'signal' in col]
    print(f"  Colunas de sinal: {len(signal_columns)}")

    print("\nPróximo passo: Usar este DataFrame no BacktestEngine!")


def main():
    """Executa todos os exemplos"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║            EXEMPLOS DE ESTRATÉGIAS SMC E WYCKOFF                             ║
║                                                                              ║
║  Demonstra como usar as estratégias Smart Money Concepts e Wyckoff          ║
║  individualmente e combinadas.                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Pergunta qual exemplo executar
        print("\nEscolha um exemplo para executar:")
        print("1 - Estratégia única (SMC Order Blocks)")
        print("2 - Múltiplas estratégias SMC combinadas")
        print("3 - Estratégias Wyckoff")
        print("4 - Estratégia combinada SMC + Wyckoff")
        print("5 - Comparação de todas as estratégias")
        print("6 - Configuração customizada")
        print("7 - Métodos de combinação de sinais")
        print("8 - Integração com Backtest")
        print("0 - Executar todos os exemplos")

        choice = input("\nDigite o número (ou Enter para sair): ").strip()

        examples = {
            '1': example_1_single_strategy,
            '2': example_2_multiple_strategies,
            '3': example_3_wyckoff_strategies,
            '4': example_4_combined_smc_wyckoff,
            '5': example_5_all_strategies_comparison,
            '6': example_6_custom_configuration,
            '7': example_7_different_combination_methods,
            '8': example_8_backtest_integration,
        }

        if choice == '0':
            # Executar todos
            for example_func in examples.values():
                example_func()
                print("\n" + "-"*80)
                input("\nPressione Enter para continuar...")
        elif choice in examples:
            examples[choice]()
        elif choice:
            print("Opção inválida!")

        print("\n\n✓ Exemplos concluídos!")

    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
    except Exception as e:
        print(f"\n\nErro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
