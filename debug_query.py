#!/usr/bin/env python3
"""
Script para debugar a query de sincronização
"""

import sqlite3
import pandas as pd
from utils import DB_FILE

def debug_query():
    print("🔍 Debugando Query de Sincronização")
    print("="*40)
    
    conn = sqlite3.connect(DB_FILE)
    
    # Verificar dados brutos
    print("\n📊 Dados brutos da tabela gestao_trilhas:")
    df_bruto = pd.read_sql_query('SELECT COUNT(*) as total FROM gestao_trilhas', conn)
    print(f"  - Total de registros: {df_bruto['total'].iloc[0]}")
    
    # Verificar valores únicos na coluna Atividade
    print("\n📋 Valores únicos na coluna Atividade:")
    df_atividade = pd.read_sql_query('''
        SELECT DISTINCT Atividade, COUNT(*) as count
        FROM gestao_trilhas 
        GROUP BY Atividade 
        ORDER BY count DESC
        LIMIT 10
    ''', conn)
    for _, row in df_atividade.iterrows():
        print(f"  - '{row['Atividade']}': {row['count']}")
    
    # Testar a query passo a passo
    print("\n🔍 Testando query passo a passo:")
    
    # Passo 1: Trilhas não nulas
    df1 = pd.read_sql_query('''
        SELECT COUNT(*) as total
        FROM gestao_trilhas 
        WHERE Trilhas IS NOT NULL AND Trilhas != ""
    ''', conn)
    print(f"  - Trilhas não nulas: {df1['total'].iloc[0]}")
    
    # Passo 2: Trilhas sem atividade
    df2 = pd.read_sql_query('''
        SELECT COUNT(*) as total
        FROM gestao_trilhas 
        WHERE Trilhas IS NOT NULL 
        AND Trilhas != "" 
        AND (Atividade IS NULL OR Atividade = "" OR Atividade = "Responsável")
    ''', conn)
    print(f"  - Trilhas sem atividade: {df2['total'].iloc[0]}")
    
    # Passo 3: Trilhas sem atividade e excluindo "Atividade"
    df3 = pd.read_sql_query('''
        SELECT COUNT(*) as total
        FROM gestao_trilhas 
        WHERE Trilhas IS NOT NULL 
        AND Trilhas != "" 
        AND (Atividade IS NULL OR Atividade = "" OR Atividade = "Responsável")
        AND Trilhas != "Atividade"
    ''', conn)
    print(f"  - Trilhas sem atividade (excluindo 'Atividade'): {df3['total'].iloc[0]}")
    
    # Passo 4: Query final
    df4 = pd.read_sql_query('''
        SELECT DISTINCT Trilhas, Código 
        FROM gestao_trilhas 
        WHERE Trilhas IS NOT NULL 
        AND Trilhas != "" 
        AND (Atividade IS NULL OR Atividade = "" OR Atividade = "Responsável")
        AND Trilhas != "Atividade"
        AND Trilhas != "Massa de dados não informada"
    ''', conn)
    print(f"  - Query final: {len(df4)} trilhas")
    
    if len(df4) > 0:
        print("  - Primeiras 3 trilhas:")
        for i, (_, row) in enumerate(df4.head(3).iterrows(), 1):
            print(f"    {i}. {row['Trilhas']}")
    else:
        print("  - Nenhuma trilha encontrada!")
        
        # Verificar se há problemas com os valores
        print("\n🔍 Verificando valores problemáticos:")
        df_problema = pd.read_sql_query('''
            SELECT Trilhas, Atividade, Código
            FROM gestao_trilhas 
            WHERE Trilhas IS NOT NULL 
            AND Trilhas != "" 
            AND (Atividade IS NULL OR Atividade = "" OR Atividade = "Responsável")
            AND Trilhas != "Atividade"
            LIMIT 5
        ''', conn)
        print("  - Primeiras 5 linhas que passaram no filtro inicial:")
        for i, (_, row) in df_problema.iterrows():
            print(f"    {i+1}. Trilha: '{row['Trilhas']}'")
            print(f"       Atividade: '{row['Atividade']}'")
            print(f"       Código: '{row['Código']}'")
            print()
    
    conn.close()

if __name__ == "__main__":
    debug_query() 