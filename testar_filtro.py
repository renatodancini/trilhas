#!/usr/bin/env python3
"""
Script para testar diferentes filtros para identificar trilhas principais
"""

import sqlite3
import pandas as pd
from utils import DB_FILE

def testar_filtros():
    print("🔍 Testando Diferentes Filtros")
    print("="*40)
    
    conn = sqlite3.connect(DB_FILE)
    
    # Teste 1: Trilhas sem atividade
    print("\n📊 Teste 1: Trilhas sem atividade")
    df1 = pd.read_sql_query('''
        SELECT DISTINCT Trilhas, Código 
        FROM gestao_trilhas 
        WHERE Trilhas IS NOT NULL 
        AND Trilhas != "" 
        AND (Atividade IS NULL OR Atividade = "" OR Atividade = "Responsável")
    ''', conn)
    print(f"  - Resultado: {len(df1)} trilhas")
    print("  - Primeiras 3:")
    for i, (_, row) in enumerate(df1.head(3).iterrows(), 1):
        print(f"    {i}. {row['Trilhas']}")
    
    # Teste 2: Trilhas que não contêm BPH
    print("\n📊 Teste 2: Trilhas que não contêm BPH")
    df2 = pd.read_sql_query('''
        SELECT DISTINCT Trilhas, Código 
        FROM gestao_trilhas 
        WHERE Trilhas IS NOT NULL 
        AND Trilhas != "" 
        AND Trilhas NOT LIKE '%BPH%'
    ''', conn)
    print(f"  - Resultado: {len(df2)} trilhas")
    print("  - Primeiras 3:")
    for i, (_, row) in enumerate(df2.head(3).iterrows(), 1):
        print(f"    {i}. {row['Trilhas']}")
    
    # Teste 3: Trilhas que não contêm números seguidos de ponto
    print("\n📊 Teste 3: Trilhas que não contêm números seguidos de ponto")
    df3 = pd.read_sql_query('''
        SELECT DISTINCT Trilhas, Código 
        FROM gestao_trilhas 
        WHERE Trilhas IS NOT NULL 
        AND Trilhas != "" 
        AND Trilhas NOT LIKE '%[0-9]\.%'
    ''', conn)
    print(f"  - Resultado: {len(df3)} trilhas")
    print("  - Primeiras 3:")
    for i, (_, row) in enumerate(df3.head(3).iterrows(), 1):
        print(f"    {i}. {row['Trilhas']}")
    
    # Teste 4: Combinando filtros
    print("\n📊 Teste 4: Combinando filtros")
    df4 = pd.read_sql_query('''
        SELECT DISTINCT Trilhas, Código 
        FROM gestao_trilhas 
        WHERE Trilhas IS NOT NULL 
        AND Trilhas != "" 
        AND Trilhas NOT LIKE '%BPH%'
        AND Trilhas NOT LIKE '%[0-9]\.%'
        AND Trilhas != "Atividade"
        AND Trilhas != "Massa de dados não informada"
        AND Trilhas NOT LIKE '%Responsável%'
        AND Trilhas NOT LIKE '%Tipo%'
        AND Trilhas NOT LIKE '%Finalizado%'
    ''', conn)
    print(f"  - Resultado: {len(df4)} trilhas")
    print("  - Primeiras 5:")
    for i, (_, row) in enumerate(df4.head(5).iterrows(), 1):
        print(f"    {i}. {row['Trilhas']}")
    
    # Teste 5: Usando códigos únicos
    print("\n📊 Teste 5: Usando códigos únicos")
    df5 = pd.read_sql_query('''
        SELECT DISTINCT Código, Trilhas
        FROM gestao_trilhas 
        WHERE Código IS NOT NULL 
        AND Código != "" 
        AND Código != "Atividade"
        AND Código != "nan"
    ''', conn)
    print(f"  - Resultado: {len(df5)} códigos únicos")
    print("  - Primeiras 5:")
    for i, (_, row) in enumerate(df5.head(5).iterrows(), 1):
        print(f"    {i}. Código: {row['Código']}")
        print(f"       Trilha: {row['Trilhas']}")
    
    conn.close()
    
    return df4, df5

if __name__ == "__main__":
    testar_filtros() 