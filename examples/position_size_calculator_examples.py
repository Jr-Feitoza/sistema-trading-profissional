"""
Exemplos de uso do Position Size Calculator
Demonstra diferentes cenários de cálculo de tamanho de posição
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe,
    calculate_optimal_leverage,
    print_position_summary
)


def example_1_basic_long():
    """
    Exemplo 1: Cálculo básico para posição LONG

    Cenário:
    - Conta: $10,000
    - Arriscar: $10 para lucrar $30 (1:3)
    - Entry: $50,000 (BTC)
    - Timeframe: 15m
    """

    print("\n" + "="*80)
    print("EXEMPLO 1: Posição LONG Básica")
    print("="*80)

    print("\n📋 CENÁRIO:")
    print("  • Saldo da conta: $10,000")
    print("  • Arriscar: $10")
    print("  • Lucrar: $30")
    print("  • Entry: $50,000 (BTC)")
    print("  • Timeframe: 15 minutos")

    calculator = PositionSizeCalculator()

    params = PositionSizeParams(
        entry_price=50000,
        account_balance=10000,
        side=PositionSide.LONG,
        risk_amount_usdt=10,
        profit_target_usdt=30,
        timeframe=Timeframe.M15
    )

    result = calculator.calculate_position_size(params)
    print_position_summary(result)

    print("💡 ANÁLISE:")
    print(f"  • Para arriscar $10, você deve comprar {result.position_size:.6f} BTC")
    print(f"  • Valor da posição: ${result.position_value_usdt:,.2f}")
    print(f"  • Stop loss: ${result.stop_loss_price:,.2f} ({result.stop_loss_distance_pct:.2f}% abaixo)")
    print(f"  • Take profit: ${result.take_profit_price:,.2f} ({result.take_profit_distance_pct:.2f}% acima)")


def example_2_short_with_leverage():
    """
    Exemplo 2: Posição SHORT com leverage

    Cenário:
    - Conta: $5,000
    - Arriscar: $10 para lucrar $30
    - Entry: $50,000 (short BTC)
    - Leverage: 5x
    - Timeframe: 5m (mais volátil)
    """

    print("\n" + "="*80)
    print("EXEMPLO 2: Posição SHORT com Leverage 5x")
    print("="*80)

    print("\n📋 CENÁRIO:")
    print("  • Saldo da conta: $5,000")
    print("  • Arriscar: $10")
    print("  • Lucrar: $30")
    print("  • Entry: $50,000 (SHORT)")
    print("  • Leverage: 5x")
    print("  • Timeframe: 5 minutos (mais volátil)")

    calculator = PositionSizeCalculator()

    params = PositionSizeParams(
        entry_price=50000,
        account_balance=5000,
        side=PositionSide.SHORT,
        risk_amount_usdt=10,
        profit_target_usdt=30,
        timeframe=Timeframe.M5,  # Mais volátil, stops mais apertados
        leverage=5
    )

    result = calculator.calculate_position_size(params)
    print_position_summary(result)

    print("💡 ANÁLISE:")
    print(f"  • Com 5x leverage, você precisa de ${result.margin_required:,.2f} de margem")
    print(f"  • Isso é {(result.margin_required / params.account_balance * 100):.1f}% do seu saldo")
    print(f"  • Preço de liquidação estimado: ${result.liquidation_price:,.2f}")
    print(f"  • Cuidado: Timeframe 5m = stops mais apertados devido à volatilidade")


def example_3_risk_percentage():
    """
    Exemplo 3: Usando percentual de risco ao invés de valor fixo

    Cenário:
    - Arriscar 2% do saldo (ao invés de $10 fixo)
    - Adapta automaticamente o risco ao tamanho da conta
    """

    print("\n" + "="*80)
    print("EXEMPLO 3: Risk Percentage (2% do saldo)")
    print("="*80)

    print("\n📋 CENÁRIO:")
    print("  • Arriscar: 2% do saldo (adapta ao tamanho da conta)")
    print("  • Risk/Reward: 1:3")

    calculator = PositionSizeCalculator()

    # Testa com diferentes saldos
    balances = [5000, 10000, 20000]

    for balance in balances:
        print(f"\n💰 Saldo: ${balance:,}")
        print(f"   Risco: ${balance * 0.02:.2f} (2%)")

        params = PositionSizeParams(
            entry_price=50000,
            account_balance=balance,
            side=PositionSide.LONG,
            risk_percentage=2.0,  # 2% do saldo
            risk_reward_ratio=3.0,
            timeframe=Timeframe.M15
        )

        result = calculator.calculate_position_size(params)

        print(f"   Position: {result.position_size:.6f} BTC (${result.position_value_usdt:,.2f})")
        print(f"   Stop: ${result.stop_loss_price:,.2f}")
        print(f"   Target: ${result.take_profit_price:,.2f}")


def example_4_atr_based_stops():
    """
    Exemplo 4: Stops baseados em ATR (volatilidade)

    ATR ajusta o stop loss baseado na volatilidade real do ativo
    """

    print("\n" + "="*80)
    print("EXEMPLO 4: Stops Baseados em ATR")
    print("="*80)

    print("\n📋 CENÁRIO:")
    print("  • Usar ATR para calcular stops (adapta à volatilidade)")
    print("  • Comparar diferentes timeframes")

    calculator = PositionSizeCalculator()

    # ATR típico do BTC em diferentes timeframes
    atr_values = {
        Timeframe.M5: 150,   # 5m = mais volátil
        Timeframe.M15: 250,  # 15m
        Timeframe.H1: 500    # 1h = menos volátil
    }

    for tf, atr in atr_values.items():
        print(f"\n⏱️ Timeframe: {tf.value} | ATR: ${atr}")

        params = PositionSizeParams(
            entry_price=50000,
            account_balance=10000,
            side=PositionSide.LONG,
            risk_amount_usdt=10,
            profit_target_usdt=30,
            timeframe=tf,
            current_atr=atr
        )

        result = calculator.calculate_position_size(params)

        print(f"   Stop loss: ${result.stop_loss_price:,.2f} ({result.stop_loss_distance_pct:.2f}%)")
        print(f"   Position size: {result.position_size:.6f} BTC")
        print(f"   💡 ATR maior = stop mais largo = position menor (mesmo risco)")


def example_5_optimal_leverage():
    """
    Exemplo 5: Cálculo automático de leverage ótima

    Calcula a leverage necessária baseada na distância do stop
    """

    print("\n" + "="*80)
    print("EXEMPLO 5: Leverage Ótima (Calculada Automaticamente)")
    print("="*80)

    print("\n📋 CENÁRIO:")
    print("  • Sistema calcula leverage ideal baseado no stop")
    print("  • Objetivo: Perder no máximo 2% se stop for atingido")

    # Diferentes stops (% de distância)
    stop_distances = [
        (49500, "1.0%"),   # Stop apertado
        (49000, "2.0%"),   # Stop médio
        (48500, "3.0%"),   # Stop largo
    ]

    for stop_price, distance_label in stop_distances:
        leverage = calculate_optimal_leverage(
            entry_price=50000,
            stop_loss_price=stop_price,
            max_loss_pct=2.0
        )

        print(f"\n🎯 Stop: ${stop_price:,} ({distance_label} de distância)")
        print(f"   Leverage ótima: {leverage}x")
        print(f"   Lógica: Com {leverage}x leverage, perder {distance_label} = perder 2% do saldo")


def example_6_different_risk_rewards():
    """
    Exemplo 6: Comparando diferentes risk/reward ratios

    Testa 1:2, 1:3, 1:4 e mostra o impacto
    """

    print("\n" + "="*80)
    print("EXEMPLO 6: Comparação de Risk/Reward Ratios")
    print("="*80)

    print("\n📋 CENÁRIO:")
    print("  • Mesmo risco ($10)")
    print("  • Diferentes targets de lucro")

    calculator = PositionSizeCalculator()

    rr_ratios = [
        (20, 2.0),   # 1:2
        (30, 3.0),   # 1:3
        (40, 4.0),   # 1:4
    ]

    for profit_target, rr in rr_ratios:
        print(f"\n💰 Risk/Reward: 1:{rr} (Arriscar $10 para lucrar ${profit_target})")

        params = PositionSizeParams(
            entry_price=50000,
            account_balance=10000,
            side=PositionSide.LONG,
            risk_amount_usdt=10,
            profit_target_usdt=profit_target,
            timeframe=Timeframe.M15
        )

        result = calculator.calculate_position_size(params)

        print(f"   Stop: ${result.stop_loss_price:,.2f}")
        print(f"   Target: ${result.take_profit_price:,.2f}")
        print(f"   Distância do target: {result.take_profit_distance_pct:.2f}%")
        print(f"   Win rate necessário: {(1 / (rr + 1) * 100):.1f}% para breakeven")


def example_7_validation_warnings():
    """
    Exemplo 7: Sistema de validação e warnings

    Mostra quando o sistema detecta problemas
    """

    print("\n" + "="*80)
    print("EXEMPLO 7: Validação e Warnings")
    print("="*80)

    calculator = PositionSizeCalculator(max_risk_per_trade_pct=2.0)

    # Cenário 1: Risk muito alto
    print("\n⚠️ CENÁRIO 1: Risk muito alto (5% do saldo)")

    params = PositionSizeParams(
        entry_price=50000,
        account_balance=10000,
        side=PositionSide.LONG,
        risk_amount_usdt=500,  # 5% do saldo (muito alto!)
        profit_target_usdt=1500,
        timeframe=Timeframe.M15
    )

    result = calculator.calculate_position_size(params)

    if not result.is_valid:
        print("   ❌ POSIÇÃO INVÁLIDA")
        for warning in result.warnings:
            print(f"   {warning}")

    # Cenário 2: Leverage muito alto
    print("\n⚠️ CENÁRIO 2: Leverage muito alto + stop próximo da liquidação")

    params = PositionSizeParams(
        entry_price=50000,
        account_balance=1000,
        side=PositionSide.LONG,
        risk_amount_usdt=10,
        profit_target_usdt=30,
        timeframe=Timeframe.M15,
        leverage=20  # 20x leverage!
    )

    result = calculator.calculate_position_size(params)

    print(f"   Liquidação: ${result.liquidation_price:,.2f}")
    print(f"   Stop loss: ${result.stop_loss_price:,.2f}")

    if result.warnings:
        for warning in result.warnings:
            print(f"   {warning}")


def example_8_real_trading_scenario():
    """
    Exemplo 8: Cenário realista de trading

    Baseado em setup real de trading
    """

    print("\n" + "="*80)
    print("EXEMPLO 8: Cenário Realista de Trading")
    print("="*80)

    print("""
