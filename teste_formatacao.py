#!/usr/bin/env python3
"""
Script de teste para verificar a formatação das atividades no Excel
"""

import pandas as pd
import sqlite3
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import DB_FILE, gerar_xlsx_trilha

def testar_formatacao_atividades():
    """Testa a formatação das atividades"""
    
    print("=== Teste de Formatação de Atividades ===")
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(DB_FILE)
    
    try:
        # Verificar se a tabela gestao_trilhas existe
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gestao_trilhas'")
        if not c.fetchone():
            print("❌ Tabela gestao_trilhas não encontrada!")
            return
        
        # Verificar estrutura da tabela
        c.execute("PRAGMA table_info(gestao_trilhas)")
        colunas = [col[1] for col in c.fetchall()]
        print(f"📋 Colunas da tabela: {colunas}")
        
        # Buscar algumas trilhas para teste
        df_trilhas = pd.read_sql_query("SELECT DISTINCT Trilhas FROM gestao_trilhas LIMIT 5", conn)
        
        if df_trilhas.empty:
            print("❌ Nenhuma trilha encontrada na tabela!")
            return
        
        print(f"📊 Trilhas encontradas: {len(df_trilhas)}")
        
        # Testar cada trilha
        for idx, row in df_trilhas.iterrows():
            trilha = row['Trilhas']
            print(f"\n🔍 Testando trilha: {trilha}")
            
            # Buscar atividades da trilha
            df_atividades = pd.read_sql_query(
                "SELECT Atividade, Responsável, Tipo, Finalizado, Observações FROM gestao_trilhas WHERE Trilhas = ? LIMIT 3",
                conn,
                params=[trilha]
            )
            
            if df_atividades.empty:
                print(f"   ⚠️  Nenhuma atividade encontrada para {trilha}")
                continue
            
            print(f"   📝 Atividades encontradas: {len(df_atividades)}")
            
            # Mostrar algumas atividades antes da formatação
            for i, atividade_row in df_atividades.iterrows():
                atividade = atividade_row['Atividade']
                print(f"   📋 Atividade {i+1}: {atividade}")
        
        # Testar geração de Excel
        print(f"\n🧪 Testando geração de Excel...")
        try:
            # Pegar a primeira trilha para teste
            trilha_teste = df_trilhas.iloc[0]['Trilhas']
            
            # Extrair código da trilha (se existir)
            import re
            padrao_cmr = r'CMR\s*\d+\.?\d*'
            match_cmr = re.search(padrao_cmr, trilha_teste, re.IGNORECASE)
            codigo_trilha = match_cmr.group(0) if match_cmr else ''
            
            print(f"   🎯 Trilha de teste: {trilha_teste}")
            print(f"   🏷️  Código extraído: {codigo_trilha}")
            
            # Gerar Excel
            xlsx_bytes = gerar_xlsx_trilha(trilha_teste, codigo_trilha)
            print(f"   ✅ Excel gerado com sucesso! Tamanho: {len(xlsx_bytes)} bytes")
            
            # Salvar arquivo de teste
            with open('teste_formatacao.xlsx', 'wb') as f:
                f.write(xlsx_bytes)
            print(f"   💾 Arquivo salvo como 'teste_formatacao.xlsx'")
            
        except Exception as e:
            print(f"   ❌ Erro ao gerar Excel: {e}")
    
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    testar_formatacao_atividades()