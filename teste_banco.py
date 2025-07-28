#!/usr/bin/env python3
"""
Script para testar o banco de dados do sistema
"""

import sqlite3
import pandas as pd
import json
from utils import DB_FILE, busca_impressao_upload, busca_gestao_trilhas

def testar_banco():
    print("🔍 Testando Banco de Dados")
    print("="*40)
    
    # Conectar ao banco
    try:
        conn = sqlite3.connect(DB_FILE)
        print("✅ Conexão com banco estabelecida")
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return
    
    # Listar tabelas
    c = conn.cursor()
    tabelas = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\n📋 Tabelas encontradas: {len(tabelas)}")
    for tabela in tabelas:
        print(f"  - {tabela[0]}")
    
    # Verificar tabela impressao_upload
    print("\n📊 Verificando tabela 'impressao_upload':")
    try:
        c.execute("SELECT COUNT(*) FROM impressao_upload")
        count = c.fetchone()[0]
        print(f"  - Registros: {count}")
        
        if count > 0:
            c.execute("SELECT colunas, dados FROM impressao_upload ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
            if row:
                colunas = json.loads(row[0])
                dados = json.loads(row[1])
                print(f"  - Colunas: {colunas}")
                print(f"  - Linhas de dados: {len(dados)}")
                if dados:
                    print(f"  - Primeira linha: {dados[0]}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    # Verificar tabela gestao_trilhas
    print("\n📊 Verificando tabela 'gestao_trilhas':")
    try:
        c.execute("SELECT COUNT(*) FROM gestao_trilhas")
        count = c.fetchone()[0]
        print(f"  - Registros: {count}")
        
        if count > 0:
            c.execute("SELECT * FROM gestao_trilhas LIMIT 3")
            rows = c.fetchall()
            print(f"  - Primeiras 3 linhas:")
            for i, row in enumerate(rows, 1):
                print(f"    {i}: {row}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    # Testar funções do utils
    print("\n🔧 Testando funções do utils:")
    
    # Testar busca_impressao_upload
    try:
        df_upload = busca_impressao_upload()
        if df_upload is not None:
            print(f"  ✅ busca_impressao_upload: {len(df_upload)} linhas")
        else:
            print("  ⚠️  busca_impressao_upload: Nenhum dado encontrado")
    except Exception as e:
        print(f"  ❌ busca_impressao_upload: {e}")
    
    # Testar busca_gestao_trilhas
    try:
        df_gestao = busca_gestao_trilhas()
        if df_gestao is not None:
            print(f"  ✅ busca_gestao_trilhas: {len(df_gestao)} linhas")
        else:
            print("  ⚠️  busca_gestao_trilhas: Nenhum dado encontrado")
    except Exception as e:
        print(f"  ❌ busca_gestao_trilhas: {e}")
    
    conn.close()
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    testar_banco() 