📊 SETUP DE TRADING:

   Estratégia: SMC Order Block + Wyckoff Spring
   Confluência: 3 conceitos concordam

   Análise:
   - BTC testou order block bullish em $49,500
   - Spring detectado (bear trap)
   - Volume de acumulação alto
   - RSI oversold no 15m

   Decisão: COMPRAR

   Conta: $10,000
   Risk: $20 (0.2% do saldo - conservador)
   Target: $60 (1:3 risk/reward)
   Timeframe: 15m
   ATR atual: $250
    """)

    calculator = PositionSizeCalculator()

    params = PositionSizeParams(
        entry_price=50000,
        account_balance=10000,
        side=PositionSide.LONG,
        risk_amount_usdt=20,
        profit_target_usdt=60,
        timeframe=Timeframe.M15,
        current_atr=250,  # ATR real
        leverage=1  # Sem leverage (conservador)
    )

    result = calculator.calculate_position_size(params)
    print_position_summary(result)

    print("📝 ORDEM A EXECUTAR:")
    print(f"   Tipo: LIMIT BUY")
    print(f"   Quantidade: {result.position_size:.6f} BTC")
    print(f"   Entry: ${result.entry_price:,.2f}")
    print(f"   Stop Loss: ${result.stop_loss_price:,.2f}")
    print(f"   Take Profit: ${result.take_profit_price:,.2f}")
    print(f"   Margem necessária: ${result.margin_required:,.2f}")
    print(f"\n✅ Posição válida e pronta para execução!")


def main():
    """Menu principal"""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           EXEMPLOS DO POSITION SIZE CALCULATOR                              ║
║                                                                              ║
║  Demonstra como calcular tamanho de posição baseado em risk/reward         ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    examples = {
        '1': ('Posição LONG básica', example_1_basic_long),
        '2': ('Posição SHORT com leverage', example_2_short_with_leverage),
        '3': ('Risk percentage (2% do saldo)', example_3_risk_percentage),
        '4': ('Stops baseados em ATR', example_4_atr_based_stops),
        '5': ('Leverage ótima (automática)', example_5_optimal_leverage),
        '6': ('Comparação de risk/reward ratios', example_6_different_risk_rewards),
        '7': ('Sistema de validação', example_7_validation_warnings),
        '8': ('Cenário realista de trading', example_8_real_trading_scenario),
    }

    print("\nEscolha um exemplo:")
    for key, (desc, _) in examples.items():
        print(f"{key} - {desc}")
    print("0 - Executar todos os exemplos")
    print()

    choice = input("Digite o número (ou Enter para sair): ").strip()

    if not choice:
        print("\nSaindo...")
        return

    try:
        if choice == '0':
            # Executar todos
            for key in sorted(examples.keys()):
                _, func = examples[key]
                func()
                input("\nPressione Enter para continuar...")
        elif choice in examples:
            _, func = examples[choice]
            func()
        else:
            print("Opção inválida!")

        print("\n\n✅ Exemplos concluídos!")

    except KeyboardInterrupt:
        print("\n\n⚠️ Execução interrompida.")
    except Exception as e:
        print(f"\n\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
