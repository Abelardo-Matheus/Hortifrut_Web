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
controller = CookieController(key='cookies')

# Verifica o cookie de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

if not st.session_state.logged_in:
    auth = controller.get("auth_token")
    if auth == "hortifrut_admin_ok":
        st.session_state.logged_in = True

@st.dialog("🔐 Acesso Restrito (Dono)")
def modal_login():
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", type="primary", use_container_width=True):
            if db.verificar_login(usuario, senha):
                st.session_state.logged_in = True
                controller.set("auth_token", "hortifrut_admin_ok", max_age=31536000)
                import time
                time.sleep(0.5)
                st.switch_page(pg_admin)
            else:
                st.error("Usuário ou senha incorretos")

if "light_mode" not in st.session_state:
    st.session_state.light_mode = False

def load_css(file_name):
    import os
    path = os.path.join(os.path.dirname(__file__), "static", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_html(file_name):
    import os
    path = os.path.join(os.path.dirname(__file__), "static", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

css_theme = load_css("light_theme.css") if st.session_state.light_mode else load_css("dark_theme.css")
css_theme += load_css("common.css")

@st.fragment
def render_pdv(produtos):
    """
    PDV isolado como fragment — só este bloco re-executa ao adicionar/remover itens.
    Grid de produtos em HTML puro (1 st.markdown call) = zero widgets por produto.
    """
    # Inicializa sessão
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []
    if '_pdv_msg' not in st.session_state:
        st.session_state._pdv_msg = None

    # Definição do callback de adicionar ao carrinho
    def add_to_cart_callback(p):
        qtd_input = st.session_state.get(f"pdv_qtd_{p['id']}", 1.0)
        
        if p.get('unidade_medida', '').lower() == 'kg':
            qtd_add = float(qtd_input) / float(p['preco_venda'])
        else:
            qtd_add = float(qtd_input)
            
        if qtd_add > p['quantidade_estoque'] and p.get('categoria') != 'Horta (Ilimitado)' and not p.get('producao_propria'):
            st.session_state._pdv_msg = ("warning", f"Estoque insuficiente de {p['nome']}!")
            return
            
        existente = next((i for i in st.session_state.carrinho if i['produto_id'] == p['id']), None)
        if existente:
            existente['quantidade'] += float(qtd_add)
            existente['subtotal'] = existente['quantidade'] * existente['preco_unitario']
            existente['custo'] = existente['quantidade'] * float(p['preco_custo'])
        else:
            st.session_state.carrinho.append({
                "produto_id": p['id'],
                "nome": p['nome'],
                "quantidade": float(qtd_add),
                "preco_unitario": float(p['preco_venda']),
                "subtotal": float(qtd_add) * float(p['preco_venda']),
                "custo": float(qtd_add) * float(p.get('preco_custo', 0)),
                "unidade_medida": p.get('unidade_medida', 'Un'),
                "is_estoque_controlado": p.get('categoria') != 'Horta (Ilimitado)' and not p.get('producao_propria'),
                "categoria": p.get('categoria', ''),
            })
        st.session_state._pdv_msg = ("success", f"✅ {p['nome']} adicionado!")
        # Reseta o número no input de quantidade após adicionar deletando a chave
        if f"pdv_qtd_{p['id']}" in st.session_state:
            del st.session_state[f"pdv_qtd_{p['id']}"]

    col_produtos, col_carrinho = st.columns([3, 2])

    with col_produtos:
        st.subheader("🛒 Produtos")

        # ── Linha superior: Apenas Busca ─────────────
        import difflib
        busca = st.text_input("🔍 Buscar", key="busca_pdv_frag", placeholder="Pesquisa automática por nome ou código...")
        
        prods_filtrados = produtos
        if busca:
            busca_lower = busca.lower()
            def get_score(p):
                nome_lower = p['nome'].lower()
                cod = str(p.get('codigo_barras', '')).lower()
                # Match exato ou contido tem pontuação máxima (1.0)
                if busca_lower in nome_lower or busca_lower in cod:
                    return 1.0
                # Fuzzy match para achar digitando um pouco errado
                score_nome = difflib.SequenceMatcher(None, busca_lower, nome_lower).ratio()
                score_cod = difflib.SequenceMatcher(None, busca_lower, cod).ratio() if cod else 0
                return max(score_nome, score_cod)

            prods_avaliados = [(p, get_score(p)) for p in produtos]
            # Filtra por similaridade > 0.4 e ordena
            prods_filtrados = [p for p, score in sorted(prods_avaliados, key=lambda x: x[1], reverse=True) if score > 0.4]
        
        st.markdown("---")
        
        # ── Grid nativo do Streamlit ──────────
        if prods_filtrados:
            exibir = prods_filtrados
            
            cols_per_row = 4
            for i in range(0, len(exibir), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(exibir):
                        p = exibir[i+j]
                        with cols[j]:
                            with st.container(border=True):
                                # Imagem
                                if p.get("imagem_url"):
                                    st.markdown(f'<div style="display:flex;justify-content:center;height:80px;align-items:center;margin-bottom:5px;"><img src="{p["imagem_url"]}" style="max-width:100%;max-height:80px;object-fit:contain;border-radius:5px;"></div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div style="height:80px;display:flex;align-items:center;justify-content:center;opacity:0.4;font-size:12px;">Sem foto</div>', unsafe_allow_html=True)
                                
                                # Detalhes
                                nome_curto = p['nome'] if len(p['nome']) <= 22 else p['nome'][:20] + '…'
                                st.markdown(f'<div style="text-align:center;font-size:13px;font-weight:bold;margin-bottom:5px;line-height:1.2;height:32px;overflow:hidden;">{nome_curto}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div style="text-align:center;font-size:14px;color:#27ae60;font-weight:bold;margin-bottom:5px;">R$ {p["preco_venda"]:.2f}</div>', unsafe_allow_html=True)
                                
                                esgotado = p['quantidade_estoque'] <= 0 and p.get('categoria') != 'Horta (Ilimitado)' and not p.get('producao_propria')
                                if esgotado:
                                    st.markdown('<div style="text-align:center;color:#e74c3c;font-size:12px;font-weight:bold;margin-bottom:10px;">Esgotado</div>', unsafe_allow_html=True)
                                    st.button("Esgotado", key=f"pdv_btn_{p['id']}", disabled=True, use_container_width=True)
                                else:
                                    if p.get('producao_propria'):
                                        st.markdown('<div style="text-align:center;color:#27ae60;font-size:12px;font-weight:bold;margin-bottom:5px;">Estoque: Disponível</div>', unsafe_allow_html=True)
                                    else:
                                        st.markdown(f'<div style="text-align:center;color:#27ae60;font-size:12px;font-weight:bold;margin-bottom:5px;">Estoque: {p["quantidade_estoque"]}</div>', unsafe_allow_html=True)
                                    
                                    if p.get('unidade_medida', '').lower() == 'kg':
                                        st.markdown('<div style="font-size:11px;text-align:center;margin-bottom:-10px;margin-top:-5px;">Valor (R$)</div>', unsafe_allow_html=True)
                                        st.number_input("Valor R$", min_value=0.01, value=float(p['preco_venda']), step=0.50, label_visibility="collapsed", format="%.2f", key=f"pdv_qtd_{p['id']}")
                                    else:
                                        st.number_input("Qtd", min_value=0.01, value=1.0, step=1.0, label_visibility="collapsed", format="%.2f", key=f"pdv_qtd_{p['id']}")
                                    st.button("➕ Add", key=f"pdv_add_{p['id']}", type="primary", on_click=add_to_cart_callback, args=(p,), use_container_width=True)
        else:
            st.info("Nenhum produto encontrado com essa busca.")

    with col_carrinho:
        st.subheader("🧾 Carrinho")

        # Exibe mensagem de feedback sem rerun
        if st.session_state._pdv_msg:
            tipo, msg = st.session_state._pdv_msg
            if tipo == "success":
                st.success(msg)
            elif tipo == "warning":
                st.warning(msg)
            st.session_state._pdv_msg = None

        st.markdown("---")

        if not st.session_state.carrinho:
            st.info("Carrinho vazio.\nBusque e selecione um produto à esquerda.")
        else:
            total = 0.0
            custo_total = 0.0
            for idx, item in enumerate(st.session_state.carrinho):
                total += item['subtotal']
                custo_total += item['custo']
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(
                        f"**{item['nome']}**  \n"
                        f"`{item['quantidade']:.2f} {item['unidade_medida']}` × R$ {item['preco_unitario']:.2f} = **R$ {item['subtotal']:.2f}**"
                    )
                with c2:
                    if st.button("✕", key=f"del_{idx}", help="Remover item"):
                        st.session_state.carrinho.pop(idx)
                        # Fragment auto-reruns, sem st.rerun() global

            st.markdown("---")
            st.markdown(f"### 💰 Total: R$ {total:.2f}")

            forma_pag = st.selectbox("💳 Forma de Pagamento",
                ["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito"],
                key="forma_pag_pdv")
            valor_pago = st.number_input("Valor Recebido (Troco)", min_value=0.0,
                                          value=float(total), step=0.50, key="valor_pago_pdv")
            if valor_pago > total:
                st.success(f"💵 Troco: R$ {valor_pago - total:.2f}")

            if st.button("✅ FINALIZAR VENDA", type="primary", use_container_width=True, key="btn_finalizar"):
                lucro = total - custo_total
                # Pré-calcula novo_estoque no cliente (sem precisar buscar do banco)
                for item in st.session_state.carrinho:
                    for p in st.session_state.get('produtos_local', []):
                        if p['id'] == item['produto_id']:
                            item['novo_estoque'] = max(0.0, p['quantidade_estoque'] - item['quantidade'])
                            break

                sucesso = db.registrar_venda(total, lucro, forma_pag, st.session_state.carrinho)
                if sucesso:
                    # Atualiza cache local de estoque
                    for item in st.session_state.carrinho:
                        for p in st.session_state.get('produtos_local', []):
                            if p['id'] == item['produto_id']:
                                p['quantidade_estoque'] = item.get('novo_estoque', p['quantidade_estoque'])
                    st.session_state.carrinho = []
                    st.success("🎉 Venda registrada com sucesso!")
                    st.balloons()
                else:
                    st.error("Erro ao registrar a venda.")

def render_admin():
    
    st.markdown(f"<style>{css_theme}</style><div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.title("🍎 Gestão Hortifruti J&M")
    
    # Carregar produtos do banco
    if 'produtos_local' not in st.session_state:
        st.session_state.produtos_local = db.get_produtos()
    produtos = st.session_state.produtos_local
    
    # Abas do Sistema
    tab_pdv, tab_estoque, tab_fiado, tab_retiradas, tab_relatorios, tab_solicitacoes = st.tabs(["🛒 Caixa", "📦 Estoque", "📝 Fiado", "🏠 Retiradas", "📊 Relatórios", "🔔 Solicitações"])
    
    # =========================================================
    # ABA 1: FRENTE DE CAIXA (PDV) — Fragment isolado
    # =========================================================
    with tab_pdv:
        render_pdv(produtos)


    
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
                
                c4, c5, c6, c7, c8 = st.columns(5)
                custo = c4.number_input("Preço de Custo (R$)", min_value=0.0, step=0.1)
                venda = c5.number_input("Preço de Venda (R$) *", min_value=0.0, step=0.1)
                estoque = c6.number_input("Estoque Inicial", min_value=0.0, step=1.0)
                data_compra = c7.text_input("Data de Compra", placeholder="Ex: 02/06/2026")
                unidade_medida = c8.selectbox("Vendido por", ["Un", "Kg"])
                
                producao_propria = st.checkbox("🌱 Produção Própria (Filtro e exibição de estoque especial)")
                imagem_upload = st.file_uploader("Foto do Produto (Opcional)", type=["png", "jpg", "jpeg"])
                
                submit = st.form_submit_button("Salvar Produto", type="primary")
                if submit:
                    if nome and venda >= 0:
                        sucesso = db.adicionar_produto(nome, codigo, categoria, custo, venda, estoque, data_compra, unidade_medida, producao_propria)
                        if sucesso:
                            st.session_state.produtos_local = db.get_produtos()
                            if imagem_upload:
                                import threading
                                def process_and_upload(img_bytes, filename, prod_nome, prod_cod):
                                    try:
                                        import io
                                        import time
                                        import uuid
                                        from PIL import Image
                                        from rembg import remove
                                        from database import supabase
                                        
                                        # Salva original primeiro
                                        ext = filename.split('.')[-1] if '.' in filename else 'jpg'
                                        safe_name = f"img_{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
                                        
                                        supabase.storage.from_("produtos").upload(
                                            path=safe_name,
                                            file=img_bytes,
                                            file_options={"content-type": f"image/{ext}", "upsert": "true"}
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
                                            file_options={"content-type": "image/png", "upsert": "true"}
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
                        
        busca_estoque = st.text_input("🔍 Buscar Produto no Estoque", placeholder="Digite o nome ou código do produto...")
        
        prods_f = produtos
        if busca_estoque:
            prods_f = [p for p in produtos if busca_estoque.lower() in p['nome'].lower() or (p['codigo_barras'] and busca_estoque in p['codigo_barras'])]
            
        if prods_f:
            cols_per_row = 5
            for i in range(0, len(prods_f), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(prods_f):
                        p = prods_f[i+j]
                        with cols[j]:
                            with st.container(border=True):
                                # Imagem
                                if p.get("imagem_url"):
                                    st.markdown(f'<div style="display: flex; justify-content: center; height: 100px; align-items: center; margin-bottom: 5px;"><img src="{p["imagem_url"]}" style="max-width: 100%; max-height: 100px; object-fit: contain; border-radius: 5px;"></div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div style="height: 105px; display:flex; align-items:center; justify-content:center; border-radius:5px; opacity: 0.5;">Sem Foto</div>', unsafe_allow_html=True)
                                
                                st.markdown(f'<div style="min-height: 45px; font-weight: bold; font-size: 15px; margin-bottom: 5px; text-align: center;">{p["nome"]}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div style="font-size: 14px; margin-bottom: 5px; text-align: center;"><b>R$ {p["preco_venda"]:.2f}</b></div>', unsafe_allow_html=True)
                                
                                if p.get('producao_propria'):
                                    estoque_txt = "Disponível" if p["quantidade_estoque"] > 0 else "Não Disponível"
                                    st.markdown(f'<div style="font-size: 13px; opacity: 0.7; margin-bottom: 10px; text-align: center;">Estoque: {estoque_txt} (Prod. Própria)</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div style="font-size: 13px; opacity: 0.7; margin-bottom: 10px; text-align: center;">Estoque: {p["quantidade_estoque"]} {p.get("unidade_medida", "Un")}</div>', unsafe_allow_html=True)
                                
                                with st.popover("✏️ Editar", use_container_width=True):
                                    with st.form(f"form_edit_{p['id']}"):
                                        e_nome = st.text_input("Nome", value=p['nome'])
                                        e_cod = st.text_input("Código", value=p.get('codigo_barras', ''))
                                        
                                        cat_opts = ["Frutas", "Legumes", "Verduras", "Horta (Ilimitado)", "Mercearia", "Outros"]
                                        idx_cat = cat_opts.index(p['categoria']) if p['categoria'] in cat_opts else 5
                                        e_cat = st.selectbox("Categoria", cat_opts, index=idx_cat)
                                        
                                        e_medida = st.selectbox("Medida", ["Un", "Kg"], index=0 if p.get('unidade_medida', 'Un') == 'Un' else 1)
                                        
                                        colA, colB = st.columns(2)
                                        e_custo = colA.number_input("Custo", value=float(p['preco_custo']), step=0.1)
                                        e_venda = colB.number_input("Venda", value=float(p['preco_venda']), step=0.1)
                                        
                                        e_estoque = st.number_input("Estoque", value=float(p['quantidade_estoque']), step=1.0)
                                        e_prod_propria = st.checkbox("Produção Própria", value=p.get('producao_propria', False), key=f"pp_edit_{p['id']}")
                                        e_img = st.file_uploader("Trocar Foto (Opcional)", type=["png", "jpg", "jpeg"], key=f"img_edit_{p['id']}")
                                        
                                        if st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True):
                                            if db.atualizar_produto(p['id'], e_nome, e_cod, e_cat, e_custo, e_venda, e_estoque, p.get('data_compra', ''), e_medida, e_prod_propria):
                                                if e_img:
                                                    img_bytes = e_img.read()
                                                    import threading
                                                    def process_edit_upload(i_bytes, fname, p_id):
                                                        try:
                                                            import io, time, uuid
                                                            from PIL import Image
                                                            from rembg import remove
                                                            from database import supabase
                                                            
                                                            # Generate unique name
                                                            ext = fname.split('.')[-1] if '.' in fname else 'jpg'
                                                            safe_name = f"{p_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
                                                            
                                                            supabase.storage.from_("produtos").upload(path=safe_name, file=i_bytes, file_options={"content-type": f"image/{ext}", "upsert": "true"})
                                                            url_orig = supabase.storage.from_("produtos").get_public_url(safe_name)
                                                            supabase.table("produtos").update({"imagem_url": url_orig}).eq("id", p_id).execute()
                                                            
                                                            img = Image.open(io.BytesIO(i_bytes))
                                                            img_nobg = remove(img)
                                                            out_bytes = io.BytesIO()
                                                            img_nobg.save(out_bytes, format='PNG')
                                                            out_bytes.seek(0)
                                                            
                                                            new_name = safe_name.split('.')[0] + "_nobg.png"
                                                            try: supabase.storage.from_("produtos").remove([new_name])
                                                            except: pass
                                                            supabase.storage.from_("produtos").upload(path=new_name, file=out_bytes.read(), file_options={"content-type": "image/png", "upsert": "true"})
                                                            url_nobg = supabase.storage.from_("produtos").get_public_url(new_name)
                                                            
                                                            supabase.table("produtos").update({"imagem_url": url_nobg}).eq("id", p_id).execute()
                                                        except Exception as e:
                                                            print("Erro update bg:", e)
                                                    t = threading.Thread(target=process_edit_upload, args=(img_bytes, e_img.name, p['id']))
                                                    t.start()
                                                
                                                st.success("Salvo!")
                                                st.session_state.produtos_local = db.get_produtos()
                                                import time; time.sleep(0.2); st.rerun()
                                    if st.button("🗑️ Excluir Produto", key=f"del_{p['id']}", use_container_width=True):
                                        if db.excluir_produto(p['id']):
                                            st.session_state.produtos_local = [prod for prod in st.session_state.produtos_local if prod['id'] != p['id']]
                                            st.rerun()
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
                    
                    st.markdown("---")
                    st.markdown("**Lista de Itens Anotados:**")
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
                            
                        if not c.get('produto_id') and c['preco_unitario'] < 0:
                            nome_prod = "Pagamento Parcial"
                        else:
                            nome_prod = c['produtos']['nome'] if c.get('produtos') else 'Produto Excluído'
                            
                        un_medida = c['produtos'].get('unidade_medida', '') if c.get('produtos') else ''
                        
                        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                        col1.write(f"📅 {data_fmt} - **{nome_prod}**")
                        
                        if c['preco_unitario'] < 0:
                            col2.write("")
                            col3.write(f"💰 **- R$ {abs(c['quantidade'] * c['preco_unitario']):.2f}**")
                        else:
                            col2.write(f"{c['quantidade']} {un_medida} x R$ {c['preco_unitario']:.2f}")
                            col3.write(f"💰 **R$ {c['quantidade'] * c['preco_unitario']:.2f}**")
                            
                        if col4.button("🗑️", key=f"del_fiado_{c['id']}", help="Excluir item e devolver ao estoque"):
                            if db.excluir_compra_anotada(c['id']):
                                st.success("Item excluído e estoque devolvido!")
                                import time; time.sleep(0.5); st.rerun()
                                
                        if col5.button("💲", key=f"pagar_fiado_{c['id']}", help="Pagar apenas este item"):
                            if db.pagar_item_unico(c['id']):
                                st.success("Item pago com sucesso!")
                                import time; time.sleep(0.5); st.rerun()
                                
                    st.markdown("---")
                    
                    c_pagar_tudo, c_pagar_parcial = st.columns([1, 1])
                    
                    with c_pagar_tudo:
                        st.markdown("#### Quitar Tudo")
                        if st.button("Pagar Conta Inteira", type="primary", use_container_width=True):
                            ids = [c['id'] for c in compras]
                            if db.pagar_compras(ids, total_devendo, 0):
                                st.success("Conta paga com sucesso!")
                                st.balloons()
                                st.rerun()
                                
                    with c_pagar_parcial:
                        st.markdown("#### Pagamento Parcial")
                        val_parcial = st.number_input("Valor Pago (R$)", min_value=0.01, max_value=float(total_devendo), step=1.0)
                        if st.button("Registrar Valor", use_container_width=True):
                            if db.registrar_pagamento_parcial_fiado(cli_selecionado['id'], val_parcial):
                                st.success(f"Pagamento de R$ {val_parcial:.2f} registrado!")
                                import time; time.sleep(0.5); st.rerun()
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
                    is_kg = p_f.get('unidade_medida', '').lower() == 'kg'
                    lbl_qtd = "Valor R$" if is_kg else "Quantidade"
                    
                    qtd_f = c1.number_input(lbl_qtd, min_value=0.01, value=float(p_f['preco_venda']) if is_kg else 1.00, key="qtd_fiado")
                    preco_f = c2.number_input("Preço Unitário", value=float(p_f['preco_venda']), key="preco_fiado")
                    
                    if st.button("Anotar na Conta"):
                        qtd_final = (qtd_f / preco_f) if (is_kg and preco_f > 0) else qtd_f
                        
                        # Pré-calcula novo_estoque do cache local
                        novo_est_val = None
                        is_est_ctrl = p_f['categoria'] != 'Horta (Ilimitado)' and not p_f.get('producao_propria')
                        for p_loc in st.session_state.get('produtos_local', []):
                            if p_loc['id'] == p_f['id'] and is_est_ctrl:
                                novo_est_val = max(0.0, p_loc['quantidade_estoque'] - qtd_final)
                        item = {
                            "produto_id": p_f['id'],
                            "quantidade": qtd_final,
                            "preco_unitario": preco_f,
                            "is_estoque_controlado": is_est_ctrl,
                            "novo_estoque": novo_est_val
                        }
                        if db.anotar_compra(cli_selecionado['id'], [item]):
                            st.success("Compra anotada com sucesso!")
                            for p in st.session_state.produtos_local:
                                if p['id'] == item['produto_id'] and is_est_ctrl:
                                    p['quantidade_estoque'] = max(0.0, p['quantidade_estoque'] - item['quantidade'])
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
                    # Pré-calcula novo_estoque do cache local
                    novo_est_r = None
                    is_est_ctrl = p_r['categoria'] != 'Horta (Ilimitado)' and not p_r.get('producao_propria')
                    for p_loc in st.session_state.get('produtos_local', []):
                        if p_loc['id'] == p_r['id'] and is_est_ctrl:
                            novo_est_r = max(0.0, p_loc['quantidade_estoque'] - qtd_r)
                    item_r = {
                        "produto_id": p_r['id'],
                        "quantidade": qtd_r,
                        "preco_custo": p_r['preco_custo'],
                        "is_estoque_controlado": is_est_ctrl,
                        "novo_estoque": novo_est_r
                    }
                    if db.registrar_retirada_casa([item_r]):
                        st.success("Retirada registrada!")
                        for p in st.session_state.produtos_local:
                            if p['id'] == item_r['produto_id'] and is_est_ctrl:
                                p['quantidade_estoque'] = max(0.0, p['quantidade_estoque'] - item_r['quantidade'])
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
                    un_medida = r['produtos'].get('unidade_medida', '') if r.get('produtos') else ''
                    sub_custo = r['quantidade'] * r['custo_unitario']
                    custo_total_ret += sub_custo
                    
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    c1.write(f"📅 {data_fmt} - **{nome_prod}**")
                    c2.write(f"{r['quantidade']} {un_medida}")
                    c3.write(f"📉 **Custo: R$ {sub_custo:.2f}**")
                    if c4.button("🗑️", key=f"del_ret_{r['id']}"):
                        if db.excluir_retirada(r['id']):
                            st.success("Retirada excluída e estoque devolvido!")
                            import time; time.sleep(0.5); st.rerun()
                            
                st.error(f"Custo Total Retirado no Mês: R$ {custo_total_ret:.2f}")
            else:
                st.success("Nenhuma retirada registrada neste mês.")
    
    # =========================================================
    # ABA 5: RELATÓRIOS
    # =========================================================
    with tab_relatorios:
        st.header("📊 Resumo de Vendas")
        
        vendas = db.get_vendas()
        
        rel_geral, rel_pp = st.tabs(["Geral", "Produção Própria"])
        
        with rel_geral:
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
                        
                qtd_vendas_hoje = len(vendas_hoje)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Vendas Hoje (R$)", f"R$ {total_hoje:.2f}")
                c2.metric("Lucro Estimado Hoje", f"R$ {lucro_hoje:.2f}")
                c3.metric("Qtd de Vendas Hoje", f"{qtd_vendas_hoje}")
                
                st.markdown("### Histórico Recente (Últimas 100 vendas)")
                for v in vendas:
                    try:
                        dt_str = v['data_venda'].split('.')[0].replace('Z', '+00:00')
                        dt_obj = datetime.datetime.fromisoformat(dt_str).astimezone(tz_br)
                    except Exception:
                        dt_obj = datetime.datetime.now(tz_br)
                    
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    c1.write(f"📅 {dt_obj.strftime('%d/%m %H:%M')}")
                    c2.write(f"Pag: {v['forma_pagamento']}")
                    c3.write(f"💰 **R$ {v['valor_total']:.2f}**")
                    if c4.button("🗑️", key=f"del_v_{v['id']}"):
                        if db.excluir_venda(v['id']):
                            st.success("Venda excluída e estoque revertido!")
                            import time; time.sleep(0.5); st.rerun()
            else:
                st.info("Ainda não há histórico de vendas registrado no banco.")
                
        with rel_pp:
            st.subheader("Relatório de Produção Própria (Mês Atual)")
            from datetime import timezone, timedelta
            tz_br = timezone(timedelta(hours=-3))
            hoje = datetime.datetime.now(tz_br)
            
            itens_pp = db.get_relatorio_producao_propria(hoje.month, hoje.year)
            if itens_pp:
                vendas_totais_pp = 0.0
                lucro_total_pp = 0.0
                qtd_total_pp = 0.0
                
                for item in itens_pp:
                    try:
                        dt_str = item['vendas']['data_venda'].split('.')[0].replace('Z', '+00:00')
                        dt_v = datetime.datetime.fromisoformat(dt_str).astimezone(tz_br)
                    except:
                        dt_v = hoje
                        
                    if dt_v.year == hoje.year and dt_v.month == hoje.month:
                        qtd_total_pp += float(item['quantidade'])
                        vendas_totais_pp += float(item['subtotal'])
                        custo_item = float(item['quantidade']) * float(item['produtos']['preco_custo'])
                        lucro_total_pp += (float(item['subtotal']) - custo_item)
                        
                c1, c2, c3 = st.columns(3)
                c1.metric("Valor Total Vendido (R$)", f"R$ {vendas_totais_pp:.2f}")
                c2.metric("Lucro Líquido (R$)", f"R$ {lucro_total_pp:.2f}")
                c3.metric("Quantidade de Itens (Qtd/Kg)", f"{qtd_total_pp:.2f}")
            else:
                st.info("Nenhuma venda de produção própria registrada neste mês.")


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
                        if r.get('receber_whatsapp'):
                            st.markdown("💬 **Avisar no WhatsApp**")
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
                            if r.get('receber_whatsapp') and r.get('telefone'):
                                import urllib.parse
                                import re
                                num = re.sub(r'\D', '', r['telefone'])
                                if not num.startswith('55') and len(num) >= 10:
                                    num = '55' + num
                                msg = f"Olá {r['nome_cliente']}! O produto '{r['nome_produto']}' que você pediu acabou de chegar no Hortifruti! 🎉"
                                safe_msg = urllib.parse.quote(msg)
                                wpp_link = f"https://api.whatsapp.com/send?phone={num}&text={safe_msg}"
                                st.markdown(f'<a href="{wpp_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:8px; border-radius:5px; text-align:center; font-weight:bold; font-size:14px; margin-top:5px; margin-bottom:5px;">📱 Enviar WhatsApp</div></a>', unsafe_allow_html=True)
    
    # ROTEAMENTO
# ==========================================
# ROTEAMENTO PRINCIPAL (PÚBLICO VS ADMIN)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False

def page_public():
    import os
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
    else:
        index_content = "<!-- STREAMLIT_WIDGETS -->"

    # ── 1. Injeta CSS diretamente (sem depender de marcadores no HTML) ──────────
    vitrine_css = load_css("vitrine.css")
    st.markdown(f"<style>{css_theme}\n{vitrine_css}</style>", unsafe_allow_html=True)

    # ── 2. Extrai o template do card do index.html ───────────────────────────────
    card_template = (
        '<div class="vitrine-card">'
        '{img_html}'
        '<div class="vitrine-nome">{nome_curto}</div>'
        '<div class="vitrine-preco"><b>R$ {preco_venda}</b></div>'
        '{estoque_html}'
        '</div>'
    )
    if "<!-- TEMPLATE_CARD_PRODUTO -->" in index_content and "<!-- FIM_TEMPLATE_CARD_PRODUTO -->" in index_content:
        start_idx = index_content.find("<!-- TEMPLATE_CARD_PRODUTO -->") + len("<!-- TEMPLATE_CARD_PRODUTO -->")
        end_idx   = index_content.find("<!-- FIM_TEMPLATE_CARD_PRODUTO -->")
        card_template = index_content[start_idx:end_idx].strip()
        # Remove o bloco de template para não renderizá-lo na tela
        index_content = index_content[:index_content.find("<!-- TEMPLATE_CARD_PRODUTO -->")]

    # ── 3. Divide em topo (header) e base (main) pelo marcador de widgets ────────
    parts    = index_content.split("<!-- STREAMLIT_WIDGETS -->")
    part_top = parts[0] if len(parts) > 0 else ""
    part_bot = parts[1] if len(parts) > 1 else ""

    # Renderiza o cabeçalho (vídeo, etc.)
    if part_top.strip():
        st.markdown(part_top, unsafe_allow_html=True)

    st.markdown("---")

    # ── 4. Widgets nativos do Streamlit (busca + botão) ─────────────────────────
    produtos = db.get_produtos()

    @st.dialog("Qual produto você não encontrou?")
    def modal_solicitacao():
        st.write("Deixe sua sugestão e nós providenciaremos para você!")
        s_prod = st.text_input("Produto que você quer *")
        s_nome = st.text_input("Seu Nome *")
        s_tel  = st.text_input("Seu Telefone / WhatsApp (Opcional)")
        receber_wpp = st.checkbox("Deseja receber uma mensagem no WhatsApp caso o produto chegue?")
        if st.button("Enviar Sugestão", type="primary", use_container_width=True):
            if s_prod and s_nome:
                if receber_wpp and not s_tel:
                    st.error("Para ser avisado pelo WhatsApp, preencha o seu Telefone!")
                else:
                    sucesso = db.add_solicitacao(s_prod, s_nome, s_tel, receber_wpp)
                if sucesso:
                    st.success("Sugestão enviada com sucesso! Muito obrigado.")
                    import time
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("Erro interno. Verifique se você rodou o schema.sql no banco de dados!")
            else:
                st.error("Preencha o Nome do Produto e o Seu Nome.")

    col_busca, col_vazio, col_btn = st.columns([3, 1, 2])
    with col_busca:
        busca = st.text_input("🔍 O que você procura hoje?", placeholder="Ex: Maçã, Alface, Abóbora...")
    with col_btn:
        st.write("")
        st.write("")
        if st.button("🤔 Não achou seu produto? Clique aqui!", use_container_width=True):
            modal_solicitacao()

    prods_vitrine = produtos
    if busca:
        prods_vitrine = [p for p in produtos if busca.lower() in p['nome'].lower()]

    st.write("")

    # ── 5. Monta os cards e injeta na grade ─────────────────────────────────────
    html_cards = []
    for p in prods_vitrine:
        if p.get("imagem_url"):
            img_html = f'<div class="vitrine-img-container"><img class="blend-img" src="{p["imagem_url"]}"></div>'
        else:
            img_html = '<div class="vitrine-img-container sem-imagem">Sem Imagem</div>'

        nome_curto = p['nome'] if len(p['nome']) <= 20 else p['nome'][:18] + '...'

        if p['quantidade_estoque'] > 0 or p['categoria'] == 'Horta (Ilimitado)':
            estoque_html = "<div class='vitrine-estoque disp'>✓ Disponível</div>"
        else:
            estoque_html = "<div class='vitrine-estoque esgot'>✗ Esgotado</div>"

        card = (card_template
                .replace("{img_html}",    img_html)
                .replace("{nome_curto}",  nome_curto)
                .replace("{preco_venda}", f"{p['preco_venda']:.2f}")
                .replace("{estoque_html}", estoque_html))
        html_cards.append(card)

    # Injeta os cards na parte inferior do index.html
    html_bot = part_bot.replace("<!-- PLACEHOLDER_CARDS -->", "".join(html_cards)) \
                       .replace("{html_cards}", "".join(html_cards))
    if html_bot.strip():
        st.markdown(html_bot, unsafe_allow_html=True)

    st.markdown("---")

def page_admin():
    if not st.session_state.logged_in:
        st.warning("Acesso restrito. Redirecionando para a vitrine...")
        import time; time.sleep(1)
        st.switch_page(pg_home)
    else:
        render_admin()

# Definição e execução da Navegação
pg_home = st.Page(page_public, title="JeMpagina inicial", url_path="JeMpagina-inicial", default=True)
pg_admin = st.Page(page_admin, title="JeMadmin", url_path="JeMadmin")

pg = st.navigation([pg_home, pg_admin], position="hidden")
pg.run()

# ── Botões funcionais do Streamlit (ficam ocultos via JS/Marker) ────
# Deixamos no final do arquivo para que não ocupem espaço (margem preta) 
# no topo da página antes do vídeo renderizar.
with st.container():
    st.markdown("<div id='hf-hidden-btns-marker' style='display:none'></div>", unsafe_allow_html=True)
    
    if pg.url_path == "JeMadmin":
        if st.button("🔓", key="st_btn_admin"):
            st.session_state.logged_in = False
            controller.remove("auth_token")
            import time; time.sleep(0.3)
            st.switch_page(pg_home)
    else:
        icon = "⚙️" if st.session_state.logged_in else "🔐"
        if st.button(icon, key="st_btn_admin"):
            if st.session_state.logged_in:
                st.switch_page(pg_admin)
            else:
                modal_login()

    _tema_icon = "🌙" if st.session_state.light_mode else "☀️"
    if st.button(_tema_icon, key="st_btn_tema"):
        st.session_state.light_mode = not st.session_state.light_mode
        st.rerun()

# ── Portal visual — box fixa superior ───────────────────────────────
import streamlit.components.v1 as _components

if pg.url_path == "JeMadmin":
    _admin_icon = "🔓"
else:
    _admin_icon = "⚙️" if st.session_state.logged_in else "🔐"
_tema_icon_js = "🌙" if st.session_state.light_mode else "☀️"

_components.html(f"""
<script>
(function() {{
    var doc = window.parent.document;
    
    // 1. Encontra e esconde o container dos botões originais do Streamlit
    var marker = doc.getElementById('hf-hidden-btns-marker');
    if (marker) {{
        var stContainer = marker.closest('[data-testid="stVerticalBlock"]');
        if (stContainer) {{
            stContainer.style.display = 'none';
        }}
    }}
    
    // 2. Remove TODOS os portais visuais anteriores para evitar duplicatas
    var oldPortals = doc.querySelectorAll('#hf-btn-portal');
    oldPortals.forEach(function(p) {{ p.remove(); }});

    // 3. Cria a box do portal com os dois botões
    var portal = doc.createElement('div');
    portal.id = 'hf-btn-portal';
    portal.innerHTML =
        '<button id="hf-btn-admin" title="Admin">{_admin_icon}</button>' +
        '<button id="hf-btn-tema"  title="Tema">{_tema_icon_js}</button>';
    
    doc.body.appendChild(portal);

    // 4. Lógica de clique que aciona os botões ocultos
    function clickSt(n) {{
        if (marker) {{
            var stContainer = marker.closest('[data-testid="stVerticalBlock"]');
            if (stContainer) {{
                var btns = stContainer.querySelectorAll('button');
                if (btns && btns[n]) btns[n].click();
            }}
        }}
    }}

    doc.getElementById('hf-btn-admin').onclick = function() {{ clickSt(0); }};
    doc.getElementById('hf-btn-tema').onclick  = function() {{ clickSt(1); }};

}})();
</script>
""", height=0, width=0)
