"""
Sistema de Backtest Histórico para Estratégias SMC e Wyckoff
Integração completa com BacktestEngine
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys

sys.path.insert(0, '/home/user/sistema-trading-profissional')

from strategies.strategy_selector import (
    StrategySelector,
    StrategyType,
    SignalCombinationMethod
)


class HistoricalDataGenerator:
    """Gera dados históricos realistas para backtesting"""

    def __init__(self, days: int = 365, initial_price: float = 50000):
        self.days = days
        self.initial_price = initial_price

    def generate_trending_market(self, trend: str = 'mixed') -> pd.DataFrame:
        """
        Gera dados históricos com diferentes tendências

        Args:
            trend: 'up', 'down', 'sideways', 'mixed'
        """
        # Gera timeframe de 1h para ter mais dados
        dates = pd.date_range(
            end=datetime.now(),
            periods=self.days * 24,  # 24 horas por dia
            freq='h'
        )

        np.random.seed(42)
        price = self.initial_price
        data = []

        for i, date in enumerate(dates):
            # Define tendência baseado no tipo
            if trend == 'up':
                trend_factor = 0.0002  # 0.02% por hora de alta
            elif trend == 'down':
                trend_factor = -0.0002
            elif trend == 'sideways':
                trend_factor = 0.0
            else:  # mixed
                # Muda de tendência a cada ~7 dias
                phase = (i // (24 * 7)) % 3
                if phase == 0:
                    trend_factor = 0.0003  # Alta
                elif phase == 1:
                    trend_factor = -0.0002  # Baixa
                else:
                    trend_factor = 0.0  # Lateral

            # Aplica tendência
            price *= (1 + trend_factor)

            # Adiciona volatilidade
            volatility = np.random.randn() * 0.015  # 1.5% volatilidade
            price *= (1 + volatility)

            # Cria OHLC
            daily_range = abs(np.random.randn()) * 0.02  # 2% range
            high = price * (1 + daily_range / 2)
            low = price * (1 - daily_range / 2)

            open_price = low + (high - low) * np.random.random()
            close = low + (high - low) * np.random.random()

            # Volume com picos ocasionais
            base_volume = 5000000
            volume_spike = 1.0
            if np.random.random() > 0.95:  # 5% chance de volume alto
                volume_spike = 2.5

            volume = abs(np.random.randn() * 1000000 + base_volume) * volume_spike

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


class BacktestRunner:
    """
    Runner de backtest simplificado e integrado
    """

    def __init__(
        self,
        initial_capital: float = 10000,
        position_size_pct: float = 1.0,  # 100% do capital por trade
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0005  # 0.05%
    ):
        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct
        self.commission = commission
        self.slippage = slippage

    def run_backtest(self, df: pd.DataFrame, strategy_name: str = "Strategy") -> Dict[str, Any]:
        """
        Executa backtest em um DataFrame com sinais

        Args:
            df: DataFrame com coluna 'signal' (-1, 0, 1)
            strategy_name: Nome da estratégia para relatório

        Returns:
            Dicionário com métricas de performance
        """
        capital = self.initial_capital
        position = 0  # 0=flat, 1=long, -1=short
        entry_price = 0
        trades = []
        equity_curve = []

        for i in range(len(df)):
            row = df.iloc[i]
            current_price = row['close']
            signal = row.get('signal', 0)

            # Registra equity
            if position == 0:
                current_equity = capital
            elif position > 0:
                unrealized_pnl = (current_price - entry_price) * (capital / entry_price)
                current_equity = capital + unrealized_pnl
            else:  # position < 0
                unrealized_pnl = (entry_price - current_price) * (capital / entry_price)
                current_equity = capital + unrealized_pnl

            equity_curve.append({
                'timestamp': row.name,
                'equity': current_equity,
                'price': current_price
            })

            # Executa trades
            if signal == 1 and position <= 0:  # Sinal de compra
                # Fecha posição short se houver
                if position < 0:
                    exit_price = current_price * (1 + self.slippage)
                    pnl = (entry_price - exit_price) * (capital / entry_price)
                    pnl -= abs(pnl) * self.commission

                    trades.append({
                        'entry_time': entry_time,
                        'exit_time': row.name,
                        'type': 'SHORT',
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'pnl_pct': (pnl / capital) * 100
                    })

                    capital += pnl
                    position = 0

                # Abre posição long
                entry_price = current_price * (1 + self.slippage)
                entry_time = row.name
                position = 1

            elif signal == -1 and position >= 0:  # Sinal de venda
                # Fecha posição long se houver
                if position > 0:
                    exit_price = current_price * (1 - self.slippage)
                    pnl = (exit_price - entry_price) * (capital / entry_price)
                    pnl -= abs(pnl) * self.commission

                    trades.append({
                        'entry_time': entry_time,
                        'exit_time': row.name,
                        'type': 'LONG',
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'pnl_pct': (pnl / capital) * 100
                    })

                    capital += pnl
                    position = 0

                # Abre posição short
                entry_price = current_price * (1 - self.slippage)
                entry_time = row.name
                position = -1

        # Fecha posição aberta no final
        if position != 0:
            exit_price = df.iloc[-1]['close']
            if position > 0:
                exit_price *= (1 - self.slippage)
                pnl = (exit_price - entry_price) * (capital / entry_price)
            else:
                exit_price *= (1 + self.slippage)
                pnl = (entry_price - exit_price) * (capital / entry_price)

            pnl -= abs(pnl) * self.commission

            trades.append({
                'entry_time': entry_time,
                'exit_time': df.index[-1],
                'type': 'LONG' if position > 0 else 'SHORT',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl': pnl,
                'pnl_pct': (pnl / capital) * 100
            })

            capital += pnl

        # Calcula métricas
        metrics = self._calculate_metrics(
            trades,
            equity_curve,
            self.initial_capital,
            capital,
            strategy_name
        )

        return metrics

    def _calculate_metrics(
        self,
        trades: List[Dict],
        equity_curve: List[Dict],
        initial_capital: float,
        final_capital: float,
        strategy_name: str
    ) -> Dict[str, Any]:
        """Calcula métricas de performance"""

        if not trades:
            return {
                'strategy_name': strategy_name,
                'total_trades': 0,
                'total_return': 0,
                'total_return_pct': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'trades': [],
                'equity_curve': equity_curve
            }

        trades_df = pd.DataFrame(trades)

        # Métricas básicas
        total_return = final_capital - initial_capital
        total_return_pct = (total_return / initial_capital) * 100

        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0

        # Profit Factor
        gross_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # Max Drawdown
        equity_df = pd.DataFrame(equity_curve)
        running_max = equity_df['equity'].cummax()
        drawdown = (equity_df['equity'] - running_max) / running_max * 100
        max_drawdown = drawdown.min()

        # Sharpe Ratio (simplificado, usando returns diários)
        returns = trades_df['pnl_pct'].values
        if len(returns) > 1:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0

        # Médias
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0

        # Maiores
        largest_win = winning_trades['pnl'].max() if len(winning_trades) > 0 else 0
        largest_loss = losing_trades['pnl'].min() if len(losing_trades) > 0 else 0

        return {
            'strategy_name': strategy_name,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'trades': trades,
            'equity_curve': equity_curve
        }


def print_metrics(metrics: Dict[str, Any]):
    """Imprime métricas de forma formatada"""
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {metrics['strategy_name']}")
    print(f"{'='*80}")
    print(f"\n📊 PERFORMANCE GERAL:")
    print(f"  Capital Inicial:    ${metrics['initial_capital']:,.2f}")
    print(f"  Capital Final:      ${metrics['final_capital']:,.2f}")
    print(f"  Retorno Total:      ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2f}%)")
    print(f"\n📈 ESTATÍSTICAS DE TRADES:")
    print(f"  Total de Trades:    {metrics['total_trades']}")
    print(f"  Trades Vencedores:  {metrics['winning_trades']} ({metrics['win_rate']:.1f}%)")
    print(f"  Trades Perdedores:  {metrics['losing_trades']}")
    print(f"\n💰 MÉTRICAS DE RISCO/RETORNO:")
    print(f"  Profit Factor:      {metrics['profit_factor']:.2f}")
    print(f"  Sharpe Ratio:       {metrics['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown:       {metrics['max_drawdown']:.2f}%")
    print(f"\n💵 TRADES:")
    print(f"  Ganho Médio:        ${metrics['avg_win']:.2f}")
    print(f"  Perda Média:        ${metrics['avg_loss']:.2f}")
    print(f"  Maior Ganho:        ${metrics['largest_win']:.2f}")
    print(f"  Maior Perda:        ${metrics['largest_loss']:.2f}")


if __name__ == "__main__":
    print("="*80)
    print("BACKTEST HISTÓRICO - ESTRATÉGIAS SMC E WYCKOFF")
    print("="*80)
    print()

    # Gera dados históricos
    print("📊 Gerando dados históricos (1 ano, timeframe 1h)...")
    data_gen = HistoricalDataGenerator(days=365)
    df = data_gen.generate_trending_market(trend='mixed')

    print(f"✓ {len(df)} barras geradas")
    print(f"  Período: {df.index[0]} até {df.index[-1]}")
    print(f"  Preço inicial: ${df['close'].iloc[0]:,.2f}")
    print(f"  Preço final: ${df['close'].iloc[-1]:,.2f}")
    print(f"  Variação: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
    print()

    # Cria runner de backtest
    runner = BacktestRunner(
        initial_capital=10000,
        commission=0.001,
        slippage=0.0005
    )

    # Lista de estratégias para testar
    strategies_to_test = [
        (StrategyType.SMC_ORDER_BLOCK, {}),
        (StrategyType.WYCKOFF_SPRING, {}),
        (StrategyType.SMC_WYCKOFF_COMBINED, {'min_confluence_score': 2}),
    ]

    all_results = []

    # Testa cada estratégia individualmente
    for strategy_type, config in strategies_to_test:
        selector = StrategySelector()
        info = selector.get_strategy_info(strategy_type)

        print(f"\n🧪 Testando: {info['name']}")
        print(f"   {info['description']}")

        selector.add_strategy(strategy_type, config=config if config else None)
        df_signals = selector.generate_combined_signals(df.copy())

        metrics = runner.run_backtest(df_signals, strategy_name=info['name'])
        all_results.append(metrics)

        print_metrics(metrics)

    # Teste com múltiplas estratégias combinadas
    print(f"\n\n🔥 TESTE ESPECIAL: Múltiplas Estratégias Combinadas")
    print(f"{'='*80}")

    selector = StrategySelector()
    selector.add_strategy(StrategyType.SMC_ORDER_BLOCK, weight=1.0)
    selector.add_strategy(StrategyType.WYCKOFF_SPRING, weight=1.2)
    selector.add_strategy(StrategyType.SMC_WYCKOFF_COMBINED, weight=1.5)

    df_combined = selector.generate_combined_signals(
        df.copy(),
        combination_method=SignalCombinationMethod.WEIGHTED
    )

    metrics_combined = runner.run_backtest(
        df_combined,
        strategy_name="Multi-Strategy WEIGHTED"
    )
    all_results.append(metrics_combined)

    print_metrics(metrics_combined)

    # Comparação final
    print(f"\n\n{'='*80}")
    print("COMPARAÇÃO DE TODAS AS ESTRATÉGIAS")
    print(f"{'='*80}\n")

    comparison_data = []
    for m in all_results:
        comparison_data.append({
            'Estratégia': m['strategy_name'][:30],
            'Trades': m['total_trades'],
            'Win%': f"{m['win_rate']:.1f}%",
            'Retorno': f"${m['total_return']:.2f}",
            'Retorno%': f"{m['total_return_pct']:.2f}%",
            'PF': f"{m['profit_factor']:.2f}",
            'Sharpe': f"{m['sharpe_ratio']:.2f}",
            'MaxDD%': f"{m['max_drawdown']:.2f}%"
        })

    comp_df = pd.DataFrame(comparison_data)
    print(comp_df.to_string(index=False))

    print(f"\n{'='*80}")
    print("✓ BACKTEST HISTÓRICO COMPLETO!")
    print(f"{'='*80}")
