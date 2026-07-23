import sys
import re

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update tabs to include solicitacoes
content = content.replace(
    'tab_pdv, tab_estoque, tab_fiado, tab_retiradas, tab_relatorios = st.tabs(["🛒 Caixa", "📦 Estoque", "📝 Fiado", "🏠 Retiradas", "📊 Relatórios"])',
    'tab_pdv, tab_estoque, tab_fiado, tab_retiradas, tab_relatorios, tab_solicitacoes = st.tabs(["🛒 Caixa", "📦 Estoque", "📝 Fiado", "🏠 Retiradas", "📊 Relatórios", "🔔 Solicitações"])'
)

# 2. Add File Uploader in add product form
old_form = '''                c4, c5, c6, c7 = st.columns(4)
                custo = c4.number_input("Preço de Custo (R$)", min_value=0.0, step=0.1)
                venda = c5.number_input("Preço de Venda (R$) *", min_value=0.0, step=0.1)
                estoque = c6.number_input("Estoque Inicial", min_value=0.0, step=1.0)
                unidade = c7.selectbox("Vendido por", ["UN", "KG"])
                
                submit = st.form_submit_button("Salvar Produto", type="primary")'''

new_form = '''                c4, c5, c6, c7 = st.columns(4)
                custo = c4.number_input("Preço de Custo (R$)", min_value=0.0, step=0.1)
                venda = c5.number_input("Preço de Venda (R$) *", min_value=0.0, step=0.1)
                estoque = c6.number_input("Estoque Inicial", min_value=0.0, step=1.0)
                unidade = c7.selectbox("Vendido por", ["UN", "KG"])
                
                imagem_upload = st.file_uploader("Foto do Produto (Opcional)", type=["png", "jpg", "jpeg"])
                
                submit = st.form_submit_button("Salvar Produto", type="primary")'''

content = content.replace(old_form, new_form)

# 3. Add background processing logic for image
old_submit = '''                if submit:
                    if nome and venda >= 0:
                        sucesso = db.adicionar_produto(nome, codigo, categoria, custo, venda, estoque, unidade)
                        if sucesso:
                            st.success("Produto cadastrado!")
                            st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios (Nome e Preço de Venda).")'''

new_submit = '''                if submit:
                    if nome and venda >= 0:
                        sucesso = db.adicionar_produto(nome, codigo, categoria, custo, venda, estoque, unidade)
                        if sucesso:
                            if imagem_upload:
                                import threading
                                def process_and_upload(img_bytes, filename, prod_nome, prod_cod):
                                    try:
                                        import io
                                        import urllib.parse
                                        from PIL import Image
                                        from rembg import remove
                                        from database import supabase
                                        
                                        # Salva original primeiro
                                        safe_name = urllib.parse.quote(filename)
                                        supabase.storage.from_("produtos").upload(
                                            path=safe_name,
                                            file=img_bytes,
                                            file_options={"content-type": "image/jpeg"}
                                        )
                                        url_original = supabase.storage.from_("produtos").get_public_url(safe_name)
                                        
                                        # Atualiza banco com original
                                        if prod_cod:
                                            supabase.table("produtos").update({"imagem_url": url_original}).eq("codigo_barras", prod_cod).execute()
                                        else:
                                            supabase.table("produtos").update({"imagem_url": url_original}).eq("nome", prod_nome).execute()
                                        
                                        # Processa IA em background
                                        img = Image.open(io.BytesIO(img_bytes))
                                        img_nobg = remove(img)
                                        out_bytes = io.BytesIO()
                                        img_nobg.save(out_bytes, format='PNG')
                                        out_bytes.seek(0)
                                        
                                        new_name = safe_name.split('.')[0] + "_nobg.png"
                                        try:
                                            supabase.storage.from_("produtos").remove([new_name])
                                        except: pass
                                        
                                        supabase.storage.from_("produtos").upload(
                                            path=new_name,
                                            file=out_bytes.read(),
                                            file_options={"content-type": "image/png"}
                                        )
                                        url_nobg = supabase.storage.from_("produtos").get_public_url(new_name)
                                        
                                        # Atualiza banco com nova imagem sem fundo
                                        if prod_cod:
                                            supabase.table("produtos").update({"imagem_url": url_nobg}).eq("codigo_barras", prod_cod).execute()
                                        else:
                                            supabase.table("produtos").update({"imagem_url": url_nobg}).eq("nome", prod_nome).execute()
                                            
                                    except Exception as e:
                                        print("Erro na IA background:", e)
                                
                                img_bytes = imagem_upload.read()
                                t = threading.Thread(target=process_and_upload, args=(img_bytes, imagem_upload.name, nome, codigo))
                                t.start()
                                
                            st.success("Produto cadastrado! (Se enviou foto, ela será processada em 1 min)")
                            st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios (Nome e Preço de Venda).")'''

