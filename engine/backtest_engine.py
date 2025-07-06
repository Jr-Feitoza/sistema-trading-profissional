import pandas as pd
from engine.execution_result import ExecutionResult

class BacktestEngine:
    def __init__(self, strategy, data_loader, order_manager, slippage_percent=0.001, brokerage_fee_percent=0.00075):
        self.strategy = strategy
        self.data_loader = data_loader
        self.order_manager = order_manager
        self.position = 0  # 0: flat, >0: long, <0: short
        self.entry_price = 0
        self.slippage_percent = slippage_percent
        self.brokerage_fee_percent = brokerage_fee_percent

    def run(self):
        df = self.data_loader.load_historical_data()
        df = self.strategy.generate_signals(df)

        trades = []
        for i, row in df.iterrows():
            current_price = row["close"]
            signal = row["signal"]

            # Apply slippage to current price for trade execution
            buy_price = current_price * (1 + self.slippage_percent)
            sell_price = current_price * (1 - self.slippage_percent)

            if signal == 1:  # Sinal de compra
                if self.position <= 0:  # Se não estiver comprado ou estiver vendido
                    # Fechar posição vendida antes de comprar
                    if self.position < 0:
                        profit = (self.entry_price - sell_price) * abs(self.position)
                        brokerage_cost = abs(self.position) * sell_price * self.brokerage_fee_percent
                        profit -= brokerage_cost
                        trades.append({
                            "timestamp": row.name,
                            "action": "cover",
                            "price": sell_price,
                            "qty": abs(self.position),
                            "profit": profit,
                            "brokerage_cost": brokerage_cost
                        })
                        self.position = 0

                    # Abrir nova posição comprada
                    self.entry_price = buy_price
                    self.position = 1  # Simplificado para 1 unidade
                    brokerage_cost = self.position * buy_price * self.brokerage_fee_percent
                    trades.append({
                        "timestamp": row.name,
                        "action": "buy",
                        "price": buy_price,
                        "qty": self.position,
                        "profit": -brokerage_cost, # Custo inicial da corretagem
                        "brokerage_cost": brokerage_cost
                    })

            elif signal == -1:  # Sinal de venda
                if self.position >= 0:  # Se não estiver vendido ou estiver comprado
                    # Fechar posição comprada antes de vender
                    if self.position > 0:
                        profit = (sell_price - self.entry_price) * self.position
                        brokerage_cost = self.position * sell_price * self.brokerage_fee_percent
                        profit -= brokerage_cost
                        trades.append({
                            "timestamp": row.name,
                            "action": "sell",
                            "price": sell_price,
                            "qty": self.position,
                            "profit": profit,
                            "brokerage_cost": brokerage_cost
                        })
                        self.position = 0

                    # Abrir nova posição vendida
                    self.entry_price = sell_price
                    self.position = -1  # Simplificado para -1 unidade
                    brokerage_cost = abs(self.position) * sell_price * self.brokerage_fee_percent
                    trades.append({
                        "timestamp": row.name,
                        "action": "short",
                        "price": sell_price,
                        "qty": abs(self.position),
                        "profit": -brokerage_cost, # Custo inicial da corretagem
                        "brokerage_cost": brokerage_cost
                    })

        # Fechar qualquer posição aberta no final do backtest
        if self.position > 0:
            profit = (sell_price - self.entry_price) * self.position
            brokerage_cost = self.position * sell_price * self.brokerage_fee_percent
            profit -= brokerage_cost
            trades.append({
                "timestamp": df.index[-1],
                "action": "sell",
                "price": sell_price,
                "qty": self.position,
                "profit": profit,
                "brokerage_cost": brokerage_cost
            })
        elif self.position < 0:
            profit = (self.entry_price - buy_price) * abs(self.position)
            brokerage_cost = abs(self.position) * buy_price * self.brokerage_fee_percent
            profit -= brokerage_cost
            trades.append({
                "timestamp": df.index[-1],
                "action": "cover",
                "price": buy_price,
                "qty": abs(self.position),
                "profit": profit,
                "brokerage_cost": brokerage_cost
            })

        return ExecutionResult(trades)


