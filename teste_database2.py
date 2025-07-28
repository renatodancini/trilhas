#!/usr/bin/env python3
"""
Script para testar o database_2.db
"""

import sqlite3
import pandas as pd

def testar_database2():
    print("🔍 Testando Database 2")
    print("="*40)
    
    # Conectar ao database_2.db
    try:
        conn = sqlite3.connect('database_2.db')
        print("✅ Conexão com database_2.db estabelecida")
    except Exception as e:
        print(f"❌ Erro ao conectar ao database_2.db: {e}")
        return
    
    # Listar tabelas
    c = conn.cursor()
    tabelas = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\n📋 Tabelas encontradas: {len(tabelas)}")
    for tabela in tabelas:
        print(f"  - {tabela[0]}")
    
    # Verificar tabela controle_trilhas
    print("\n📊 Verificando tabela 'controle_trilhas':")
    try:
        c.execute("SELECT COUNT(*) FROM controle_trilhas")
        count = c.fetchone()[0]
        print(f"  - Registros: {count}")
        
        if count > 0:
            c.execute("SELECT * FROM controle_trilhas LIMIT 3")
            rows = c.fetchall()
            print(f"  - Primeiras 3 linhas:")
            for i, row in enumerate(rows, 1):
                print(f"    {i}: {row}")
        else:
            print("  - Nenhum registro encontrado!")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    # Verificar estrutura da tabela
    print("\n🏗️  Estrutura da tabela 'controle_trilhas':")
    try:
        c.execute("PRAGMA table_info(controle_trilhas)")
        columns = c.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    conn.close()
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    testar_database2() 