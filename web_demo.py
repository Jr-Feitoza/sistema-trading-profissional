"""
Web Demo - Sistema Trading Profissional
Interface interativa para Position Size Calculator usando Streamlit
"""

import streamlit as st
import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from risk_management.position_size_calculator import (
    PositionSizeCalculator,
    PositionSizeParams,
    PositionSide,
    Timeframe,
    calculate_optimal_leverage
)

# Page config
st.set_page_config(
    page_title="Sistema Trading Profissional",
    page_icon="🚀",
    layout="wide"
)

# Title
st.title("🚀 Sistema Trading Profissional")
st.markdown("### Calculadora de Position Size com Risk Management Avançado")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Configurações")

# Mode selection
mode = st.sidebar.radio(
    "Modo",
    ["🎯 Position Size Calculator", "📊 Leverage Calculator", "📖 Sobre"]
)

if mode == "🎯 Position Size Calculator":
    st.sidebar.markdown("### Parâmetros da Posição")

    # Entry price
    entry_price = st.sidebar.number_input(
        "💵 Preço de Entrada (USDT)",
        value=50000.0,
        step=100.0,
        format="%.2f"
    )

    # Account balance
    account_balance = st.sidebar.number_input(
        "💰 Saldo da Conta (USDT)",
        value=10000.0,
        step=100.0,
        format="%.2f"
    )

    # Side
    side = st.sidebar.selectbox(
        "📈 Lado da Operação",
        ["LONG (Compra)", "SHORT (Venda)"]
    )

    # Risk amount
    risk_amount = st.sidebar.number_input(
        "⚠️ Quanto Arriscar (USDT)",
        value=10.0,
        step=1.0,
        format="%.2f",
        help="Quanto você está disposto a perder neste trade"
    )

    # Profit target
    profit_target = st.sidebar.number_input(
        "🎯 Objetivo de Lucro (USDT)",
        value=30.0,
        step=1.0,
        format="%.2f",
        help="Quanto você quer lucrar neste trade"
    )

    # Timeframe
    timeframe = st.sidebar.selectbox(
        "⏱️ Timeframe",
        ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        index=2  # Default: 15m
    )

    # Stop loss (optional)
    use_custom_stop = st.sidebar.checkbox("Definir Stop Loss Manualmente")

    stop_loss_price = None
    if use_custom_stop:
        stop_loss_price = st.sidebar.number_input(
            "🛡️ Preço do Stop Loss (USDT)",
            value=entry_price * 0.99 if side.startswith("LONG") else entry_price * 1.01,
            step=10.0,
            format="%.2f"
        )

    # Leverage
    use_leverage = st.sidebar.checkbox("Usar Alavancagem")

    max_leverage = 1
    if use_leverage:
        max_leverage = st.sidebar.slider(
            "⚡ Alavancagem Máxima",
            min_value=1,
            max_value=50,
            value=10,
            step=1
        )

    # Calculate button
    st.sidebar.markdown("---")
    calculate_button = st.sidebar.button("🔥 Calcular Position Size", type="primary", use_container_width=True)

    # Main area
    if calculate_button:
        # Map timeframe
        tf_map = {
            "1m": Timeframe.M1,
            "5m": Timeframe.M5,
            "15m": Timeframe.M15,
            "30m": Timeframe.M30,
            "1h": Timeframe.H1,
            "4h": Timeframe.H4,
            "1d": Timeframe.D1
        }

        # Map side
        position_side = PositionSide.LONG if side.startswith("LONG") else PositionSide.SHORT

        # Create calculator
        calculator = PositionSizeCalculator(max_risk_per_trade_pct=10.0)

        # Create params
        params = PositionSizeParams(
            entry_price=entry_price,
            account_balance=account_balance,
            side=position_side,
            risk_amount_usdt=risk_amount,
            profit_target_usdt=profit_target,
            timeframe=tf_map[timeframe],
            stop_loss_price=stop_loss_price,
            leverage=max_leverage if use_leverage else 1
        )

        # Calculate
        with st.spinner("Calculando..."):
            result = calculator.calculate_position_size(params)

        # Display results
        if result.is_valid:
            st.success("✅ Posição Calculada com Sucesso!")
        else:
            st.error("❌ Posição Inválida - Verifique os Avisos Abaixo")

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="📦 Position Size",
                value=f"{result.position_size:.6f}",
                help="Quantidade de ativos a comprar/vender"
            )

        with col2:
            st.metric(
                label="💵 Valor da Posição",
                value=f"${result.position_value_usdt:,.2f}",
                help="Valor total da posição em USDT"
            )

        with col3:
            st.metric(
                label="💳 Margem Necessária",
                value=f"${result.margin_required:,.2f}",
                help="Margem necessária para abrir a posição"
            )

        with col4:
            rr_display = f"1:{result.risk_reward_ratio:.2f}"
            st.metric(
                label="⚖️ Risk/Reward",
                value=rr_display,
                help="Ratio entre risco e recompensa"
            )

        st.markdown("---")

        # Detailed info
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📉 Stop Loss")
            st.markdown(f"**Preço:** ${result.stop_loss_price:,.2f}")
            st.markdown(f"**Distância:** {result.stop_loss_distance_pct:.2f}%")
            st.markdown(f"**Risco:** ${result.risk_amount:.2f}")
            st.markdown(f"**Risco % da Conta:** {result.risk_percentage_of_account:.2f}%")

        with col2:
            st.markdown("### 📈 Take Profit")
            st.markdown(f"**Preço:** ${result.take_profit_price:,.2f}")
            st.markdown(f"**Distância:** {result.take_profit_distance_pct:.2f}%")
            st.markdown(f"**Lucro Potencial:** ${result.profit_potential:.2f}")

        # Leverage info
        if use_leverage and result.liquidation_price:
            st.markdown("---")
            st.markdown("### ⚡ Informações de Leverage")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Leverage Utilizada:** {max_leverage}x")

            with col2:
                st.markdown(f"**Preço de Liquidação:** ${result.liquidation_price:,.2f}")

            with col3:
                if position_side == PositionSide.LONG:
                    margin_to_liq = ((result.stop_loss_price - result.liquidation_price) / result.liquidation_price) * 100
                else:
                    margin_to_liq = ((result.liquidation_price - result.stop_loss_price) / result.liquidation_price) * 100

                st.markdown(f"**Margem até Liquidação:** {margin_to_liq:.2f}%")

        # Warnings
        if result.warnings:
            st.markdown("---")
            st.warning("⚠️ **Avisos:**")
            for warning in result.warnings:
                st.markdown(f"- {warning}")

        # Chart (price levels)
        st.markdown("---")
        st.markdown("### 📊 Níveis de Preço")

        prices = {
            "Take Profit": result.take_profit_price,
            "Entry": entry_price,
            "Stop Loss": result.stop_loss_price
        }

        if use_leverage and result.liquidation_price:
            prices["Liquidação"] = result.liquidation_price

        # Create a simple chart
        import pandas as pd

        df_chart = pd.DataFrame([
            {"Nível": k, "Preço": v} for k, v in prices.items()
        ])

        st.bar_chart(df_chart.set_index("Nível"))

    else:
        # Welcome message
        st.info("👈 Configure os parâmetros na barra lateral e clique em **Calcular Position Size**")

        st.markdown("### 📚 Sobre o Position Size Calculator")
        st.markdown("""
        Este calculador ajuda você a determinar o **tamanho ideal da posição** baseado em:

        - ✅ **Risk/Reward Ratio**: Defina quanto arriscar para quanto lucrar
        - ✅ **Timeframe**: Ajusta stops baseado na volatilidade do timeframe
        - ✅ **ATR**: Usa volatilidade real do mercado
        - ✅ **Leverage**: Calcula margem e preço de liquidação
        - ✅ **Validações**: Verifica se a posição é segura

        #### Como usar:
        1. Defina o preço de entrada e saldo da conta
        2. Escolha quanto quer arriscar e quanto quer lucrar
        3. Selecione o timeframe e lado (long/short)
        4. Opcionalmente, defina stop loss manual e leverage
        5. Clique em "Calcular Position Size"

        O sistema calculará automaticamente:
        - Quantidade exata a comprar/vender
        - Stop loss ideal (se não definido)
        - Take profit baseado no risk/reward
        - Preço de liquidação (se usar leverage)
        - Todas as validações de segurança
        """)

