import sys

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS for responsiveness
old_css = '''    /* Expandir a tela mantendo-a centralizada e sem encostar no scroll */
    .block-container {
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
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
    }'''

new_css = '''    /* Expandir a tela mantendo-a centralizada e sem encostar no scroll */
    .block-container {
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Responsividade para Celulares */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }
    
    /* Imagem menor para caber mais na tela */
    .blend-img {
        max-width: 100%; 
        max-height: 120px; 
        object-fit: contain; 
        border-radius: 5px;
    }
    
    /* Grid CSS Responsivo para a Vitrine (muito superior as colunas nativas) */
    .vitrine-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 15px;
        width: 100%;
    }
    
    @media (max-width: 768px) {
        .vitrine-grid {
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 10px;
        }
    }
    
    .vitrine-card {
        border: 3px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 0.8rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        box-sizing: border-box;
        background-color: transparent;
    }'''
content = content.replace(old_css, new_css)

# 2. Replace the python st.columns loop with raw HTML generator
old_grid_loop = '''    cols_per_row = 6
    for i in range(0, len(prods_vitrine), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(prods_vitrine):
                p = prods_vitrine[i+j]
                with cols[j]:
                    with st.container(border=True):
                        # Imagem com o blend mode (fundo branco fica transparente)
                        if p.get("imagem_url"):
                            st.markdown(f'<div style="display: flex; justify-content: center; height: 120px; align-items: center; margin-bottom: 10px;"><img class="blend-img" src="{p["imagem_url"]}"></div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height: 120px; display: flex; justify-content: center; align-items: center; color: #ccc; margin-bottom: 10px;">Sem Imagem</div>', unsafe_allow_html=True)
                            
                        # Nome do Produto
                        nome_curto = p['nome'] if len(p['nome']) <= 20 else p['nome'][:18] + '...'
                        st.markdown(f'<div style=\"height: 48px; overflow: hidden; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 18px; margin-bottom: 5px; text-align: center;\">{nome_curto}</div>', unsafe_allow_html=True)
                        
                        # Preço
                        st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; font-size: 20px; margin-bottom: 5px; color: #27ae60; text-align: center;"><b>R$ {p["preco_venda"]:.2f}</b> <span style="font-size:14px; color:#7f8c8d; margin-left: 5px;">/ {p["unidade_medida"]}</span></div>', unsafe_allow_html=True)
                        
                        # Estoque/Disponibilidade
                        if p['quantidade_estoque'] > 0 or p['categoria'] == 'Horta (Ilimitado)':
                            st.markdown(f"<div style='text-align: center; color: #2980b9; font-weight: bold; font-size: 14px;'>✓ Disponível</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align: center; color: #e74c3c; font-weight: bold; font-size: 14px;'>✗ Esgotado</div>", unsafe_allow_html=True)'''

new_grid_loop = '''    html_cards = []
    for p in prods_vitrine:
        # Imagem
        if p.get("imagem_url"):
            img_html = f'<div style="display: flex; justify-content: center; height: 120px; align-items: center; margin-bottom: 10px;"><img class="blend-img" src="{p["imagem_url"]}"></div>'
        else:
            img_html = '<div style="height: 120px; display: flex; justify-content: center; align-items: center; color: #ccc; margin-bottom: 10px;">Sem Imagem</div>'
            
        # Nome do Produto
        nome_curto = p['nome'] if len(p['nome']) <= 20 else p['nome'][:18] + '...'
        nome_html = f'<div style="height: 48px; overflow: hidden; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 18px; margin-bottom: 5px; text-align: center;">{nome_curto}</div>'
        
        # Preço
        preco_html = f'<div style="display: flex; justify-content: center; align-items: center; font-size: 20px; margin-bottom: 5px; color: #27ae60; text-align: center;"><b>R$ {p["preco_venda"]:.2f}</b> <span style="font-size:14px; color:#7f8c8d; margin-left: 5px;">/ {p["unidade_medida"]}</span></div>'
        
        # Estoque
        if p['quantidade_estoque'] > 0 or p['categoria'] == 'Horta (Ilimitado)':
            estoque_html = "<div style='text-align: center; color: #2980b9; font-weight: bold; font-size: 14px;'>✓ Disponível</div>"
        else:
            estoque_html = "<div style='text-align: center; color: #e74c3c; font-weight: bold; font-size: 14px;'>✗ Esgotado</div>"
            
        card_html = f\'\'\'
        <div class="vitrine-card">
            {img_html}
            {nome_html}
            {preco_html}
            {estoque_html}
        </div>
        \'\'\'
        html_cards.append(card_html)
        
    grid_html = f\'\'\'
    <div class="vitrine-grid">
        {"".join(html_cards)}
    </div>
    \'\'\'
    st.markdown(grid_html, unsafe_allow_html=True)'''

content = content.replace(old_grid_loop, new_grid_loop)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch de responsividade concluído!")
