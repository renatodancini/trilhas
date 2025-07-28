#!/usr/bin/env python3
"""
Script para executar o sistema Impressão de Trilhas localmente
"""

import subprocess
import sys
import os

def check_venv():
    """Verifica se o ambiente virtual existe"""
    if not os.path.exists("venv"):
        print("❌ Ambiente virtual não encontrado!")
        print("Execute primeiro: python install_requirements.py")
        return False
    return True

def run_streamlit():
    """Executa o aplicativo Streamlit"""
    print("🚀 Iniciando Sistema de Impressão de Trilhas...")
    print("="*50)
    
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python.exe"
    else:  # Linux/Mac
        python_path = "venv/bin/python"
    
    # Verificar se o arquivo app.py existe
    if not os.path.exists("app.py"):
        print("❌ Arquivo app.py não encontrado!")
        return False
    
    # Executar Streamlit
    try:
        print("🌐 Abrindo navegador...")
        print("📱 O sistema estará disponível em: http://localhost:8501")
        print("⏹️  Para parar o servidor, pressione Ctrl+C")
        print("-" * 50)
        
        # Executar streamlit run app.py
        subprocess.run([python_path, "-m", "streamlit", "run", "app.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado pelo usuário")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar Streamlit: {e}")
        return False
    except FileNotFoundError:
        print("❌ Python não encontrado no ambiente virtual")
        print("Execute: python install_requirements.py")
        return False

def main():
    print("🎯 Executor Local - Impressão de Trilhas")
    print("="*40)
    
    # Verificar ambiente virtual
    if not check_venv():
        return False
    
    # Executar aplicação
    return run_streamlit()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 