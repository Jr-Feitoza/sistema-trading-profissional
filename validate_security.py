#!/usr/bin/env python3
"""
Sistema de Validação de Segurança - Trading Profissional

Este script demonstra todas as validações de segurança do sistema:
- Warnings em tempo real
- Verificação de margem até liquidação
- Validação de posição (segura vs perigosa)
- Cálculos de risco detalhados
- Rejeição de posições inválidas

Autor: AI Agent System
Data: 2025-11-06
"""

import sys
sys.path.insert(0, '.')

from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe
)
from typing import List, Dict
import time


class SecurityValidator:
    """Valida segurança de posições de trading"""

    def __init__(self):
        self.calculator = PositionSizeCalculator()
        self.warning_count = 0
        self.error_count = 0

    def print_header(self, title: str):
        """Imprime header formatado"""
        print("\n" + "="*80)
        print(f"🔒 {title}")
        print("="*80)

    def print_subheader(self, title: str):
        """Imprime subheader"""
        print("\n" + "─"*80)
        print(f"📋 {title}")
        print("─"*80)

    def print_warning(self, message: str):
        """Imprime warning"""
        self.warning_count += 1
        print(f"⚠️  WARNING: {message}")

    def print_error(self, message: str):
        """Imprime erro"""
        self.error_count += 1
        print(f"❌ ERROR: {message}")

    def print_success(self, message: str):
        """Imprime sucesso"""
        print(f"✅ {message}")

    def print_info(self, message: str):
        """Imprime info"""
        print(f"ℹ️  {message}")

    def validate_position_safety(
        self,
        params: PositionSizeParams,
        scenario_name: str
    ) -> Dict:
        """
        Valida segurança de uma posição

        Retorna dict com:
        - is_valid: bool
        - result: PositionSizeResult
        - warnings: List[str]
        - errors: List[str]
        """
        self.print_subheader(f"CENÁRIO: {scenario_name}")

        # Mostrar parâmetros
        print(f"\n📊 PARÂMETROS:")
        print(f"   Entry Price: ${params.entry_price:,.2f}")
        print(f"   Account Balance: ${params.account_balance:,.2f}")
        print(f"   Side: {params.side.value}")

        if params.risk_amount_usdt:
            print(f"   Risk Amount: ${params.risk_amount_usdt:.2f}")
        if params.profit_target_usdt:
            print(f"   Profit Target: ${params.profit_target_usdt:.2f}")
        if params.risk_reward_ratio:
            print(f"   R:R Ratio: 1:{params.risk_reward_ratio}")

        print(f"   Timeframe: {params.timeframe.value}")
        print(f"   Leverage: {params.leverage}x")

        if params.stop_loss_price:
            print(f"   Stop Loss (manual): ${params.stop_loss_price:,.2f}")
        if params.take_profit_price:
            print(f"   Take Profit (manual): ${params.take_profit_price:,.2f}")

        # Calcular posição
        print(f"\n🔄 Calculando posição...")

        try:
            result = self.calculator.calculate_position_size(params)

            # Mostrar resultados
            print(f"\n💰 RESULTADO:")
            print(f"   Position Size: {result.position_size:.6f} BTC")
            print(f"   Position Value: ${result.position_value:,.2f}")
            print(f"   Margin Required: ${result.margin_required:,.2f}")
            print(f"   Stop Loss: ${result.stop_loss_price:,.2f}")
            print(f"   Take Profit: ${result.take_profit_price:,.2f}")

            # Calcular distâncias
            if params.side == PositionSide.LONG:
                stop_distance_pct = ((params.entry_price - result.stop_loss_price) /
                                    params.entry_price * 100)
                tp_distance_pct = ((result.take_profit_price - params.entry_price) /
                                  params.entry_price * 100)
            else:
                stop_distance_pct = ((result.stop_loss_price - params.entry_price) /
                                    params.entry_price * 100)
                tp_distance_pct = ((params.entry_price - result.take_profit_price) /
                                  params.entry_price * 100)

            print(f"\n📏 DISTÂNCIAS:")
            print(f"   Stop Distance: {stop_distance_pct:.2f}%")
            print(f"   TP Distance: {tp_distance_pct:.2f}%")

            # Análise de risco
            print(f"\n⚖️  ANÁLISE DE RISCO:")
            print(f"   Risk Amount: ${result.risk_amount:,.2f} ({result.risk_percentage_of_account:.2f}% da conta)")
            print(f"   Potential Profit: ${result.potential_profit:,.2f} ({result.profit_percentage_of_account:.2f}% da conta)")
            print(f"   R:R Ratio: 1:{result.actual_risk_reward_ratio:.2f}")

            # VALIDAÇÕES DE SEGURANÇA
            warnings = []
            errors = []

            # 1. Verificar risco percentual
            print(f"\n🔍 VALIDAÇÕES DE SEGURANÇA:")
            print(f"\n1️⃣  Verificando risco percentual...")

            if result.risk_percentage_of_account > 2.0:
                self.print_error(f"Risco muito alto: {result.risk_percentage_of_account:.2f}% (máx recomendado: 2%)")
                errors.append("risk_too_high")
            elif result.risk_percentage_of_account > 1.0:
                self.print_warning(f"Risco moderado: {result.risk_percentage_of_account:.2f}% (recomendado: <1%)")
                warnings.append("risk_moderate")
            else:
                self.print_success(f"Risco aceitável: {result.risk_percentage_of_account:.2f}%")

            # 2. Verificar margem
            print(f"\n2️⃣  Verificando margem disponível...")

            margin_pct = (result.margin_required / params.account_balance) * 100

            if margin_pct > 50:
                self.print_error(f"Margem muito alta: {margin_pct:.1f}% da conta (máx recomendado: 50%)")
                errors.append("margin_too_high")
            elif margin_pct > 30:
                self.print_warning(f"Margem elevada: {margin_pct:.1f}% da conta (recomendado: <30%)")
                warnings.append("margin_elevated")
            else:
                self.print_success(f"Margem saudável: {margin_pct:.1f}% da conta")

            free_margin = params.account_balance - result.margin_required
            print(f"   Margem Livre: ${free_margin:,.2f} ({(free_margin/params.account_balance)*100:.1f}% da conta)")

            # 3. Verificar liquidação (se usar leverage)
            if params.leverage > 1 and result.liquidation_price:
                print(f"\n3️⃣  Verificando risco de liquidação...")
                print(f"   Liquidation Price: ${result.liquidation_price:,.2f}")

                if params.side == PositionSide.LONG:
                    distance_to_liq = ((result.stop_loss_price - result.liquidation_price) /
                                      result.liquidation_price * 100)
                else:
                    distance_to_liq = ((result.liquidation_price - result.stop_loss_price) /
                                      result.liquidation_price * 100)

                print(f"   Distância Stop → Liquidação: {distance_to_liq:.2f}%")

                if distance_to_liq < 10:
                    self.print_error(f"Stop muito próximo da liquidação! Distância: {distance_to_liq:.1f}%")
                    errors.append("liquidation_too_close")
                elif distance_to_liq < 20:
                    self.print_warning(f"Stop relativamente próximo da liquidação: {distance_to_liq:.1f}%")
                    warnings.append("liquidation_close")
                else:
                    self.print_success(f"Stop seguro em relação à liquidação: {distance_to_liq:.1f}%")

                # Calcular % de perda até liquidação
                if params.side == PositionSide.LONG:
                    loss_to_liq_pct = ((params.entry_price - result.liquidation_price) /
                                      params.entry_price * 100)
                else:
                    loss_to_liq_pct = ((result.liquidation_price - params.entry_price) /
                                      params.entry_price * 100)

                loss_to_liq_usdt = result.position_value * (loss_to_liq_pct / 100)

                print(f"   Perda até Liquidação: ${loss_to_liq_usdt:,.2f} ({loss_to_liq_pct:.2f}% do position value)")

                if loss_to_liq_usdt > params.account_balance:
                    self.print_error("Liquidação causaria perda total da conta!")
                    errors.append("liquidation_wipes_account")
            else:
                print(f"\n3️⃣  Sem risco de liquidação (leverage 1x)")
                self.print_success("Posição sem leverage - máxima segurança")

            # 4. Verificar stop loss distance
            print(f"\n4️⃣  Verificando distância do stop loss...")

            if stop_distance_pct < 0.3:
                self.print_warning(f"Stop muito apertado: {stop_distance_pct:.2f}% (pode ser hit por noise)")
                warnings.append("stop_too_tight")
            elif stop_distance_pct > 5.0:
                self.print_warning(f"Stop muito largo: {stop_distance_pct:.2f}% (R:R pode ser ruim)")
                warnings.append("stop_too_wide")
            else:
                self.print_success(f"Stop bem posicionado: {stop_distance_pct:.2f}%")

            # 5. Verificar R:R ratio
            print(f"\n5️⃣  Verificando Risk/Reward ratio...")

            if result.actual_risk_reward_ratio < 1.5:
                self.print_warning(f"R:R baixo: 1:{result.actual_risk_reward_ratio:.2f} (recomendado: >1.5)")
                warnings.append("rr_low")
            else:
                self.print_success(f"R:R favorável: 1:{result.actual_risk_reward_ratio:.2f}")

            # 6. Verificar position size
            print(f"\n6️⃣  Verificando tamanho da posição...")

            position_pct = (result.position_value / params.account_balance) * 100

            if position_pct > 100:
                self.print_warning(f"Posição maior que conta: {position_pct:.0f}% (usando leverage {params.leverage}x)")
                warnings.append("position_leveraged")
            else:
                self.print_info(f"Position size: {position_pct:.1f}% da conta")

            # RESULTADO FINAL
            print(f"\n" + "="*80)

            is_valid = len(errors) == 0

            if is_valid:
                if len(warnings) == 0:
                    print(f"✅ POSIÇÃO TOTALMENTE SEGURA - Nenhum warning detectado!")
                else:
                    print(f"⚠️  POSIÇÃO VÁLIDA COM WARNINGS - {len(warnings)} avisos detectados")
                    print(f"\n   Warnings:")
                    for w in warnings:
                        print(f"   • {w}")
            else:
                print(f"❌ POSIÇÃO REJEITADA - {len(errors)} erros críticos detectados")
                print(f"\n   Erros:")
                for e in errors:
                    print(f"   • {e}")
                if len(warnings) > 0:
                    print(f"\n   Warnings adicionais:")
                    for w in warnings:
                        print(f"   • {w}")

            print("="*80)

            return {
                'is_valid': is_valid,
                'result': result,
                'warnings': warnings,
                'errors': errors,
                'margin_pct': margin_pct,
                'stop_distance_pct': stop_distance_pct
            }

        except Exception as e:
            print(f"\n❌ ERRO NO CÁLCULO: {str(e)}")
            self.print_error(f"Não foi possível calcular posição: {str(e)}")

            return {
                'is_valid': False,
                'result': None,
                'warnings': [],
                'errors': [str(e)],
                'margin_pct': 0,
                'stop_distance_pct': 0
            }


