import sys
import re

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Truncate admin PDV name
content = re.sub(
    r'(st\.markdown\(f\'<div style="height: 45px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-weight: bold; font-size: 15px; margin-bottom: 5px;">\{p\["nome"\]\}</div>\', unsafe_allow_html=True\))',
    r"nome_curto = p['nome'] if len(p['nome']) <= 20 else p['nome'][:18] + '...'\n                            st.markdown(f'<div style=\"height: 45px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-weight: bold; font-size: 15px; margin-bottom: 5px;\">{nome_curto}</div>', unsafe_allow_html=True)",
    content
)

# 2. Truncate public storefront name
content = re.sub(
    r'(st\.markdown\(f\'<div style="height: 48px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-weight: bold; font-size: 20px; margin-bottom: 5px; text-align: center;">\{p\["nome"\]\}</div>\', unsafe_allow_html=True\))',
    r"nome_curto = p['nome'] if len(p['nome']) <= 20 else p['nome'][:18] + '...'\n                        st.markdown(f'<div style=\"height: 48px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-weight: bold; font-size: 20px; margin-bottom: 5px; text-align: center;\">{nome_curto}</div>', unsafe_allow_html=True)",
    content
)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Nomes truncados!")
