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


def render_admin():
    
    
    
    st.title("🍎 Gestão Hortifruti Online")
    
    # Carregar produtos do banco
    produtos = db.get_produtos()
    
    # Abas do Sistema
    tab_pdv, tab_estoque, tab_fiado, tab_retiradas, tab_relatorios = st.tabs(["🛒 Caixa", "📦 Estoque", "📝 Fiado", "🏠 Retiradas", "📊 Relatórios"])
    
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
                                st.markdown(f'<div style="font-size: 14px; margin-bottom: 5px;"><b>R$ {p["preco_venda"]:.2f}</b> / {p["unidade_medida"]}</div>', unsafe_allow_html=True)
                                st.caption(f"Estoque: {p['quantidade_estoque']}")
                                
                                # Formulario de adição dentro do mesmo container
                                qtd = st.number_input("Quantidade", min_value=0.01, value=1.00, step=1.0 if p['unidade_medida']=='UN' else 0.1, key=f"qtd_{p['id']}", label_visibility="collapsed")
                                
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
                unidade = c7.selectbox("Vendido por", ["UN", "KG"])
                
                submit = st.form_submit_button("Salvar Produto", type="primary")
                if submit:
                    if nome and venda >= 0:
                        sucesso = db.adicionar_produto(nome, codigo, categoria, custo, venda, estoque, unidade)
                        if sucesso:
                            st.success("Produto cadastrado!")
                            st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios (Nome e Preço de Venda).")
                        
        st.markdown("### 📋 Tabela de Produtos")
        
        if produtos:
            produtos_view = []
            for p in produtos:
                estoque_str = f"⚠️ {p['quantidade_estoque']}" if p['quantidade_estoque'] <= 5 else p['quantidade_estoque']
                produtos_view.append({
                    'Nome': p['nome'],
                    'Categoria': p['categoria'],
                    'Estoque': estoque_str,
                    'UN/KG': p['unidade_medida'],
                    'Custo (R$)': p['preco_custo'],
                    'Venda (R$)': p['preco_venda']
                })
            
            st.dataframe(produtos_view, use_container_width=True, hide_index=True)
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
                        un_medida = c['produtos']['unidade_medida'] if c.get('produtos') else 'UN'
                        
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
                    un_medida = r['produtos']['unidade_medida'] if r.get('produtos') else 'UN'
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
    
    # CSS para as imagens da vitrine
    st.markdown('''
    <style>
    .blend-img {
        max-width: 100%; 
        max-height: 160px; 
        object-fit: contain; 
        border-radius: 5px;
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
                        nome_curto = p['nome'] if len(p['nome']) <= 20 else p['nome'][:18] + '...'
                        st.markdown(f'<div style=\"height: 48px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-weight: bold; font-size: 20px; margin-bottom: 5px; text-align: center;\">{nome_curto}</div>', unsafe_allow_html=True)
                        
                        # Preço
                        st.markdown(f'<div style="font-size: 22px; margin-bottom: 5px; color: #27ae60; text-align: center;"><b>R$ {p["preco_venda"]:.2f}</b> <span style="font-size:14px; color:#7f8c8d;">/ {p["unidade_medida"]}</span></div>', unsafe_allow_html=True)
                        
                        # Estoque/Disponibilidade
                        if p['quantidade_estoque'] > 0 or p['categoria'] == 'Horta (Ilimitado)':
                            st.markdown(f"<div style='text-align: center; color: #2980b9; font-weight: bold; font-size: 14px;'>✓ Disponível</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align: center; color: #e74c3c; font-weight: bold; font-size: 14px;'>✗ Esgotado</div>", unsafe_allow_html=True)
