import sys

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update margin to 10px on the right
old_css_padding = '''    /* Expandir a tela ao máximo possível */
    .block-container {
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }'''

new_css_padding = '''    /* Expandir a tela ao máximo possível com margem direita de 10px */
    .block-container {
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 10px !important;
        max-width: 100% !important;
    }'''
content = content.replace(old_css_padding, new_css_padding)

# 2. Convert login to st.form to allow Enter key, and enhance sidebar closing script
old_login = '''    with st.sidebar:
        st.header("🔐 Acesso Restrito")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if usuario == "joel" and senha == "531735":
                st.session_state.logged_in = True
                st.session_state.fechar_sidebar = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")'''

new_login = '''    with st.sidebar:
        st.header("🔐 Acesso Restrito")
        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submit_login = st.form_submit_button("Entrar", type="primary", use_container_width=True)
            if submit_login:
                if usuario == "joel" and senha == "531735":
                    st.session_state.logged_in = True
                    st.session_state.fechar_sidebar = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")'''
content = content.replace(old_login, new_login)


# 3. Enhance the JavaScript for closing the sidebar
old_js = '''        components.html(\'\'\'
            <script>
                // Tenta encontrar o botão de fechar a sidebar no painel pai e clica
                const doc = window.parent.document;
                const buttons = Array.from(doc.querySelectorAll('button'));
                const closeBtn = buttons.find(b => b.getAttribute('data-testid') === 'baseButton-headerNoPadding' || b.innerHTML.includes('svg'));
                if(closeBtn) closeBtn.click();
            </script>
        \'\'\', height=0, width=0)'''

new_js = '''        components.html(\'\'\'
            <script>
                setTimeout(() => {
                    const doc = window.parent.document;
                    // Procura o botão de toggle da sidebar que fica no header
                    const toggleBtn = doc.querySelector('[data-testid="collapsedControl"]');
                    if (toggleBtn) {
                        toggleBtn.click();
                    } else {
                        // Tenta abordagem genérica procurando SVGs que indicam fechar
                        const buttons = Array.from(doc.querySelectorAll('button'));
                        const closeBtn = buttons.find(b => b.getAttribute('aria-expanded') === 'true' || b.getAttribute('data-testid') === 'baseButton-header');
                        if(closeBtn) closeBtn.click();
                    }
                }, 100);
            </script>
        \'\'\', height=0, width=0)'''
content = content.replace(old_js, new_js)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch concluído!")
