#!/usr/bin/env python3
"""
Script para corrigir trilhas que estão sem códigos
Extrai o código do nome da trilha quando possível
"""

import sqlite3
import pandas as pd
import re
from utils import DB_FILE

def extrair_codigo_da_trilha(nome_trilha):
    """
    Extrai o código da trilha do nome
    Exemplo: "CMR 205.1 - Nome da Trilha" -> "CMR 205.1"
    """
    if pd.isna(nome_trilha) or not nome_trilha:
        return None
    
    # Padrão para encontrar códigos CMR seguidos de números
    padrao = r'^(CMR\s*\d+\.?\d*)'
    match = re.search(padrao, str(nome_trilha), re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return None

def corrigir_codigos_trilhas():
    """
    Identifica e corrige trilhas que estão sem códigos
    """
    print("🔧 Corrigindo códigos das trilhas")
    print("="*50)
    
    conn = sqlite3.connect(DB_FILE)
    
    # Buscar todas as trilhas
    df = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
    
    print(f"📊 Total de trilhas no banco: {len(df)}")
    
    # Identificar trilhas sem códigos (incluindo valores 'nan' como string)
    trilhas_sem_codigo = df[
        df['Código'].isna() | 
        (df['Código'] == '') | 
        (df['Código'] == 'nan') |
        (df['Código'].astype(str).str.lower() == 'nan')
    ]
    print(f"❌ Trilhas sem código: {len(trilhas_sem_codigo)}")
    
    if len(trilhas_sem_codigo) == 0:
        print("✅ Todas as trilhas já têm códigos!")
        conn.close()
        return
    
    # Mostrar exemplos de trilhas sem código
    print("\n📝 Exemplos de trilhas sem código:")
    for i, (_, row) in enumerate(trilhas_sem_codigo.head(10).iterrows(), 1):
        print(f"  {i}. Trilha: '{row['Trilhas']}'")
        print(f"     Código atual: '{row['Código']}'")
        print()
    
    # Tentar extrair códigos das trilhas sem código
    correcoes = []
    for idx, row in trilhas_sem_codigo.iterrows():
        nome_trilha = row['Trilhas']
        codigo_extraido = extrair_codigo_da_trilha(nome_trilha)
        
        if codigo_extraido:
            correcoes.append({
                'id': idx,
                'trilha_original': nome_trilha,
                'codigo_extraido': codigo_extraido
            })
    
    print(f"\n🔍 Códigos extraídos: {len(correcoes)}")
    
    if len(correcoes) > 0:
        print("\n📋 Correções que serão aplicadas:")
        for i, correcao in enumerate(correcoes[:10], 1):
            print(f"  {i}. {correcao['trilha_original']}")
            print(f"     → Código: {correcao['codigo_extraido']}")
            print()
        
        # Aplicar correções
        cursor = conn.cursor()
        for correcao in correcoes:
            cursor.execute(
                'UPDATE gestao_trilhas SET "Código" = ? WHERE rowid = ?',
                (correcao['codigo_extraido'], correcao['id'])
            )
        
        conn.commit()
        print(f"✅ {len(correcoes)} correções aplicadas com sucesso!")
        
        # Verificar resultado
        df_apos = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
        trilhas_sem_codigo_apos = df_apos[
            df_apos['Código'].isna() | 
            (df_apos['Código'] == '') | 
            (df_apos['Código'] == 'nan') |
            (df_apos['Código'].astype(str).str.lower() == 'nan')
        ]
        print(f"📊 Trilhas sem código após correção: {len(trilhas_sem_codigo_apos)}")
        
        if len(trilhas_sem_codigo_apos) > 0:
            print("\n⚠️ Trilhas que ainda estão sem código:")
            for i, (_, row) in enumerate(trilhas_sem_codigo_apos.head(5).iterrows(), 1):
                print(f"  {i}. {row['Trilhas']}")
    else:
        print("❌ Nenhum código pôde ser extraído das trilhas sem código.")
        print("   Verifique se os nomes das trilhas seguem o padrão 'CMR XXX.X'")
    
    conn.close()

def verificar_codigos_unicos():
    """
    Verifica se há códigos duplicados ou inconsistentes
    """
    print("\n🔍 Verificando códigos únicos")
    print("="*30)
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT "Código", COUNT(*) as total FROM gestao_trilhas WHERE "Código" IS NOT NULL AND "Código" != "" AND "Código" != "nan" GROUP BY "Código" HAVING COUNT(*) > 1', conn)
    
    if len(df) > 0:
        print(f"⚠️ Códigos duplicados encontrados: {len(df)}")
        for _, row in df.iterrows():
            print(f"  - {row['Código']}: {row['total']} ocorrências")
    else:
        print("✅ Nenhum código duplicado encontrado!")
    
    conn.close()

def mostrar_estatisticas():
    """
    Mostra estatísticas dos códigos
    """
    print("\n📊 Estatísticas dos códigos")
    print("="*30)
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT "Código" FROM gestao_trilhas', conn)
    
    # Códigos válidos (não nulos, não vazios, não 'nan')
    codigos_validos = df[
        df['Código'].notna() & 
        (df['Código'] != '') & 
        (df['Código'] != 'nan') &
        (df['Código'].astype(str).str.lower() != 'nan')
    ]
    
    print(f"📈 Total de trilhas: {len(df)}")
    print(f"✅ Trilhas com código válido: {len(codigos_validos)}")
    print(f"❌ Trilhas sem código válido: {len(df) - len(codigos_validos)}")
    
    # Códigos únicos
    codigos_unicos = codigos_validos['Código'].drop_duplicates()
    print(f"🔢 Códigos únicos: {len(codigos_unicos)}")
    
    conn.close()

if __name__ == "__main__":
    mostrar_estatisticas()
    corrigir_codigos_trilhas()
    verificar_codigos_unicos() 