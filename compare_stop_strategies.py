"""
Script de Comparação de Estratégias de Stop Loss
Compara resultados com: Stop fixo, Breakeven, Trailing Stop e combinações
"""

import pandas as pd
import sys
from datetime import datetime

# Adiciona path para imports
sys.path.append('.')

from backtest.enhanced_backtest_runner import (
    EnhancedBacktestRunner,
    print_enhanced_metrics,
    Timeframe
)
from strategies.strategy_selector import (
    StrategySelector,
    StrategyType,
    SignalCombinationMethod
)
from run_historical_backtest import HistoricalDataGenerator


def run_comparison_backtest(
    df: pd.DataFrame,
    strategy_name: str = "SMC+Wyckoff Combined",
    risk_reward_ratio: float = 3.0,
    use_leverage: bool = False
):
    """
    Executa backtest com 4 configurações diferentes de stop management

    Configurações testadas:
    1. Stop Fixo: Apenas stop loss e take profit fixos
    2. Breakeven: Stop fixo + breakeven após 1R
    3. Trailing: Stop fixo + trailing após 1.5R
    4. Breakeven + Trailing: Combinação de ambos

    Args:
        df: DataFrame com dados históricos
        strategy_name: Nome da estratégia a testar
        risk_reward_ratio: Ratio de risk/reward (3.0 = 1:3)
        use_leverage: Se deve usar leverage
    """

    print(f"\n{'='*80}")
    print(f"COMPARAÇÃO DE ESTRATÉGIAS DE STOP MANAGEMENT")
    print(f"{'='*80}")
    print(f"\nEstratégia: {strategy_name}")
    print(f"Risk/Reward: 1:{risk_reward_ratio}")
    print(f"Leverage: {'SIM' if use_leverage else 'NÃO'}")
    print(f"Período: {df.index[0]} até {df.index[-1]}")
    print(f"Total de barras: {len(df)}")
    print(f"\n{'='*80}\n")

    # Gera sinais da estratégia
    selector = StrategySelector()
    selector.add_strategy(
        StrategyType.SMC_WYCKOFF_COMBINED,
        config={'min_confluence_score': 2}
    )
    df_signals = selector.generate_combined_signals(df.copy())

    total_signals = len(df_signals[df_signals['signal'] != 0])
    print(f"📊 Sinais gerados pela estratégia: {total_signals}\n")

    # Configurações a testar
    configs = [
        {
            'name': '1. Stop Fixo (Sem BE/Trailing)',
            'use_breakeven': False,
            'use_trailing_stop': False
        },
        {
            'name': '2. Breakeven (após 1R)',
            'use_breakeven': True,
            'breakeven_trigger_rr': 1.0,
            'use_trailing_stop': False
        },
        {
            'name': '3. Trailing Stop (após 1.5R)',
            'use_breakeven': False,
            'use_trailing_stop': True,
            'trailing_stop_activation_rr': 1.5
        },
        {
            'name': '4. Breakeven + Trailing',
            'use_breakeven': True,
            'breakeven_trigger_rr': 1.0,
            'use_trailing_stop': True,
            'trailing_stop_activation_rr': 1.5
        }
    ]

    results = []

    # Testa cada configuração
    for config in configs:
        print(f"\n{'─'*80}")
        print(f"🧪 TESTANDO: {config['name']}")
        print(f"{'─'*80}")

        # Cria runner com configuração
        runner = EnhancedBacktestRunner(
            initial_capital=10000,
            risk_per_trade_usdt=10,
            profit_target_usdt=30,
            risk_reward_ratio=risk_reward_ratio,
            use_leverage=use_leverage,
            max_leverage=10,
            timeframe=Timeframe.M15,
            use_atr_stops=True,
            use_breakeven=config.get('use_breakeven', False),
            breakeven_trigger_rr=config.get('breakeven_trigger_rr', 1.0),
            use_trailing_stop=config.get('use_trailing_stop', False),
            trailing_stop_activation_rr=config.get('trailing_stop_activation_rr', 1.5),
            trailing_stop_distance_atr=2.0,
            trailing_stop_distance_pct=0.01,
            commission=0.001,
            slippage=0.0005
        )

        # Executa backtest
        metrics = runner.run_backtest(
            df_signals.copy(),
            strategy_name=config['name']
        )

        # Imprime resultados
        print_enhanced_metrics(metrics)

        # Armazena para comparação
        results.append({
            'Configuração': config['name'],
            'Trades': metrics['total_trades'],
            'Win%': f"{metrics['win_rate']:.1f}%",
            'Retorno': f"${metrics['total_return']:.0f}",
            'Retorno%': f"{metrics['total_return_pct']:.1f}%",
            'PF': f"{metrics['profit_factor']:.2f}",
            'Sharpe': f"{metrics['sharpe_ratio']:.2f}",
            'MaxDD%': f"{metrics['max_drawdown']:.1f}%",
            'R:R Médio': f"1:{metrics['avg_rr_realized']:.1f}",
            'BE Usado': metrics['breakeven_used_count'],
            'Trail Usado': metrics['trailing_used_count'],
            'TP Hit': metrics['took_profit_count'],
            'Stop Hit': metrics['stopped_out_count']
        })

    # Comparação final
    print(f"\n\n{'='*80}")
    print("📊 COMPARAÇÃO FINAL DE TODAS AS CONFIGURAÇÕES")
    print(f"{'='*80}\n")

    comparison_df = pd.DataFrame(results)
    print(comparison_df.to_string(index=False))

    print(f"\n{'='*80}")
    print("💡 INSIGHTS E RECOMENDAÇÕES")
    print(f"{'='*80}\n")

    # Análise dos resultados
    returns = [float(r['Retorno'].replace('$', '').replace(',', '')) for r in results]
    best_idx = returns.index(max(returns))
    worst_idx = returns.index(min(returns))

    print(f"✅ MELHOR CONFIGURAÇÃO: {results[best_idx]['Configuração']}")
    print(f"   Retorno: {results[best_idx]['Retorno']} ({results[best_idx]['Retorno%']})")
    print(f"   Profit Factor: {results[best_idx]['PF']}")
    print(f"   Max Drawdown: {results[best_idx]['MaxDD%']}")

    print(f"\n❌ PIOR CONFIGURAÇÃO: {results[worst_idx]['Configuração']}")
    print(f"   Retorno: {results[worst_idx]['Retorno']} ({results[worst_idx]['Retorno%']})")

    # Análise de breakeven
    be_configs = [r for r in results if r['BE Usado'] > 0]
    if be_configs:
        print(f"\n🔄 IMPACTO DO BREAKEVEN:")
        print(f"   Configurações que usaram BE: {len(be_configs)}")
        for config in be_configs:
            print(f"   • {config['Configuração']}: {config['BE Usado']} trades movidos para BE")

    # Análise de trailing
    trail_configs = [r for r in results if r['Trail Usado'] > 0]
    if trail_configs:
        print(f"\n📈 IMPACTO DO TRAILING STOP:")
        print(f"   Configurações que usaram Trailing: {len(trail_configs)}")
        for config in trail_configs:
            print(f"   • {config['Configuração']}: {config['Trail Usado']} trades com trailing ativo")

    print(f"\n{'='*80}\n")

    return results


