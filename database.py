import os
import streamlit as st
from supabase import create_client, Client
# Carregar chaves locais do .env (se estiver rodando no PC)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_supabase_client() -> Client:
    """Inicializa e retorna o cliente do Supabase de forma segura"""
    # 1. Tenta pegar do st.secrets (para Streamlit Cloud)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        # 2. Se não achar, tenta pegar do ambiente local (.env)
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
    if not url or not key:
        st.error("Erro: Credenciais do Supabase não configuradas!")
        st.stop()
        
    return create_client(url, key)

supabase = get_supabase_client()

def verificar_login(usuario, senha):
    try:
        resp = supabase.table('usuarios').select('*').eq('usuario', usuario).eq('senha', senha).execute()
        if resp.data and len(resp.data) > 0:
            return True
        return False
    except Exception as e:
        print('Erro ao verificar login:', e)
        return False

# ==========================================
# CRUD DE PRODUTOS
# ==========================================

@st.cache_data(ttl=300)
def get_produtos():
    """Retorna todos os produtos cadastrados ordenados pelo nome"""
    try:
        response = supabase.table("produtos").select("*").order("nome").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar produtos: {e}")
        return []

def adicionar_produto(nome, codigo_barras, categoria, preco_custo, preco_venda, estoque, data_compra, unidade_medida="Un", producao_propria=False):
    """Adiciona um novo produto ao banco"""
    try:
        data = {
            "nome": nome,
            "codigo_barras": codigo_barras,
            "categoria": categoria,
            "preco_custo": float(preco_custo),
            "preco_venda": float(preco_venda),
            "quantidade_estoque": float(estoque),
            "data_compra": data_compra,
            "unidade_medida": unidade_medida,
            "producao_propria": producao_propria
        }
        supabase.table("produtos").insert(data).execute()
        get_produtos.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar produto: {e}")
        return False

def atualizar_produto(produto_id, nome, codigo_barras, categoria, preco_custo, preco_venda, estoque, data_compra, unidade_medida="Un", producao_propria=False):
    """Atualiza as informações de um produto existente"""
    try:
        data = {
            "nome": nome,
            "codigo_barras": codigo_barras,
            "categoria": categoria,
            "preco_custo": float(preco_custo),
            "preco_venda": float(preco_venda),
            "quantidade_estoque": float(estoque),
            "data_compra": data_compra,
            "unidade_medida": unidade_medida,
            "producao_propria": producao_propria
        }
        supabase.table("produtos").update(data).eq("id", produto_id).execute()
        get_produtos.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar produto: {e}")
        return False

def excluir_produto(produto_id):
    """Exclui um produto do banco de dados"""
    try:
        supabase.table("produtos").delete().eq("id", produto_id).execute()
        get_produtos.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir produto: {e}")
        return False

# ==========================================
# GESTÃO DE VENDAS
# ==========================================

def registrar_venda(valor_total, lucro_total, forma_pagamento, itens):
    """
    Registra uma venda e seus itens em batch.
    O desconto de estoque é feito em background (não bloqueia a UI).
    O novo_estoque de cada item deve ser pré-calculado pelo cliente e passado em item['novo_estoque'].
    """
    import threading
    try:
        # 1. Inserir venda
        dados_venda = {
            "valor_total": float(valor_total),
            "lucro_total": float(lucro_total),
            "forma_pagamento": forma_pagamento
        }
        resp_venda = supabase.table("vendas").insert(dados_venda).execute()

        if not resp_venda.data:
            return False

        venda_id = resp_venda.data[0]['id']

        # 2. Batch insert de todos os itens de uma vez (1 query ao invés de N)
        dados_itens = [
            {
                "venda_id": venda_id,
                "produto_id": item['produto_id'],
                "quantidade": float(item['quantidade']),
                "preco_unitario": float(item['preco_unitario']),
                "subtotal": float(item['subtotal'])
            }
            for item in itens
        ]
        supabase.table("itens_venda").insert(dados_itens).execute()

        # 3. Atualizar estoque em background (não bloqueia a UI)
        # O cliente já calculou novo_estoque = estoque_local - qtd_vendida
        def _atualizar_estoques(itens_snapshot):
            try:
                for item in itens_snapshot:
                    if item.get('is_estoque_controlado', True) and 'novo_estoque' in item:
                        supabase.table("produtos").update(
                            {"quantidade_estoque": float(item['novo_estoque'])}
                        ).eq("id", item['produto_id']).execute()
            except Exception as e_bg:
                print(f"[BG] Erro ao atualizar estoque: {e_bg}")

        t = threading.Thread(target=_atualizar_estoques, args=(list(itens),), daemon=True)
        t.start()

        get_produtos.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar venda: {e}")
        return False

