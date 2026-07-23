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

# Estilização CSS customizada (Design Limpo e Responsivo)
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 16px;
    }
    .produto-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍎 Gestão Hortifruti Online")

# Carregar produtos do banco
produtos = db.get_produtos()

# Abas do Sistema
tab_pdv, tab_estoque, tab_relatorios = st.tabs(["🛒 Frente de Caixa", "📦 Gestão de Estoque", "📊 Relatórios"])

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
        cols_per_row = 3
        for i in range(0, len(prods_filtrados), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(prods_filtrados):
                    p = prods_filtrados[i+j]
                    with cols[j]:
                        img_tag = f'<img src="{p.get("imagem_url")}" style="max-width: 100%; border-radius: 5px; margin-bottom: 10px; max-height: 120px; object-fit: contain;">' if p.get("imagem_url") else ""
                        html_content = f"""
<div class="produto-card">
    {img_tag}
    <h4 style="margin-bottom: 5px; color: #2c3e50;">{p['nome']}</h4>
    <p style="margin-bottom: 5px; color: #27ae60; font-weight: bold; font-size: 18px;">R$ {p['preco_venda']:.2f} / {p['unidade_medida']}</p>
    <p style="margin-bottom: 10px; color: #7f8c8d; font-size: 12px;">Estoque: {p['quantidade_estoque']}</p>
</div>
"""
                        st.markdown(html_content, unsafe_allow_html=True)
                        
                        # Formulario de adição (Qtd manual)
                        qtd = st.number_input(f"Qtd ({p['unidade_medida']})", min_value=0.01, value=1.00, step=1.0 if p['unidade_medida']=='UN' else 0.1, key=f"qtd_{p['id']}")
                        
                        # Bloqueio de Estoque
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
# ABA 3: RELATÓRIOS
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
