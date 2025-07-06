class ExecutionResult:
    def __init__(self, trades):
        self.trades = trades

    def calculate_metrics(self):
        total_trades = len(self.trades)
        if total_trades == 0:
            return {
                "total_trades": 0,
                "roi": 0.0,
                "win_rate": 0.0,
                "average_gain": 0.0,
                "average_loss": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0
            }

        total_profit = sum(t.get("profit", 0) for t in self.trades)
        initial_capital = 1000.0  # Capital inicial para cálculo de ROI
        roi = (total_profit / initial_capital) if initial_capital != 0 else 0.0

        winning_trades = [t for t in self.trades if t.get("profit", 0) > 0]
        losing_trades = [t for t in self.trades if t.get("profit", 0) < 0]

        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0
        average_gain = sum(t["profit"] for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
        average_loss = sum(t["profit"] for t in losing_trades) / len(losing_trades) if losing_trades else 0.0

        total_gain = sum(t["profit"] for t in winning_trades)
        total_loss = abs(sum(t["profit"] for t in losing_trades))
        profit_factor = total_gain / total_loss if total_loss > 0 else float("inf")

        # Cálculo de Max Drawdown (simplificado, requer histórico de capital)
        # Para um cálculo mais preciso, precisaríamos de um histórico de valor da carteira.
        # Aqui, uma estimativa baseada nos lucros/prejuízos individuais.
        max_drawdown = 0.0
        current_drawdown = 0.0
        peak_equity = initial_capital
        equity = initial_capital

        for trade in self.trades:
            equity += trade.get("profit", 0)
            if equity > peak_equity:
                peak_equity = equity
            current_drawdown = (peak_equity - equity) / peak_equity if peak_equity > 0 else 0.0
            if current_drawdown > max_drawdown:
                max_drawdown = current_drawdown

        return {
            "total_trades": total_trades,
            "roi": roi,
            "win_rate": win_rate,
            "average_gain": average_gain,
            "average_loss": average_loss,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown
        }

