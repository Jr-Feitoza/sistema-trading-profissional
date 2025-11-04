"""
Position Size Calculator
Calcula automaticamente o tamanho da posição baseado em risk/reward, timeframe e leverage
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, Dict
from enum import Enum


class Timeframe(Enum):
    """Timeframes suportados"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class PositionSide(Enum):
    """Lado da posição"""
    LONG = "long"
    SHORT = "short"


@dataclass
class PositionSizeParams:
    """
    Parâmetros para cálculo de tamanho de posição

    Campos principais:
    - entry_price: Preço de entrada
    - stop_loss_price: Preço do stop loss
    - account_balance: Saldo da conta em USDT
    - risk_amount_usdt: Quanto arriscar em USDT (ex: 10)
    - profit_target_usdt: Quanto lucrar em USDT (ex: 30)
    - timeframe: Timeframe da análise
    - leverage: Alavancagem a usar
    """
    entry_price: float
    account_balance: float
    side: PositionSide

    # Risk management
    risk_amount_usdt: Optional[float] = None  # Ex: 10 USDT
    risk_percentage: Optional[float] = None   # Ex: 2% do saldo
    profit_target_usdt: Optional[float] = None  # Ex: 30 USDT
    risk_reward_ratio: Optional[float] = None   # Ex: 1:3 = 3.0

    # Stop loss / Take profit
    stop_loss_price: Optional[float] = None
    stop_loss_pct: Optional[float] = None  # Ex: 2% do entry
    take_profit_price: Optional[float] = None
    take_profit_pct: Optional[float] = None

    # Market conditions
    timeframe: Timeframe = Timeframe.M15
    current_atr: Optional[float] = None  # ATR para volatilidade
    leverage: int = 1

    # Exchange limits
    min_position_size: float = 0.001
    max_position_size: Optional[float] = None
    price_tick_size: float = 0.01
    quantity_step_size: float = 0.001

    # Fees
    maker_fee: float = 0.0002  # 0.02%
    taker_fee: float = 0.0005  # 0.05%
    estimated_slippage: float = 0.001  # 0.1%


