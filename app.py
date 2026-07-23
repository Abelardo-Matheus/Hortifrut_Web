import streamlit as st
import datetime

# Configuração da Página Web - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Sistema Hortifruti Online",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import database as db

from streamlit_cookies_controller import CookieController
controller = CookieController()

# Verifica o cookie de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth = controller.get("auth_token")
    if auth == "hortifrut_admin_ok":
        st.session_state.logged_in = True
        # st.rerun()

@st.dialog("🔐 Acesso Restrito (Dono)")
def modal_login():
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", type="primary", use_container_width=True):
            if usuario == "joel" and senha == "531735":
                st.session_state.logged_in = True
                controller.set("auth_token", "hortifrut_admin_ok", max_age=31536000)
                import time
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

if "light_mode" not in st.session_state:
    st.session_state.light_mode = False

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.markdown('<div id="btn-anchor" style="position:absolute; width:0; height:0; visibility:hidden;"></div>', unsafe_allow_html=True)
    if st.session_state.logged_in:
        if st.button("🔓", help="Sair do Modo Admin"):
            st.session_state.logged_in = False
            controller.remove("auth_token")
            import time
            time.sleep(0.5)
            st.rerun()
    else:
        if st.button("🔐", help="Login Administrativo"):
            modal_login()

with col_btn2:
    tema_icon = "🌙" if st.session_state.light_mode else "☀️"
    if st.button(tema_icon, help="Mudar Tema"):
        st.session_state.light_mode = not st.session_state.light_mode
        st.rerun()

if st.session_state.light_mode:
    css_theme = '''
        .stApp { 
            filter: invert(1) hue-rotate(180deg); 
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
            background-color: #000000 !important;
        }
        img, iframe { 
            filter: invert(1) hue-rotate(180deg); 
            border-radius: 10px;
        }
        .video-container {
            filter: invert(1) hue-rotate(180deg); 
            background-color: #0e1117;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
            margin-top: -80px;
            margin-bottom: 5px;
            height: 350px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }
        .logo-video {
            mix-blend-mode: screen;
            width: 100vw;
            height: 70%;
            object-fit: cover;
        }
    '''
else:
    css_theme = '''
        img, iframe { 
            border-radius: 10px;
        }
        .video-container {
            background-color: #0e1117;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
            margin-top: -80px;
            margin-bottom: 5px;
            height: 350px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }
        .logo-video {
            mix-blend-mode: screen;
            width: 100vw;
            height: 70%;
            object-fit: cover;
        }
    '''

css_theme += '''
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }
        .block-container { padding-top: 0rem !important; margin-top: 0 !important; }
        
        /* Flutuar os botões sobre o vídeo e forçar lado a lado nos cantos */
        [data-testid="stHorizontalBlock"]:has(#btn-anchor) {
            position: fixed !important;
            top: 15px;
            left: 0px;
            right: 0px;
            width: 100vw !important;
            padding: 0 15px !important;
            box-sizing: border-box !important;
            z-index: 999999;
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            justify-content: space-between !important;
            align-items: center !important;
        }
        [data-testid="stHorizontalBlock"]:has(#btn-anchor) > [data-testid="column"] {
            width: auto !important;
            min-width: 0 !important;
            flex: 0 0 auto !important;
        }
        [data-testid="stHorizontalBlock"]:has(#btn-anchor) button {
            margin: 0 !important;
        }
        [data-testid="stElementContainer"]:has(#btn-anchor) {
            display: none !important;
        }
'''

st.markdown(f'<style>{css_theme}</style>', unsafe_allow_html=True)

