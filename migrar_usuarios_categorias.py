#!/usr/bin/env python3
"""
Script para migrar usuários existentes para incluir categorias
"""

import pandas as pd
import os
from utils import USERS_FILE, obter_categorias_disponiveis

def migrar_usuarios_categorias():
    """Migra usuários existentes para incluir a coluna de categorias"""
    
    print("=== MIGRAÇÃO DE USUÁRIOS PARA CATEGORIAS ===")
    
    try:
        # Verificar se o arquivo de usuários existe
        if not os.path.exists(USERS_FILE):
            print("❌ Arquivo de usuários não encontrado!")
            return False
        
        # Ler arquivo de usuários
        df_usuarios = pd.read_csv(USERS_FILE)
        print(f"📋 Encontrados {len(df_usuarios)} usuários no arquivo")
        
        # Verificar se a coluna categorias já existe
        if 'categorias' in df_usuarios.columns:
            print("✅ Coluna 'categorias' já existe!")
            return True
        
        # Obter categorias disponíveis
        categorias_disponiveis = obter_categorias_disponiveis()
        print(f"📂 Categorias disponíveis: {categorias_disponiveis}")
        
        # Adicionar coluna categorias com valor padrão
        df_usuarios['categorias'] = '[]'  # JSON vazio para usuários existentes
        
        # Salvar arquivo atualizado
        df_usuarios.to_csv(USERS_FILE, index=False)
        
        print("✅ Migração concluída com sucesso!")
        print(f"📊 {len(df_usuarios)} usuários migrados")
        print("💡 Usuários existentes terão acesso a todas as trilhas até definirem suas categorias")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False

def mostrar_usuarios_categorias():
    """Mostra os usuários e suas categorias atuais"""
    
    try:
        if not os.path.exists(USERS_FILE):
            print("❌ Arquivo de usuários não encontrado!")
            return
        
        df_usuarios = pd.read_csv(USERS_FILE)
        
        print("\n=== USUÁRIOS E CATEGORIAS ===")
        for _, usuario in df_usuarios.iterrows():
            categorias = usuario.get('categorias', '[]')
            print(f"👤 {usuario['nome']} ({usuario['email']}) - Tipo: {usuario['tipo']}")
            print(f"   📂 Categorias: {categorias}")
            print()
            
    except Exception as e:
        print(f"❌ Erro ao mostrar usuários: {e}")

if __name__ == "__main__":
    # Executar migração
    sucesso = migrar_usuarios_categorias()
    
    if sucesso:
        # Mostrar usuários após migração
        mostrar_usuarios_categorias()
        
        print("\n🎉 Migração concluída!")
        print("📝 Próximos passos:")
        print("1. Os usuários existentes terão acesso a todas as trilhas")
        print("2. Novos usuários poderão selecionar categorias durante o registro")
        print("3. Administradores podem editar categorias dos usuários se necessário")
    else:
        print("\n❌ Migração falhou!") 