def test_different_risk_rewards():
    """Testa diferentes ratios de risk/reward"""

    print(f"\n{'='*100}")
    print(f"TESTE DE DIFERENTES RISK/REWARD RATIOS")
    print(f"{'='*100}\n")

    # Gera dados
    print("📊 Gerando dados históricos...")
    data_gen = HistoricalDataGenerator(days=365)
    df = data_gen.generate_trending_market(trend='mixed')
    print(f"✓ {len(df)} barras geradas\n")

    risk_rewards = [2.0, 3.0, 4.0]
    all_results = []

    for rr in risk_rewards:
        print(f"\n{'='*100}")
        print(f"TESTANDO RISK/REWARD 1:{rr}")
        print(f"{'='*100}\n")

        results = run_comparison_backtest(
            df.copy(),
            risk_reward_ratio=rr,
            use_leverage=False
        )

        # Adiciona RR aos resultados
        for r in results:
            r['R:R Target'] = f"1:{rr}"
            all_results.append(r)

    # Comparação final de todos
    print(f"\n\n{'='*100}")
    print("🎯 COMPARAÇÃO FINAL: TODAS AS CONFIGURAÇÕES E RISK/REWARDS")
    print(f"{'='*100}\n")

    all_df = pd.DataFrame(all_results)
    print(all_df.to_string(index=False))

    print(f"\n{'='*100}\n")