def render_admin():
    
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.title("🍎 Gestão Hortifruti Online")
    
    # Carregar produtos do banco
    produtos = db.get_produtos()
    
    # Abas do Sistema
    tab_pdv, tab_estoque, tab_fiado, tab_retiradas, tab_relatorios, tab_solicitacoes = st.tabs(["🛒 Caixa", "📦 Estoque", "📝 Fiado", "🏠 Retiradas", "📊 Relatórios", "🔔 Solicitações"])
    
    # =========================================================
    # ABA 1: FRENTE DE CAIXA (PDV)
    # =========================================================
    with tab_pdv:
        col_produtos, col_carrinho = st.columns([2, 1])
        
        # Inicializa o carrinho na sessão
        if 'carrinho' not in st.session_state:
            st.session_state.carrinho = []
            
        with col_produtos:
            st.subheader("Produtos")
            busca = st.text_input("Buscar Produto (Nome ou Código de Barras):", key="busca_pdv")
            
            # Filtra produtos
            prods_filtrados = produtos
            if busca:
                prods_filtrados = [p for p in produtos if busca.lower() in p['nome'].lower() or (p['codigo_barras'] and busca in p['codigo_barras'])]
                
            # Exibição em Grid (usando colunas do Streamlit)
            cols_per_row = 5
            for i in range(0, len(prods_filtrados), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(prods_filtrados):
                        p = prods_filtrados[i+j]
                        with cols[j]:
                            # Container com borda (Altura automática que evita scroll, mas fica igual porque o conteúdo tem altura fixa)
                            with st.container(border=True):
                                # Imagem com altura controlada e centralizada
                                if p.get("imagem_url"):
                                    st.markdown(f'<div style="display: flex; justify-content: center; height: 100px; align-items: center; margin-bottom: 5px;"><img src="{p["imagem_url"]}" style="max-width: 100%; max-height: 100px; object-fit: contain; border-radius: 5px;"></div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div style="height: 105px;"></div>', unsafe_allow_html=True)
                                    
                                # Textos nativos do Streamlit (adaptam automaticamente para Claro/Escuro sem sumir)
                                # Usa altura fixa de 45px e corta com "..." se passar de 2 linhas
                                nome_curto = p['nome'] if len(p['nome']) <= 20 else p['nome'][:18] + '...'
                                st.markdown(f'<div style="height: 45px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-weight: bold; font-size: 15px; margin-bottom: 5px;">{nome_curto}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div style="font-size: 14px; margin-bottom: 5px;"><b>R$ {p["preco_venda"]:.2f}</b></div>', unsafe_allow_html=True)
                                st.caption(f"Estoque: {p['quantidade_estoque']}")
                                
                                # Formulario de adição dentro do mesmo container
                                qtd = st.number_input("Quantidade", min_value=0.01, value=1.00, step=1.0, key=f"qtd_{p['id']}", label_visibility="collapsed")
                                
                                is_out_of_stock = p['quantidade_estoque'] <= 0
                                if is_out_of_stock:
                                    st.button("Esgotado", key=f"btn_add_{p['id']}", use_container_width=True, disabled=True)
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
                                            st.rerun()
                                        
        with col_carrinho:
            st.subheader("Carrinho")
            st.markdown("---")
            
            if not st.session_state.carrinho:
                st.info("Carrinho vazio.")
            else:
                total = 0.0
                custo_total = 0.0
                for idx, item in enumerate(st.session_state.carrinho):
                    total += item['subtotal']
                    custo_total += item['custo']
                    
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{item['quantidade']} {item['unidade_medida']}** x {item['nome']}<br>R$ {item['subtotal']:.2f}", unsafe_allow_html=True)
                    with c2:
                        if st.button("X", key=f"del_item_{idx}", help="Remover"):
                            st.session_state.carrinho.pop(idx)
                            st.rerun()
                            
                st.markdown("---")
                st.markdown(f"<h3 style='color: #27ae60; text-align: right;'>Total: R$ {total:.2f}</h3>", unsafe_allow_html=True)
                
                # Finalizar Compra
                forma_pag = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito"])
                valor_pago = st.number_input("Valor Recebido (Para Troco)", min_value=0.0, value=float(total), step=1.0)
                
                if valor_pago > total:
                    st.success(f"Troco: R$ {valor_pago - total:.2f}")
                    
                if st.button("FINALIZAR VENDA", type="primary", use_container_width=True):
                    lucro = total - custo_total
                    sucesso = db.registrar_venda(total, lucro, forma_pag, st.session_state.carrinho)
                    if sucesso:
                        st.success("Venda registrada com sucesso!")
                        st.session_state.carrinho = [] # Limpa carrinho
                        st.balloons()
                    else:
                        st.error("Erro ao registrar a venda.")
    
    # =========================================================
    # ABA 2: GESTÃO DE ESTOQUE
    # =========================================================
    with tab_estoque:
        st.header("📦 Gestão de Produtos e Estoque")
        
        with st.expander("➕ CADASTRAR NOVO PRODUTO", expanded=False):
            with st.form("form_novo_produto"):
                c1, c2, c3 = st.columns(3)
                nome = c1.text_input("Nome do Produto *")
                codigo = c2.text_input("Código de Barras")
                categoria = c3.selectbox("Categoria", ["Frutas", "Legumes", "Verduras", "Horta (Ilimitado)", "Mercearia", "Outros"])
                
                c4, c5, c6, c7 = st.columns(4)
                custo = c4.number_input("Preço de Custo (R$)", min_value=0.0, step=0.1)
                venda = c5.number_input("Preço de Venda (R$) *", min_value=0.0, step=0.1)
                estoque = c6.number_input("Estoque Inicial", min_value=0.0, step=1.0)
                unidade = c7.text_input("Data de Compra", placeholder="Ex: 02/06/2026")
                
                imagem_upload = st.file_uploader("Foto do Produto (Opcional)", type=["png", "jpg", "jpeg"])
                
                submit = st.form_submit_button("Salvar Produto", type="primary")
                if submit:
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
                        st.error("Preencha os campos obrigatórios (Nome e Preço de Venda).")
                        
        st.markdown("### 📋 Tabela de Produtos (Edite diretamente na tabela)")
        
        busca_estoque = st.text_input("🔍 Buscar Produto no Estoque", placeholder="Digite o nome ou código do produto...")
        
        prods_f = produtos
        if busca_estoque:
            prods_f = [p for p in produtos if busca_estoque.lower() in p['nome'].lower() or (p['codigo_barras'] and busca_estoque in p['codigo_barras'])]
            
        if prods_f:
            import pandas as pd
            df_prods = pd.DataFrame([{
                '_ID': p['id'],
                'Nome': p['nome'],
                'Código': p.get('codigo_barras', ''),
                'Categoria': p['categoria'],
                'Estoque': float(p['quantidade_estoque']),
                'Data Compra': p.get('data_compra', ''),
                'Custo': float(p['preco_custo']),
                'Venda': float(p['preco_venda'])
            } for p in prods_f])
            
            edited_df = st.data_editor(
                df_prods,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                column_config={
                    "_ID": None,
                    "Categoria": st.column_config.SelectboxColumn("Categoria", options=["Frutas", "Legumes", "Verduras", "Horta (Ilimitado)", "Mercearia", "Outros"]),
                    "Custo": st.column_config.NumberColumn("Custo (R$)", min_value=0.0, step=0.1, format="%.2f"),
                    "Venda": st.column_config.NumberColumn("Venda (R$)", min_value=0.0, step=0.1, format="%.2f"),
                    "Estoque": st.column_config.NumberColumn("Estoque", min_value=0.0, step=1.0)
                }
            )
            
            if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                with st.spinner("Salvando..."):
                    sucesso = True
                    
                    # 1. Checar adições e edições
                    for _, row in edited_df.iterrows():
                        prod_id = row['_ID']
                        if pd.isna(prod_id) or prod_id == "": # Produto novo adicionado na tabela
                            res = db.adicionar_produto(row['Nome'], row['Código'], row['Categoria'], row['Custo'], row['Venda'], row['Estoque'], row['Data Compra'])
                            if not res: sucesso = False
                        else:
                            # Buscar original
                            orig = df_prods[df_prods['_ID'] == prod_id].iloc[0]
                            if not row.equals(orig):
                                res = db.atualizar_produto(prod_id, row['Nome'], row['Código'], row['Categoria'], row['Custo'], row['Venda'], row['Estoque'], row['Data Compra'])
                                if not res: sucesso = False
                                
                    # 2. Checar exclusões
                    edited_ids = edited_df['_ID'].dropna().tolist()
                    for _, orig_row in df_prods.iterrows():
                        if orig_row['_ID'] not in edited_ids:
                            res = db.excluir_produto(orig_row['_ID'])
                            if not res: sucesso = False
                            
                    if sucesso:
                        st.success("Tudo salvo com sucesso!")
                        import time
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Ocorreu um erro ao salvar algumas alterações.")
        else:
            if busca_estoque:
                st.warning("Nenhum produto encontrado com essa busca.")
            else:
                st.info("Nenhum produto cadastrado no banco de dados.")
    
    # =========================================================
    # ABA 3: FIADO (ANOTADO)
    # =========================================================
    with tab_fiado:
        st.header("📝 Controle de Fiados e Anotados")
        
        col_cli_list, col_cli_detail = st.columns([1, 2])
        
        clientes = db.get_clientes()
        
        with col_cli_list:
            st.subheader("Clientes")
            with st.expander("➕ Novo Cliente", expanded=False):
                with st.form("form_novo_cliente"):
                    nome_cli = st.text_input("Nome do Cliente *")
                    tel_cli = st.text_input("Telefone (Opcional)")
                    if st.form_submit_button("Salvar", type="primary"):
                        if nome_cli:
                            if db.add_cliente(nome_cli, tel_cli):
                                st.success("Cliente salvo!")
                                st.rerun()
                        else:
                            st.error("Nome é obrigatório.")
                            
            if clientes:
                cli_nomes = [c['nome'] for c in clientes]
                cli_selecionado_nome = st.selectbox("Selecione um Cliente", cli_nomes)
                cli_selecionado = next(c for c in clientes if c['nome'] == cli_selecionado_nome)
            else:
                st.info("Nenhum cliente cadastrado.")
                cli_selecionado = None
                
        with col_cli_detail:
            if cli_selecionado:
                st.subheader(f"Conta de: {cli_selecionado['nome']}")
                if cli_selecionado['telefone']:
                    st.caption(f"📞 {cli_selecionado['telefone']}")
                    
                compras = db.get_compras_anotadas(cli_selecionado['id'])
                
                if compras:
                    total_devendo = sum(c['quantidade'] * c['preco_unitario'] for c in compras)
                    st.error(f"Dívida Total: R$ {total_devendo:.2f}")
                    
                    dividas_view = []
                    for c in compras:
                        try:
                            from datetime import timezone, timedelta
                            import datetime as dt_lib
                            tz_br = timezone(timedelta(hours=-3))
                            dt_str = c['data_hora'].split('.')[0].replace('Z', '+00:00')
                            dt_obj = dt_lib.datetime.fromisoformat(dt_str).astimezone(tz_br)
                            data_fmt = dt_obj.strftime('%d/%m %H:%M')
                        except:
                            data_fmt = c['data_hora']
                            
                        nome_prod = c['produtos']['nome'] if c.get('produtos') else 'Produto Excluído'
                        un_medida = c['produtos'].get('data_compra', '') if c.get('produtos') else ''
                        
                        dividas_view.append({
                            "ID": c['id'],
                            "Data": data_fmt,
                            "Produto": nome_prod,
                            "Qtd": f"{c['quantidade']} {un_medida}",
                            "Preço Un.": f"R$ {c['preco_unitario']:.2f}",
                            "Subtotal": f"R$ {c['quantidade'] * c['preco_unitario']:.2f}"
                        })
                        
                    st.dataframe(dividas_view, use_container_width=True, hide_index=True)
                    
                    if st.button("Pagar Conta (Quitar tudo)", type="primary"):
                        ids = [c['id'] for c in compras]
                        if db.pagar_compras(ids, total_devendo, 0):
                            st.success("Conta paga com sucesso!")
                            st.balloons()
                            st.rerun()
                else:
                    st.success("Este cliente não tem dívidas em aberto!")
                    
                st.markdown("---")
                st.markdown("#### Anotar Nova Compra")
                busca_f = st.text_input("Buscar Produto:", key="busca_fiado")
                prods_f = produtos
                if busca_f:
                    prods_f = [p for p in produtos if busca_f.lower() in p['nome'].lower()]
                    
                if prods_f:
                    p_f_nome = st.selectbox("Produto", [p['nome'] for p in prods_f], key="sel_prod_fiado")
                    p_f = next(p for p in prods_f if p['nome'] == p_f_nome)
                    
                    c1, c2 = st.columns(2)
                    qtd_f = c1.number_input("Quantidade", min_value=0.01, value=1.00, key="qtd_fiado")
                    preco_f = c2.number_input("Preço Unitário", value=float(p_f['preco_venda']), key="preco_fiado")
                    
                    if st.button("Anotar na Conta"):
                        item = {
                            "produto_id": p_f['id'],
                            "quantidade": qtd_f,
                            "preco_unitario": preco_f,
                            "is_estoque_controlado": p_f['categoria'] != 'Horta (Ilimitado)'
                        }
                        if db.anotar_compra(cli_selecionado['id'], [item]):
                            st.success("Compra anotada com sucesso!")
                            st.rerun()
    
    # =========================================================
    # ABA 4: RETIRADAS PARA CASA
    # =========================================================
    with tab_retiradas:
        st.header("🏠 Retiradas para Consumo Próprio")
        
        col_ret_add, col_ret_hist = st.columns([1, 1])
        
        with col_ret_add:
            st.subheader("Nova Retirada")
            st.info("Produtos retirados para casa são descontados do estoque (sem gerar lucro no caixa).")
            
            busca_r = st.text_input("Buscar Produto:", key="busca_ret")
            prods_r = produtos
            if busca_r:
                prods_r = [p for p in produtos if busca_r.lower() in p['nome'].lower()]
                
            if prods_r:
                p_r_nome = st.selectbox("Produto", [p['nome'] for p in prods_r], key="sel_prod_ret")
                p_r = next(p for p in prods_r if p['nome'] == p_r_nome)
                
                qtd_r = st.number_input("Quantidade Retirada", min_value=0.01, value=1.00, key="qtd_ret")
                
                st.markdown(f"**Custo Estimado da Retirada:** R$ {qtd_r * p_r['preco_custo']:.2f}")
                
                if st.button("Registrar Retirada", type="primary"):
                    item_r = {
                        "produto_id": p_r['id'],
                        "quantidade": qtd_r,
                        "preco_custo": p_r['preco_custo'],
                        "is_estoque_controlado": p_r['categoria'] != 'Horta (Ilimitado)'
                    }
                    if db.registrar_retirada_casa([item_r]):
                        st.success("Retirada registrada!")
                        st.rerun()
                        
        with col_ret_hist:
            from datetime import timezone, timedelta
            import datetime as dt_lib
            tz_br = timezone(timedelta(hours=-3))
            hoje = dt_lib.datetime.now(tz_br)
            
            st.subheader(f"Retiradas em {hoje.strftime('%m/%Y')}")
            retiradas = db.get_retiradas_mes(hoje.year, hoje.month)
            
            if retiradas:
                ret_view = []
                custo_total_ret = 0.0
                for r in retiradas:
                    try:
                        dt_str = r['data_hora'].split('.')[0].replace('Z', '+00:00')
                        dt_obj = dt_lib.datetime.fromisoformat(dt_str).astimezone(tz_br)
                        data_fmt = dt_obj.strftime('%d/%m %H:%M')
                    except:
                        data_fmt = r['data_hora']
                        
                    nome_prod = r['produtos']['nome'] if r.get('produtos') else 'Produto Excluído'
                    un_medida = r['produtos'].get('data_compra', '') if r.get('produtos') else ''
                    sub_custo = r['quantidade'] * r['custo_unitario']
                    custo_total_ret += sub_custo
                    
                    ret_view.append({
                        "Data": data_fmt,
                        "Produto": nome_prod,
                        "Qtd": f"{r['quantidade']} {un_medida}",
                        "Custo (R$)": f"R$ {sub_custo:.2f}"
                    })
                    
                st.error(f"Custo Total Retirado no Mês: R$ {custo_total_ret:.2f}")
                st.dataframe(ret_view, use_container_width=True, hide_index=True)
            else:
                st.success("Nenhuma retirada registrada neste mês.")
    
    # =========================================================
    # ABA 5: RELATÓRIOS
    # =========================================================
    with tab_relatorios:
        st.header("📊 Resumo de Vendas")
        
        vendas = db.get_vendas()
        
        if vendas:
            from datetime import timezone, timedelta
            
            tz_br = timezone(timedelta(hours=-3))
            hoje = datetime.datetime.now(tz_br).date()
            
            vendas_hoje = []
            hist_view = []
            
            total_hoje = 0.0
            lucro_hoje = 0.0
            
            for v in vendas:
                try:
                    dt_str = v['data_venda'].split('.')[0].replace('Z', '+00:00')
                    dt_obj = datetime.datetime.fromisoformat(dt_str).astimezone(tz_br)
                except Exception:
                    dt_obj = datetime.datetime.now(tz_br)
                    
                if dt_obj.date() == hoje:
                    vendas_hoje.append(v)
                    total_hoje += v['valor_total']
                    lucro_hoje += v['lucro_total']
                    
                hist_view.append({
                    'Data/Hora': dt_obj.strftime('%d/%m/%Y %H:%M:%S'),
                    'Valor Total (R$)': v['valor_total'],
                    'Forma Pagamento': v['forma_pagamento']
                })
                
            qtd_vendas_hoje = len(vendas_hoje)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Vendas Hoje (R$)", f"R$ {total_hoje:.2f}")
            c2.metric("Lucro Estimado Hoje", f"R$ {lucro_hoje:.2f}")
            c3.metric("Qtd de Vendas Hoje", f"{qtd_vendas_hoje}")
            
            st.markdown("### Histórico Recente (Últimas 100 vendas)")
            st.dataframe(hist_view, use_container_width=True, hide_index=True)
        else:
            st.info("Ainda não há histórico de vendas registrado no banco.")


    # =========================================================
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
# ==========================================
# ROTEAMENTO PRINCIPAL (PÚBLICO VS ADMIN)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    render_admin()
else:
    # ==========================================
    # VITRINE PÚBLICA (CLIENTES)
    # ==========================================
    
    video_html = """
    <div class="video-container">
        <video class="logo-video" src="https://bslfvnhtirrykxedgpkw.supabase.co/storage/v1/object/public/produtos/logo_nova.mp4" autoplay muted playsinline></video>
    </div>
    """
    st.markdown(video_html, unsafe_allow_html=True)
    
    
    produtos = db.get_produtos()
    
    # CSS para as imagens da vitrine
    st.markdown('''
    <style>
    /* Expandir a tela mantendo-a centralizada e sem encostar no scroll */
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
    }
    .vitrine-img-container {
        display: flex; justify-content: center; height: 120px; align-items: center; margin-bottom: 10px;
    }
    .sem-imagem {
        color: #ccc;
    }
    .vitrine-nome {
        height: 48px; overflow: hidden; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 18px; margin-bottom: 5px; text-align: center;
    }
    .vitrine-preco {
        display: flex; justify-content: center; align-items: center; font-size: 20px; margin-bottom: 5px; color: #27ae60; text-align: center;
    }
    .vitrine-preco span {
        font-size:14px; color:#7f8c8d; margin-left: 5px;
    }
    .vitrine-estoque {
        text-align: center; font-weight: bold; font-size: 14px;
    }
    .disp { color: #2980b9; }
    .esgot { color: #e74c3c; }
    
    @media (max-width: 768px) {
        .vitrine-grid {
            /* Força 3 colunas em telas pequenas, independente de quão pequenas sejam */
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 5px;
        }
        .vitrine-card {
            padding: 0.3rem !important;
            border-width: 2px !important;
        }
        .blend-img { max-height: 80px; }
        .vitrine-img-container { height: 80px; margin-bottom: 5px; }
        .vitrine-nome { font-size: 13px !important; height: 34px !important; line-height: 1.2; }
        .vitrine-preco { font-size: 14px !important; }
        .vitrine-preco span { font-size: 11px !important; margin-left: 2px; }
        .vitrine-estoque { font-size: 11px !important; }
    }
    </style>
    ''', unsafe_allow_html=True)
    
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
        prods_vitrine = [p for p in produtos if busca.lower() in p['nome'].lower()]
            
    st.write("")
    st.markdown("---")
    
    html_cards = []
    for p in prods_vitrine:
        # Imagem
        if p.get("imagem_url"):
            img_html = f'<div class="vitrine-img-container"><img class="blend-img" src="{p["imagem_url"]}"></div>'
        else:
            img_html = '<div class="vitrine-img-container sem-imagem">Sem Imagem</div>'
            
        # Nome do Produto
        nome_curto = p['nome'] if len(p['nome']) <= 20 else p['nome'][:18] + '...'
        nome_html = f'<div class="vitrine-nome">{nome_curto}</div>'
        
        # Preço
        preco_html = f'<div class="vitrine-preco"><b>R$ {p["preco_venda"]:.2f}</b></div>'
        
        # Estoque
        if p['quantidade_estoque'] > 0 or p['categoria'] == 'Horta (Ilimitado)':
            estoque_html = "<div class='vitrine-estoque disp'>✓ Disponível</div>"
        else:
            estoque_html = "<div class='vitrine-estoque esgot'>✗ Esgotado</div>"
            
        card_html = f"""<div class="vitrine-card">
{img_html}
{nome_html}
{preco_html}
{estoque_html}
</div>"""
        html_cards.append(card_html)
        
    grid_html = f"""<div class="vitrine-grid">
{"".join(html_cards)}
</div>"""
    st.markdown(grid_html, unsafe_allow_html=True)

    st.markdown("---")
