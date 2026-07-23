import sys
import re

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Acha onde começa a lógica do admin (depois do import db)
header_end = 0
for i, line in enumerate(lines):
    if "import database as db" in line:
        header_end = i + 1
        break

header = lines[:header_end]
body = lines[header_end:]

# Identação do body para virar a função render_admin()
indented_body = ["    " + line for line in body]

new_content = "".join(header) + """

def render_admin():
""" + "".join(indented_body) + """

# ==========================================
# ROTEAMENTO PRINCIPAL (PÚBLICO VS ADMIN)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    if not st.session_state.logged_in:
        st.subheader("🔐 Acesso Restrito (Dono)")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if usuario == "joel" and senha == "531735":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")
    else:
        st.success("Você está logado como Admin.")
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

if st.session_state.logged_in:
    render_admin()
else:
    # ==========================================
    # VITRINE PÚBLICA (CLIENTES)
    # ==========================================
    st.markdown("<h1 style='text-align: center; color: #27ae60; font-size: 50px; margin-bottom: 0;'>Hortifruti J & M 🍎</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px; color: #7f8c8d;'>Seja muito bem-vindo! Confira nossos produtos fresquinhos:</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    produtos = db.get_produtos()
    
    # CSS Mágico para fundo transparente: mix-blend-mode: multiply
    # Isso remove o fundo branco das fotos baixadas da internet!
    st.markdown('''
    <style>
    .blend-img {
        max-width: 100%; 
        max-height: 160px; 
        object-fit: contain; 
        border-radius: 5px;
        mix-blend-mode: multiply; /* MAGIA DA TRANSPARÊNCIA */
    }
    </style>
    ''', unsafe_allow_html=True)
    
    col_busca, _ = st.columns([1, 1])
    with col_busca:
        busca = st.text_input("🔍 O que você procura hoje?", placeholder="Ex: Maçã, Alface, Abóbora...")
    
    prods_vitrine = produtos
    if busca:
        prods_vitrine = [p for p in produtos if busca.lower() in p['nome'].lower()]
        
    st.write("") # espaco
    
    cols_per_row = 4
    for i in range(0, len(prods_vitrine), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(prods_vitrine):
                p = prods_vitrine[i+j]
                with cols[j]:
                    with st.container(border=True):
                        # Imagem com o blend mode (fundo branco fica transparente)
                        if p.get("imagem_url"):
                            st.markdown(f'<div style="display: flex; justify-content: center; height: 160px; align-items: center; margin-bottom: 10px;"><img class="blend-img" src="{p["imagem_url"]}"></div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height: 170px; display: flex; justify-content: center; align-items: center; color: #ccc;">Sem Imagem</div>', unsafe_allow_html=True)
                            
                        # Nome do Produto
                        st.markdown(f'<div style="height: 48px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-weight: bold; font-size: 20px; margin-bottom: 5px; text-align: center;">{p["nome"]}</div>', unsafe_allow_html=True)
                        
                        # Preço
                        st.markdown(f'<div style="font-size: 22px; margin-bottom: 5px; color: #27ae60; text-align: center;"><b>R$ {p["preco_venda"]:.2f}</b> <span style="font-size:14px; color:#7f8c8d;">/ {p["unidade_medida"]}</span></div>', unsafe_allow_html=True)
                        
                        # Estoque/Disponibilidade
                        if p['quantidade_estoque'] > 0 or p['categoria'] == 'Horta (Ilimitado)':
                            st.markdown(f"<div style='text-align: center; color: #2980b9; font-weight: bold; font-size: 14px;'>✓ Disponível</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align: center; color: #e74c3c; font-weight: bold; font-size: 14px;'>✗ Esgotado</div>", unsafe_allow_html=True)
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("app.py atualizado para separar Cliente e Admin!")
