"""
Enhanced Backtest Runner
Integra o PositionSizeCalculator para backtests com risk/reward, leverage e stops
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

import sys
sys.path.append('..')

from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe,
    calculate_optimal_leverage
)


class EnhancedBacktestRunner:
    """
    Backtest Runner Avançado com:
    - Position sizing baseado em risk/reward
    - Stop loss e take profit automáticos
    - Suporte a leverage
    - Análise por timeframe
    - Métricas detalhadas
    """

    def __init__(
        self,
        initial_capital: float = 10000,
        risk_per_trade_usdt: float = 10,  # Quanto arriscar por trade
        profit_target_usdt: float = 30,   # Quanto lucrar por trade
        risk_reward_ratio: float = 3.0,   # 1:3 risk/reward
        use_leverage: bool = False,
        max_leverage: int = 10,
        timeframe: Timeframe = Timeframe.M15,
        use_atr_stops: bool = True,
        # Breakeven e Trailing Stop
        use_breakeven: bool = True,
        breakeven_trigger_rr: float = 1.0,  # Move para BE após 1R de lucro
        use_trailing_stop: bool = True,
        trailing_stop_activation_rr: float = 1.5,  # Ativa trailing após 1.5R
        trailing_stop_distance_atr: float = 2.0,  # Distância em ATR
        trailing_stop_distance_pct: float = 0.01,  # Ou 1% se sem ATR
        # Fees
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0005,   # 0.05%
        max_risk_per_trade_pct: float = 2.0  # Máximo 2% do saldo
    ):
        """
        Args:
            initial_capital: Capital inicial em USDT
            risk_per_trade_usdt: Quanto arriscar por trade (ex: 10 USDT)
            profit_target_usdt: Quanto lucrar por trade (ex: 30 USDT)
            risk_reward_ratio: Ratio risk/reward (ex: 3.0 = 1:3)
            use_leverage: Se deve usar leverage
            max_leverage: Leverage máxima permitida
            timeframe: Timeframe para análise
            use_atr_stops: Usar ATR para calcular stops
            use_breakeven: Mover stop para breakeven após lucro
            breakeven_trigger_rr: Quantos R de lucro para ativar BE (ex: 1.0 = 1R)
            use_trailing_stop: Usar trailing stop
            trailing_stop_activation_rr: Quantos R para ativar trailing
            trailing_stop_distance_atr: Distância do trailing em ATR
            trailing_stop_distance_pct: Distância do trailing em % (se sem ATR)
            commission: Taxa de comissão
            slippage: Slippage estimado
            max_risk_per_trade_pct: Risco máximo por trade (% do saldo)
        """
        self.initial_capital = initial_capital
        self.risk_per_trade_usdt = risk_per_trade_usdt
        self.profit_target_usdt = profit_target_usdt
        self.risk_reward_ratio = risk_reward_ratio
        self.use_leverage = use_leverage
        self.max_leverage = max_leverage
        self.timeframe = timeframe
        self.use_atr_stops = use_atr_stops
        self.use_breakeven = use_breakeven
        self.breakeven_trigger_rr = breakeven_trigger_rr
        self.use_trailing_stop = use_trailing_stop
        self.trailing_stop_activation_rr = trailing_stop_activation_rr
        self.trailing_stop_distance_atr = trailing_stop_distance_atr
        self.trailing_stop_distance_pct = trailing_stop_distance_pct
        self.commission = commission
        self.slippage = slippage
        self.max_risk_per_trade_pct = max_risk_per_trade_pct

        # Cria calculadora de position size
        self.position_calculator = PositionSizeCalculator(
            max_risk_per_trade_pct=max_risk_per_trade_pct
        )

    def run_backtest(
        self,
        df: pd.DataFrame,
        strategy_name: str = "Strategy"
    ) -> Dict[str, Any]:
        """
        Executa backtest com position sizing, stop loss e take profit

        Args:
            df: DataFrame com coluna 'signal' (-1, 0, 1)
            strategy_name: Nome da estratégia

        Returns:
            Dicionário com métricas de performance
        """
        # Prepara DataFrame
        df = df.copy()

        # Calcula ATR se necessário
        if self.use_atr_stops:
            df = self.position_calculator.calculate_atr_based_stops(
                df,
                self.timeframe,
                atr_period=14
            )

        # Variáveis de controle
        capital = self.initial_capital
        position = None  # None = flat, dict com detalhes da posição
        trades = []
        equity_curve = []
        rejected_trades = []  # Trades que não passaram na validação

        # Loop pelo histórico
        for i in range(len(df)):
            row = df.iloc[i]
            current_price = row['close']
            signal = row.get('signal', 0)
            timestamp = row.name

            # Calcula equity atual
            current_equity = self._calculate_current_equity(
                capital,
                position,
                current_price
            )

            equity_curve.append({
                'timestamp': timestamp,
                'equity': current_equity,
                'price': current_price,
                'position': 'LONG' if position and position['side'] == PositionSide.LONG else
                           'SHORT' if position and position['side'] == PositionSide.SHORT else 'FLAT'
            })

            # Verifica e atualiza stops (breakeven e trailing)
            if position:
                self._update_position_stops(
                    position,
                    current_price,
                    row.get('atr', None)
                )

                # Verifica se stop loss ou take profit foi atingido
                hit_stop, hit_tp = self._check_stop_and_tp(
                    position,
                    row['high'],
                    row['low'],
                    current_price
                )

                if hit_stop or hit_tp:
                    # Fecha posição
                    exit_type = 'STOP_LOSS' if hit_stop else 'TAKE_PROFIT'
                    exit_price = position['stop_loss_price'] if hit_stop else position['take_profit_price']

                    trade_result = self._close_position(
                        position,
                        exit_price,
                        timestamp,
                        capital,
                        exit_type
                    )

                    trades.append(trade_result)
                    capital = trade_result['capital_after']
                    position = None

            # Processa sinais
            if signal != 0 and position is None:
                # Tenta abrir nova posição
                side = PositionSide.LONG if signal == 1 else PositionSide.SHORT

                # Calcula position size
                try:
                    position_params = self._create_position_params(
                        entry_price=current_price,
                        side=side,
                        account_balance=capital,
                        current_atr=row.get('atr', None) if self.use_atr_stops else None
                    )

                    position_result = self.position_calculator.calculate_position_size(
                        position_params
                    )

                    # Valida posição
                    if position_result.is_valid:
                        # Calcula leverage ótima se habilitada
                        leverage = 1
                        if self.use_leverage:
                            leverage = calculate_optimal_leverage(
                                position_result.entry_price,
                                position_result.stop_loss_price,
                                self.max_risk_per_trade_pct
                            )
                            leverage = min(leverage, self.max_leverage)

                        # Abre posição
                        position = {
                            'side': side,
                            'entry_price': current_price * (1 + self.slippage if side == PositionSide.LONG else 1 - self.slippage),
                            'entry_time': timestamp,
                            'position_size': position_result.position_size,
                            'position_value': position_result.position_value_usdt,
                            'stop_loss_price': position_result.stop_loss_price,
                            'initial_stop_loss_price': position_result.stop_loss_price,  # Para calcular R
                            'take_profit_price': position_result.take_profit_price,
                            'leverage': leverage,
                            'margin_used': position_result.margin_required,
                            'risk_amount': position_result.risk_amount,
                            'profit_potential': position_result.profit_potential,
                            'breakeven_activated': False,
                            'trailing_activated': False,
                            'max_favorable_price': current_price  # Track highest/lowest price
                        }

                    else:
                        # Posição rejeitada
                        rejected_trades.append({
                            'timestamp': timestamp,
                            'side': side.value,
                            'reason': ', '.join(position_result.warnings)
                        })

                except Exception as e:
                    rejected_trades.append({
                        'timestamp': timestamp,
                        'side': side.value,
                        'reason': f'Error: {str(e)}'
                    })

            # Sinal de saída (reversão)
            elif signal != 0 and position is not None:
                # Fecha posição atual se sinal oposto
                if (signal == 1 and position['side'] == PositionSide.SHORT) or \
                   (signal == -1 and position['side'] == PositionSide.LONG):

                    trade_result = self._close_position(
                        position,
                        current_price,
                        timestamp,
                        capital,
                        'SIGNAL_REVERSE'
                    )

                    trades.append(trade_result)
                    capital = trade_result['capital_after']
                    position = None

        # Fecha posição aberta no final
        if position is not None:
            final_price = df.iloc[-1]['close']
            trade_result = self._close_position(
                position,
                final_price,
                df.index[-1],
                capital,
                'END_OF_BACKTEST'
            )
            trades.append(trade_result)
            capital = trade_result['capital_after']

        # Calcula métricas
        metrics = self._calculate_metrics(
            trades,
            equity_curve,
            self.initial_capital,
            capital,
            strategy_name,
            rejected_trades
        )

        return metrics

    def _create_position_params(
        self,
        entry_price: float,
        side: PositionSide,
        account_balance: float,
        current_atr: Optional[float]
    ) -> PositionSizeParams:
        """Cria parâmetros para o calculador de position size"""

        params = PositionSizeParams(
            entry_price=entry_price,
            account_balance=account_balance,
            side=side,
            risk_amount_usdt=self.risk_per_trade_usdt,
            profit_target_usdt=self.profit_target_usdt,
            risk_reward_ratio=self.risk_reward_ratio,
            timeframe=self.timeframe,
            current_atr=current_atr,
            leverage=self.max_leverage if self.use_leverage else 1,
            maker_fee=self.commission,
            taker_fee=self.commission,
            estimated_slippage=self.slippage
        )

        return params

    def _update_position_stops(
        self,
        position: Dict,
        current_price: float,
        current_atr: Optional[float]
    ):
        """
        Atualiza stops (breakeven e trailing) baseado no preço atual

        Lógica:
        1. Breakeven: Após X R de lucro, move stop para entry (risco zero)
        2. Trailing: Após Y R de lucro, segue o preço mantendo distância

        Modifica o dict position in-place
        """
        entry_price = position['entry_price']
        initial_stop = position['initial_stop_loss_price']
        side = position['side']

        # Calcula 1R (risco inicial)
        one_r = abs(entry_price - initial_stop)

        # Calcula lucro atual em R
        if side == PositionSide.LONG:
            current_profit = current_price - entry_price
            # Atualiza max favorable price
            if current_price > position['max_favorable_price']:
                position['max_favorable_price'] = current_price
        else:  # SHORT
            current_profit = entry_price - current_price
            # Atualiza max favorable price (lowest for short)
            if current_price < position['max_favorable_price']:
                position['max_favorable_price'] = current_price

        current_profit_in_r = current_profit / one_r if one_r > 0 else 0

        # 1. BREAKEVEN STOP
        if self.use_breakeven and not position['breakeven_activated']:
            if current_profit_in_r >= self.breakeven_trigger_rr:
                # Move stop para entry (breakeven)
                position['stop_loss_price'] = entry_price
                position['breakeven_activated'] = True

        # 2. TRAILING STOP
        if self.use_trailing_stop:
            if current_profit_in_r >= self.trailing_stop_activation_rr:
                position['trailing_activated'] = True

            if position['trailing_activated']:
                # Calcula nova posição do trailing stop
                if current_atr and self.use_atr_stops:
                    # Usa ATR
                    trailing_distance = current_atr * self.trailing_stop_distance_atr
                else:
                    # Usa percentual
                    trailing_distance = position['max_favorable_price'] * self.trailing_stop_distance_pct

                if side == PositionSide.LONG:
                    # Trail abaixo do preço
                    new_stop = position['max_favorable_price'] - trailing_distance

                    # Só move o stop para cima (nunca para baixo)
                    if new_stop > position['stop_loss_price']:
                        position['stop_loss_price'] = new_stop

                else:  # SHORT
                    # Trail acima do preço
                    new_stop = position['max_favorable_price'] + trailing_distance

                    # Só move o stop para baixo (nunca para cima)
                    if new_stop < position['stop_loss_price']:
                        position['stop_loss_price'] = new_stop

    def _check_stop_and_tp(
        self,
        position: Dict,
        bar_high: float,
        bar_low: float,
        bar_close: float
    ) -> tuple:
        """
        Verifica se stop loss ou take profit foram atingidos

        Returns:
            (hit_stop, hit_tp)
        """
        hit_stop = False
        hit_tp = False

        if position['side'] == PositionSide.LONG:
            # Long: stop abaixo, TP acima
            if bar_low <= position['stop_loss_price']:
                hit_stop = True
            elif bar_high >= position['take_profit_price']:
                hit_tp = True

        else:  # SHORT
            # Short: stop acima, TP abaixo
            if bar_high >= position['stop_loss_price']:
                hit_stop = True
            elif bar_low <= position['take_profit_price']:
                hit_tp = True

        return hit_stop, hit_tp

    def _close_position(
        self,
        position: Dict,
        exit_price: float,
        exit_time,
        capital_before: float,
        exit_type: str
    ) -> Dict:
        """Fecha uma posição e calcula P&L"""

        # Aplica slippage
        if position['side'] == PositionSide.LONG:
            exit_price = exit_price * (1 - self.slippage)
        else:
            exit_price = exit_price * (1 + self.slippage)

        # Calcula P&L
        if position['side'] == PositionSide.LONG:
            pnl = (exit_price - position['entry_price']) * position['position_size']
        else:
            pnl = (position['entry_price'] - exit_price) * position['position_size']

        # Aplica leverage no P&L
        pnl = pnl * position['leverage']

        # Deduz comissões (entry + exit)
        commission_cost = (position['position_value'] * self.commission * 2)
        pnl -= commission_cost

        capital_after = capital_before + pnl
        pnl_pct = (pnl / capital_before) * 100

        return {
            'entry_time': position['entry_time'],
            'exit_time': exit_time,
            'type': position['side'].value.upper(),
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'position_size': position['position_size'],
            'position_value': position['position_value'],
            'leverage': position['leverage'],
            'stop_loss_price': position['stop_loss_price'],
            'initial_stop_loss_price': position['initial_stop_loss_price'],
            'take_profit_price': position['take_profit_price'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'capital_before': capital_before,
            'capital_after': capital_after,
            'exit_type': exit_type,
            'risk_amount': position['risk_amount'],
            'profit_potential': position['profit_potential'],
            'realized_rr': abs(pnl / position['risk_amount']) if position['risk_amount'] > 0 else 0,
            'breakeven_used': position['breakeven_activated'],
            'trailing_used': position['trailing_activated']
        }

    def _calculate_current_equity(
        self,
        capital: float,
        position: Optional[Dict],
        current_price: float
    ) -> float:
        """Calcula equity atual incluindo posição aberta"""

        if position is None:
            return capital

        # Calcula P&L não realizado
        if position['side'] == PositionSide.LONG:
            unrealized_pnl = (current_price - position['entry_price']) * position['position_size']
        else:
            unrealized_pnl = (position['entry_price'] - current_price) * position['position_size']

        unrealized_pnl = unrealized_pnl * position['leverage']

        return capital + unrealized_pnl

    def _calculate_metrics(
        self,
        trades: List[Dict],
        equity_curve: List[Dict],
        initial_capital: float,
        final_capital: float,
        strategy_name: str,
        rejected_trades: List[Dict]
    ) -> Dict[str, Any]:
        """Calcula métricas de performance"""

        if not trades:
            return {
                'strategy_name': strategy_name,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_return': 0,
                'total_return_pct': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'initial_capital': initial_capital,
                'final_capital': final_capital,
                'trades': [],
                'equity_curve': equity_curve,
                'rejected_trades': rejected_trades
            }

        trades_df = pd.DataFrame(trades)

        # Separar ganhos e perdas
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] <= 0]

        # Métricas básicas
        total_return = final_capital - initial_capital
        total_return_pct = (total_return / initial_capital) * 100
        win_rate = (len(winning_trades) / len(trades)) * 100 if len(trades) > 0 else 0

        # Profit Factor
        total_wins = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        total_losses = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else (float('inf') if total_wins > 0 else 0)

        # Max Drawdown
        equity_series = pd.Series([e['equity'] for e in equity_curve])
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()

        # Sharpe Ratio
        returns = trades_df['pnl_pct']
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

        # Médias
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        avg_rr_realized = trades_df['realized_rr'].mean()

        # Maiores
        largest_win = winning_trades['pnl'].max() if len(winning_trades) > 0 else 0
        largest_loss = losing_trades['pnl'].min() if len(losing_trades) > 0 else 0

        # Estatísticas de stop/TP
        stopped_out = len(trades_df[trades_df['exit_type'] == 'STOP_LOSS'])
        took_profit = len(trades_df[trades_df['exit_type'] == 'TAKE_PROFIT'])
        signal_exits = len(trades_df[trades_df['exit_type'] == 'SIGNAL_REVERSE'])

        # Breakeven e Trailing statistics
        breakeven_used_count = len(trades_df[trades_df['breakeven_used'] == True])
        trailing_used_count = len(trades_df[trades_df['trailing_used'] == True])

        # Trades que usaram BE/Trailing e ganharam
        be_and_won = len(trades_df[(trades_df['breakeven_used'] == True) & (trades_df['pnl'] > 0)])
        trailing_and_won = len(trades_df[(trades_df['trailing_used'] == True) & (trades_df['pnl'] > 0)])

        # Leverage médio usado
        avg_leverage = trades_df['leverage'].mean()

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
            'avg_rr_realized': avg_rr_realized,
            'stopped_out_count': stopped_out,
            'took_profit_count': took_profit,
            'signal_exits_count': signal_exits,
            'breakeven_used_count': breakeven_used_count,
            'breakeven_won_count': be_and_won,
            'trailing_used_count': trailing_used_count,
            'trailing_won_count': trailing_and_won,
            'avg_leverage': avg_leverage,
            'rejected_trades_count': len(rejected_trades),
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'trades': trades,
            'equity_curve': equity_curve,
            'rejected_trades': rejected_trades
        }


def print_enhanced_metrics(metrics: Dict[str, Any]):
    """Imprime métricas do backtest avançado"""
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {metrics['strategy_name']}")
    print(f"{'='*80}")

    print(f"\n💰 PERFORMANCE GERAL:")
    print(f"  Capital Inicial:      ${metrics['initial_capital']:,.2f}")
    print(f"  Capital Final:        ${metrics['final_capital']:,.2f}")
    print(f"  Retorno Total:        ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2f}%)")

    print(f"\n📊 ESTATÍSTICAS DE TRADES:")
    print(f"  Total de Trades:      {metrics['total_trades']}")
    print(f"  Trades Vencedores:    {metrics['winning_trades']} ({metrics['win_rate']:.1f}%)")
    print(f"  Trades Perdedores:    {metrics['losing_trades']}")
    print(f"  Trades Rejeitados:    {metrics['rejected_trades_count']}")

    print(f"\n🎯 STOP LOSS & TAKE PROFIT:")
    print(f"  Stopped Out:          {metrics['stopped_out_count']}")
    print(f"  Take Profit Hit:      {metrics['took_profit_count']}")
    print(f"  Exits por Sinal:      {metrics['signal_exits_count']}")

    print(f"\n🔄 BREAKEVEN & TRAILING:")
    print(f"  Breakeven Usado:      {metrics['breakeven_used_count']} "
          f"(Ganhos: {metrics['breakeven_won_count']})")
    print(f"  Trailing Usado:       {metrics['trailing_used_count']} "
          f"(Ganhos: {metrics['trailing_won_count']})")

    print(f"\n📈 MÉTRICAS DE RISCO/RETORNO:")
    print(f"  Profit Factor:        {metrics['profit_factor']:.2f}")
    print(f"  Sharpe Ratio:         {metrics['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown:         {metrics['max_drawdown']:.2f}%")
    print(f"  R:R Médio Realizado:  1:{metrics['avg_rr_realized']:.2f}")

    print(f"\n💵 TRADES:")
    print(f"  Ganho Médio:          ${metrics['avg_win']:.2f}")
    print(f"  Perda Média:          ${metrics['avg_loss']:.2f}")
    print(f"  Maior Ganho:          ${metrics['largest_win']:.2f}")
    print(f"  Maior Perda:          ${metrics['largest_loss']:.2f}")

    if metrics.get('avg_leverage', 1) > 1:
        print(f"\n⚡ LEVERAGE:")
        print(f"  Leverage Médio:       {metrics['avg_leverage']:.1f}x")

    print(f"\n{'='*80}\n")