content = content.replace(old_submit, new_submit)

# 4. Add Solicitacoes Tab implementation
admin_tabs_insert_pos = content.find('def render_admin():')
if admin_tabs_insert_pos != -1:
    admin_tab_content = '''    # =========================================================
    # ABA 6: SOLICITAÇÕES
    # =========================================================
    with tab_solicitacoes:
        st.header("🔔 Solicitações de Clientes")
        
        reqs = db.get_solicitacoes()
        if not reqs:
            st.info("Nenhuma solicitação no momento.")
        else:
            for r in reqs:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"**Produto:** {r['nome_produto']}")
                        st.markdown(f"**Cliente:** {r['nome_cliente']} (Tel: {r['telefone']})")
                    with c2:
                        from datetime import timezone, timedelta
                        import datetime as dt_lib
                        try:
                            tz_br = timezone(timedelta(hours=-3))
                            dt_str = r['data_solicitacao'].split('.')[0].replace('Z', '+00:00')
                            dt_obj = dt_lib.datetime.fromisoformat(dt_str).astimezone(tz_br)
                            data_fmt = dt_obj.strftime('%d/%m/%Y %H:%M')
                        except:
                            data_fmt = r['data_solicitacao']
                        st.caption(f"Data: {data_fmt}")
                        st.markdown(f"**Status:** {r['status']}")
                    with c3:
                        if r['status'] == 'Pendente':
                            if st.button("Atendido", key=f"req_ok_{r['id']}", type="primary"):
                                db.update_solicitacao_status(r['id'], 'Atendido')
                                st.rerun()
                            if st.button("Recusado", key=f"req_no_{r['id']}"):
                                db.update_solicitacao_status(r['id'], 'Recusado')
                                st.rerun()
    
    # ROTEAMENTO
'''
    # Replace '# ROTEAMENTO PRINCIPAL (PÚBLICO VS ADMIN)' to inject before it.
    # Wait, the end of render_admin() is just before ROTEAMENTO PRINCIPAL.
    content = content.replace('# ==========================================\n# ROTEAMENTO PRINCIPAL (PÚBLICO VS ADMIN)', admin_tab_content + '# ==========================================\n# ROTEAMENTO PRINCIPAL (PÚBLICO VS ADMIN)')

# 5. Add "Não achou seu produto?" button in public storefront
public_btn = '''    st.write("") # espaco
    
    # Dialog para solicitar produto
    @st.dialog("Qual produto você não encontrou?")
    def modal_solicitacao():
        st.write("Deixe sua sugestão e nós providenciaremos para você!")
        s_prod = st.text_input("Produto que você quer *")
        s_nome = st.text_input("Seu Nome *")
        s_tel = st.text_input("Seu Telefone (Opcional)")
        if st.button("Enviar Sugestão", type="primary", use_container_width=True):
            if s_prod and s_nome:
                db.add_solicitacao(s_prod, s_nome, s_tel)
                st.success("Sugestão enviada com sucesso! Muito obrigado.")
            else:
                st.error("Preencha o Nome do Produto e o Seu Nome.")
    
    c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
    with c_btn2:
        if st.button("🤔 Não achou seu produto? Clique aqui!", use_container_width=True):
            modal_solicitacao()
            
    st.write("")
    st.markdown("---")
    
    cols_per_row = 4'''

content = content.replace('''    st.write("") # espaco
    
    cols_per_row = 4''', public_btn)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch concluído!")
