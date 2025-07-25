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
    
    # Salvar como XLSX com formatação
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Escrever o DataFrame primeiro para criar a worksheet
        df_xlsx.to_excel(writer, sheet_name='Trilha', startrow=2, index=False)
        
        # Agora podemos acessar a worksheet
        worksheet = writer.sheets['Trilha']
        workbook = writer.book
        
        # Título da trilha na primeira linha
        worksheet.write(0, 0, f"{codigo} - {nome_trilha}")
        
        # Linha vazia na segunda linha
        worksheet.write(1, 0, '')
        
        # Formatar o título da trilha (primeira linha)
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'left'
        })
        worksheet.set_row(0, 20, title_format)
        
        # Formatar o cabeçalho (terceira linha) - fundo cinza escuro, texto branco em negrito
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#404040',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Aplicar formatação ao cabeçalho
        for col_num, value in enumerate(df_xlsx.columns.values):
            worksheet.write(2, col_num, value, header_format)
        
        # Ajustar largura das colunas
        worksheet.set_column('A:A', 60)  # Atividade
        worksheet.set_column('B:B', 30)  # Responsável
        worksheet.set_column('C:C', 15)  # Tipo
        worksheet.set_column('D:D', 15)  # Finalizado
        worksheet.set_column('E:E', 20)  # Observações
    
    buffer.seek(0)
    return buffer.read() 