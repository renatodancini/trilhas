#!/usr/bin/env python3
"""
Script para analisar e identificar as regras para distinguir trilhas de atividades
"""

import sqlite3
import pandas as pd
from utils import DB_FILE

def analisar_trilhas():
    print("🔍 Analisando Regras para Identificar Trilhas")
    print("="*50)
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
    
    # Analisar padrões na coluna Trilhas
    print("\n📊 Análise de padrões na coluna 'Trilhas':")
    
    # Verificar linhas que contêm "BPH" (atividades)
    trilhas_com_bph = df[df['Trilhas'].str.contains('BPH', na=False)]
    print(f"  - Linhas com 'BPH': {len(trilhas_com_bph)}")
    
    # Verificar linhas que contêm "CMR" (trilhas principais)
    trilhas_com_cmr = df[df['Trilhas'].str.contains('CMR', na=False)]
    print(f"  - Linhas com 'CMR': {len(trilhas_com_cmr)}")
    
    # Verificar linhas que contêm números (atividades)
    trilhas_com_numeros = df[df['Trilhas'].str.contains(r'\d+\.', na=False)]
    print(f"  - Linhas com números seguidos de ponto: {len(trilhas_com_numeros)}")
    
    # Verificar linhas que são títulos principais (não têm atividade preenchida)
    trilhas_sem_atividade = df[df['Atividade'].isna() | (df['Atividade'] == '')]
    print(f"  - Linhas sem atividade: {len(trilhas_sem_atividade)}")
    
    # Verificar linhas que têm atividade preenchida
    trilhas_com_atividade = df[df['Atividade'].notna() & (df['Atividade'] != '')]
    print(f"  - Linhas com atividade: {len(trilhas_com_atividade)}")
    
    # Mostrar exemplos de cada tipo
    print("\n📝 Exemplos de trilhas principais (sem atividade):")
    for i, (_, row) in enumerate(trilhas_sem_atividade.head(5).iterrows(), 1):
        print(f"  {i}. {row['Trilhas']}")
    
    print("\n📝 Exemplos de atividades (com atividade preenchida):")
    for i, (_, row) in enumerate(trilhas_com_atividade.head(5).iterrows(), 1):
        print(f"  {i}. {row['Trilhas']} -> {row['Atividade']}")
    
    # Verificar se há padrão na coluna Código
    print("\n🔢 Análise da coluna 'Código':")
    codigos_unicos = df['Código'].dropna().drop_duplicates()
    print(f"  - Códigos únicos: {len(codigos_unicos)}")
    
    # Verificar se os códigos correspondem às trilhas principais
    trilhas_principais_por_codigo = df.groupby('Código')['Trilhas'].first()
    print(f"  - Trilhas principais por código: {len(trilhas_principais_por_codigo)}")
    
    print("\n📋 Primeiras 5 trilhas principais por código:")
    for i, (codigo, trilha) in enumerate(trilhas_principais_por_codigo.head().items(), 1):
        print(f"  {i}. Código: {codigo}")
        print(f"     Trilha: {trilha}")
        print()
    
    conn.close()
    
    return trilhas_principais_por_codigo

if __name__ == "__main__":
    analisar_trilhas() 