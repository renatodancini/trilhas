#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar usuário Renato Dancini como administrador
"""

import pandas as pd
import os

def adicionar_admin():
    """Adiciona o usuário Renato Dancini como administrador"""
    print("Adicionando usuário Renato Dancini como administrador...")
    
    try:
        # Dados do usuário administrador
        admin_data = {
            'nome': ['Renato Dancini'],
            'email': ['renato.dancini@sipal.com.br'],
            'senha': ['admin123'],  # Senha padrão - pode ser alterada depois
            'tipo': ['admin']
        }
        
        # Criar DataFrame com o usuário admin
        df_admin = pd.DataFrame(admin_data)
        
        # Salvar no arquivo usuarios.csv
        df_admin.to_csv('usuarios.csv', index=False)
        
        print("✓ Usuário Renato Dancini adicionado como administrador!")
        print(f"  - Email: renato.dancini@sipal.com.br")
        print(f"  - Senha: admin123")
        print(f"  - Tipo: admin")
        print("\n⚠️  IMPORTANTE: Altere a senha padrão após o primeiro login!")
        
    except Exception as e:
        print(f"Erro ao adicionar administrador: {e}")

def verificar_arquivo():
    """Verifica se o arquivo usuarios.csv existe e mostra seu conteúdo"""
    print("Verificando arquivo usuarios.csv...")
    
    if os.path.exists('usuarios.csv'):
        try:
            df = pd.read_csv('usuarios.csv')
            if df.empty:
                print("  - Arquivo existe mas está vazio")
            else:
                print("  - Conteúdo atual:")
                for index, row in df.iterrows():
                    print(f"    * {row['nome']} ({row['email']}) - {row['tipo']}")
        except Exception as e:
            print(f"  - Erro ao ler arquivo: {e}")
    else:
        print("  - Arquivo não existe")

def main():
    """Função principal"""
    print("=" * 50)
    print("ADICIONAR USUÁRIO ADMINISTRADOR")
    print("=" * 50)
    
    # Verificar arquivo atual
    verificar_arquivo()
    
    # Confirmar ação
    resposta = input("\nDeseja adicionar Renato Dancini como administrador? (s/N): ").strip().lower()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("Operação cancelada pelo usuário.")
        return
    
    # Adicionar administrador
    adicionar_admin()
    
    print("\n" + "=" * 50)
    print("PROCESSO CONCLUÍDO!")
    print("=" * 50)

if __name__ == "__main__":
    main() 