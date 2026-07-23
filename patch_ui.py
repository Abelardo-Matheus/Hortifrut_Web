import sys

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the Search bar and "Não achou" button to be on the same line
old_search_section = '''    col_busca, _ = st.columns([1, 1])
    with col_busca:
        busca = st.text_input("🔍 O que você procura hoje?", placeholder="Ex: Maçã, Alface, Abóbora...")
    
    prods_vitrine = produtos
    if busca:
        prods_vitrine = [p for p in produtos if busca.lower() in p['nome'].lower()]
        
    st.write("") # espaco
    
    # Dialog para solicitar produto
    @st.dialog("Qual produto você não encontrou?")
    def modal_solicitacao():
        st.write("Deixe sua sugestão e nós providenciaremos para você!")
        s_prod = st.text_input("Produto que você quer *")
        s_nome = st.text_input("Seu Nome *")
        s_tel = st.text_input("Seu Telefone (Opcional)")
        if st.button("Enviar Sugestão", type="primary", use_container_width=True):
            if s_prod and s_nome:
                sucesso = db.add_solicitacao(s_prod, s_nome, s_tel)
                if sucesso:
                    st.success("Sugestão enviada com sucesso! Muito obrigado.")
                    import time
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("Erro interno. Verifique se você rodou o schema.sql no banco de dados!")
            else:
                st.error("Preencha o Nome do Produto e o Seu Nome.")
    
    c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
    with c_btn2:
        if st.button("🤔 Não achou seu produto? Clique aqui!", use_container_width=True):
            modal_solicitacao()'''

new_search_section = '''    # Dialog para solicitar produto
    @st.dialog("Qual produto você não encontrou?")
    def modal_solicitacao():
        st.write("Deixe sua sugestão e nós providenciaremos para você!")
        s_prod = st.text_input("Produto que você quer *")
        s_nome = st.text_input("Seu Nome *")
        s_tel = st.text_input("Seu Telefone (Opcional)")
        if st.button("Enviar Sugestão", type="primary", use_container_width=True):
            if s_prod and s_nome:
                sucesso = db.add_solicitacao(s_prod, s_nome, s_tel)
                if sucesso:
                    st.success("Sugestão enviada com sucesso! Muito obrigado.")
                    import time
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("Erro interno. Verifique se você rodou o schema.sql no banco de dados!")
            else:
                st.error("Preencha o Nome do Produto e o Seu Nome.")

    # Filtro de pesquisa na esquerda e Botão na direita
    col_busca, col_vazio, col_btn = st.columns([3, 1, 2])
    with col_busca:
        busca = st.text_input("🔍 O que você procura hoje?", placeholder="Ex: Maçã, Alface, Abóbora...")
    
    with col_btn:
        st.write("") # alinhamento vertical com o text_input
        st.write("")
        if st.button("🤔 Não achou seu produto? Clique aqui!", use_container_width=True):
            modal_solicitacao()

    prods_vitrine = produtos
    if busca:
        prods_vitrine = [p for p in produtos if busca.lower() in p['nome'].lower()]'''

content = content.replace(old_search_section, new_search_section)

# 2. Update CSS to maximize width and set 3px border, reduce box image size
old_css = '''    st.markdown(\'\'\'
    <style>
    .blend-img {
        max-width: 100%; 
        max-height: 160px; 
        object-fit: contain; 
        border-radius: 5px;
    }
    </style>
    \'\'\', unsafe_allow_html=True)'''

new_css = '''    st.markdown(\'\'\'
    <style>
    /* Expandir a tela ao máximo possível */
    .block-container {
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Imagem menor para caber mais na tela */
    .blend-img {
        max-width: 100%; 
        max-height: 120px; 
        object-fit: contain; 
        border-radius: 5px;
    }
    
    /* Borda de 3px para as caixas de produtos */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-width: 3px !important;
        border-radius: 10px !important;
        padding: 0.8rem !important;
    }
    </style>
    \'\'\', unsafe_allow_html=True)'''

content = content.replace(old_css, new_css)

# 3. Increase columns from 4 to 6
content = content.replace("cols_per_row = 4", "cols_per_row = 6")

# 4. Decrease image container height inline
content = content.replace('height: 160px;', 'height: 120px;')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch UI concluído!")
