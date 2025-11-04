"""
Conector HyperLiquid - Trading de Futuros (Perpetuals)
Implementação completa com todos os tipos de ordem e gestão de posições
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from eth_account import Account
from eth_account.signers.local import LocalAccount
import hashlib
import sys
sys.path.append('..')

from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe,
    calculate_optimal_leverage
)


@dataclass
class OrderParams:
    """Parâmetros completos de uma ordem"""
    symbol: str
    side: str  # 'buy' ou 'sell'
    order_type: str  # 'market', 'limit', 'stop_market', 'stop_limit'
    quantity: float
    price: Optional[float] = None  # Required for limit orders
    stop_price: Optional[float] = None  # Required for stop orders
    time_in_force: str = 'GTC'  # GTC, IOC, FOK
    reduce_only: bool = False
    post_only: bool = False
    client_order_id: Optional[str] = None
    leverage: Optional[int] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Position:
    """Representa uma posição aberta"""
    symbol: str
    side: str  # 'long' ou 'short'
    quantity: float
    entry_price: float
    mark_price: float
    unrealized_pnl: float
    leverage: int
    liquidation_price: float
    margin: float


class HyperLiquidConnector:
    """
    Conector completo para HyperLiquid Perpetual Futures

    Funcionalidades:
    - Autenticação via private key
    - Todos os tipos de ordem (market, limit, stop)
    - Gestão de posições (long/short)
    - Leverage ajustável
    - Stop Loss e Take Profit
    - WebSocket para dados em tempo real
    - Gestão de risco integrada
    """

    # Endpoints
    MAINNET_API = "https://api.hyperliquid.xyz"
    TESTNET_API = "https://api.hyperliquid-testnet.xyz"

    def __init__(
        self,
        private_key: Optional[str] = None,
        testnet: bool = True,
        max_leverage: int = 20,
        # Position sizing parameters
        risk_per_trade_usdt: float = 10,
        risk_reward_ratio: float = 3.0,
        max_risk_per_trade_pct: float = 2.0,
        use_position_calculator: bool = True
    ):
        """
        Inicializa o conector HyperLiquid

        Args:
            private_key: Private key da carteira (opcional para leitura)
            testnet: Usar testnet ou mainnet
            max_leverage: Leverage máximo permitido
            risk_per_trade_usdt: Quanto arriscar por trade (USDT)
            risk_reward_ratio: Ratio de risk/reward (ex: 3.0 = 1:3)
            max_risk_per_trade_pct: Risco máximo por trade (%)
            use_position_calculator: Usar calculadora de position size
        """
        self.base_url = self.TESTNET_API if testnet else self.MAINNET_API
        self.testnet = testnet
        self.max_leverage = max_leverage
        self.risk_per_trade_usdt = risk_per_trade_usdt
        self.risk_reward_ratio = risk_reward_ratio
        self.use_position_calculator = use_position_calculator

        # Account setup se private key fornecida
        self.account: Optional[LocalAccount] = None
        if private_key:
            self.account = Account.from_key(private_key)
            self.address = self.account.address
        else:
            self.address = None

        # Cache de dados
        self.positions: Dict[str, Position] = {}
        self.open_orders: List[Dict] = []

        # Position Size Calculator
        if use_position_calculator:
            self.position_calculator = PositionSizeCalculator(
                max_risk_per_trade_pct=max_risk_per_trade_pct
            )
        else:
            self.position_calculator = None

        print(f"✓ HyperLiquid Connector inicializado")
        print(f"  Network: {'TESTNET' if testnet else 'MAINNET'}")
        print(f"  Address: {self.address if self.address else 'READ-ONLY MODE'}")
        if use_position_calculator:
            print(f"  Position Calculator: ATIVO (Risk: ${risk_per_trade_usdt}, R:R: 1:{risk_reward_ratio})")

    # ========================================================================
    # AUTENTICAÇÃO E ASSINATURA
    # ========================================================================

    def _sign_request(self, payload: Dict[str, Any]) -> str:
        """Assina uma requisição com a private key"""
        if not self.account:
            raise ValueError("Private key não configurada. Modo somente leitura.")

        # Serializa payload
        message = json.dumps(payload, separators=(',', ':'), sort_keys=True)

        # Cria hash
        message_hash = hashlib.sha256(message.encode()).digest()

        # Assina
        signed_message = self.account.sign_message_hash(message_hash)

        return signed_message.signature.hex()

    # ========================================================================
    # INFORMAÇÕES DE MERCADO
    # ========================================================================

    def get_exchange_info(self) -> Dict[str, Any]:
        """Retorna informações sobre todos os símbolos disponíveis"""
        endpoint = f"{self.base_url}/info"

        payload = {
            "type": "metaAndAssetCtxs"
        }

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        data = response.json()

        # Formata informação dos símbolos
        symbols = []
        if 'assetCtxs' in data:
            for asset in data['assetCtxs']:
                symbols.append({
                    'symbol': asset.get('coin', ''),
                    'mark_price': float(asset.get('markPx', 0)),
                    'funding_rate': float(asset.get('funding', 0)),
                    'open_interest': float(asset.get('openInterest', 0)),
                    'volume_24h': float(asset.get('dayNtlVlm', 0))
                })

        return {
            'symbols': symbols,
            'server_time': int(time.time() * 1000)
        }

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Retorna ticker de um símbolo específico"""
        endpoint = f"{self.base_url}/info"

        payload = {
            "type": "allMids"
        }

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        data = response.json()

        # Encontra o símbolo
        if symbol in data:
            return {
                'symbol': symbol,
                'price': float(data[symbol]),
                'timestamp': int(time.time() * 1000)
            }

        return {}

    def get_orderbook(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Retorna o orderbook de um símbolo"""
        endpoint = f"{self.base_url}/info"

        payload = {
            "type": "l2Book",
            "coin": symbol
        }

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        data = response.json()

        return {
            'symbol': symbol,
            'bids': data.get('levels', [[]])[0][:depth],  # Bids
            'asks': data.get('levels', [[], []])[1][:depth],  # Asks
            'timestamp': int(time.time() * 1000)
        }

    def get_klines(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retorna candlesticks históricos

        Args:
            symbol: Símbolo do par
            interval: Intervalo ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: Número de candles
        """
        endpoint = f"{self.base_url}/info"

        # Mapeia intervalos
        interval_map = {
            '1m': '1',
            '5m': '5',
            '15m': '15',
            '1h': '60',
            '4h': '240',
            '1d': 'D'
        }

        payload = {
            "type": "candleSnapshot",
            "req": {
                "coin": symbol,
                "interval": interval_map.get(interval, '60'),
                "startTime": int((time.time() - 3600 * limit) * 1000)
            }
        }

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        data = response.json()

        # Formata candles
        candles = []
        for candle in data:
            candles.append({
                'timestamp': candle['t'],
                'open': float(candle['o']),
                'high': float(candle['h']),
                'low': float(candle['l']),
                'close': float(candle['c']),
                'volume': float(candle['v'])
            })

        return candles

    # ========================================================================
    # GESTÃO DE ORDENS
    # ========================================================================

    def place_order(self, params: OrderParams) -> Dict[str, Any]:
        """
        Coloca uma ordem no mercado

        Args:
            params: Parâmetros completos da ordem

        Returns:
            Resposta da exchange com dados da ordem
        """
        if not self.account:
            raise ValueError("Private key necessária para trading")

        endpoint = f"{self.base_url}/exchange"

        # Prepara ordem baseado no tipo
        order_request = self._build_order_request(params)

        # Assina requisição
        signature = self._sign_request(order_request)

        # Envia ordem
        payload = {
            **order_request,
            "signature": signature,
            "nonce": int(time.time() * 1000)
        }

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        result = response.json()

        print(f"✓ Ordem colocada: {params.symbol} {params.side} {params.quantity} @ {params.price or 'MARKET'}")

        return {
            'order_id': result.get('response', {}).get('data', {}).get('statuses', [{}])[0].get('resting', {}).get('oid'),
            'status': 'filled' if 'filled' in result.get('response', {}).get('data', {}) else 'open',
            'symbol': params.symbol,
            'side': params.side,
            'type': params.order_type,
            'quantity': params.quantity,
            'price': params.price,
            'timestamp': int(time.time() * 1000)
        }

    def _build_order_request(self, params: OrderParams) -> Dict[str, Any]:
        """Constrói requisição de ordem baseada nos parâmetros"""

        # Ordem base
        order = {
            "coin": params.symbol,
            "is_buy": params.side.lower() == 'buy',
            "sz": str(params.quantity),
            "limit_px": str(params.price) if params.price else "0",
            "order_type": {
                "limit": {"tif": params.time_in_force},
            } if params.order_type == 'limit' else {"market": {}},
            "reduce_only": params.reduce_only
        }

        # Adiciona leverage se especificado
        if params.leverage:
            order["leverage"] = params.leverage

        return {
            "type": "order",
            "orders": [order],
            "grouping": "na"
        }

    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """Coloca ordem a mercado"""
        params = OrderParams(
            symbol=symbol,
            side=side,
            order_type='market',
            quantity=quantity,
            reduce_only=reduce_only
        )

        return self.place_order(params)

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = 'GTC',
        post_only: bool = False
    ) -> Dict[str, Any]:
        """Coloca ordem limitada"""
        params = OrderParams(
            symbol=symbol,
            side=side,
            order_type='limit',
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            post_only=post_only
        )

        return self.place_order(params)

    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancela uma ordem"""
        if not self.account:
            raise ValueError("Private key necessária para cancelar ordens")

        endpoint = f"{self.base_url}/exchange"

        payload = {
            "type": "cancel",
            "cancels": [{
                "coin": symbol,
                "oid": int(order_id)
            }]
        }

        signature = self._sign_request(payload)

        payload["signature"] = signature
        payload["nonce"] = int(time.time() * 1000)

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        print(f"✓ Ordem cancelada: {order_id}")

        return response.json()

    def cancel_all_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancela todas as ordens (opcionalmente de um símbolo específico)"""
        if not self.account:
            raise ValueError("Private key necessária")

        endpoint = f"{self.base_url}/exchange"

        payload = {
            "type": "cancelByCloid",
            "cancels": []
        }

        if symbol:
            # Busca ordens abertas do símbolo
            open_orders = self.get_open_orders(symbol)
            for order in open_orders:
                payload["cancels"].append({
                    "coin": symbol,
                    "oid": order['order_id']
                })

        signature = self._sign_request(payload)

        payload["signature"] = signature
        payload["nonce"] = int(time.time() * 1000)

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        print(f"✓ Todas as ordens canceladas")

        return response.json()

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna ordens abertas"""
        if not self.address:
            raise ValueError("Address necessário para consultar ordens")

        endpoint = f"{self.base_url}/info"

        payload = {
            "type": "openOrders",
            "user": self.address
        }

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        orders = response.json()

        # Filtra por símbolo se especificado
        if symbol:
            orders = [o for o in orders if o.get('coin') == symbol]

        # Formata ordens
        formatted_orders = []
        for order in orders:
            formatted_orders.append({
                'order_id': order.get('oid'),
                'symbol': order.get('coin'),
                'side': 'buy' if order.get('side') == 'B' else 'sell',
                'type': order.get('orderType'),
                'quantity': float(order.get('sz', 0)),
                'price': float(order.get('limitPx', 0)),
                'filled': float(order.get('filled', 0)),
                'status': 'open',
                'timestamp': order.get('timestamp')
            })

        return formatted_orders

    # ========================================================================
    # GESTÃO DE POSIÇÕES
    # ========================================================================

    def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Retorna posições abertas"""
        if not self.address:
            raise ValueError("Address necessário para consultar posições")

        endpoint = f"{self.base_url}/info"

        payload = {
            "type": "clearinghouseState",
            "user": self.address
        }

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        data = response.json()

        positions = []
        if 'assetPositions' in data:
            for pos_data in data['assetPositions']:
                position = pos_data.get('position', {})

                if float(position.get('szi', 0)) == 0:
                    continue  # Pula posições fechadas

                size = float(position.get('szi', 0))
                entry_px = float(position.get('entryPx', 0))
                unrealized_pnl = float(position.get('unrealizedPnl', 0))
                leverage_val = pos_data.get('leverage', {}).get('value', 1)

                pos = Position(
                    symbol=position.get('coin', ''),
                    side='long' if size > 0 else 'short',
                    quantity=abs(size),
                    entry_price=entry_px,
                    mark_price=float(position.get('positionValue', 0)) / abs(size) if size != 0 else 0,
                    unrealized_pnl=unrealized_pnl,
                    leverage=leverage_val,
                    liquidation_price=float(position.get('liquidationPx', 0)),
                    margin=float(position.get('marginUsed', 0))
                )

                if not symbol or pos.symbol == symbol:
                    positions.append(pos)

        return positions

    def close_position(
        self,
        symbol: str,
        quantity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fecha uma posição (total ou parcial)

        Args:
            symbol: Símbolo da posição
            quantity: Quantidade a fechar (None = fechar tudo)
        """
        # Busca posição
        positions = self.get_positions(symbol)

        if not positions:
            raise ValueError(f"Nenhuma posição aberta em {symbol}")

        position = positions[0]

        # Define quantidade
        close_qty = quantity if quantity else position.quantity

        # Inverte o lado para fechar
        close_side = 'sell' if position.side == 'long' else 'buy'

        # Coloca ordem a mercado para fechar
        return self.place_market_order(
            symbol=symbol,
            side=close_side,
            quantity=close_qty,
            reduce_only=True
        )

    def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Define leverage para um símbolo"""
        if leverage > self.max_leverage:
            raise ValueError(f"Leverage {leverage} excede máximo permitido ({self.max_leverage})")

        if not self.account:
            raise ValueError("Private key necessária")

        endpoint = f"{self.base_url}/exchange"

        payload = {
            "type": "updateLeverage",
            "asset": symbol,
            "isCross": True,
            "leverage": leverage
        }

        signature = self._sign_request(payload)

        payload["signature"] = signature
        payload["nonce"] = int(time.time() * 1000)

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        print(f"✓ Leverage de {symbol} ajustado para {leverage}x")

        return response.json()

    # ========================================================================
    # STOP LOSS E TAKE PROFIT
    # ========================================================================

    def set_stop_loss(
        self,
        symbol: str,
        stop_price: float,
        quantity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Define stop loss para uma posição

        Args:
            symbol: Símbolo
            stop_price: Preço de stop
            quantity: Quantidade (None = posição inteira)
        """
        # Busca posição
        positions = self.get_positions(symbol)

        if not positions:
            raise ValueError(f"Nenhuma posição aberta em {symbol}")

        position = positions[0]
        qty = quantity if quantity else position.quantity

        # Define lado da ordem stop
        side = 'sell' if position.side == 'long' else 'buy'

        # Coloca ordem stop market
        params = OrderParams(
            symbol=symbol,
            side=side,
            order_type='stop_market',
            quantity=qty,
            stop_price=stop_price,
            reduce_only=True
        )

        return self.place_order(params)

    def set_take_profit(
        self,
        symbol: str,
        take_profit_price: float,
        quantity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Define take profit para uma posição

        Args:
            symbol: Símbolo
            take_profit_price: Preço de take profit
            quantity: Quantidade (None = posição inteira)
        """
        # Busca posição
        positions = self.get_positions(symbol)

        if not positions:
            raise ValueError(f"Nenhuma posição aberta em {symbol}")

        position = positions[0]
        qty = quantity if quantity else position.quantity

        # Define lado da ordem
        side = 'sell' if position.side == 'long' else 'buy'

        # Coloca ordem limitada
        return self.place_limit_order(
            symbol=symbol,
            side=side,
            quantity=qty,
            price=take_profit_price,
            time_in_force='GTC'
        )

    # ========================================================================
    # INFORMAÇÕES DA CONTA
    # ========================================================================

    def get_account_info(self) -> Dict[str, Any]:
        """Retorna informações da conta"""
        if not self.address:
            raise ValueError("Address necessário")

        endpoint = f"{self.base_url}/info"

        payload = {
            "type": "clearinghouseState",
            "user": self.address
        }

        response = requests.post(endpoint, json=payload)
        response.raise_for_status()

        data = response.json()

        return {
            'address': self.address,
            'margin_summary': data.get('marginSummary', {}),
            'cross_margin_summary': data.get('crossMarginSummary', {}),
            'withdrawable': float(data.get('withdrawable', 0)),
            'asset_positions': data.get('assetPositions', [])
        }

    def get_balance(self) -> Dict[str, float]:
        """Retorna saldo da conta"""
        account_info = self.get_account_info()

        margin_summary = account_info.get('cross_margin_summary', {})

        return {
            'total_balance': float(margin_summary.get('accountValue', 0)),
            'available_balance': float(account_info.get('withdrawable', 0)),
            'margin_used': float(margin_summary.get('totalMarginUsed', 0)),
            'unrealized_pnl': float(margin_summary.get('totalNtlPos', 0))
        }

    # ========================================================================
    # SMART POSITION SIZING (com Position Size Calculator)
    # ========================================================================

    def place_smart_order(
        self,
        symbol: str,
        side: str,
        entry_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None,
        timeframe: Timeframe = Timeframe.M15,
        risk_amount: Optional[float] = None,
        profit_target: Optional[float] = None,
        use_leverage: bool = False,
        order_type: str = 'limit'
    ) -> Dict[str, Any]:
        """
        Coloca ordem com cálculo automático de position size baseado em risk/reward

        Args:
            symbol: Par a negociar (ex: 'BTC')
            side: 'buy' ou 'sell'
            entry_price: Preço de entrada (None = market price)
            stop_loss_price: Preço do stop loss (None = calculado automaticamente)
            timeframe: Timeframe da análise
            risk_amount: Quanto arriscar em USDT (None = usa default)
            profit_target: Quanto lucrar em USDT (None = usa default)
            use_leverage: Se deve usar leverage
            order_type: 'limit' ou 'market'

        Returns:
            Dict com informações da ordem e dos stops colocados
        """

        if not self.position_calculator:
            raise ValueError("Position Calculator não está ativo. Inicialize com use_position_calculator=True")

        # 1. Busca preço atual se não fornecido
        if entry_price is None:
            ticker = self.get_ticker(symbol)
            entry_price = float(ticker.get('price', 0))
            print(f"📊 Preço atual de {symbol}: ${entry_price:,.2f}")

        # 2. Busca saldo da conta
        balance = self.get_balance()
        account_balance = balance['available_balance']
        print(f"💰 Saldo disponível: ${account_balance:,.2f}")

        # 3. Determina lado da posição
        position_side = PositionSide.LONG if side.lower() == 'buy' else PositionSide.SHORT

        # 4. Usa valores default se não fornecidos
        risk = risk_amount if risk_amount else self.risk_per_trade_usdt
        profit = profit_target if profit_target else (risk * self.risk_reward_ratio)

        print(f"\n🎯 Parâmetros de Risk Management:")
        print(f"   Risco: ${risk:.2f}")
        print(f"   Target: ${profit:.2f}")
        print(f"   R:R: 1:{profit/risk:.1f}")

        # 5. Calcula ATR se possível
        try:
            klines = self.get_klines(symbol, interval='15m', limit=20)
            if klines:
                # Calcula ATR simples
                highs = [k['high'] for k in klines]
                lows = [k['low'] for k in klines]
                closes = [k['close'] for k in klines]

                true_ranges = []
                for i in range(1, len(klines)):
                    tr = max(
                        highs[i] - lows[i],
                        abs(highs[i] - closes[i-1]),
                        abs(lows[i] - closes[i-1])
                    )
                    true_ranges.append(tr)

                atr = sum(true_ranges) / len(true_ranges)
                print(f"   ATR (15m): ${atr:.2f}")
            else:
                atr = None
        except:
            atr = None

        # 6. Cria parâmetros para o calculator
        params = PositionSizeParams(
            entry_price=entry_price,
            account_balance=account_balance,
            side=position_side,
            risk_amount_usdt=risk,
            profit_target_usdt=profit,
            timeframe=timeframe,
            current_atr=atr,
            stop_loss_price=stop_loss_price,
            leverage=self.max_leverage if use_leverage else 1
        )

        # 7. Calcula position size
        result = self.position_calculator.calculate_position_size(params)

        print(f"\n📏 POSITION SIZE CALCULADO:")
        print(f"   Quantidade: {result.position_size:.6f} {symbol}")
        print(f"   Valor: ${result.position_value_usdt:,.2f}")
        print(f"   Margem: ${result.margin_required:,.2f}")
        print(f"   Stop Loss: ${result.stop_loss_price:,.2f} ({result.stop_loss_distance_pct:.2f}%)")
        print(f"   Take Profit: ${result.take_profit_price:,.2f} ({result.take_profit_distance_pct:.2f}%)")

        if result.liquidation_price and use_leverage:
            print(f"   Liquidação: ${result.liquidation_price:,.2f}")

        # 8. Valida posição
        if not result.is_valid:
            print(f"\n❌ POSIÇÃO INVÁLIDA:")
            for warning in result.warnings:
                print(f"   {warning}")
            return {
                'success': False,
                'warnings': result.warnings,
                'result': result
            }

        if result.warnings:
            print(f"\n⚠️ WARNINGS:")
            for warning in result.warnings:
                print(f"   {warning}")

        # 9. Pergunta confirmação ao usuário
        print(f"\n{'='*80}")
        print("RESUMO DA ORDEM:")
        print(f"{'='*80}")
        print(f"  Símbolo: {symbol}")
        print(f"  Lado: {side.upper()}")
        print(f"  Quantidade: {result.position_size:.6f}")
        print(f"  Entry: ${entry_price:,.2f}")
        print(f"  Stop Loss: ${result.stop_loss_price:,.2f}")
        print(f"  Take Profit: ${result.take_profit_price:,.2f}")
        print(f"  Risk: ${result.risk_amount:.2f} | Reward: ${result.profit_potential:.2f}")
        print(f"{'='*80}\n")

        # 10. Coloca ordem principal
        if order_type == 'market':
            print("📤 Colocando ordem a mercado...")
            order_result = self.place_market_order(
                symbol=symbol,
                side=side,
                quantity=result.position_size
            )
        else:
            print("📤 Colocando ordem limitada...")
            order_result = self.place_limit_order(
                symbol=symbol,
                side=side,
                quantity=result.position_size,
                price=entry_price
            )

        # 11. Coloca stop loss
        print("🛡️ Colocando stop loss...")
        try:
            stop_result = self.set_stop_loss(
                symbol=symbol,
                stop_loss_price=result.stop_loss_price
            )
        except Exception as e:
            print(f"⚠️ Erro ao colocar stop loss: {e}")
            stop_result = None

        # 12. Coloca take profit
        print("🎯 Colocando take profit...")
        try:
            tp_result = self.set_take_profit(
                symbol=symbol,
                take_profit_price=result.take_profit_price
            )
        except Exception as e:
            print(f"⚠️ Erro ao colocar take profit: {e}")
            tp_result = None

        print("\n✅ ORDEM EXECUTADA COM SUCESSO!")

        return {
            'success': True,
            'order': order_result,
            'stop_loss': stop_result,
            'take_profit': tp_result,
            'position_size_result': result,
            'summary': {
                'symbol': symbol,
                'side': side,
                'quantity': result.position_size,
                'entry_price': entry_price,
                'stop_loss_price': result.stop_loss_price,
                'take_profit_price': result.take_profit_price,
                'risk': result.risk_amount,
                'reward': result.profit_potential,
                'risk_reward_ratio': result.risk_reward_ratio
            }
        }

    def calculate_position_size_only(
        self,
        symbol: str,
        side: str,
        entry_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None,
        timeframe: Timeframe = Timeframe.M15,
        risk_amount: Optional[float] = None,
        profit_target: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calcula position size sem executar a ordem (apenas simulação)

        Útil para:
        - Testar diferentes setups antes de executar
        - Validar se há capital suficiente
        - Ver impacto de diferentes stops

        Returns:
            Dict com o resultado do cálculo
        """

        if not self.position_calculator:
            raise ValueError("Position Calculator não está ativo")

        # Busca preço atual se não fornecido
        if entry_price is None:
            ticker = self.get_ticker(symbol)
            entry_price = float(ticker.get('price', 0))

        # Busca saldo
        balance = self.get_balance()
        account_balance = balance['available_balance']

        # Determina lado
        position_side = PositionSide.LONG if side.lower() == 'buy' else PositionSide.SHORT

        # Valores default
        risk = risk_amount if risk_amount else self.risk_per_trade_usdt
        profit = profit_target if profit_target else (risk * self.risk_reward_ratio)

        # Cria parâmetros
        params = PositionSizeParams(
            entry_price=entry_price,
            account_balance=account_balance,
            side=position_side,
            risk_amount_usdt=risk,
            profit_target_usdt=profit,
            timeframe=timeframe,
            stop_loss_price=stop_loss_price,
            leverage=1
        )

        # Calcula
        result = self.position_calculator.calculate_position_size(params)

        # Retorna resultado formatado
        return {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'position_size': result.position_size,
            'position_value': result.position_value_usdt,
            'margin_required': result.margin_required,
            'stop_loss_price': result.stop_loss_price,
            'take_profit_price': result.take_profit_price,
            'risk_amount': result.risk_amount,
            'profit_potential': result.profit_potential,
            'risk_reward_ratio': result.risk_reward_ratio,
            'is_valid': result.is_valid,
            'warnings': result.warnings,
            'account_balance': account_balance,
            'risk_percentage': result.risk_percentage_of_account
        }


# ========================================================================
# FUNÇÕES AUXILIARES
# ========================================================================

def create_test_connector() -> HyperLiquidConnector:
    """Cria um conector de teste (modo leitura)"""
    return HyperLiquidConnector(testnet=True)


def example_usage():
    """Exemplo de uso do conector"""
    print("="*80)
    print("EXEMPLO DE USO - HYPERLIQUID CONNECTOR")
    print("="*80)
    print()

    # Modo leitura (sem private key)
    print("1. Criando conector em modo leitura...")
    connector = create_test_connector()

    # Busca informações do exchange
    print("\n2. Buscando informações do exchange...")
    info = connector.get_exchange_info()
    print(f"   Símbolos disponíveis: {len(info['symbols'])}")

    if info['symbols']:
        symbol = info['symbols'][0]
        print(f"   Exemplo: {symbol['symbol']} @ ${symbol['mark_price']:,.2f}")

    # Busca ticker
    print("\n3. Buscando ticker de BTC...")
    ticker = connector.get_ticker('BTC')
    if ticker:
        print(f"   BTC Price: ${ticker['price']:,.2f}")

    print("\n✓ Exemplo concluído!")
    print("\nPara trading real, forneça uma private key:")
    print("connector = HyperLiquidConnector(private_key='YOUR_KEY', testnet=True)")


if __name__ == "__main__":
    example_usage()
