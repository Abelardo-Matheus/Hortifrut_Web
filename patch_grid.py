import sys
import re

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove custom CSS that was breaking text colors
css_block = r"""# Estilização CSS customizada \(Design Limpo e Responsivo\)
st\.markdown\(\"\"\"
<style>
    \.stTabs \[data-baseweb=\"tab-list\"\] \{
        gap: 20px;
    \}
    \.stTabs \[data-baseweb=\"tab\"\] \{
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 16px;
    \}
    \.produto-card \{
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba\(0,0,0,0\.1\);
        text-align: center;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
    \}
</style>
\"\"\", unsafe_allow_html=True\)"""

content = re.sub(css_block, "", content)

# 2. Rewrite the product grid to use st.container
old_grid = r"""                        img_tag = f'<img src="\{p\.get\("imagem_url"\)\}" style="max-width: 100%; border-radius: 5px; margin-bottom: 10px; max-height: 120px; object-fit: contain;">' if p\.get\("imagem_url"\) else ""
                        html_content = f\"\"\"
<div class="produto-card">
    \{img_tag\}
    <h4 style="margin-bottom: 5px; color: #2c3e50;">\{p\['nome'\]\}</h4>
    <p style="margin-bottom: 5px; color: #27ae60; font-weight: bold; font-size: 18px;">R\$ \{p\['preco_venda'\]:\.2f\} / \{p\['unidade_medida'\]\}</p>
    <p style="margin-bottom: 10px; color: #7f8c8d; font-size: 12px;">Estoque: \{p\['quantidade_estoque'\]\}</p>
</div>
\"\"\"
                        st\.markdown\(html_content, unsafe_allow_html=True\)
                        
                        # Formulario de adição \(Qtd manual\)
                        qtd = st\.number_input\(f"Qtd \(\{p\['unidade_medida'\]\}\)", min_value=0\.01, value=1\.00, step=1\.0 if p\['unidade_medida'\]=='UN' else 0\.1, key=f"qtd_\{p\['id'\]\}"\)
                        
                        # Bloqueio de Estoque
                        is_out_of_stock = p\['quantidade_estoque'\] <= 0
                        
                        if is_out_of_stock:
                            st\.error\("ESGOTADO"\)
                        else:
                            if st\.button\("Adicionar", key=f"btn_add_\{p\['id'\]\}", use_container_width=True, type="primary"\):
                                if qtd > p\['quantidade_estoque'\] and p\['categoria'\] != 'Horta \(Ilimitado\)':
                                    st\.warning\("Estoque insuficiente!"\)
                                else:
                                    st\.session_state\.carrinho\.append\(\{
                                        "produto_id": p\['id'\],
                                        "nome": p\['nome'\],
                                        "quantidade": float\(qtd\),
                                        "preco_unitario": float\(p\['preco_venda'\]\),
                                        "subtotal": float\(qtd\) \* float\(p\['preco_venda'\]\),
                                        "custo": float\(qtd\) \* float\(p\['preco_custo'\]\),
                                        "unidade_medida": p\['unidade_medida'\]
                                    \}\)
                                    st\.rerun\(\)"""

new_grid = """                        # Container de tamanho fixo com borda para agrupar TUDO (Native Streamlit)
                        with st.container(height=390, border=True):
                            # Imagem com altura controlada e centralizada
                            if p.get("imagem_url"):
                                st.markdown(f'<div style="display: flex; justify-content: center; height: 120px; align-items: center; margin-bottom: 10px;"><img src="{p["imagem_url"]}" style="max-width: 100%; max-height: 120px; object-fit: contain; border-radius: 5px;"></div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="height: 130px;"></div>', unsafe_allow_html=True)
                                
                            # Textos nativos do Streamlit (adaptam automaticamente para Claro/Escuro sem sumir)
                            st.markdown(f"#### {p['nome']}")
                            st.markdown(f"**R$ {p['preco_venda']:.2f}** / {p['unidade_medida']}")
                            st.caption(f"Estoque: {p['quantidade_estoque']}")
                            
                            # Formulario de adição dentro do mesmo container
                            qtd = st.number_input("Quantidade", min_value=0.01, value=1.00, step=1.0 if p['unidade_medida']=='UN' else 0.1, key=f"qtd_{p['id']}", label_visibility="collapsed")
                            
                            is_out_of_stock = p['quantidade_estoque'] <= 0
                            if is_out_of_stock:
                                st.error("ESGOTADO")
                            else:
                                if st.button("Adicionar", key=f"btn_add_{p['id']}", use_container_width=True, type="primary"):
                                    if qtd > p['quantidade_estoque'] and p['categoria'] != 'Horta (Ilimitado)':
                                        st.warning("Estoque insuficiente!")
                                    else:
                                        st.session_state.carrinho.append({
                                            "produto_id": p['id'],
                                            "nome": p['nome'],
                                            "quantidade": float(qtd),
                                            "preco_unitario": float(p['preco_venda']),
                                            "subtotal": float(qtd) * float(p['preco_venda']),
                                            "custo": float(qtd) * float(p['preco_custo']),
                                            "unidade_medida": p['unidade_medida']
                                        })
                                        st.rerun()"""

content = re.sub(old_grid, new_grid, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Grid consertado!")