@dataclass
class PositionSizeResult:
    """Resultado do cálculo de position size"""

    # Position details
    position_size: float  # Quantidade a comprar/vender
    position_value_usdt: float  # Valor total da posição
    margin_required: float  # Margem necessária com leverage

    # Risk/Reward
    risk_amount: float  # Quanto está arriscando
    profit_potential: float  # Quanto pode lucrar
    risk_reward_ratio: float  # Ratio risk:reward

    # Prices
    entry_price: float
    stop_loss_price: float
    take_profit_price: float

    # Risk metrics
    risk_percentage_of_account: float  # % do saldo em risco
    stop_loss_distance_pct: float  # Distância do SL em %
    take_profit_distance_pct: float  # Distância do TP em %

    # Optional fields (with defaults)
    liquidation_price: Optional[float] = None
    warnings: list = None
    is_valid: bool = True

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class PositionSizeCalculator:
    """
    Calculadora de Tamanho de Posição

    Funcionalidades:
    1. Calcula position size baseado em risk fixo (USDT) ou % do saldo
    2. Ajusta para timeframe específico (volatilidade)
    3. Considera leverage e margin requirements
    4. Valida limites de exchange e risco
    5. Calcula stop loss e take profit ótimos
    """

    # Multiplicadores de volatilidade por timeframe
    TIMEFRAME_VOLATILITY_MULTIPLIERS = {
        Timeframe.M1: 0.5,   # Muito volátil, stops apertados
        Timeframe.M5: 0.7,   # Volátil, stops moderados
        Timeframe.M15: 1.0,  # Baseline
        Timeframe.M30: 1.2,  # Menos volátil, stops mais largos
        Timeframe.H1: 1.5,
        Timeframe.H4: 2.0,
        Timeframe.D1: 3.0,   # Muito menos volátil, stops largos
    }

    # ATR multipliers para stop loss por timeframe
    ATR_STOP_MULTIPLIERS = {
        Timeframe.M1: 1.0,
        Timeframe.M5: 1.5,
        Timeframe.M15: 2.0,
        Timeframe.M30: 2.5,
        Timeframe.H1: 3.0,
        Timeframe.H4: 4.0,
        Timeframe.D1: 5.0,
    }

    def __init__(self, max_risk_per_trade_pct: float = 2.0):
        """
        Args:
            max_risk_per_trade_pct: Risco máximo por trade (% do saldo)
        """
        self.max_risk_per_trade_pct = max_risk_per_trade_pct

    def calculate_position_size(
        self,
        params: PositionSizeParams
    ) -> PositionSizeResult:
        """
        Calcula o tamanho ideal da posição

        Returns:
            PositionSizeResult com todos os detalhes
        """
        # 1. Determina stop loss price se não fornecido
        stop_loss_price = self._calculate_stop_loss(params)

        # 2. Determina quanto arriscar (USDT ou %)
        risk_amount = self._calculate_risk_amount(params)

        # 3. Calcula position size baseado no risco
        position_size = self._calculate_size_from_risk(
            entry_price=params.entry_price,
            stop_loss_price=stop_loss_price,
            risk_amount=risk_amount,
            side=params.side
        )

        # 4. Ajusta para limites da exchange
        position_size = self._apply_exchange_limits(position_size, params)

        # 5. Calcula take profit
        take_profit_price = self._calculate_take_profit(
            params=params,
            stop_loss_price=stop_loss_price,
            position_size=position_size
        )

        # 6. Calcula métricas finais
        result = self._build_result(
            params=params,
            position_size=position_size,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            risk_amount=risk_amount
        )

        # 7. Valida e adiciona warnings
        self._validate_result(result, params)

        return result

    def _calculate_stop_loss(self, params: PositionSizeParams) -> float:
        """Calcula o preço do stop loss"""

        # Se já fornecido, usa
        if params.stop_loss_price:
            return params.stop_loss_price

        # Se fornecido como percentual
        if params.stop_loss_pct:
            if params.side == PositionSide.LONG:
                return params.entry_price * (1 - params.stop_loss_pct)
            else:
                return params.entry_price * (1 + params.stop_loss_pct)

        # Calcula baseado em ATR se disponível
        if params.current_atr:
            atr_multiplier = self.ATR_STOP_MULTIPLIERS[params.timeframe]
            stop_distance = params.current_atr * atr_multiplier

            if params.side == PositionSide.LONG:
                return params.entry_price - stop_distance
            else:
                return params.entry_price + stop_distance

        # Default: usa multiplicador de timeframe
        volatility_mult = self.TIMEFRAME_VOLATILITY_MULTIPLIERS[params.timeframe]

        # Base stop: 1% para M15, ajustado por timeframe
        base_stop_pct = 0.01 * volatility_mult

        if params.side == PositionSide.LONG:
            return params.entry_price * (1 - base_stop_pct)
        else:
            return params.entry_price * (1 + base_stop_pct)

    def _calculate_risk_amount(self, params: PositionSizeParams) -> float:
        """Determina quanto arriscar em USDT"""

        # Prioridade 1: Risk amount fixo
        if params.risk_amount_usdt:
            risk = params.risk_amount_usdt

        # Prioridade 2: Risk percentage
        elif params.risk_percentage:
            risk = params.account_balance * (params.risk_percentage / 100)

        # Default: usa max_risk_per_trade_pct
        else:
            risk = params.account_balance * (self.max_risk_per_trade_pct / 100)

        # Valida limite máximo
        max_risk = params.account_balance * (self.max_risk_per_trade_pct / 100)
        if risk > max_risk:
            risk = max_risk

        return risk

    def _calculate_size_from_risk(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_amount: float,
        side: PositionSide
    ) -> float:
        """
        Calcula position size baseado no risco

        Fórmula:
        Position Size = Risk Amount / Stop Loss Distance

        Exemplo:
        - Entry: 50000
        - Stop: 49000
        - Risk: 10 USDT
        - Distance: 1000 (2%)
        - Position Size = 10 / 1000 = 0.01 BTC = 500 USDT @ entry
        """

        # Calcula distância do stop em preço
        if side == PositionSide.LONG:
            stop_distance = entry_price - stop_loss_price
        else:
            stop_distance = stop_loss_price - entry_price

        if stop_distance <= 0:
            raise ValueError(f"Invalid stop loss: distance = {stop_distance}")

        # Position size = Risk / Distance por unidade
        position_size = risk_amount / stop_distance

        return position_size

    def _apply_exchange_limits(
        self,
        position_size: float,
        params: PositionSizeParams
    ) -> float:
        """Aplica limites de mínimo/máximo e arredondamento"""

        # Arredonda para step size
        position_size = self._round_to_step(position_size, params.quantity_step_size)

        # Aplica mínimo
        if position_size < params.min_position_size:
            position_size = params.min_position_size

        # Aplica máximo se definido
        if params.max_position_size and position_size > params.max_position_size:
            position_size = params.max_position_size

        return position_size

    def _calculate_take_profit(
        self,
        params: PositionSizeParams,
        stop_loss_price: float,
        position_size: float
    ) -> float:
        """Calcula o preço do take profit"""

        # Se já fornecido, usa
        if params.take_profit_price:
            return params.take_profit_price

        # Se fornecido como percentual
        if params.take_profit_pct:
            if params.side == PositionSide.LONG:
                return params.entry_price * (1 + params.take_profit_pct)
            else:
                return params.entry_price * (1 - params.take_profit_pct)

        # Calcula baseado em profit target USDT
        if params.profit_target_usdt:
            # Profit per unit = profit_target / position_size
            profit_per_unit = params.profit_target_usdt / position_size

            if params.side == PositionSide.LONG:
                return params.entry_price + profit_per_unit
            else:
                return params.entry_price - profit_per_unit

        # Calcula baseado em risk/reward ratio
        risk_reward = params.risk_reward_ratio if params.risk_reward_ratio else 3.0

        stop_distance = abs(params.entry_price - stop_loss_price)
        tp_distance = stop_distance * risk_reward

        if params.side == PositionSide.LONG:
            return params.entry_price + tp_distance
        else:
            return params.entry_price - tp_distance

    def _build_result(
        self,
        params: PositionSizeParams,
        position_size: float,
        stop_loss_price: float,
        take_profit_price: float,
        risk_amount: float
    ) -> PositionSizeResult:
        """Constrói o resultado final"""

        # Valor da posição
        position_value = position_size * params.entry_price

        # Margem necessária
        margin_required = position_value / params.leverage

        # Profit potencial
        if params.side == PositionSide.LONG:
            profit_potential = (take_profit_price - params.entry_price) * position_size
        else:
            profit_potential = (params.entry_price - take_profit_price) * position_size

        # Risk/Reward ratio
        risk_reward_ratio = profit_potential / risk_amount if risk_amount > 0 else 0

        # Distâncias percentuais
        stop_distance_pct = abs(params.entry_price - stop_loss_price) / params.entry_price * 100
        tp_distance_pct = abs(take_profit_price - params.entry_price) / params.entry_price * 100

        # Risk % of account
        risk_pct = (risk_amount / params.account_balance) * 100

        # Liquidation price (aproximado)
        liquidation_price = self._estimate_liquidation_price(
            params.entry_price,
            params.side,
            params.leverage,
            margin_required,
            position_value
        )

        return PositionSizeResult(
            position_size=position_size,
            position_value_usdt=position_value,
            margin_required=margin_required,
            risk_amount=risk_amount,
            profit_potential=profit_potential,
            risk_reward_ratio=risk_reward_ratio,
            entry_price=params.entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            liquidation_price=liquidation_price,
            risk_percentage_of_account=risk_pct,
            stop_loss_distance_pct=stop_distance_pct,
            take_profit_distance_pct=tp_distance_pct,
            warnings=[]
        )

    def _estimate_liquidation_price(
        self,
        entry_price: float,
        side: PositionSide,
        leverage: int,
        margin: float,
        position_value: float
    ) -> float:
        """Estima o preço de liquidação"""

        if leverage == 1:
            return 0.0  # Sem leverage, sem liquidação

        # Liquidation acontece quando perda = margin
        # Para long: liquidation = entry * (1 - 1/leverage)
        # Para short: liquidation = entry * (1 + 1/leverage)

        maintenance_margin_rate = 0.005  # 0.5% típico

        if side == PositionSide.LONG:
            liq_price = entry_price * (1 - (1 / leverage) + maintenance_margin_rate)
        else:
            liq_price = entry_price * (1 + (1 / leverage) - maintenance_margin_rate)

        return liq_price

    def _validate_result(self, result: PositionSizeResult, params: PositionSizeParams):
        """Valida o resultado e adiciona warnings"""

        # Check 1: Risk muito alto
        if result.risk_percentage_of_account > self.max_risk_per_trade_pct:
            result.warnings.append(
                f"⚠️ Risk muito alto: {result.risk_percentage_of_account:.2f}% "
                f"(máximo: {self.max_risk_per_trade_pct}%)"
            )
            result.is_valid = False

        # Check 2: Margin insuficiente
        if result.margin_required > params.account_balance:
            result.warnings.append(
                f"⚠️ Margin insuficiente: precisa {result.margin_required:.2f} USDT, "
                f"tem {params.account_balance:.2f} USDT"
            )
            result.is_valid = False

        # Check 3: Stop loss muito próximo de liquidação
        if result.liquidation_price and params.leverage > 1:
            if params.side == PositionSide.LONG:
                distance_to_liq = ((params.stop_loss_price - result.liquidation_price)
                                 / result.liquidation_price * 100)
            else:
                distance_to_liq = ((result.liquidation_price - params.stop_loss_price)
                                 / result.liquidation_price * 100)

            if distance_to_liq < 10:  # Menos de 10% de margem
                result.warnings.append(
                    f"⚠️ Stop loss muito próximo da liquidação: {distance_to_liq:.2f}% de margem"
                )

        # Check 4: Risk/Reward muito baixo
        if result.risk_reward_ratio < 1.5:
            result.warnings.append(
                f"⚠️ Risk/Reward baixo: {result.risk_reward_ratio:.2f} "
                f"(recomendado: >= 2.0)"
            )

        # Check 5: Position size muito pequena
        if result.position_size < params.min_position_size:
            result.warnings.append(
                f"⚠️ Position size muito pequena: {result.position_size} "
                f"(mínimo: {params.min_position_size})"
            )
            result.is_valid = False

    def _round_to_step(self, value: float, step: float) -> float:
        """Arredonda valor para o step size mais próximo"""
        return round(value / step) * step

    def calculate_atr_based_stops(
        self,
        df: pd.DataFrame,
        timeframe: Timeframe,
        atr_period: int = 14
    ) -> pd.DataFrame:
        """
        Calcula stops baseados em ATR

        Args:
            df: DataFrame com colunas high, low, close
            timeframe: Timeframe para ajuste do multiplicador
            atr_period: Período do ATR

        Returns:
            DataFrame com colunas: atr, stop_long, stop_short
        """
        df = df.copy()

        # Calcula ATR
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift(1))
        low_close = abs(df['low'] - df['close'].shift(1))

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=atr_period).mean()

        df['atr'] = atr

        # Multiplier baseado em timeframe
        multiplier = self.ATR_STOP_MULTIPLIERS[timeframe]

        # Stops
        df['stop_long'] = df['close'] - (atr * multiplier)
        df['stop_short'] = df['close'] + (atr * multiplier)

        return df


