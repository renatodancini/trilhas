#!/usr/bin/env python3
"""
Script para limpar trilhas inválidas do banco de dados
Remove trilhas com valores None, vazios ou inválidos
"""

import sqlite3
import pandas as pd
from utils import DB_FILE

def limpar_trilhas_invalidas():
    """
    Remove trilhas inválidas do banco de dados
    """
    print("🧹 Limpando trilhas inválidas")
    print("="*40)
    
    conn = sqlite3.connect(DB_FILE)
    
    # Buscar todas as trilhas
    df = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
    
    print(f"📊 Total de trilhas no banco: {len(df)}")
    
    # Identificar trilhas inválidas
    trilhas_invalidas = df[
        df['Trilhas'].isna() | 
        (df['Trilhas'] == '') | 
        (df['Trilhas'] == 'None') |
        (df['Trilhas'].astype(str).str.lower() == 'none')
    ]
    
    print(f"❌ Trilhas inválidas encontradas: {len(trilhas_invalidas)}")
    
    if len(trilhas_invalidas) == 0:
        print("✅ Nenhuma trilha inválida encontrada!")
        conn.close()
        return
    
    # Mostrar exemplos de trilhas inválidas
    print("\n📝 Exemplos de trilhas inválidas:")
    for i, (_, row) in enumerate(trilhas_invalidas.head(10).iterrows(), 1):
        print(f"  {i}. Trilha: '{row['Trilhas']}'")
        print(f"     Código: '{row['Código']}'")
        print(f"     Atividade: '{row['Atividade']}'")
        print()
    
    # Confirmar remoção
    print(f"⚠️ Deseja remover {len(trilhas_invalidas)} trilhas inválidas?")
    print("   Isso irá limpar o banco de dados de registros corrompidos.")
    
    # Remover trilhas inválidas
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gestao_trilhas WHERE "Trilhas" IS NULL OR "Trilhas" = "" OR "Trilhas" = "None"')
    
    registros_removidos = cursor.rowcount
    conn.commit()
    
    print(f"✅ {registros_removidos} trilhas inválidas removidas!")
    
    # Verificar resultado
    df_apos = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
    print(f"📊 Total de trilhas após limpeza: {len(df_apos)}")
    
    # Verificar trilhas sem código válido
    trilhas_sem_codigo = df_apos[
        df_apos['Código'].isna() | 
        (df_apos['Código'] == '') | 
        (df_apos['Código'] == 'nan') |
        (df_apos['Código'].astype(str).str.lower() == 'nan')
    ]
    
    print(f"📊 Trilhas sem código válido: {len(trilhas_sem_codigo)}")
    
    if len(trilhas_sem_codigo) > 0:
        print("\n📝 Exemplos de trilhas sem código válido:")
        for i, (_, row) in enumerate(trilhas_sem_codigo.head(5).iterrows(), 1):
            print(f"  {i}. {row['Trilhas']}")
    
    conn.close()

def mostrar_estatisticas_finais():
    """
    Mostra estatísticas finais após a limpeza
    """
    print("\n📊 Estatísticas finais")
    print("="*25)
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
    
    # Códigos válidos
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
    
    # Trilhas principais (sem atividade)
    trilhas_principais = df[df['Atividade'].isna() | (df['Atividade'] == '')]
    print(f"📋 Trilhas principais: {len(trilhas_principais)}")
    
    # Atividades
    atividades = df[df['Atividade'].notna() & (df['Atividade'] != '')]
    print(f"🔧 Atividades: {len(atividades)}")
    
    conn.close()

if __name__ == "__main__":
    limpar_trilhas_invalidas()
    mostrar_estatisticas_finais() 