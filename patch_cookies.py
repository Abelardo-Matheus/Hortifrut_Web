import sys

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CookieController import and initialization at the top
init_code = '''import database as db

from streamlit_cookies_controller import CookieController
controller = CookieController()

# Verifica o cookie de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth = controller.get("auth_token")
    if auth == "hortifrut_admin_ok":
        st.session_state.logged_in = True
        # Re-executa para aplicar o estado
        # st.rerun() # Não obrigatório, o layout reage a session_state
'''
content = content.replace('import database as db\n', init_code)

# 2. Add controller.set inside the login logic
old_login = '''                if usuario == "joel" and senha == "531735":
                    st.session_state.logged_in = True
                    st.session_state.fechar_sidebar = True
                    st.rerun()
                else:'''

new_login = '''                if usuario == "joel" and senha == "531735":
                    st.session_state.logged_in = True
                    st.session_state.fechar_sidebar = True
                    controller.set("auth_token", "hortifrut_admin_ok", max_age=31536000) # 1 ano
                    import time
                    time.sleep(0.5) # Aguarda o cookie salvar no navegador
                    st.rerun()
                else:'''
content = content.replace(old_login, new_login)

# 3. Add controller.remove inside the logout logic
old_logout = '''    if st.sidebar.button("🚪 Sair do Sistema"):
        st.session_state.logged_in = False
        st.rerun()'''

new_logout = '''    if st.sidebar.button("🚪 Sair do Sistema"):
        st.session_state.logged_in = False
        controller.remove("auth_token")
        import time
        time.sleep(0.5)
        st.rerun()'''
content = content.replace(old_logout, new_logout)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch de cookies concluído!")