def calculate_optimal_leverage(
    entry_price: float,
    stop_loss_price: float,
    max_loss_pct: float = 2.0
) -> int:
    """
    Calcula a alavancagem ótima baseada no stop loss

    Args:
        entry_price: Preço de entrada
        stop_loss_price: Preço do stop
        max_loss_pct: Perda máxima permitida em % do saldo

    Returns:
        Leverage recomendado (inteiro)

    Example:
        entry = 50000, stop = 49000 (2% de distância)
        max_loss = 2% do saldo
        leverage = 2% / 2% = 1x (sem leverage necessária)

        entry = 50000, stop = 49500 (1% de distância)
        max_loss = 2% do saldo
        leverage = 2% / 1% = 2x
    """
    stop_distance_pct = abs(entry_price - stop_loss_price) / entry_price * 100

    if stop_distance_pct >= max_loss_pct:
        return 1  # Sem leverage necessária

    # Leverage = max_loss / stop_distance
    leverage = max_loss_pct / stop_distance_pct

    # Arredonda para inteiro
    leverage = int(round(leverage))

    # Limita a 20x (típico de exchanges)
    leverage = min(leverage, 20)

    return leverage


def print_position_summary(result: PositionSizeResult):
    """Imprime um resumo formatado da posição"""

    print("\n" + "="*70)
    print("📊 RESUMO DA POSIÇÃO")
    print("="*70)

    print(f"\n💰 TAMANHO DA POSIÇÃO:")
    print(f"   Quantidade: {result.position_size:.6f}")
    print(f"   Valor Total: ${result.position_value_usdt:,.2f}")
    print(f"   Margem Necessária: ${result.margin_required:,.2f}")

    print(f"\n📈 PREÇOS:")
    print(f"   Entry: ${result.entry_price:,.2f}")
    print(f"   Stop Loss: ${result.stop_loss_price:,.2f} ({result.stop_loss_distance_pct:.2f}%)")
    print(f"   Take Profit: ${result.take_profit_price:,.2f} ({result.take_profit_distance_pct:.2f}%)")

    if result.liquidation_price:
        print(f"   Liquidação: ${result.liquidation_price:,.2f}")

    print(f"\n⚖️ RISK/REWARD:")
    print(f"   Risco: ${result.risk_amount:.2f} ({result.risk_percentage_of_account:.2f}% da conta)")
    print(f"   Potencial: ${result.profit_potential:.2f}")
    print(f"   Ratio: 1:{result.risk_reward_ratio:.2f}")

    if result.warnings:
        print(f"\n⚠️ AVISOS:")
        for warning in result.warnings:
            print(f"   {warning}")

    print(f"\n✅ Status: {'VÁLIDO' if result.is_valid else '❌ INVÁLIDO'}")
    print("="*70 + "\n")
