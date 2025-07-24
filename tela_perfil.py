import streamlit as st
import pandas as pd
from utils import USERS_FILE

def tela_perfil():
    st.write("# Perfil do Usuário")
    df_usuarios = pd.read_csv(USERS_FILE)
    dados = df_usuarios[df_usuarios['nome'] == st.session_state['usuario']].iloc[0]
    st.write(f"**Nome:** {dados['nome']}")
    st.write(f"**Email:** {dados['email']}")
    st.write(f"**Tipo:** {dados['tipo']}")
    st.write("---")
    st.write("## Trocar senha")
    with st.form("form_troca_senha"):
        senha_atual = st.text_input("Senha atual", type="password")
        nova_senha = st.text_input("Nova senha", type="password")
        nova_senha2 = st.text_input("Repita a nova senha", type="password")
        def senha_valida(s):
            import re
            return len(s) >= 6 and bool(re.search(r"[A-Za-z]", s)) and bool(re.search(r"[0-9]", s))
        senha_ok = senha_valida(nova_senha)
        if nova_senha and not senha_ok:
            st.error("A senha deve ter no mínimo 6 caracteres e ser alfanumérica.")
        if st.form_submit_button("Alterar senha"):
            if senha_atual != dados['senha']:
                st.error("Senha atual incorreta.")
            elif not senha_ok:
                st.error("A nova senha deve ter no mínimo 6 caracteres e ser alfanumérica.")
            elif nova_senha != nova_senha2:
                st.error("As senhas não coincidem.")
            else:
                df_usuarios.loc[df_usuarios['email'] == dados['email'], 'senha'] = nova_senha
                df_usuarios.to_csv(USERS_FILE, index=False)
                st.success("Senha alterada com sucesso!")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
    st.stop() 