#!/usr/bin/env python3
"""
Interface Headless para o Sistema de Trading
Permite execução via linha de comando sem dependência do Streamlit
"""

import sys
import os
import pandas as pd

# Adicionar o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategies.irf2_strategy import IRF2Strategy
from strategies.rsi_strategy import RSIStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from connectors.binance_connector import BinanceConnector
from engine.backtest_engine import BacktestEngine
from engine.order_manager import OrderManager
from utils.profile_manager import salvar_perfil, carregar_perfil, listar_perfis

def executar_backtest_com_perfil(nome_perfil):
    """Executa um backtest usando um perfil salvo"""
    print(f"Carregando perfil: {nome_perfil}")
    
    perfil = carregar_perfil(nome_perfil)
    if not perfil:
        print(f"❌ Perfil '{nome_perfil}' não encontrado.")
        return

    # Extrair configurações do perfil
    symbol = perfil.get("symbol", "BTCUSDT")
    timeframe = perfil.get("timeframe", "15m")
    estrategia_nome = perfil.get("estrategia", "RSI")
    parametros = perfil.get("parametros", {})
    overlays = perfil.get("overlays", [])

    print(f"📊 Configurações do Perfil:")
    print(f"   Ativo: {symbol}")
    print(f"   Timeframe: {timeframe}")
    print(f"   Estratégia: {estrategia_nome}")
    print(f"   Parâmetros: {parametros}")
    print(f"   Indicadores: {overlays}")
    print()

    # Criar estratégia baseada no perfil
    if estrategia_nome == "IRF2 (Rompimento)":
        strategy = IRF2Strategy(breakout_margin=parametros.get("margin", 1.0))
    elif estrategia_nome == "RSI (Sobrecompra/venda)":
        strategy = RSIStrategy(
            period=parametros.get("period", 14),
            overbought=parametros.get("overbought", 70),
            oversold=parametros.get("oversold", 30)
        )
    elif estrategia_nome == "Médias Móveis":
        strategy = MovingAverageStrategy(
            short_window=parametros.get("short_window", 10),
            long_window=parametros.get("long_window", 50)
        )
    else:
        print(f"❌ Estratégia '{estrategia_nome}' não reconhecida.")
        return

    print(f"🚀 Executando backtest com estratégia {estrategia_nome} no par {symbol} [{timeframe}]")
    print("⏳ Carregando dados históricos...")

    try:
        # Configurar componentes do backtest
        data_loader = BinanceConnector()
        order_manager = OrderManager(mode="backtest")
        engine = BacktestEngine(strategy, data_loader, order_manager)

        # Carregar dados históricos
        df = data_loader.load_historical_data(symbol=symbol, interval=timeframe)
        print(f"✅ Dados carregados: {len(df)} candles")

        # Executar backtest
        print("🔄 Executando estratégia...")
        engine.data_loader.load_historical_data = lambda: df
        resultado = engine.run()
        
        trades = resultado.trades
        metricas = resultado.calculate_metrics()

        # Exibir resultados
        print("\n" + "="*60)
        print("📈 RESULTADOS DO BACKTEST")
        print("="*60)
        
        print(f"Total de Operações: {metricas['total_trades']}")
        print(f"ROI: {metricas['roi']*100:.2f}%")
        print(f"Taxa de Acerto: {metricas['win_rate']*100:.2f}%")
        print(f"Lucro Médio: ${metricas['average_gain']:.2f}")
        print(f"Prejuízo Médio: ${metricas['average_loss']:.2f}")
        print(f"Fator de Lucro: {metricas['profit_factor']:.2f}")
        print(f"Máximo Rebaixamento: {metricas['max_drawdown']*100:.2f}%")
        
        if trades:
            print(f"\n📋 Últimas 5 operações:")
            for trade in trades[-5:]:
                action = trade['action']
                price = trade['price']
                profit = trade.get('profit', 0)
                timestamp = trade['timestamp']
                print(f"   {timestamp} | {action.upper()} @ ${price:.2f} | P&L: ${profit:.2f}")
        
        print("="*60)
        
        return resultado

    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")
        return None

def criar_perfil_exemplo():
    """Cria um perfil de exemplo para demonstração"""
    perfil_exemplo = {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "estrategia": "RSI (Sobrecompra/venda)",
        "parametros": {
            "period": 14,
            "overbought": 70,
            "oversold": 30
        },
        "overlays": ["EMA20", "RSI14"]
    }
    
    salvar_perfil("Exemplo_RSI", perfil_exemplo)
    print("✅ Perfil de exemplo 'Exemplo_RSI' criado com sucesso!")

def main():
    """Função principal para execução headless"""
    print("🤖 Sistema de Trading - Modo Headless")
    print("="*50)
    
    perfis = listar_perfis()
    
    if not perfis:
        print("⚠️  Nenhum perfil encontrado.")
        print("Criando perfil de exemplo...")
        criar_perfil_exemplo()
        perfis = listar_perfis()
    
    print("📁 Perfis disponíveis:")
    for i, perfil in enumerate(perfis, 1):
        print(f"   {i}. {perfil}")
    
    try:
        escolha = input("\nEscolha um perfil (número) ou 'q' para sair: ").strip()
        
        if escolha.lower() == 'q':
            print("👋 Saindo...")
            return
        
        idx = int(escolha) - 1
        if 0 <= idx < len(perfis):
            executar_backtest_com_perfil(perfis[idx])
        else:
            print("❌ Opção inválida.")
    
    except ValueError:
        print("❌ Por favor, digite um número válido.")
    except KeyboardInterrupt:
        print("\n👋 Execução interrompida pelo usuário.")

if __name__ == "__main__":
    main()

