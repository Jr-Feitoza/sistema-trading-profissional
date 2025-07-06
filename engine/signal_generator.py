import pandas as pd

class SignalGenerator:
    def __init__(self, strategy):
        self.strategy = strategy

    def generate_realtime_signal(self, latest_data: pd.DataFrame) -> int:
        # A estratégia deve ser capaz de gerar um sinal para o último ponto de dados
        # Assumimos que latest_data contém dados suficientes para a estratégia calcular
        # seus indicadores e gerar um sinal para a última linha.
        df_with_signal = self.strategy.generate_signals(latest_data.copy())
        return df_with_signal["signal"].iloc[-1]