def run_security_validation_tests():
    """Executa bateria de testes de validação de segurança"""

    validator = SecurityValidator()

    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "VALIDAÇÃO DE SEGURANÇA - SISTEMA DE TRADING" + " "*14 + "║")
    print("║" + " "*78 + "║")
    print("║" + " "*15 + "Testa validações de segurança em tempo real" + " "*18 + "║")
    print("╚" + "="*78 + "╝")

    results = []

    # =========================================================================
    # TESTE 1: Posição SEGURA - Conservadora
    # =========================================================================
    validator.print_header("TESTE 1: Posição SEGURA (Conservadora)")

    params1 = PositionSizeParams(
        entry_price=50000,
        account_balance=10000,
        side=PositionSide.LONG,
        risk_amount_usdt=10,      # 0.1% apenas
        profit_target_usdt=30,    # 1:3 R:R
        timeframe=Timeframe.M15,
        leverage=1                # Sem leverage
    )

    result1 = validator.validate_position_safety(params1, "Conservative Long - No Leverage")
    results.append(('Conservative', result1))

    input("\n⏸️  Pressione Enter para continuar...")

    # =========================================================================
    # TESTE 2: Posição MODERADA - Com Leverage
    # =========================================================================
    validator.print_header("TESTE 2: Posição MODERADA (Com Leverage)")

    params2 = PositionSizeParams(
        entry_price=50000,
        account_balance=10000,
        side=PositionSide.LONG,
        risk_amount_usdt=20,      # 0.2%
        profit_target_usdt=60,    # 1:3 R:R
        timeframe=Timeframe.M15,
        leverage=3                # Leverage moderado
    )

    result2 = validator.validate_position_safety(params2, "Moderate Long - 3x Leverage")
    results.append(('Moderate', result2))

    input("\n⏸️  Pressione Enter para continuar...")

    # =========================================================================
    # TESTE 3: Posição ARRISCADA - Alto Leverage
    # =========================================================================
    validator.print_header("TESTE 3: Posição ARRISCADA (Alto Leverage)")

    params3 = PositionSizeParams(
        entry_price=50000,
        account_balance=10000,
        side=PositionSide.LONG,
        risk_amount_usdt=50,      # 0.5% - alto
        profit_target_usdt=150,   # 1:3 R:R
        timeframe=Timeframe.M5,   # Timeframe curto
        leverage=10               # Leverage alto!
    )

    result3 = validator.validate_position_safety(params3, "Aggressive Long - 10x Leverage")
    results.append(('Aggressive', result3))

    input("\n⏸️  Pressione Enter para continuar...")

    # =========================================================================
    # TESTE 4: Posição PERIGOSA - Risco Muito Alto
    # =========================================================================
    validator.print_header("TESTE 4: Posição PERIGOSA (Risco Excessivo)")

    params4 = PositionSizeParams(
        entry_price=50000,
        account_balance=10000,
        side=PositionSide.LONG,
        risk_amount_usdt=300,     # 3% - MUITO alto!
        profit_target_usdt=600,   # 1:2 R:R
        timeframe=Timeframe.M15,
        leverage=5
    )

    result4 = validator.validate_position_safety(params4, "DANGEROUS - Excessive Risk")
    results.append(('Dangerous', result4))

    input("\n⏸️  Pressione Enter para continuar...")

    # =========================================================================
    # TESTE 5: Posição SHORT - Alta Margem
    # =========================================================================
    validator.print_header("TESTE 5: Posição SHORT (Alta Margem)")

    params5 = PositionSizeParams(
        entry_price=50000,
        account_balance=5000,     # Conta pequena
        side=PositionSide.SHORT,
        risk_amount_usdt=50,      # 1% de risco
        profit_target_usdt=150,   # 1:3 R:R
        timeframe=Timeframe.M15,
        leverage=8                # Leverage alto
    )

    result5 = validator.validate_position_safety(params5, "Short High Leverage - Small Account")
    results.append(('Short High Leverage', result5))

    input("\n⏸️  Pressione Enter para continuar...")

    # =========================================================================
    # TESTE 6: Stop Manual Muito Próximo da Liquidação
    # =========================================================================
    validator.print_header("TESTE 6: Stop PERIGOSO (Próximo da Liquidação)")

    params6 = PositionSizeParams(
        entry_price=50000,
        account_balance=10000,
        side=PositionSide.LONG,
        stop_loss_price=47000,    # Stop 6% abaixo
        take_profit_price=56000,  # TP 12% acima
        timeframe=Timeframe.M15,
        leverage=10               # Leverage 10x
    )

    result6 = validator.validate_position_safety(params6, "Manual Stop Near Liquidation")
    results.append(('Near Liquidation', result6))

    input("\n⏸️  Pressione Enter para continuar...")

    # =========================================================================
    # COMPARAÇÃO FINAL
    # =========================================================================
    validator.print_header("COMPARAÇÃO FINAL DE SEGURANÇA")

    print("\n📊 RESUMO DE TODOS OS TESTES:\n")
    print(f"{'Cenário':<25} {'Status':<15} {'Warnings':<10} {'Errors':<10} {'Margem %':<12} {'Stop %':<10}")
    print("─" * 95)

    for name, result in results:
        status = "✅ VÁLIDA" if result['is_valid'] else "❌ REJEITADA"
        warnings = len(result['warnings'])
        errors = len(result['errors'])
        margin = result['margin_pct']
        stop = result['stop_distance_pct']

        print(f"{name:<25} {status:<15} {warnings:<10} {errors:<10} {margin:<11.1f}% {stop:<9.2f}%")

    # Estatísticas
    total_tests = len(results)
    valid_tests = sum(1 for _, r in results if r['is_valid'])
    invalid_tests = total_tests - valid_tests
    total_warnings = sum(len(r['warnings']) for _, r in results)
    total_errors = sum(len(r['errors']) for _, r in results)

    print("\n" + "="*95)
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"   Total de Testes: {total_tests}")
    print(f"   Posições Válidas: {valid_tests} ({valid_tests/total_tests*100:.0f}%)")
    print(f"   Posições Rejeitadas: {invalid_tests} ({invalid_tests/total_tests*100:.0f}%)")
    print(f"   Total de Warnings: {total_warnings}")
    print(f"   Total de Erros: {total_errors}")

    # Recomendações
    print("\n" + "="*95)
    print("💡 RECOMENDAÇÕES DE SEGURANÇA:")
    print("="*95)
    print("""
✅ SEMPRE:
   • Manter risco por trade < 1% da conta
   • Usar leverage ≤ 3x para iniciantes
   • Verificar distância stop → liquidação > 20%
   • Manter margem < 30% da conta
   • Usar R:R mínimo de 1:2

⚠️  CUIDADO:
   • Leverage > 5x aumenta muito o risco
   • Timeframes curtos (5m) têm mais noise
   • Stop < 0.5% pode ser hit por volatilidade normal
   • Múltiplas posições simultâneas aumentam risco total

❌ NUNCA:
   • Arriscar > 2% por trade
   • Usar leverage > 10x
   • Entrar sem stop loss
   • Colocar stop próximo da liquidação (<10%)
   • Usar toda a margem disponível
    """)

    print("="*95)
    print("✅ VALIDAÇÃO DE SEGURANÇA CONCLUÍDA!")
    print("="*95)


