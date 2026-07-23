import sys
import re

file_path = r"c:\Users\Usuario\Documents\Hortifrut_Web\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Tabs
content = content.replace(
    'tab_pdv, tab_estoque, tab_relatorios = st.tabs(["🛒 Frente de Caixa", "📦 Gestão de Estoque", "📊 Relatórios"])',
    'tab_pdv, tab_estoque, tab_fiado, tab_retiradas, tab_relatorios = st.tabs(["🛒 Caixa", "📦 Estoque", "📝 Fiado", "🏠 Retiradas", "📊 Relatórios"])'
)

# 2. Add Fiado and Retiradas before Relatorios
new_sections = """# =========================================================
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
# ABA """

content = content.replace(
    '# =========================================================\n# ABA 3: RELATÓRIOS',
    new_sections + '5: RELATÓRIOS'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("app.py atualizado com sucesso!")