elif mode == "📊 Leverage Calculator":
    st.markdown("### 📊 Calculadora de Leverage Ótima")

    st.markdown("""
    Esta ferramenta calcula a **leverage ideal** baseada na distância do seu stop loss.

    **Objetivo:** Garantir que se o stop loss for atingido, você perca exatamente a % de risco planejada.
    """)

    col1, col2 = st.columns(2)

    with col1:
        entry = st.number_input("Preço de Entrada", value=50000.0, step=100.0)
        stop = st.number_input("Preço do Stop Loss", value=49500.0, step=100.0)

    with col2:
        max_loss_pct = st.number_input("Perda Máxima Permitida (%)", value=2.0, step=0.1, format="%.1f")

    if st.button("Calcular Leverage Ótima"):
        leverage = calculate_optimal_leverage(entry, stop, max_loss_pct)

        stop_dist_pct = abs(entry - stop) / entry * 100

        st.success(f"### ⚡ Leverage Ótima: **{leverage}x**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Distância do Stop", f"{stop_dist_pct:.2f}%")

        with col2:
            st.metric("Perda Máxima", f"{max_loss_pct:.2f}%")

        with col3:
            st.metric("Leverage", f"{leverage}x")

        st.markdown("---")
        st.info(f"""
        **Explicação:**

        Com leverage de **{leverage}x**, se o preço se mover {stop_dist_pct:.2f}% até o stop loss,
        você perderá exatamente **{max_loss_pct:.2f}%** do seu capital.

        Fórmula: `Leverage = Perda Máxima / Distância do Stop`

        `{leverage} = {max_loss_pct:.2f}% / {stop_dist_pct:.2f}%`
        """)

