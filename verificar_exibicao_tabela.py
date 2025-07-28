#!/usr/bin/env python3
"""
Script para verificar e corrigir a exibição da tabela controle_trilhas
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

def verificar_exibicao_tabela():
    """
    Verifica e corrige a exibição da tabela controle_trilhas
    """
    print("🔍 Verificando exibição da tabela controle_trilhas")
    print("="*55)
    
    # Conectar aos bancos
    conn2 = sqlite3.connect('database_2.db')
    conn_gestao = sqlite3.connect('login_status.db')
    
    # Verificar estrutura da tabela controle_trilhas
    print("📊 Verificando estrutura da tabela controle_trilhas:")
    try:
        df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
        print(f"  - Total de registros: {len(df_controle)}")
        print(f"  - Colunas: {list(df_controle.columns)}")
        
        if len(df_controle) > 0:
            print("  - Primeiras 3 trilhas:")
            for i, (_, row) in enumerate(df_controle.head(3).iterrows(), 1):
                print(f"    {i}. {row['Trilhas'][:80]}...")
        else:
            print("  - ⚠️ Tabela está vazia!")
            
    except Exception as e:
        print(f"  - ❌ Erro ao ler tabela: {e}")
    
    # Verificar dados da gestão
    print("\n📊 Verificando dados da gestão:")
    try:
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        print(f"  - Total de trilhas na gestão: {len(df_gestao)}")
        print(f"  - Trilhas com código: {len(df_gestao[df_gestao['Código'].notna()])}")
    except Exception as e:
        print(f"  - ❌ Erro ao ler gestão: {e}")
    
    # Simular a lógica da página de impressão
    print("\n🔗 Simulando lógica da página de impressão:")
    
    try:
        # Buscar trilhas do controle
        df_trilhas_controle = pd.read_sql_query('SELECT Trilhas FROM controle_trilhas', conn2)
        print(f"  - Trilhas do controle: {len(df_trilhas_controle)}")
        
        # Buscar códigos da gestão
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        print(f"  - Trilhas da gestão: {len(df_gestao)}")
        
        # Limpar duplicatas
        df_trilhas_controle = df_trilhas_controle.drop_duplicates(subset=['Trilhas'])
        df_gestao = df_gestao.drop_duplicates(subset=['Trilhas'])
        
        # Mesclar
        df_trilhas_completas = pd.merge(df_trilhas_controle, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
        print(f"  - Após mesclagem: {len(df_trilhas_completas)}")
        
        # Remover duplicatas da mesclagem
        df_trilhas_completas = df_trilhas_completas.drop_duplicates(subset=['Trilhas'])
        print(f"  - Após remoção de duplicatas: {len(df_trilhas_completas)}")
        
        # Verificar combobox
        opcoes_combo = []
        for _, row in df_trilhas_completas.iterrows():
            codigo = row['Código'] if pd.notnull(row['Código']) and row['Código'] and row['Código'] != 'nan' else ''
            trilha = row['Trilhas']
            
            # Se não tem código, tentar extrair do nome da trilha
            if not codigo:
                codigo = extrair_codigo_da_trilha(trilha)
            
            # Criar opção
            if codigo:
                opcao = f"{codigo} - {trilha}"
            else:
                opcao = trilha
            
            opcoes_combo.append(opcao)
        
        # Remover duplicatas das opções
        opcoes_combo = list(dict.fromkeys(opcoes_combo))
        print(f"  - Opções no combobox: {len(opcoes_combo)}")
        
        # Verificar tabela de exibição
        try:
            df_ctrl = pd.read_sql_query('SELECT Trilhas, Status, "Modificado por", "Modificado em" FROM controle_trilhas', conn2)
            print(f"  - Dados da tabela controle: {len(df_ctrl)}")
            
            # Mesclar para obter os códigos
            df_final = pd.merge(df_ctrl, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
            print(f"  - Dados finais para exibição: {len(df_final)}")
            
            # Contar trilhas com código
            trilhas_com_codigo = 0
            for _, row in df_final.iterrows():
                codigo = row['Código'] if pd.notnull(row['Código']) and row['Código'] and row['Código'] != 'nan' else ''
                if not codigo:
                    codigo = extrair_codigo_da_trilha(row['Trilhas'])
                if codigo:
                    trilhas_com_codigo += 1
            
            print(f"  - Trilhas com código na tabela: {trilhas_com_codigo}")
            print(f"  - Trilhas sem código na tabela: {len(df_final) - trilhas_com_codigo}")
            
        except Exception as e:
            print(f"  - ❌ Erro ao processar tabela de exibição: {e}")
        
    except Exception as e:
        print(f"  - ❌ Erro na simulação: {e}")
    
    # Verificar se há problemas específicos
    print("\n🔧 Verificando problemas específicos:")
    
    try:
        # Verificar se há trilhas com nomes muito longos
        df_controle = pd.read_sql_query('SELECT Trilhas FROM controle_trilhas', conn2)
        trilhas_longas = df_controle[df_controle['Trilhas'].str.len() > 200]
        print(f"  - Trilhas com nomes muito longos (>200 chars): {len(trilhas_longas)}")
        
        # Verificar se há trilhas com duplicações no nome
        trilhas_duplicadas = df_controle[df_controle.duplicated(subset=['Trilhas'], keep=False)]
        print(f"  - Trilhas com nomes duplicados: {len(trilhas_duplicadas)}")
        
        # Verificar se há trilhas sem código
        trilhas_sem_codigo = []
        for _, row in df_controle.iterrows():
            codigo = extrair_codigo_da_trilha(row['Trilhas'])
            if not codigo:
                trilhas_sem_codigo.append(row['Trilhas'])
        
        print(f"  - Trilhas sem código: {len(trilhas_sem_codigo)}")
        
        if trilhas_sem_codigo:
            print("  - Exemplos de trilhas sem código:")
            for i, trilha in enumerate(trilhas_sem_codigo[:3], 1):
                print(f"    {i}. {trilha[:80]}...")
        
    except Exception as e:
        print(f"  - ❌ Erro na verificação: {e}")
    
    conn2.close()
    conn_gestao.close()

if __name__ == "__main__":
    verificar_exibicao_tabela() 