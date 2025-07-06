#!/usr/bin/env python3
"""
Testes unitários para os indicadores técnicos
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from indicators.ema_indicator import EMAIndicator
from indicators.rsi_indicator import RSIIndicator
from indicators.macd_indicator import MACDIndicator
from indicators.atr_indicator import ATRIndicator

class TestIndicators(unittest.TestCase):
    
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
    
    def test_ema_indicator(self):
        """Testar indicador EMA"""
        indicator = EMAIndicator(window=20)
        result = indicator.calculate(self.test_data)
        
        # Verificar se o resultado é uma Series
        self.assertIsInstance(result, pd.Series)
        
        # Verificar se não há valores NaN após o período de aquecimento
        self.assertFalse(result.iloc[25:].isna().any())
        
        # Verificar se os valores são numéricos
        self.assertTrue(pd.api.types.is_numeric_dtype(result))
    
    def test_rsi_indicator(self):
        """Testar indicador RSI"""
        indicator = RSIIndicator(window=14)
        result = indicator.calculate(self.test_data)
        
        # Verificar se o resultado é uma Series
        self.assertIsInstance(result, pd.Series)
        
        # Verificar se os valores estão no range 0-100
        valid_values = result.dropna()
        self.assertTrue((valid_values >= 0).all())
        self.assertTrue((valid_values <= 100).all())
    
    def test_macd_indicator(self):
        """Testar indicador MACD"""
        indicator = MACDIndicator()
        result = indicator.calculate(self.test_data)
        
        # Verificar se o resultado é uma Series
        self.assertIsInstance(result, pd.Series)
        
        # Verificar se os valores são numéricos
        self.assertTrue(pd.api.types.is_numeric_dtype(result))
    
    def test_atr_indicator(self):
        """Testar indicador ATR"""
        indicator = ATRIndicator(window=14)
        result = indicator.calculate(self.test_data)
        
        # Verificar se o resultado é uma Series
        self.assertIsInstance(result, pd.Series)
        
        # Verificar se todos os valores são positivos (ATR sempre >= 0)
        valid_values = result.dropna()
        self.assertTrue((valid_values >= 0).all())

if __name__ == '__main__':
    unittest.main()

