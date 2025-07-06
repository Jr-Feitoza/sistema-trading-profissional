#!/usr/bin/env python3
"""
Sistema Profissional de Trading
Desenvolvido para traders de varejo
Focado em testes de estratégias e emissão de sinais
"""

import sys
import os
import subprocess

def main():
    """Função principal para executar o sistema"""
    print("🚀 Sistema Profissional de Trading")
    print("=" * 50)
    print("1. Interface Web (Streamlit)")
    print("2. Modo Headless (Linha de comando)")
    print("3. Instalar dependências")
    print("4. Sair")
    print("=" * 50)
    
    choice = input("Escolha uma opção (1-4): ").strip()
    
    if choice == "1":
        print("Iniciando interface web...")
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "visualization/ui.py", 
                "--server.port=8501",
                "--server.address=0.0.0.0"
            ])
        except KeyboardInterrupt:
            print("\nInterface web encerrada.")
    
    elif choice == "2":
        print("Executando modo headless...")
        try:
            from visualization.ui_headless import executar_backtest_com_perfil
            from utils.profile_manager import listar_perfis
            
            perfis = listar_perfis()
            if not perfis:
                print("Nenhum perfil encontrado. Use a interface web para criar perfis.")
                return
            
            print("Perfis disponíveis:")
            for i, perfil in enumerate(perfis, 1):
                print(f"{i}. {perfil}")
            
            try:
                escolha = int(input("Escolha um perfil: ")) - 1
                if 0 <= escolha < len(perfis):
                    executar_backtest_com_perfil(perfis[escolha])
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Por favor, digite um número válido.")
        
        except ImportError as e:
            print(f"Erro ao importar módulos: {e}")
            print("Certifique-se de que todas as dependências estão instaladas.")
    
    elif choice == "3":
        print("Instalando dependências...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Dependências instaladas com sucesso!")
        except Exception as e:
            print(f"Erro ao instalar dependências: {e}")
    
    elif choice == "4":
        print("Saindo...")
        sys.exit(0)
    
    else:
        print("Opção inválida. Tente novamente.")
        main()

if __name__ == "__main__":
    main()

