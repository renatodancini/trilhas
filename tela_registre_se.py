import streamlit as st
from utils import cadastra_usuario

def tela_registre_se():
    st.write("Entrou na tela de registro")  # Depuração
    col_reg1, col_reg2, col_reg3 = st.columns([2.75,2.5,2.75])
    with col_reg2:
        st.markdown('<h3 style="text-align:center; margin-bottom: 20px; font-size:1.1em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Cadastro de Usuário</h3>', unsafe_allow_html=True)
        with st.form("form_registro_usuario"):
            nome = st.text_input("Nome", key="reg_nome")
            email = st.text_input("Email", key="reg_email")
            senha = st.text_input("Senha", type="password", key="reg_senha")
            if st.form_submit_button("Cadastrar"):
                try:
                    if cadastra_usuario(nome, email, senha, "Usuário"):
                        st.success("Usuário cadastrado com sucesso! Faça login para acessar o sistema.")
                    else:
                        st.error("Email já cadastrado.")
                except Exception as e:
                    st.error(f"Erro ao cadastrar usuário: {e}")
    st.stop() 