import sys
import re

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False

# We need to remove the `with st.sidebar:` block and `st.session_state.get("fechar_sidebar")` hack.
i = 0
while i < len(lines):
    line = lines[i]
    
    # 1. Remove the JS hack for closing the sidebar
    if 'if st.session_state.get("fechar_sidebar", False):' in line:
        # Skip this block
        i += 1
        while i < len(lines) and (lines[i].startswith(' ') or lines[i].strip() == ''):
            if 'st.session_state.fechar_sidebar = False' in lines[i]:
                i += 1
                break
            i += 1
        continue
        
    # 2. Add logout button to the Admin Title
    if 'st.title("🍎 Gestão Hortifruti Online")' in line:
        new_lines.append(line)
        new_lines.append('    col_t1, col_t2 = st.columns([4, 1])\n')
        new_lines.append('    with col_t2:\n')
        new_lines.append('        st.write("")\n')
        new_lines.append('        if st.button("🚪 Sair", use_container_width=True):\n')
        new_lines.append('            st.session_state.logged_in = False\n')
        new_lines.append('            controller.remove("auth_token")\n')
        new_lines.append('            import time\n')
        new_lines.append('            time.sleep(0.5)\n')
        new_lines.append('            st.rerun()\n')
        i += 1
        continue

    # 3. Remove the sidebar login entirely
    if 'with st.sidebar:' in line:
        # Skip everything until `if st.session_state.logged_in:`
        while i < len(lines) and not lines[i].startswith('if st.session_state.logged_in:'):
            i += 1
        continue
        
    # 4. Insert Login Modal definition right before the public vitrine
    if "st.markdown(\"<h1 style='text-align: center; color: #27ae60; font-size: 50px; margin-bottom: 0;'>Hortifruti J & M 🍎</h1>\", unsafe_allow_html=True)" in line:
        # Define the modal
        new_lines.append('    @st.dialog("🔐 Acesso Restrito (Dono)")\n')
        new_lines.append('    def modal_login():\n')
        new_lines.append('        with st.form("login_form"):\n')
        new_lines.append('            usuario = st.text_input("Usuário")\n')
        new_lines.append('            senha = st.text_input("Senha", type="password")\n')
        new_lines.append('            if st.form_submit_button("Entrar", type="primary", use_container_width=True):\n')
        new_lines.append('                if usuario == "joel" and senha == "531735":\n')
        new_lines.append('                    st.session_state.logged_in = True\n')
        new_lines.append('                    controller.set("auth_token", "hortifrut_admin_ok", max_age=31536000)\n')
        new_lines.append('                    import time\n')
        new_lines.append('                    time.sleep(0.5)\n')
        new_lines.append('                    st.rerun()\n')
        new_lines.append('                else:\n')
        new_lines.append('                    st.error("Usuário ou senha incorretos")\n\n')
        new_lines.append(line)
        i += 1
        continue
        
    # 5. Insert Login button at the very end of the file
    if line.strip() == "st.markdown(grid_html, unsafe_allow_html=True)":
        new_lines.append(line)
        new_lines.append('\n')
        new_lines.append('    st.markdown("---")\n')
        new_lines.append('    c_end1, c_end2, c_end3 = st.columns([2,1,2])\n')
        new_lines.append('    with c_end2:\n')
        new_lines.append('        if st.button("🔐 Área Administrativa", use_container_width=True):\n')
        new_lines.append('            modal_login()\n')
        i += 1
        continue

    new_lines.append(line)
    i += 1

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Patch aplicado com sucesso!")
