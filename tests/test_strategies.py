#!/usr/bin/env python3
"""
Testes unitários para as estratégias de trading
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategies.rsi_strategy import RSIStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from strategies.irf2_strategy import IRF2Strategy

class TestStrategies(unittest.TestCase):
    
    def setUp(self):
        """Configurar dados de teste"""
        # Criar dados de exemplo para testes
        dates = pd.date_range('2023-01-01', periods=100, freq='1H')
        np.random.seed(42)  # Para resultados reproduzíveis
        
        # Simular dados de preços
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        self.test_data = pd.DataFrame({
            'open': prices + np.random.randn(100) * 0.1,
            'high': prices + np.abs(np.random.randn(100) * 0.3),
            'low': prices - np.abs(np.random.randn(100) * 0.3),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
    
    def test_rsi_strategy_initialization(self):
        """Testar inicialização da estratégia RSI"""
        strategy = RSIStrategy(period=14, overbought=70, oversold=30)
        
        self.assertEqual(strategy.period, 14)
        self.assertEqual(strategy.overbought, 70)
        self.assertEqual(strategy.oversold, 30)
    
    def test_rsi_strategy_signals(self):
        """Testar geração de sinais da estratégia RSI"""
        strategy = RSIStrategy(period=14, overbought=70, oversold=30)
        result = strategy.generate_signals(self.test_data.copy())
        
        # Verificar se a coluna de sinal foi criada
        self.assertIn('signal', result.columns)
        self.assertIn('rsi', result.columns)
        
        # Verificar se os sinais estão no range correto
        unique_signals = result['signal'].unique()
        for signal in unique_signals:
            self.assertIn(signal, [-1, 0, 1])
    
    def test_moving_average_strategy_initialization(self):
        """Testar inicialização da estratégia de médias móveis"""
        strategy = MovingAverageStrategy(short_window=10, long_window=50)
        
        self.assertEqual(strategy.short_window, 10)
        self.assertEqual(strategy.long_window, 50)
    
    def test_moving_average_strategy_signals(self):
        """Testar geração de sinais da estratégia de médias móveis"""
        strategy = MovingAverageStrategy(short_window=10, long_window=20)
        result = strategy.generate_signals(self.test_data.copy())
        
        # Verificar se as colunas necessárias foram criadas
        self.assertIn('signal', result.columns)
        self.assertIn('short_ma', result.columns)
        self.assertIn('long_ma', result.columns)
        
        # Verificar se os sinais estão no range correto
        unique_signals = result['signal'].unique()
        for signal in unique_signals:
            self.assertIn(signal, [-1, 0, 1])
    
    def test_irf2_strategy_initialization(self):
        """Testar inicialização da estratégia IRF2"""
        strategy = IRF2Strategy(breakout_margin=1.0)
        
        self.assertEqual(strategy.breakout_margin, 1.0)
    
    def test_irf2_strategy_signals(self):
        """Testar geração de sinais da estratégia IRF2"""
        strategy = IRF2Strategy(breakout_margin=1.0)
        result = strategy.generate_signals(self.test_data.copy())
        
        # Verificar se a coluna de sinal foi criada
        self.assertIn('signal', result.columns)
        
        # Verificar se os sinais estão no range correto
        unique_signals = result['signal'].unique()
        for signal in unique_signals:
            self.assertIn(signal, [-1, 0, 1])

if __name__ == '__main__':
    unittest.main()

