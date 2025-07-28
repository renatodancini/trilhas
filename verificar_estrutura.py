#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela gestao_trilhas
"""

import sqlite3
import pandas as pd
from utils import DB_FILE

def verificar_estrutura():
    print("🔍 Verificando Estrutura da Tabela gestao_trilhas")
    print("="*50)
    
    conn = sqlite3.connect(DB_FILE)
    
    # Verificar estrutura da tabela
    print("\n🏗️  Estrutura da tabela:")
    c = conn.cursor()
    c.execute("PRAGMA table_info(gestao_trilhas)")
    columns = c.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Buscar dados
    df = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
    print(f"\n📊 Total de registros: {len(df)}")
    
    # Verificar colunas
    print(f"\n📋 Colunas: {list(df.columns)}")
    
    # Analisar dados únicos na coluna Trilhas
    print("\n🔍 Análise da coluna 'Trilhas':")
    trilhas_unicas = df['Trilhas'].dropna().drop_duplicates()
    print(f"  - Trilhas únicas: {len(trilhas_unicas)}")
    
    # Mostrar primeiras 10 trilhas únicas
    print("\n📝 Primeiras 10 trilhas únicas:")
    for i, trilha in enumerate(trilhas_unicas.head(10), 1):
        print(f"  {i}. {trilha}")
    
    # Verificar se há códigos
    if 'Código' in df.columns:
        print("\n🔢 Análise da coluna 'Código':")
        codigos_unicos = df['Código'].dropna().drop_duplicates()
        print(f"  - Códigos únicos: {len(codigos_unicos)}")
        print(f"  - Primeiros códigos: {list(codigos_unicos.head())}")
    
    # Verificar se há atividades
    if 'Atividade' in df.columns:
        print("\n📋 Análise da coluna 'Atividade':")
        atividades_unicas = df['Atividade'].dropna().drop_duplicates()
        print(f"  - Atividades únicas: {len(atividades_unicas)}")
        print(f"  - Primeiras atividades: {list(atividades_unicas.head())}")
    
    # Verificar padrão de dados
    print("\n🔍 Padrão de dados:")
    for i in range(min(5, len(df))):
        print(f"  Linha {i+1}:")
        for col in df.columns:
            valor = df.iloc[i][col]
            if pd.notnull(valor) and str(valor).strip():
                print(f"    {col}: {valor}")
        print()
    
    conn.close()

if __name__ == "__main__":
    verificar_estrutura() 