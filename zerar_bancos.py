#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para zerar todos os bancos de dados do projeto
"""

import sqlite3
import os
import pandas as pd

def zerar_login_status_db():
    """Zera o banco de dados login_status.db"""
    print("Zerando login_status.db...")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('login_status.db')
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"Tabelas encontradas em login_status.db: {[t[0] for t in tabelas]}")
        
        # Zerar cada tabela
        for tabela in tabelas:
            nome_tabela = tabela[0]
            cursor.execute(f"DELETE FROM {nome_tabela}")
            print(f"  - Tabela '{nome_tabela}' zerada")
        
        # Resetar os contadores de auto-incremento
        cursor.execute("DELETE FROM sqlite_sequence")
        
        conn.commit()
        conn.close()
        print("✓ login_status.db zerado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao zerar login_status.db: {e}")

def zerar_database_2_db():
    """Zera o banco de dados database_2.db"""
    print("Zerando database_2.db...")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('database_2.db')
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"Tabelas encontradas em database_2.db: {[t[0] for t in tabelas]}")
        
        # Zerar cada tabela
        for tabela in tabelas:
            nome_tabela = tabela[0]
            cursor.execute(f"DELETE FROM {nome_tabela}")
            print(f"  - Tabela '{nome_tabela}' zerada")
        
        # Resetar os contadores de auto-incremento
        cursor.execute("DELETE FROM sqlite_sequence")
        
        conn.commit()
        conn.close()
        print("✓ database_2.db zerado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao zerar database_2.db: {e}")

def zerar_usuarios_csv():
    """Zera o arquivo usuarios.csv"""
    print("Zerando usuarios.csv...")
    
    try:
        # Criar um DataFrame vazio com as colunas corretas
        df_vazio = pd.DataFrame(columns=['nome', 'email', 'senha', 'tipo'])
        df_vazio.to_csv('usuarios.csv', index=False)
        print("✓ usuarios.csv zerado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao zerar usuarios.csv: {e}")

def verificar_arquivos_banco():
    """Verifica quais arquivos de banco existem"""
    print("Verificando arquivos de banco de dados...")
    
    arquivos_banco = []
    
    if os.path.exists('login_status.db'):
        tamanho = os.path.getsize('login_status.db')
        arquivos_banco.append(('login_status.db', tamanho))
        print(f"  - login_status.db encontrado ({tamanho} bytes)")
    
    if os.path.exists('database_2.db'):
        tamanho = os.path.getsize('database_2.db')
        arquivos_banco.append(('database_2.db', tamanho))
        print(f"  - database_2.db encontrado ({tamanho} bytes)")
    
    if os.path.exists('usuarios.csv'):
        tamanho = os.path.getsize('usuarios.csv')
        arquivos_banco.append(('usuarios.csv', tamanho))
        print(f"  - usuarios.csv encontrado ({tamanho} bytes)")
    
    return arquivos_banco

def main():
    """Função principal"""
    print("=" * 50)
    print("ZERANDO TODOS OS BANCOS DE DADOS")
    print("=" * 50)
    
    # Verificar arquivos existentes
    arquivos = verificar_arquivos_banco()
    
    if not arquivos:
        print("Nenhum arquivo de banco de dados encontrado!")
        return
    
    print(f"\nEncontrados {len(arquivos)} arquivo(s) de banco de dados.")
    
    # Confirmar ação
    resposta = input("\nDeseja realmente zerar todos os bancos de dados? (s/N): ").strip().lower()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("Operação cancelada pelo usuário.")
        return
    
    print("\nIniciando processo de limpeza...")
    
    # Zerar cada banco
    zerar_login_status_db()
    print()
    zerar_database_2_db()
    print()
    zerar_usuarios_csv()
    
    print("\n" + "=" * 50)
    print("PROCESSO CONCLUÍDO!")
    print("Todos os bancos de dados foram zerados com sucesso.")
    print("=" * 50)

if __name__ == "__main__":
    main() 