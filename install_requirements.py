#!/usr/bin/env python3
"""
Script para instalar dependências do projeto Impressão de Trilhas
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"\n{'='*50}")
    print(f"Executando: {description}")
    print(f"Comando: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print("✅ Sucesso!")
        if result.stdout:
            print("Saída:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Erro!")
        print("Erro:", e.stderr)
        return False

def main():
    print("🚀 Instalador de Dependências - Impressão de Trilhas")
    print("="*60)
    
    # Verificar se Python está instalado
    print(f"Python versão: {sys.version}")
    
    # Verificar se pip está disponível
    if not run_command("pip --version", "Verificando pip"):
        print("❌ pip não encontrado. Instale o Python primeiro.")
        return False
    
    # Criar ambiente virtual se não existir
    if not os.path.exists("venv"):
        print("\n📦 Criando ambiente virtual...")
        if not run_command("python -m venv venv", "Criando ambiente virtual"):
            print("❌ Falha ao criar ambiente virtual")
            return False
    
    # Ativar ambiente virtual
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:  # Linux/Mac
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    # Instalar dependências
    print("\n📚 Instalando dependências...")
    
    dependencies = [
        "streamlit>=1.47.0",
        "pandas>=2.3.1", 
        "openpyxl>=3.1.5",
        "numpy>=2.3.1",
        "altair>=5.5.0",
        "pydeck>=0.9.1"
    ]
    
    success_count = 0
    for dep in dependencies:
        if run_command(f"{pip_path} install {dep}", f"Instalando {dep}"):
            success_count += 1
    
    print(f"\n📊 Resumo: {success_count}/{len(dependencies)} dependências instaladas com sucesso")
    
    if success_count == len(dependencies):
        print("\n✅ Todas as dependências foram instaladas com sucesso!")
        print("\n🎯 Para executar o sistema:")
        print("   Windows: execute 'run_local.bat'")
        print("   Linux/Mac: execute 'python run_local.py'")
        return True
    else:
        print("\n⚠️  Algumas dependências falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 