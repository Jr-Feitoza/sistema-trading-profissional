#!/usr/bin/env python3
"""
Testes unitários para o BacktestEngine
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.backtest_engine import BacktestEngine
from engine.order_manager import OrderManager
from strategies.rsi_strategy import RSIStrategy

class MockDataLoader:
    """Mock do data loader para testes"""
    
    def __init__(self, data):
        self.data = data
    
    def load_historical_data(self, symbol=None, interval=None):
        return self.data

class TestBacktestEngine(unittest.TestCase):
    
    def setUp(self):
        """Configurar dados de teste"""
        dates = pd.date_range('2023-01-01', periods=100, freq='1H')
        np.random.seed(42)
        
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        self.test_data = pd.DataFrame({
            'open': prices + np.random.randn(100) * 0.1,
            'high': prices + np.abs(np.random.randn(100) * 0.3),
            'low': prices - np.abs(np.random.randn(100) * 0.3),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        self.strategy = RSIStrategy(period=14, overbought=70, oversold=30)
        self.data_loader = MockDataLoader(self.test_data)
        self.order_manager = OrderManager(mode="backtest")
    
    def test_backtest_engine_initialization(self):
        """Testar inicialização do BacktestEngine"""
        engine = BacktestEngine(
            strategy=self.strategy,
            data_loader=self.data_loader,
            order_manager=self.order_manager
        )
        
        self.assertEqual(engine.strategy, self.strategy)
        self.assertEqual(engine.data_loader, self.data_loader)
        self.assertEqual(engine.order_manager, self.order_manager)
        self.assertEqual(engine.position, 0)
        self.assertEqual(engine.entry_price, 0)
    
    def test_backtest_execution(self):
        """Testar execução do backtest"""
        engine = BacktestEngine(
            strategy=self.strategy,
            data_loader=self.data_loader,
            order_manager=self.order_manager
        )
        
        result = engine.run()
        
        # Verificar se o resultado tem a estrutura esperada
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'trades'))
        self.assertTrue(hasattr(result, 'calculate_metrics'))
        
        # Verificar se as métricas podem ser calculadas
        metrics = result.calculate_metrics()
        self.assertIsInstance(metrics, dict)
        
        # Verificar se as métricas esperadas estão presentes
        expected_metrics = [
            'total_trades', 'roi', 'win_rate', 'average_gain',
            'average_loss', 'profit_factor', 'max_drawdown'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
    
    def test_slippage_and_brokerage(self):
        """Testar aplicação de slippage e custos de corretagem"""
        engine = BacktestEngine(
            strategy=self.strategy,
            data_loader=self.data_loader,
            order_manager=self.order_manager,
            slippage_percent=0.001,
            brokerage_fee_percent=0.001
        )
        
        self.assertEqual(engine.slippage_percent, 0.001)
        self.assertEqual(engine.brokerage_fee_percent, 0.001)
        
        result = engine.run()
        
        # Verificar se os trades incluem custos de corretagem
        if result.trades:
            for trade in result.trades:
                self.assertIn('brokerage_cost', trade)

if __name__ == '__main__':
    unittest.main()