def get_vendas():
    """Busca histórico de vendas (Limitado as 100 mais recentes)"""
    try:
        response = supabase.table("vendas").select("*").order("data_venda", desc=True).limit(100).execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar histórico de vendas: {e}")
        return []

# ==========================================
# FIADO (ANOTADO)
# ==========================================

def get_clientes():
    try:
        resp = supabase.table("clientes").select("*").order("nome").execute()
        return resp.data
    except Exception as e:
        st.error(f"Erro ao buscar clientes: {e}")
        return []

def add_cliente(nome, telefone=""):
    try:
        supabase.table("clientes").insert({"nome": nome.strip().title(), "telefone": telefone}).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar cliente (Talvez nome já exista): {e}")
        return False

def delete_cliente(cliente_id):
    try:
        # FK constraints handle cascade delete for compras_anotadas
        supabase.table("clientes").delete().eq("id", cliente_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir cliente: {e}")
        return False

def anotar_compra(cliente_id, itens):
    """
    Anota compras em lote. Se item tiver 'novo_estoque', usa esse valor diretamente
    (cliente pre-calcula para evitar SELECT desnecessario).
    """
    import threading
    try:
        dados_list = [
            {
                "cliente_id": cliente_id,
                "produto_id": item['produto_id'],
                "quantidade": float(item['quantidade']),
                "preco_unitario": float(item['preco_unitario'])
            }
            for item in itens
        ]
        supabase.table("compras_anotadas").insert(dados_list).execute()

        def _atualizar_estoques(itens_snapshot):
            try:
                for item in itens_snapshot:
                    if item.get('is_estoque_controlado', True) and 'novo_estoque' in item:
                        supabase.table("produtos").update(
                            {"quantidade_estoque": float(item['novo_estoque'])}
                        ).eq("id", item['produto_id']).execute()
                    elif item.get('is_estoque_controlado', True):
                        # Fallback: busca e desconta (caso novo_estoque nao fornecido)
                        prod_data = supabase.table("produtos").select("quantidade_estoque").eq("id", item['produto_id']).execute()
                        if prod_data.data:
                            novo_est = max(0.0, prod_data.data[0]['quantidade_estoque'] - float(item['quantidade']))
                            supabase.table("produtos").update({"quantidade_estoque": novo_est}).eq("id", item['produto_id']).execute()
            except Exception as e_bg:
                print(f"[BG] Erro ao atualizar estoque (anotar_compra): {e_bg}")

        t = threading.Thread(target=_atualizar_estoques, args=(list(itens),), daemon=True)
        t.start()
        get_produtos.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao anotar compra: {e}")
        return False

def get_compras_anotadas(cliente_id):
    try:
        resp = supabase.table("compras_anotadas").select("*, produtos(nome, data_compra)").eq("cliente_id", cliente_id).eq("pago", False).order("data_hora", desc=True).execute()
        return resp.data
    except Exception as e:
        st.error(f"Erro ao buscar fiado: {e}")
        return []

def pagar_compras(compras_ids, total_venda, lucro_venda):
    if not compras_ids: return False
    try:
        # 1. Registra no Caixa do dia (Vendas)
        if total_venda > 0:
            supabase.table("vendas").insert({
                "valor_total": float(total_venda),
                "lucro_total": float(lucro_venda),
                "forma_pagamento": "Fiado Pago"
            }).execute()
            
        # 2. Marca as compras como pagas
        supabase.table("compras_anotadas").update({"pago": True}).in_("id", compras_ids).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao pagar compras: {e}")
        return False

def excluir_compra_anotada(compra_id):
    try:
        # 1. Pega os dados para devolver ao estoque
        resp = supabase.table("compras_anotadas").select("produto_id, quantidade, pago").eq("id", compra_id).execute()
        if resp.data and not resp.data[0]['pago']:
            prod_id = resp.data[0]['produto_id']
            qtd = resp.data[0]['quantidade']
            
            # Devolve ao estoque
            prod_data = supabase.table("produtos").select("quantidade_estoque").eq("id", prod_id).execute()
            if prod_data.data:
                novo_est = prod_data.data[0]['quantidade_estoque'] + qtd
                supabase.table("produtos").update({"quantidade_estoque": novo_est}).eq("id", prod_id).execute()
                
        # 2. Exclui a anotação
        supabase.table("compras_anotadas").delete().eq("id", compra_id).execute()
        get_produtos.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir fiado: {e}")
        return False

# ==========================================
# RETIRADAS PARA CASA
# ==========================================

def registrar_retirada_casa(itens):
    """
    Registra retiradas em lote. Se item tiver 'novo_estoque', usa esse valor diretamente.
    """
    import threading
    try:
        dados_list = [
            {
                "produto_id": item['produto_id'],
                "quantidade": float(item['quantidade']),
                "custo_unitario": float(item['preco_custo'])
            }
            for item in itens
        ]
        supabase.table("retiradas_casa").insert(dados_list).execute()

        def _atualizar_estoques(itens_snapshot):
            try:
                for item in itens_snapshot:
                    if item.get('is_estoque_controlado', True) and 'novo_estoque' in item:
                        supabase.table("produtos").update(
                            {"quantidade_estoque": float(item['novo_estoque'])}
                        ).eq("id", item['produto_id']).execute()
                    elif item.get('is_estoque_controlado', True):
                        prod_data = supabase.table("produtos").select("quantidade_estoque").eq("id", item['produto_id']).execute()
                        if prod_data.data:
                            novo_est = max(0.0, prod_data.data[0]['quantidade_estoque'] - float(item['quantidade']))
                            supabase.table("produtos").update({"quantidade_estoque": novo_est}).eq("id", item['produto_id']).execute()
            except Exception as e_bg:
                print(f"[BG] Erro ao atualizar estoque (retirada): {e_bg}")

        t = threading.Thread(target=_atualizar_estoques, args=(list(itens),), daemon=True)
        t.start()
        get_produtos.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar retirada: {e}")
        return False

def get_retiradas_mes(ano, mes):
    # Para campos timestamp no Postgres/Supabase, não podemos usar .like()
    # Devemos usar maior ou igual (gte) ao primeiro dia do mês, 
    # e menor que (lt) o primeiro dia do próximo mês.
    data_inicio = f"{ano}-{mes:02d}-01T00:00:00.000Z"
    
    if mes == 12:
        prox_ano = ano + 1
        prox_mes = 1
    else:
        prox_ano = ano
        prox_mes = mes + 1
        
    data_fim = f"{prox_ano}-{prox_mes:02d}-01T00:00:00.000Z"
    
    try:
        resp = supabase.table("retiradas_casa").select("*, produtos(nome, data_compra)").gte("data_hora", data_inicio).lt("data_hora", data_fim).order("data_hora", desc=True).execute()
        return resp.data
    except Exception as e:
        st.error(f"Erro ao buscar retiradas: {e}")
        return []

def excluir_retirada_casa(retirada_id):
    try:
        resp = supabase.table("retiradas_casa").select("produto_id, quantidade").eq("id", retirada_id).execute()
        if resp.data:
            prod_id = resp.data[0]['produto_id']
            qtd = resp.data[0]['quantidade']
            
            prod_data = supabase.table("produtos").select("quantidade_estoque").eq("id", prod_id).execute()
            if prod_data.data:
                novo_est = prod_data.data[0]['quantidade_estoque'] + qtd
                supabase.table("produtos").update({"quantidade_estoque": novo_est}).eq("id", prod_id).execute()
                
        supabase.table("retiradas_casa").delete().eq("id", retirada_id).execute()
        get_produtos.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir retirada: {e}")
        return False

# ==========================================
# BALANÇO MENSAL
# ==========================================

def get_balanco_mes(ano, mes):
    try:
        resp = supabase.table("balanco_mensal").select("*").eq("ano", ano).eq("mes", mes).execute()
        if resp.data:
            return resp.data[0]
        return {'estoque_inicial': 0.0, 'estoque_final': 0.0}
    except Exception as e:
        return {'estoque_inicial': 0.0, 'estoque_final': 0.0}

def save_balanco_mes(ano, mes, estoque_inicial, estoque_final):
    try:
        # Tenta buscar se existe
        resp = supabase.table("balanco_mensal").select("id").eq("ano", ano).eq("mes", mes).execute()
        if resp.data:
            supabase.table("balanco_mensal").update({
                "estoque_inicial": float(estoque_inicial),
                "estoque_final": float(estoque_final)
            }).eq("id", resp.data[0]['id']).execute()
        else:
            supabase.table("balanco_mensal").insert({
                "ano": ano,
                "mes": mes,
                "estoque_inicial": float(estoque_inicial),
                "estoque_final": float(estoque_final)
            }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar balanço: {e}")
        return False

# ==========================================
# SOLICITAÇÕES DE PRODUTOS
# ==========================================

def get_solicitacoes():
    try:
        resp = supabase.table('solicitacoes').select('*').order('data_solicitacao', desc=True).execute()
        return resp.data
    except Exception as e:
        print('Erro ao buscar solicitacoes:', e)
        return []

def add_solicitacao(nome_produto, nome_cliente, telefone, receber_whatsapp=False):
    try:
        data = {
            'nome_produto': nome_produto,
            'nome_cliente': nome_cliente,
            'telefone': telefone,
            'receber_whatsapp': receber_whatsapp,
            'status': 'Pendente'
        }
        supabase.table('solicitacoes').insert(data).execute()
        return True
    except Exception as e:
        print('Erro ao adicionar solicitacao:', e)
        return False

def update_solicitacao_status(req_id, novo_status):
    try:
        supabase.table('solicitacoes').update({'status': novo_status}).eq('id', req_id).execute()
        return True
    except Exception as e:
        print('Erro ao atualizar solicitacao:', e)
        return False

# ==========================================
# EXCLUSOES COM RETORNO DE ESTOQUE
# ==========================================

def reverter_estoque(produto_id, quantidade_devolvida):
    try:
        if not produto_id: return
        p = supabase.table('produtos').select('quantidade_estoque').eq('id', produto_id).execute()
        if p.data:
            nova_qtd = float(p.data[0]['quantidade_estoque']) + float(quantidade_devolvida)
            supabase.table('produtos').update({'quantidade_estoque': nova_qtd}).eq('id', produto_id).execute()
            # Limpa cache local se estiver usando
            if 'get_produtos' in globals() and hasattr(get_produtos, 'clear'):
                get_produtos.clear()
    except Exception as e:
        print('Erro ao reverter estoque:', e)

def excluir_venda(venda_id):
    try:
        itens = supabase.table('itens_venda').select('*').eq('venda_id', venda_id).execute()
        for item in itens.data:
            reverter_estoque(item['produto_id'], item['quantidade'])
            
        supabase.table('itens_venda').delete().eq('venda_id', venda_id).execute()
        supabase.table('vendas').delete().eq('id', venda_id).execute()
        return True
    except Exception as e:
        print('Erro ao excluir venda:', e)
        return False

def excluir_compra_anotada(id):
    try:
        compra = supabase.table('compras_anotadas').select('*').eq('id', id).execute()
        if compra.data:
            reverter_estoque(compra.data[0]['produto_id'], compra.data[0]['quantidade'])
        supabase.table('compras_anotadas').delete().eq('id', id).execute()
        return True
    except Exception as e:
        print('Erro ao excluir compra anotada:', e)
        return False

def excluir_retirada(id):
    try:
        ret = supabase.table('retiradas_casa').select('*').eq('id', id).execute()
        if ret.data:
            reverter_estoque(ret.data[0]['produto_id'], ret.data[0]['quantidade'])
        supabase.table('retiradas_casa').delete().eq('id', id).execute()
        return True
    except Exception as e:
        print('Erro ao excluir retirada:', e)
        return False

def get_relatorio_producao_propria(mes, ano):
    try:
        from datetime import timezone, timedelta
        import datetime as dt_lib
        # Simplificando, buscar itens com seus produtos onde producao_propria=True
        itens = supabase.table('itens_venda').select('*, produtos!inner(*), vendas!inner(*)').eq('produtos.producao_propria', True).execute()
        return itens.data
    except Exception as e:
        print('Erro ao buscar relatorio producao propria:', e)
        return []

def pagar_item_unico(compra_id):
    try:
        resp = supabase.table('compras_anotadas').select('*, produtos(*)').eq('id', compra_id).execute()
        if not resp.data: return False
        c = resp.data[0]
        if c['pago']: return True
        val_total = float(c['quantidade']) * float(c['preco_unitario'])
        custo = float(c['quantidade']) * float(c['produtos']['preco_custo']) if c.get('produtos') else 0
        lucro = val_total - custo
        supabase.table('vendas').insert({'valor_total': val_total, 'lucro_total': lucro, 'forma_pagamento': 'Fiado Pago'}).execute()
        supabase.table('compras_anotadas').update({'pago': True}).eq('id', compra_id).execute()
        return True
    except Exception as e:
        print(e); return False

def registrar_pagamento_parcial_fiado(cliente_id, valor):
    try:
        supabase.table('vendas').insert({'valor_total': float(valor), 'lucro_total': float(valor), 'forma_pagamento': 'Fiado Pago (Parcial)'}).execute()
        supabase.table('compras_anotadas').insert({'cliente_id': cliente_id, 'quantidade': 1.0, 'preco_unitario': -float(valor), 'pago': False}).execute()
        return True
    except Exception as e:
        print(e); return False