else:  # Sobre
    st.markdown("### 📖 Sobre o Sistema")

    st.markdown("""
    ## 🚀 Sistema Trading Profissional

    Sistema completo de trading automatizado com:

    ### 🤖 Componentes Principais

    1. **AI Agents**: Sistema multi-agente para automação de desenvolvimento
    2. **Estratégias**: SMC (Smart Money Concepts) e Wyckoff
    3. **Position Sizing**: Cálculo automático baseado em risk/reward
    4. **Backtest**: Sistema avançado com breakeven e trailing stops
    5. **HyperLiquid**: Integração completa com DEX de futuros

    ### 📚 Documentação

    - [Cálculo de Alavancagem](docs/LEVERAGE_CALCULATION_GUIDE.md)
    - [Sistema HyperLiquid](docs/HYPERLIQUID_LEVERAGE_SYSTEM.md)
    - [Como Testar Online](docs/COMO_TESTAR_ONLINE.md)

    ### 🔧 Tecnologias

    - Python 3.11+
    - Pandas, Numpy
    - Streamlit (esta interface)
    - eth-account (HyperLiquid)

    ### ⚠️ Disclaimer

    Este sistema é para fins educacionais. Trading envolve riscos significativos.
    Use por sua própria conta e risco.

    ---

    Made with ❤️ and Python
    """)

# Footer
st.markdown("---")
st.markdown("© 2024 Sistema Trading Profissional | [GitHub](https://github.com/Jr-Feitoza/sistema-trading-profissional)")
