import pandas as pd
import io

def gerar_xlsx_para_trilha(nome_trilha, codigo, df_completo):
    """
    Gera um arquivo XLSX para uma trilha específica com estrutura padronizada.
    """
    # Template das 18 atividades padronizadas
    atividades_template = [
        {
            'codigo_atividade': 'BPH004251',
            'descricao': 'Relatório de estoques / Disponibilidade do Produto',
            'responsavel': 'bill.vakuda@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH004047',
            'descricao': 'Criar contrato de compra',
            'responsavel': 'bruno.lobo@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH003890',
            'descricao': 'Aprovar contrato de Compras',
            'responsavel': 'lucas.sbardella@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH003890',
            'descricao': 'Consultar aprovação de workflow',
            'responsavel': 'lucas.sbardella@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH003625',
            'descricao': 'Avaliar fluxo de caixa diário',
            'responsavel': 'caroline.silva@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH004065',
            'descricao': 'Criar pedido de compra vinculado ao contrato',
            'responsavel': 'bruno.lobo@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH003386',
            'descricao': 'Realizar Pré Validação Fiscal do Pedido de Compra [VALIDAÇÃO]',
            'responsavel': 'everton.siqueira@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH003625',
            'descricao': 'Avaliar fluxo de caixa diário',
            'responsavel': 'caroline.silva@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH004054',
            'descricao': 'Lançar contrato de Venda',
            'responsavel': 'anna.santos@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH004301',
            'descricao': 'Aprovar contrato de Venda',
            'responsavel': 'anna.santos@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH003625',
            'descricao': 'Avaliar fluxo de caixa diário',
            'responsavel': 'caroline.silva@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH004055',
            'descricao': 'Lançar ordem de venda no sistema',
            'responsavel': 'lucas.sbardella@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH003523',
            'descricao': 'Realizar Pré Validação Fiscal da Ordem de Venda [VALIDAÇÃO]',
            'responsavel': 'luiz.ferreira@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH001162',
            'descricao': 'Identificar a demanda na plataforma',
            'responsavel': 'simone.tessaro@sipal.com.br',
            'tipo': 'Tarken'
        },
        {
            'codigo_atividade': 'BPH001162',
            'descricao': 'Definir a garantia que será exigida para dar sequência na operação analisada.',
            'responsavel': 'simone.tessaro@sipal.com.br',
            'tipo': 'Tarken'
        },
        {
            'codigo_atividade': 'BPH001162',
            'descricao': 'Inserir limite de crédito no SAP',
            'responsavel': 'simone.tessaro@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH004197',
            'descricao': 'Administrar deferimentos de crédito documentado',
            'responsavel': 'simone.tessaro@sipal.com.br',
            'tipo': 'SAP'
        },
        {
            'codigo_atividade': 'BPH004197',
            'descricao': 'Liberar para Faturamento',
            'responsavel': 'simone.tessaro@sipal.com.br',
            'tipo': 'SAP'
        }
    ]
    
    # Criar DataFrame com as atividades
    dados = []
    for i, atividade in enumerate(atividades_template, 1):
        dados.append({
            'Atividade': f"{codigo} - {atividade['codigo_atividade']} - {i}. {atividade['descricao']}",
            'Responsável': atividade['responsavel'],
            'Tipo': atividade['tipo'],
            'Finalizado': '',
            'Observações': ''
        })
    
    df_xlsx = pd.DataFrame(dados)
    
    # Criar buffer para o arquivo
    buffer = io.BytesIO()
    
    # Salvar como XLSX
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_xlsx.to_excel(writer, sheet_name='Trilha', index=False)
    
    buffer.seek(0)
    return buffer.read() 