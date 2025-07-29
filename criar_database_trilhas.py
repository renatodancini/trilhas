#!/usr/bin/env python3
"""
Script para criar o banco de dados database_trilhas com as colunas especificadas
"""

import sqlite3
import os

def criar_database_trilhas():
    """Cria o banco de dados database_trilhas com a estrutura especificada"""
    
    # Caminho correto para o banco de dados
    db_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    print(f"=== Criando banco de dados: {db_path} ===")
    
    # Verificar se o diretório existe, se não, criar
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"📁 Diretório criado: {db_dir}")
    
    # Conectar ao banco de dados (cria se não existir)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Criar tabela trilhas com as colunas especificadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trilhas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Trilhas TEXT,
                Atividades TEXT NOT NULL,
                Responsável TEXT,
                Tipo TEXT,
                Finalizado TEXT,
                Observações TEXT
            )
        ''')
        
        # Criar tabela controle_downloads para rastrear downloads
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS controle_downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Trilhas TEXT NOT NULL,
                Impresso TEXT DEFAULT 'NÃO',
                Impresso_por TEXT,
                Modificado_em DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verificar se a tabela foi criada corretamente
        cursor.execute("PRAGMA table_info(trilhas)")
        colunas = cursor.fetchall()
        
        print("✅ Tabela 'trilhas' criada com sucesso!")
        print("📋 Estrutura da tabela 'trilhas':")
        for coluna in colunas:
            print(f"   - {coluna[1]} ({coluna[2]})")
        
        # Verificar tabela controle_downloads
        cursor.execute("PRAGMA table_info(controle_downloads)")
        colunas_controle = cursor.fetchall()
        
        print("✅ Tabela 'controle_downloads' criada com sucesso!")
        print("📋 Estrutura da tabela 'controle_downloads':")
        for coluna in colunas_controle:
            print(f"   - {coluna[1]} ({coluna[2]})")
        
        # Commit das alterações
        conn.commit()
        print("✅ Banco de dados criado com sucesso!")
        
        # Verificar tamanho do arquivo
        if os.path.exists(db_path):
            tamanho = os.path.getsize(db_path)
            print(f"📁 Tamanho do arquivo: {tamanho} bytes")
            print(f"📁 Caminho completo: {os.path.abspath(db_path)}")
        
    except Exception as e:
        print(f"❌ Erro ao criar banco de dados: {e}")
        conn.rollback()
    
    finally:
        conn.close()
        print("🔒 Conexão com banco de dados fechada.")

def verificar_database_trilhas():
    """Verifica se o banco de dados foi criado corretamente"""
    
    db_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Arquivo {db_path} não encontrado!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(trilhas)")
        colunas = cursor.fetchall()
        
        print(f"\n=== Verificação do banco {db_path} ===")
        print("📋 Estrutura da tabela 'trilhas':")
        for coluna in colunas:
            print(f"   - {coluna[1]} ({coluna[2]})")
        
        # Verificar tabela controle_downloads
        cursor.execute("PRAGMA table_info(controle_downloads)")
        colunas_controle = cursor.fetchall()
        
        print("📋 Estrutura da tabela 'controle_downloads':")
        for coluna in colunas_controle:
            print(f"   - {coluna[1]} ({coluna[2]})")
        
        # Contar registros em ambas as tabelas
        cursor.execute("SELECT COUNT(*) FROM trilhas")
        total_registros_trilhas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM controle_downloads")
        total_registros_controle = cursor.fetchone()[0]
        
        print(f"📊 Total de registros na tabela 'trilhas': {total_registros_trilhas}")
        print(f"📊 Total de registros na tabela 'controle_downloads': {total_registros_controle}")
        
        if total_registros_trilhas == 0:
            print("✅ Tabela 'trilhas' está vazia, conforme solicitado!")
        
        if total_registros_controle == 0:
            print("✅ Tabela 'controle_downloads' está vazia, conforme esperado!")
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco de dados: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    # Criar o banco de dados
    criar_database_trilhas()
    
    # Verificar se foi criado corretamente
    verificar_database_trilhas()
    
    print("\n🎉 Processo concluído!")