def run_realtime_monitoring_demo():
    """Demonstra monitoramento em tempo real"""

    validator = SecurityValidator()

    validator.print_header("DEMO: MONITORAMENTO EM TEMPO REAL")

    print("""
📡 CENÁRIO: Você está em uma posição LONG de BTC
    Entry: $50,000
    Stop Loss: $49,500
    Take Profit: $51,500
    Position: 0.04 BTC
    Leverage: 5x
    Liquidation: $40,000

Vamos simular mudanças de preço e ver warnings em tempo real...
    """)

    input("Pressione Enter para iniciar monitoramento...")

    # Parâmetros da posição
    entry = 50000
    stop = 49500
    tp = 51500
    position_size = 0.04
    leverage = 5
    liquidation = 40000
    account_balance = 10000

    # Simular preços
    prices = [
        (50100, "Preço subiu levemente"),
        (50500, "Preço subindo - 1R alcançado"),
        (51000, "Preço em 2R - considere trailing stop"),
        (51500, "🎯 TAKE PROFIT HIT!"),
        (51000, "Pullback após TP"),
        (50500, "Retracing..."),
        (50000, "Voltou ao entry"),
        (49800, "Abaixo do entry - stop próximo"),
        (49500, "🛑 STOP LOSS HIT"),
    ]

    for price, event in prices:
        print("\n" + "─"*80)
        print(f"💹 Preço Atual: ${price:,.2f} - {event}")
        print("─"*80)

        # Calcular P&L
        pnl = (price - entry) * position_size
        pnl_pct = ((price - entry) / entry) * 100 * leverage
        pnl_account_pct = (pnl / account_balance) * 100

        print(f"\n📊 P&L:")
        if pnl >= 0:
            print(f"   Unrealized Profit: ${pnl:,.2f} ({pnl_account_pct:+.2f}% da conta)")
        else:
            print(f"   Unrealized Loss: ${pnl:,.2f} ({pnl_account_pct:+.2f}% da conta)")

        # Distâncias
        dist_to_stop = abs(price - stop)
        dist_to_tp = abs(tp - price)
        dist_to_liq = abs(price - liquidation)

        print(f"\n📏 Distâncias:")
        print(f"   Até Stop Loss: ${dist_to_stop:,.2f} ({((price - stop)/price)*100:.2f}%)")
        print(f"   Até Take Profit: ${dist_to_tp:,.2f} ({((tp - price)/price)*100:.2f}%)")
        print(f"   Até Liquidação: ${dist_to_liq:,.2f} ({((price - liquidation)/price)*100:.2f}%)")

        # Warnings em tempo real
        print(f"\n🚨 Análise de Segurança:")

        if price <= stop:
            validator.print_error("STOP LOSS HIT - Posição fechada!")
            break

        if price >= tp:
            validator.print_success("TAKE PROFIT HIT - Lucro realizado!")
            continue

        if price < entry * 0.995:  # 0.5% abaixo
            validator.print_warning("Preço abaixo do entry - monitor closely")

        if dist_to_stop < 100:
            validator.print_warning(f"Stop loss muito próximo! Apenas ${dist_to_stop:.0f}")

        if dist_to_liq < price * 0.25:  # < 25% até liquidação
            validator.print_error(f"RISCO DE LIQUIDAÇÃO! Distância: {((price-liquidation)/liquidation)*100:.1f}%")

        if pnl_account_pct < -1.5:
            validator.print_warning(f"Perda aproximando de -2%: {pnl_account_pct:.2f}%")

        if price > entry * 1.015:  # 1.5% acima
            validator.print_info("Considere mover stop para breakeven (se configurado)")

        if price > entry * 1.03:  # 3% acima
            validator.print_info("Considere trailing stop para proteger lucros")

        time.sleep(1.5)

    print("\n" + "="*80)
    print("✅ DEMO DE MONITORAMENTO EM TEMPO REAL CONCLUÍDO")
    print("="*80)


def main():
    """Menu principal"""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      VALIDAÇÃO DE SEGURANÇA                                  ║
║                                                                              ║
║  Sistema completo de validação com:                                         ║
║  • Warnings em tempo real                                                   ║
║  • Verificação de margem até liquidação                                     ║
║  • Confirmação se posição é válida                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Escolha um teste:
1 - Bateria completa de validação (6 cenários)
2 - Demo de monitoramento em tempo real
3 - Executar ambos

""")

    choice = input("Digite sua escolha (ou Enter para sair): ").strip()

    if choice == '1':
        run_security_validation_tests()
    elif choice == '2':
        run_realtime_monitoring_demo()
    elif choice == '3':
        run_security_validation_tests()
        input("\n⏸️  Pressione Enter para continuar para demo de tempo real...")
        run_realtime_monitoring_demo()
    elif choice == '':
        print("Saindo...")
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    main()
