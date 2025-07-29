#!/usr/bin/env python3
"""
Script para migrar o banco de dados database_trilhas.db
e adicionar a coluna Trilhas se ela não existir
"""

import sqlite3
import os
import pandas as pd

def migrar_banco_trilhas():
    """Migra o banco de dados para incluir a coluna Trilhas"""
    
    db_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    print(f"🔄 Migrando banco de dados: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura atual da tabela
        cursor.execute("PRAGMA table_info(trilhas)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        
        print(f"📊 Colunas existentes: {colunas_existentes}")
        
        # Se a coluna Trilhas não existe, adicionar
        if 'Trilhas' not in colunas_existentes:
            print("➕ Adicionando coluna 'Trilhas'...")
            
            # Adicionar a coluna Trilhas
            cursor.execute("ALTER TABLE trilhas ADD COLUMN Trilhas TEXT")
            
            # Verificar se a migração foi bem-sucedida
            cursor.execute("PRAGMA table_info(trilhas)")
            colunas_apos_migracao = [col[1] for col in cursor.fetchall()]
            
            if 'Trilhas' in colunas_apos_migracao:
                print("✅ Coluna 'Trilhas' adicionada com sucesso!")
                
                # Contar registros existentes
                cursor.execute("SELECT COUNT(*) FROM trilhas")
                total_registros = cursor.fetchone()[0]
                print(f"📊 Total de registros: {total_registros}")
                
                # Atualizar registros existentes com valor padrão para Trilhas
                if total_registros > 0:
                    cursor.execute("UPDATE trilhas SET Trilhas = 'Trilha Padrão' WHERE Trilhas IS NULL")
                    print("🔄 Registros existentes atualizados com valor padrão para Trilhas")
                
                conn.commit()
                print("✅ Migração concluída com sucesso!")
                return True
            else:
                print("❌ Erro: Coluna 'Trilhas' não foi adicionada!")
                return False
        else:
            print("✅ Coluna 'Trilhas' já existe no banco!")
            return True
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
        print("🔒 Conexão com banco de dados fechada.")

def verificar_estrutura_banco():
    """Verifica a estrutura atual do banco de dados"""
    
    db_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(trilhas)")
        colunas = cursor.fetchall()
        
        print(f"\n📊 Estrutura da tabela 'trilhas':")
        print("-" * 50)
        for col in colunas:
            print(f"  • {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM trilhas")
        total_registros = cursor.fetchone()[0]
        print(f"\n📊 Total de registros: {total_registros}")
        
        # Mostrar alguns registros de exemplo
        if total_registros > 0:
            cursor.execute("SELECT * FROM trilhas LIMIT 3")
            registros = cursor.fetchall()
            print(f"\n📋 Exemplo de registros:")
            print("-" * 50)
            for i, registro in enumerate(registros, 1):
                print(f"  Registro {i}: {registro}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

def recriar_banco_com_trilhas():
    """Recria o banco de dados com a estrutura correta incluindo Trilhas"""
    
    db_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    print(f"🔄 Recriando banco de dados: {db_path}")
    
    try:
        # Fazer backup dos dados existentes se houver
        dados_existentes = None
        if os.path.exists(db_path):
            conn_backup = sqlite3.connect(db_path)
            try:
                dados_existentes = pd.read_sql_query("SELECT * FROM trilhas", conn_backup)
                print(f"💾 Backup de {len(dados_existentes)} registros criado")
            except:
                print("⚠️ Não foi possível fazer backup dos dados existentes")
            finally:
                conn_backup.close()
        
        # Remover arquivo do banco
        if os.path.exists(db_path):
            os.remove(db_path)
            print("🗑️ Banco de dados antigo removido")
        
        # Criar novo banco com estrutura correta
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE trilhas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Trilhas TEXT,
                Atividades TEXT NOT NULL,
                Responsável TEXT,
                Tipo TEXT,
                Finalizado TEXT,
                Observações TEXT
            )
        ''')
        
        print("✅ Nova tabela 'trilhas' criada com estrutura correta")
        
        # Restaurar dados se houver backup
        if dados_existentes is not None and not dados_existentes.empty:
            # Adicionar coluna Trilhas se não existir
            if 'Trilhas' not in dados_existentes.columns:
                dados_existentes['Trilhas'] = 'Trilha Padrão'
            
            # Inserir dados restaurados
            dados_existentes.to_sql('trilhas', conn, if_exists='append', index=False)
            print(f"✅ {len(dados_existentes)} registros restaurados")
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados recriado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recriar banco: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("    MIGRAÇÃO DO BANCO DE DADOS - COLUNA TRILHAS")
    print("=" * 60)
    print()
    
    # Verificar estrutura atual
    print("🔍 Verificando estrutura atual...")
    verificar_estrutura_banco()
    print()
    
    # Tentar migração simples primeiro
    print("🔄 Tentando migração simples...")
    if migrar_banco_trilhas():
        print("✅ Migração simples bem-sucedida!")
    else:
        print("⚠️ Migração simples falhou, tentando recriar banco...")
        if recriar_banco_com_trilhas():
            print("✅ Banco recriado com sucesso!")
        else:
            print("❌ Falha na recriação do banco!")
    
    print()
    print("🔍 Verificando estrutura final...")
    verificar_estrutura_banco()
    print()
    print("🎉 Processo de migração concluído!")