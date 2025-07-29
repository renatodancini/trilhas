#!/usr/bin/env python3
"""
Script para testar a categorização por número sequencial das atividades
"""

import pandas as pd
import re

def extrair_numero_sequencial(atividade):
    """Função para extrair número sequencial da atividade"""
    import re
    # Procurar pelo número após o segundo "-" (formato: X. Descrição)
    # Exemplo: "CMR205.1 - BPH003890 - 1. Aprovar contrato" -> extrair "1"
    match = re.search(r'-\s*(\d+)\.', atividade)
    if match:
        return int(match.group(1))
    return 0  # Se não encontrar número sequencial, colocar no início

def extrair_categoria_sequencial(atividade):
    """Função para extrair categoria baseada no número sequencial"""
    numero = extrair_numero_sequencial(atividade)
    if numero > 0:
        return f"Categoria {numero}"
    return "Sem Categoria"

def testar_categorizacao_sequencial():
    """Testa a categorização por número sequencial com dados de exemplo"""
    
    # Dados de teste baseados no exemplo da imagem
    atividades_teste = [
        "CMR205.1 - BPH003890 - 1. Aprovar contrato de Compras",
        "CMR205.1 - BPH003890 - 2. Consultar aprovação de workflow",
        "CMR205.1 - BPH004040 - 3. Validar dados da nota fiscal",
        "CMR205.1 - BPH003890 - 4. Verificar documentação",
        "CMR205.1 - BPH004040 - 5. Processar pagamento",
        "CMR205.1 - BPH005123 - 6. Finalizar processo"
    ]
    
    # Criar DataFrame de teste
    df_teste = pd.DataFrame({
        'Atividades': atividades_teste,
        'Responsável': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Lucia'],
        'Tipo': ['A', 'B', 'C', 'A', 'B', 'C'],
        'Finalizado': ['Não', 'Sim', 'Não', 'Sim', 'Não', 'Sim'],
        'Observações': ['Obs 1', 'Obs 2', 'Obs 3', 'Obs 4', 'Obs 5', 'Obs 6']
    })
    
    print("=== TESTE DE CATEGORIZAÇÃO POR NÚMERO SEQUENCIAL ===")
    print("\n📋 Atividades ANTES da categorização:")
    for i, atividade in enumerate(df_teste['Atividades'], 1):
        print(f"{i}. {atividade}")
    
    # Aplicar categorização por número sequencial
    df_teste['categoria_sequencial'] = df_teste['Atividades'].apply(extrair_categoria_sequencial)
    df_teste['numero_sequencial'] = df_teste['Atividades'].apply(extrair_numero_sequencial)
    
    # Ordenar por número sequencial
    df_teste = df_teste.sort_values('numero_sequencial')
    
    print("\n📋 Atividades DEPOIS da categorização:")
    print("=" * 80)
    
    # Agrupar e mostrar por categoria
    grupos_sequencial = df_teste.groupby('categoria_sequencial')
    
    for categoria, grupo in grupos_sequencial:
        if categoria != "Sem Categoria":
            print(f"\n🏷️  {categoria}")
            print("-" * 50)
        else:
            print(f"\n📝 ATIVIDADES SEM CATEGORIA")
            print("-" * 50)
        
        for i, (_, row) in enumerate(grupo.iterrows(), 1):
            print(f"{i}. {row['Atividades']}")
    
    print("\n✅ Teste de categorização por número sequencial concluído!")
    
    # Verificar se a categorização está correta
    categorias_esperadas = ['Categoria 1', 'Categoria 2', 'Categoria 3', 'Categoria 4', 'Categoria 5', 'Categoria 6']
    categorias_encontradas = list(grupos_sequencial.groups.keys())
    
    print(f"\n🔍 Categorias encontradas: {categorias_encontradas}")
    
    if all(cat in categorias_encontradas for cat in categorias_esperadas):
        print("✅ Categorização está CORRETA!")
    else:
        print("❌ Categorização está INCORRETA!")
    
    return df_teste

if __name__ == "__main__":
    df_resultado = testar_categorizacao_sequencial() 