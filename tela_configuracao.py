import streamlit as st
import pandas as pd
import sqlite3
from utils import USERS_FILE, DB_FILE, cadastra_usuario, salva_impressao_upload, limpa_gestao_trilhas, salva_gestao_trilhas, busca_gestao_trilhas

def tela_configuracao():
    st.write("# Configurações")
    aba1, aba2, aba3 = st.tabs(["Cadastro de Usuários", "Upload de dados", "Banco de Dados"])
    with aba1:
        with st.form("cadastro_usuario"):
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            tipo = st.selectbox("Tipo do cadastro: Usuário ou Administrador", ["Usuário", "Administrador"])
            if st.form_submit_button("Cadastrar"):
                if cadastra_usuario(nome, email, senha, tipo):
                    st.success("Usuário cadastrado com sucesso!")
                else:
                    st.error("Email já cadastrado.")
        st.write("## Usuários cadastrados")
        df_usuarios = pd.read_csv(USERS_FILE)
        st.dataframe(df_usuarios)
        st.write("## Alterar permissões dos usuários")
        df_usuarios = pd.read_csv(USERS_FILE)
        col1, col2, col3, col4, col5 = st.columns([3, 4, 2, 2, 2])
        with col1:
            st.markdown("<div style='border-right:1px solid #ddd;'><b>Nome</b></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='border-right:1px solid #ddd;'><b>Email</b></div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div style='border-right:1px solid #ddd;'><b>Usuário</b></div>", unsafe_allow_html=True)
        with col4:
            st.markdown("<div style='border-right:1px solid #ddd;'><b>Administrador</b></div>", unsafe_allow_html=True)
        with col5:
            st.markdown("<b>Ação</b>", unsafe_allow_html=True)
        novos_tipos = []
        excluir_idx = None
        for i, row in df_usuarios.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 4, 2, 2, 2])
            with col1:
                st.markdown(f"<div style='border-right:1px solid #ddd;padding:8px;background:#fff'>{row['nome']}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='border-right:1px solid #ddd;padding:8px;background:#fff'>{row['email']}</div>", unsafe_allow_html=True)
            with col3:
                checked_user = row['tipo'] == "Usuário"
                user_cb = st.checkbox("", value=checked_user, key=f"cb_user_{i}")
                st.markdown("<div style='border-right:1px solid #ddd;position:relative;top:-38px;'>&nbsp;</div>", unsafe_allow_html=True)
            with col4:
                checked_admin = row['tipo'] == "Administrador"
                admin_cb = st.checkbox("", value=checked_admin, key=f"cb_admin_{i}")
                st.markdown("<div style='border-right:1px solid #ddd;position:relative;top:-38px;'>&nbsp;</div>", unsafe_allow_html=True)
            if admin_cb:
                novos_tipos.append("Administrador")
            else:
                novos_tipos.append("Usuário")
            with col5:
                if st.button("Excluir", key=f"excluir_{i}"):
                    excluir_idx = i
        with st.form("form_permissoes"):
            if st.form_submit_button("Salvar permissões"):
                df_usuarios['tipo'] = novos_tipos
                df_usuarios.to_csv(USERS_FILE, index=False)
                st.success("Permissões atualizadas com sucesso!")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
        if excluir_idx is not None:
            df_usuarios = df_usuarios.drop(excluir_idx).reset_index(drop=True)
            df_usuarios.to_csv(USERS_FILE, index=False)
            st.success("Usuário excluído com sucesso!")
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
    with aba2:
        st.write("## Upload de dados")
        if st.button('Deletar tabela de uploads'):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('DROP TABLE IF EXISTS impressao_upload')
            c.execute('''CREATE TABLE IF NOT EXISTS impressao_upload (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                colunas TEXT,
                dados TEXT
            )''')
            conn.commit()
            conn.close()
            st.success('Tabela de uploads deletada e recriada com sucesso!')
        arquivo = st.file_uploader("Selecione um arquivo para upload (CSV ou Excel)", type=["csv", "xlsx"])
        if arquivo is not None:
            import io
            if arquivo.name.endswith('.csv'):
                df_upload = pd.read_csv(arquivo)
            else:
                xls = pd.ExcelFile(arquivo)
                if 'Impressão' in xls.sheet_names:
                    df_upload = pd.read_excel(xls, sheet_name='Impressão')
                    df_upload = df_upload.copy()
                    titulo_col = []
                    titulo_atual = None
                    for idx, row in df_upload.iterrows():
                        is_titulo = not row.astype(str).str.contains('BPH', na=False).any()
                        if is_titulo:
                            titulo_atual = str(row.iloc[0])
                        titulo_col.append(titulo_atual)
                    df_upload['titulo'] = titulo_col
                    salva_impressao_upload(df_upload)
                    st.success("Dados da aba 'Impressão' salvos no banco de dados!")
                    limpa_gestao_trilhas()
                    colunas_trilhas = ["Trilhas", "Atividade", "Responsável", "Tipo", "Finalizado", "Observações", "Código"]
                    df_trilhas = pd.DataFrame(columns=colunas_trilhas)
                    if df_upload.shape[1] >= 7:
                        df_trilhas = pd.DataFrame({
                            "Trilhas": df_upload.iloc[:, 0],
                            "Atividade": df_upload.iloc[:, 1],
                            "Responsável": df_upload.iloc[:, 2],
                            "Tipo": df_upload.iloc[:, 3],
                            "Finalizado": df_upload.iloc[:, 4],
                            "Observações": df_upload.iloc[:, 5],
                            "Código": df_upload.iloc[:, 6],
                        })
                    salva_gestao_trilhas(df_trilhas)
        st.write("### Tabela de Gestão de Trilhas")
        df_trilhas_banco = busca_gestao_trilhas()
        if df_trilhas_banco is not None:
            st.dataframe(df_trilhas_banco)
        else:
            st.info("Nenhum dado disponível na tabela de gestão de trilhas.")
    with aba3:
        st.write("## Visualização Completa do Banco de Dados")
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        tabelas = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for tabela in tabelas:
            nome_tabela = tabela[0]
            st.write(f"### Tabela: {nome_tabela}")
            try:
                df = pd.read_sql_query(f'SELECT * FROM {nome_tabela}', conn)
                st.dataframe(df)
            except Exception as e:
                st.warning(f"Não foi possível exibir a tabela {nome_tabela}: {e}")
        conn.close() 