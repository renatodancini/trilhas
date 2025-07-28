#!/usr/bin/env python3
"""
Script para corrigir a exibição das trilhas na página de impressão
Remove duplicações e garante que os códigos sejam exibidos corretamente
"""

import sqlite3
import pandas as pd
import re

def extrair_codigo_da_trilha(nome_trilha):
    """
    Extrai o código da trilha do nome
    """
    if pd.isna(nome_trilha) or not nome_trilha:
        return None
    
    # Padrão para encontrar códigos CMR seguidos de números
    padrao = r'^(CMR\s*\d+\.?\d*)'
    match = re.search(padrao, str(nome_trilha), re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return None

def corrigir_exibicao_trilhas():
    """
    Corrige a exibição das trilhas na página de impressão
    """
    print("🔧 Corrigindo exibição das trilhas")
    print("="*45)
    
    # Buscar trilhas do controle
    conn2 = sqlite3.connect('database_2.db')
    try:
        df_trilhas_controle = pd.read_sql_query('SELECT Trilhas FROM controle_trilhas', conn2)
        print(f"📊 Trilhas no controle: {len(df_trilhas_controle)}")
    except Exception as e:
        print(f"❌ Erro ao ler controle_trilhas: {e}")
        df_trilhas_controle = pd.DataFrame(columns=['Trilhas'])
    conn2.close()
    
    # Buscar códigos das trilhas
    conn_gestao = sqlite3.connect('login_status.db')
    try:
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        print(f"📊 Trilhas na gestão: {len(df_gestao)}")
    except Exception as e:
        print(f"❌ Erro ao ler gestao_trilhas: {e}")
        df_gestao = pd.DataFrame(columns=['Trilhas', 'Código'])
    conn_gestao.close()
    
    # Limpar duplicatas
    df_trilhas_controle = df_trilhas_controle.drop_duplicates(subset=['Trilhas'])
    df_gestao = df_gestao.drop_duplicates(subset=['Trilhas'])
    
    print(f"📊 Trilhas no controle (sem duplicatas): {len(df_trilhas_controle)}")
    print(f"📊 Trilhas na gestão (sem duplicatas): {len(df_gestao)}")
    
    # Mesclar para obter os códigos
    df_trilhas_completas = pd.merge(df_trilhas_controle, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
    
    print(f"📊 Trilhas após mesclagem: {len(df_trilhas_completas)}")
    
    # Identificar trilhas sem código
    trilhas_sem_codigo = df_trilhas_completas[
        df_trilhas_completas['Código'].isna() | 
        (df_trilhas_completas['Código'] == '') | 
        (df_trilhas_completas['Código'] == 'nan')
    ]
    
    print(f"❌ Trilhas sem código: {len(trilhas_sem_codigo)}")
    
    # Tentar extrair códigos das trilhas sem código
    correcoes = []
    for idx, row in trilhas_sem_codigo.iterrows():
        nome_trilha = row['Trilhas']
        codigo_extraido = extrair_codigo_da_trilha(nome_trilha)
        
        if codigo_extraido:
            correcoes.append({
                'trilha': nome_trilha,
                'codigo': codigo_extraido
            })
    
    print(f"🔍 Códigos extraídos: {len(correcoes)}")
    
    # Aplicar correções no banco de gestão
    if correcoes:
        conn_gestao = sqlite3.connect('login_status.db')
        cursor = conn_gestao.cursor()
        
        for correcao in correcoes:
            cursor.execute(
                'UPDATE gestao_trilhas SET "Código" = ? WHERE "Trilhas" = ?',
                (correcao['codigo'], correcao['trilha'])
            )
        
        conn_gestao.commit()
        conn_gestao.close()
        print(f"✅ {len(correcoes)} correções aplicadas no banco!")
    
    # Recarregar dados após correções
    conn_gestao = sqlite3.connect('login_status.db')
    df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
    conn_gestao.close()
    
    df_gestao = df_gestao.drop_duplicates(subset=['Trilhas'])
    df_trilhas_completas = pd.merge(df_trilhas_controle, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
    
    # Criar opções do combobox
    opcoes_combo = []
    for _, row in df_trilhas_completas.iterrows():
        codigo = row['Código'] if pd.notnull(row['Código']) and row['Código'] else ''
        trilha = row['Trilhas']
        
        # Se não tem código, tentar extrair
        if not codigo:
            codigo_extraido = extrair_codigo_da_trilha(trilha)
            if codigo_extraido:
                codigo = codigo_extraido
        
        opcao = f"{codigo} - {trilha}" if codigo else trilha
        opcoes_combo.append(opcao)
    
    print(f"📊 Total de opções no combobox: {len(opcoes_combo)}")
    
    # Verificar resultado
    opcoes_com_codigo = [op for op in opcoes_combo if op.startswith(('CMR', 'cmr'))]
    opcoes_sem_codigo = [op for op in opcoes_combo if not op.startswith(('CMR', 'cmr'))]
    
    print(f"✅ Opções com código: {len(opcoes_com_codigo)}")
    print(f"❌ Opções sem código: {len(opcoes_sem_codigo)}")
    
    # Mostrar exemplos
    print("\n📝 Exemplos de opções com código:")
    for i, opcao in enumerate(opcoes_com_codigo[:5], 1):
        print(f"  {i}. {opcao}")
    
    if opcoes_sem_codigo:
        print("\n⚠️ Exemplos de opções sem código:")
        for i, opcao in enumerate(opcoes_sem_codigo[:3], 1):
            print(f"  {i}. {opcao}")

def limpar_duplicatas_controle():
    """
    Remove duplicatas da tabela controle_trilhas
    """
    print("\n🧹 Limpando duplicatas da tabela controle_trilhas")
    print("="*50)
    
    conn2 = sqlite3.connect('database_2.db')
    
    # Verificar duplicatas
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    print(f"📊 Total de registros: {len(df_controle)}")
    
    # Identificar duplicatas
    duplicatas = df_controle[df_controle.duplicated(subset=['Trilhas'], keep=False)]
    print(f"📊 Registros duplicados: {len(duplicatas)}")
    
    if len(duplicatas) > 0:
        print("📝 Exemplos de duplicatas:")
        for i, (_, row) in enumerate(duplicatas.head(5).iterrows(), 1):
            print(f"  {i}. {row['Trilhas']}")
        
        # Remover duplicatas mantendo apenas o primeiro
        df_controle_limpo = df_controle.drop_duplicates(subset=['Trilhas'], keep='first')
        
        # Salvar de volta
        df_controle_limpo.to_sql('controle_trilhas', conn2, if_exists='replace', index=False)
        
        print(f"✅ Duplicatas removidas! Registros restantes: {len(df_controle_limpo)}")
    
    conn2.close()

if __name__ == "__main__":
    limpar_duplicatas_controle()
    corrigir_exibicao_trilhas() 