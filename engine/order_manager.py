class OrderManager:
    def __init__(self, mode="backtest"):
        self.mode = mode
        self.orders = []

    def execute_order(self, symbol, order_type, price, quantity):
        # Lógica simplificada de execução de ordem para backtest
        order = {
            "symbol": symbol,
            "type": order_type,
            "price": price,
            "quantity": quantity,
            "status": "filled"
        }
        self.orders.append(order)
        return order


