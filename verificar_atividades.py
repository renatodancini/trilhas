#!/usr/bin/env python3
"""
Script para verificar as atividades na tabela gestao_trilhas
"""

import sqlite3
import pandas as pd

def verificar_atividades():
    """
    Verifica as atividades na tabela gestao_trilhas
    """
    print("🔍 Verificando atividades na tabela gestao_trilhas")
    print("="*55)
    
    conn = sqlite3.connect('login_status.db')
    
    # Verificar estrutura da tabela
    print("📊 Estrutura da tabela:")
    try:
        df_info = pd.read_sql_query('SELECT * FROM gestao_trilhas LIMIT 1', conn)
        print(f"  - Colunas: {list(df_info.columns)}")
    except Exception as e:
        print(f"  - ❌ Erro ao ler estrutura: {e}")
        return
    
    # Verificar total de registros
    print("\n📊 Estatísticas gerais:")
    try:
        total = pd.read_sql_query('SELECT COUNT(*) as total FROM gestao_trilhas', conn)
        print(f"  - Total de registros: {total.iloc[0]['total']}")
        
        # Verificar registros com atividades válidas
        atividades_validas = pd.read_sql_query(
            'SELECT COUNT(*) as total FROM gestao_trilhas WHERE Atividade IS NOT NULL AND Atividade != "Atividade" AND Atividade != ""',
            conn
        )
        print(f"  - Registros com atividades válidas: {atividades_validas.iloc[0]['total']}")
        
    except Exception as e:
        print(f"  - ❌ Erro ao contar registros: {e}")
    
    # Verificar algumas trilhas específicas
    print("\n📊 Verificando trilhas específicas:")
    try:
        # Buscar trilhas que começam com CMR
        trilhas_cmr = pd.read_sql_query(
            'SELECT DISTINCT Trilhas FROM gestao_trilhas WHERE Trilhas LIKE "CMR%" LIMIT 5',
            conn
        )
        print(f"  - Trilhas com código CMR encontradas: {len(trilhas_cmr)}")
        
        if len(trilhas_cmr) > 0:
            print("  - Exemplos de trilhas CMR:")
            for i, (_, row) in enumerate(trilhas_cmr.iterrows(), 1):
                print(f"    {i}. {row['Trilhas'][:80]}...")
        
        # Verificar atividades de uma trilha específica
        if len(trilhas_cmr) > 0:
            trilha_teste = trilhas_cmr.iloc[0]['Trilhas']
            print(f"\n  - Atividades da trilha: {trilha_teste[:50]}...")
            
            atividades = pd.read_sql_query(
                'SELECT Atividade, Responsável, Tipo, Finalizado, Observações FROM gestao_trilhas WHERE Trilhas = ?',
                conn,
                params=[trilha_teste]
            )
            
            print(f"    - Total de atividades: {len(atividades)}")
            
            if len(atividades) > 0:
                print("    - Primeiras 3 atividades:")
                for i, (_, row) in enumerate(atividades.head(3).iterrows(), 1):
                    atividade = row['Atividade'] if pd.notnull(row['Atividade']) else 'N/A'
                    responsavel = row['Responsável'] if pd.notnull(row['Responsável']) else 'N/A'
                    tipo = row['Tipo'] if pd.notnull(row['Tipo']) else 'N/A'
                    print(f"      {i}. [{tipo}] {atividade[:60]}... | Responsável: {responsavel}")
            else:
                print("    - ⚠️ Nenhuma atividade encontrada")
        
    except Exception as e:
        print(f"  - ❌ Erro ao verificar trilhas: {e}")
    
    # Verificar problemas na tabela
    print("\n🔧 Verificando problemas:")
    try:
        # Verificar registros com Atividade = "Atividade" (cabeçalho)
        cabecalhos = pd.read_sql_query(
            'SELECT COUNT(*) as total FROM gestao_trilhas WHERE Atividade = "Atividade"',
            conn
        )
        print(f"  - Registros com Atividade = 'Atividade': {cabecalhos.iloc[0]['total']}")
        
        # Verificar registros vazios
        vazios = pd.read_sql_query(
            'SELECT COUNT(*) as total FROM gestao_trilhas WHERE Atividade IS NULL OR Atividade = ""',
            conn
        )
        print(f"  - Registros com Atividade vazia: {vazios.iloc[0]['total']}")
        
        # Verificar trilhas sem atividades
        trilhas_sem_atividades = pd.read_sql_query(
            'SELECT COUNT(DISTINCT Trilhas) as total FROM gestao_trilhas WHERE Atividade IS NULL OR Atividade = "" OR Atividade = "Atividade"',
            conn
        )
        print(f"  - Trilhas sem atividades válidas: {trilhas_sem_atividades.iloc[0]['total']}")
        
    except Exception as e:
        print(f"  - ❌ Erro ao verificar problemas: {e}")
    
    conn.close()

if __name__ == "__main__":
    verificar_atividades() 