def test_with_and_without_leverage():
    """Testa com e sem leverage"""

    print(f"\n{'='*100}")
    print(f"TESTE COM E SEM LEVERAGE")
    print(f"{'='*100}\n")

    # Gera dados
    print("📊 Gerando dados históricos...")
    data_gen = HistoricalDataGenerator(days=365)
    df = data_gen.generate_trending_market(trend='mixed')
    print(f"✓ {len(df)} barras geradas\n")

    # Teste sem leverage
    print("\n" + "="*100)
    print("SEM LEVERAGE (1x)")
    print("="*100)
    results_no_lev = run_comparison_backtest(
        df.copy(),
        risk_reward_ratio=3.0,
        use_leverage=False
    )

    # Teste com leverage
    print("\n" + "="*100)
    print("COM LEVERAGE (até 10x)")
    print("="*100)
    results_with_lev = run_comparison_backtest(
        df.copy(),
        risk_reward_ratio=3.0,
        use_leverage=True
    )

    # Comparação
    print(f"\n\n{'='*100}")
    print("⚖️ COMPARAÇÃO: LEVERAGE vs SEM LEVERAGE")
    print(f"{'='*100}\n")

    print("Melhores configurações:\n")
    print("SEM LEVERAGE:")
    best_no_lev = max(results_no_lev, key=lambda x: float(x['Retorno'].replace('$', '').replace(',', '')))
    print(f"  {best_no_lev['Configuração']}: {best_no_lev['Retorno']} ({best_no_lev['Retorno%']})")

    print("\nCOM LEVERAGE:")
    best_with_lev = max(results_with_lev, key=lambda x: float(x['Retorno'].replace('$', '').replace(',', '')))
    print(f"  {best_with_lev['Configuração']}: {best_with_lev['Retorno']} ({best_with_lev['Retorno%']})")

    print(f"\n{'='*100}\n")


def main():
    """Menu principal"""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║        COMPARAÇÃO DE ESTRATÉGIAS DE STOP MANAGEMENT                         ║
║                                                                              ║
║  Testa diferentes configurações de stop loss para encontrar a melhor        ║
║  combinação de breakeven e trailing stop.                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    print("Escolha um teste:")
    print("1 - Comparação básica (stop fixo vs breakeven vs trailing)")
    print("2 - Teste de diferentes risk/reward ratios (1:2, 1:3, 1:4)")
    print("3 - Teste com e sem leverage")
    print("4 - Executar todos os testes")
    print()

    choice = input("Digite sua escolha (ou Enter para sair): ").strip()

    if not choice:
        print("\nSaindo...")
        return

    # Gera dados
    print("\n📊 Gerando dados históricos (1 ano)...")
    data_gen = HistoricalDataGenerator(days=365)
    df = data_gen.generate_trending_market(trend='mixed')
    print(f"✓ {len(df)} barras geradas")
    print(f"  Período: {df.index[0]} até {df.index[-1]}")
    print(f"  Variação do mercado: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%\n")

    try:
        if choice == '1':
            run_comparison_backtest(df, risk_reward_ratio=3.0, use_leverage=False)

        elif choice == '2':
            test_different_risk_rewards()

        elif choice == '3':
            test_with_and_without_leverage()

        elif choice == '4':
            print("\n🚀 EXECUTANDO TODOS OS TESTES...\n")
            run_comparison_backtest(df.copy(), risk_reward_ratio=3.0, use_leverage=False)
            test_different_risk_rewards()
            test_with_and_without_leverage()

        else:
            print("Opção inválida!")

        print("\n✅ TESTES CONCLUÍDOS!")

    except KeyboardInterrupt:
        print("\n\n⚠️ Execução interrompida pelo usuário.")
    except Exception as e:
        print(f"\n\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
