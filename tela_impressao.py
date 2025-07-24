import streamlit as st
import pandas as pd
from utils import busca_gestao_trilhas

def tela_impressao():
    st.write("### Trilhas registradas")
    df_trilhas_banco = busca_gestao_trilhas()
    if df_trilhas_banco is not None and 'Trilhas' in df_trilhas_banco.columns:
        if 'Responsável' in df_trilhas_banco.columns:
            df_trilhas_banco = df_trilhas_banco.rename(columns={'Responsável': 'Impresso por'})
        trilhas_unicas = df_trilhas_banco['Trilhas'].dropna().unique()
        codigos = []
        for trilha in trilhas_unicas:
            codigo = df_trilhas_banco.loc[df_trilhas_banco['Trilhas'] == trilha, 'Código'].astype(str).values
            codigos.append(codigo[0] if len(codigo) > 0 else '')
        df_trilhas_home = pd.DataFrame({
            'Código': codigos,
            'Trilhas': trilhas_unicas,
            'Status da impressão': [''] * len(trilhas_unicas),
            'Impressão': [''] * len(trilhas_unicas)
        })
        for i, row in df_trilhas_home.iterrows():
            cols = st.columns(len(df_trilhas_home.columns))
            for j, col in enumerate(df_trilhas_home.columns):
                if col == 'Impressão':
                    if cols[j].button('Imprimir', key=f"btn_imprimir_{i}"):
                        trilha = row['Trilhas']
                        codigo = row['Código']
                        df_atividades = df_trilhas_banco[df_trilhas_banco['Trilhas'] == trilha]
                        if not df_atividades.empty:
                            df_xlsx = df_atividades.drop(columns=['Código'])
                            df_xlsx = df_xlsx.replace([float('nan'), float('inf'), float('-inf')], '', regex=True)
                            df_xlsx = df_xlsx.fillna('')
                        else:
                            df_xlsx = pd.DataFrame()
                        import io
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                            workbook = writer.book
                            worksheet = workbook.add_worksheet('Impressao')
                            writer.sheets['Impressao'] = worksheet
                            title_format = workbook.add_format({'bold': True})
                            worksheet.write(0, 0, f"{codigo} - {trilha}", title_format)
                            header_format = workbook.add_format({'bold': True, 'bg_color': '#666666', 'font_color': '#FFFFFF'})
                            if not df_xlsx.empty:
                                for col_num, value in enumerate(df_xlsx.columns):
                                    worksheet.write(2, col_num, value, header_format)
                                cell_format = workbook.add_format({'border': 1})
                                for row_num, row_data in enumerate(df_xlsx.values):
                                    for col_num, cell_value in enumerate(row_data):
                                        worksheet.write(row_num + 3, col_num, cell_value, cell_format)
                            for i, col in enumerate(df_xlsx.columns):
                                max_len = max([len(str(val)) for val in df_xlsx[col].values] + [len(col)])
                                if col.strip().lower().startswith('observa'):
                                    worksheet.set_column(i, i, int((max_len + 2) * 1.1))
                                else:
                                    worksheet.set_column(i, i, max_len + 2)
                        buffer.seek(0)
                        st.session_state['xlsx_bytes'] = buffer.read()
                        st.session_state['trilha_impressao'] = trilha
                        st.session_state['codigo_impressao'] = codigo
                        st.session_state['show_impressao'] = True
                else:
                    cols[j].write(row[col]) 