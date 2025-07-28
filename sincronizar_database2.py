#!/usr/bin/env python3
"""
Script para sincronizar o database_2.db com os dados do banco principal
"""

from utils import sincronizar_database2, busca_gestao_trilhas
import sqlite3
import pandas as pd

def main():
    print("🔄 Sincronizando Database 2")
    print("="*40)
    
    # Verificar dados no banco principal
    print("\n📊 Verificando dados no banco principal...")
    df_gestao = busca_gestao_trilhas()
    if df_gestao is not None and not df_gestao.empty:
        trilhas_unicas = df_gestao['Trilhas'].dropna().drop_duplicates()
        print(f"  - Trilhas encontradas: {len(trilhas_unicas)}")
        print(f"  - Primeiras 5 trilhas: {list(trilhas_unicas.head())}")
    else:
        print("  - Nenhum dado encontrado no banco principal")
        return
    
    # Sincronizar database_2.db
    print("\n🔄 Iniciando sincronização...")
    if sincronizar_database2():
        print("\n✅ Sincronização concluída!")
        
        # Verificar resultado
        print("\n📊 Verificando resultado no database_2.db...")
        try:
            conn = sqlite3.connect('database_2.db')
            
            # Verificar tabela controle_trilhas
            df_ctrl = pd.read_sql_query('SELECT COUNT(*) as total FROM controle_trilhas', conn)
            print(f"  - Trilhas na tabela controle_trilhas: {df_ctrl['total'].iloc[0]}")
            
            # Verificar tabela controle_execucao
            df_exec = pd.read_sql_query('SELECT COUNT(*) as total FROM controle_execucao', conn)
            print(f"  - Trilhas na tabela controle_execucao: {df_exec['total'].iloc[0]}")
            
            # Mostrar algumas trilhas
            df_exemplo = pd.read_sql_query('SELECT Trilhas, Status FROM controle_trilhas LIMIT 5', conn)
            print(f"  - Exemplos de trilhas:")
            for _, row in df_exemplo.iterrows():
                print(f"    * {row['Trilhas']} - {row['Status']}")
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ Erro ao verificar resultado: {e}")
    else:
        print("\n❌ Falha na sincronização!")

if __name__ == "__main__":
    main() 