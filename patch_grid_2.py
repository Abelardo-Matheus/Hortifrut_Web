import sys
import re

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_grid = r"""        cols_per_row = 3
        for i in range\(0, len\(prods_filtrados\), cols_per_row\):
            cols = st\.columns\(cols_per_row\)
            for j in range\(cols_per_row\):
                if i \+ j < len\(prods_filtrados\):
                    p = prods_filtrados\[i\+j\]
                    with cols\[j\]:
                        # Container de tamanho fixo com borda para agrupar TUDO \(Native Streamlit\)
                        with st\.container\(height=390, border=True\):
                            # Imagem com altura controlada e centralizada
                            if p\.get\("imagem_url"\):
                                st\.markdown\(f'<div style="display: flex; justify-content: center; height: 120px; align-items: center; margin-bottom: 10px;"><img src="\{p\["imagem_url"\]\}" style="max-width: 100%; max-height: 120px; object-fit: contain; border-radius: 5px;"></div>', unsafe_allow_html=True\)
                            else:
                                st\.markdown\('<div style="height: 130px;"></div>', unsafe_allow_html=True\)
                                
                            # Textos nativos do Streamlit \(adaptam automaticamente para Claro/Escuro sem sumir\)
                            st\.markdown\(f"#### \{p\['nome'\]\}"\)
                            st\.markdown\(f"\*\*R\$ \{p\['preco_venda'\]:\.2f\}\*\* / \{p\['unidade_medida'\]\}"\)
                            st\.caption\(f"Estoque: \{p\['quantidade_estoque'\]\}"\)"""

new_grid = """        cols_per_row = 5
        for i in range(0, len(prods_filtrados), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(prods_filtrados):
                    p = prods_filtrados[i+j]
                    with cols[j]:
                        # Container de tamanho fixo com borda para agrupar TUDO (Native Streamlit)
                        with st.container(height=360, border=True):
                            # Imagem com altura controlada e centralizada
                            if p.get("imagem_url"):
                                st.markdown(f'<div style="display: flex; justify-content: center; height: 100px; align-items: center; margin-bottom: 5px;"><img src="{p["imagem_url"]}" style="max-width: 100%; max-height: 100px; object-fit: contain; border-radius: 5px;"></div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="height: 105px;"></div>', unsafe_allow_html=True)
                                
                            # Textos nativos do Streamlit (adaptam automaticamente para Claro/Escuro sem sumir)
                            # Usa altura fixa de 45px e corta com "..." se passar de 2 linhas
                            st.markdown(f'<div style="height: 45px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-weight: bold; font-size: 15px; margin-bottom: 5px;">{p["nome"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div style="font-size: 14px; margin-bottom: 5px;"><b>R$ {p["preco_venda"]:.2f}</b> / {p["unidade_medida"]}</div>', unsafe_allow_html=True)
                            st.caption(f"Estoque: {p['quantidade_estoque']}")"""

content = re.sub(old_grid, new_grid, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Grid consertado para 5 colunas com títulos travados!")
