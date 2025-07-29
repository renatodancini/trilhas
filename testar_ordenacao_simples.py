#!/usr/bin/env python3
"""
Script para testar a ordenação simples das atividades
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

def testar_ordenacao_simples():
    """Testa a ordenação simples com dados de exemplo"""
    
    # Dados de teste com números variados
    atividades_teste = [
        "CMR205.1 - BPH003890 - 20. Finalizar processo",
        "CMR205.1 - BPH003890 - 1. Aprovar contrato de Compras",
        "CMR205.1 - BPH004040 - 15. Validar dados da nota fiscal",
        "CMR205.1 - BPH003890 - 5. Consultar aprovação de workflow",
        "CMR205.1 - BPH004040 - 10. Processar pagamento",
        "CMR205.1 - BPH005123 - 3. Verificar documentação",
        "CMR205.1 - BPH003890 - 8. Analisar crédito",
        "CMR205.1 - BPH004040 - 12. Aprovar solicitação"
    ]
    
    # Criar DataFrame de teste
    df_teste = pd.DataFrame({
        'Atividades': atividades_teste,
        'Responsável': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Lucia', 'Paulo', 'Sofia'],
        'Tipo': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B'],
        'Finalizado': ['Não', 'Sim', 'Não', 'Sim', 'Não', 'Sim', 'Não', 'Sim'],
        'Observações': ['Obs 1', 'Obs 2', 'Obs 3', 'Obs 4', 'Obs 5', 'Obs 6', 'Obs 7', 'Obs 8']
    })
    
    print("=== TESTE DE ORDENAÇÃO SIMPLES ===")
    print("\n📋 Atividades ANTES da ordenação:")
    for i, atividade in enumerate(df_teste['Atividades'], 1):
        print(f"{i}. {atividade}")
    
    # Aplicar ordenação por número sequencial
    df_teste['numero_sequencial'] = df_teste['Atividades'].apply(extrair_numero_sequencial)
    
    # Ordenar por número sequencial (do menor para o maior)
    df_teste = df_teste.sort_values('numero_sequencial')
    
    # Remover coluna auxiliar
    df_teste = df_teste.drop('numero_sequencial', axis=1)
    
    print("\n📋 Atividades DEPOIS da ordenação:")
    print("=" * 80)
    
    for i, (_, row) in enumerate(df_teste.iterrows(), 1):
        print(f"{i}. {row['Atividades']}")
    
    print("\n✅ Teste de ordenação simples concluído!")
    
    # Verificar se a ordenação está correta
    numeros_sequenciais = [extrair_numero_sequencial(atividade) for atividade in df_teste['Atividades']]
    print(f"\n🔢 Números sequenciais extraídos: {numeros_sequenciais}")
    
    if numeros_sequenciais == sorted(numeros_sequenciais):
        print("✅ Ordenação está CORRETA!")
    else:
        print("❌ Ordenação está INCORRETA!")
    
    return df_teste

if __name__ == "__main__":
    df_resultado = testar_ordenacao_simples() 