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
        raise ValueError("Chaves do Supabase não encontradas. Configure o .env ou o st.secrets.")
        
    return create_client(url, key)

supabase = get_supabase_client()

# ==========================================
# CRUD DE PRODUTOS
# ==========================================

def get_produtos():
    """Retorna todos os produtos cadastrados ordenados pelo nome"""
    try:
        response = supabase.table("produtos").select("*").order("nome").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar produtos: {e}")
        return []

def adicionar_produto(nome, codigo_barras, categoria, preco_custo, preco_venda, estoque, data_compra):
    """Adiciona um novo produto ao banco"""
    try:
        data = {
            "nome": nome,
            "codigo_barras": codigo_barras,
            "categoria": categoria,
            "preco_custo": float(preco_custo),
            "preco_venda": float(preco_venda),
            "quantidade_estoque": float(estoque),
            "data_compra": data_compra
        }
        supabase.table("produtos").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar produto: {e}")
        return False

def atualizar_produto(produto_id, nome, codigo_barras, categoria, preco_custo, preco_venda, estoque, data_compra):
    """Atualiza as informações de um produto existente"""
    try:
        data = {
            "nome": nome,
            "codigo_barras": codigo_barras,
            "categoria": categoria,
            "preco_custo": float(preco_custo),
            "preco_venda": float(preco_venda),
            "quantidade_estoque": float(estoque),
            "data_compra": data_compra
        }
        supabase.table("produtos").update(data).eq("id", produto_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar produto: {e}")
        return False

def excluir_produto(produto_id):
    """Exclui um produto do banco de dados"""
    try:
        supabase.table("produtos").delete().eq("id", produto_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir produto: {e}")
        return False

# ==========================================
# GESTÃO DE VENDAS
# ==========================================

def registrar_venda(valor_total, lucro_total, forma_pagamento, itens):
    """
    Registra uma venda, os itens da venda, e desconta do estoque.
    Por ser um banco via API, faremos as operações de forma sequencial.
    """
    try:
        # 1. Registrar a Venda
        dados_venda = {
            "valor_total": float(valor_total),
            "lucro_total": float(lucro_total),
            "forma_pagamento": forma_pagamento
        }
        resp_venda = supabase.table("vendas").insert(dados_venda).execute()
        
        if not resp_venda.data:
            return False
            
        venda_id = resp_venda.data[0]['id']
        
        # 2. Inserir itens da venda e descontar estoque
        for item in itens:
            prod_id = item['produto_id']
            qtd = float(item['quantidade'])
            
            # Inserir na tabela itens_venda
            dados_item = {
                "venda_id": venda_id,
                "produto_id": prod_id,
                "quantidade": qtd,
                "preco_unitario": float(item['preco_unitario']),
                "subtotal": float(item['subtotal'])
            }
            supabase.table("itens_venda").insert(dados_item).execute()
            
            # Descontar do estoque (Se não for Horta ilimitada)
            if item.get('is_estoque_controlado', True):
                # Busca o estoque atual
                prod_data = supabase.table("produtos").select("quantidade_estoque").eq("id", prod_id).execute()
                if prod_data.data:
                    estoque_atual = prod_data.data[0]['quantidade_estoque']
                    novo_estoque = max(0.0, estoque_atual - qtd)
                    # Atualiza o estoque
                    supabase.table("produtos").update({"quantidade_estoque": novo_estoque}).eq("id", prod_id).execute()
                    
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
    try:
        for item in itens:
            prod_id = item['produto_id']
            qtd = float(item['quantidade'])
            
            dados = {
                "cliente_id": cliente_id,
                "produto_id": prod_id,
                "quantidade": qtd,
                "preco_unitario": float(item['preco_unitario'])
            }
            supabase.table("compras_anotadas").insert(dados).execute()
            
            # Descontar do estoque (Se não for Horta)
            if item.get('is_estoque_controlado', True):
                prod_data = supabase.table("produtos").select("quantidade_estoque").eq("id", prod_id).execute()
                if prod_data.data:
                    novo_est = max(0.0, prod_data.data[0]['quantidade_estoque'] - qtd)
                    supabase.table("produtos").update({"quantidade_estoque": novo_est}).eq("id", prod_id).execute()
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
        return True
    except Exception as e:
        st.error(f"Erro ao excluir fiado: {e}")
        return False

# ==========================================
# RETIRADAS PARA CASA
# ==========================================

def registrar_retirada_casa(itens):
    try:
        for item in itens:
            prod_id = item['produto_id']
            qtd = float(item['quantidade'])
            
            dados = {
                "produto_id": prod_id,
                "quantidade": qtd,
                "custo_unitario": float(item['preco_custo']) # Retirada é a preço de custo
            }
            supabase.table("retiradas_casa").insert(dados).execute()
            
            # Descontar do estoque
            if item.get('is_estoque_controlado', True):
                prod_data = supabase.table("produtos").select("quantidade_estoque").eq("id", prod_id).execute()
                if prod_data.data:
                    novo_est = max(0.0, prod_data.data[0]['quantidade_estoque'] - qtd)
                    supabase.table("produtos").update({"quantidade_estoque": novo_est}).eq("id", prod_id).execute()
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

def add_solicitacao(nome_produto, nome_cliente, telefone):
    try:
        data = {
            'nome_produto': nome_produto,
            'nome_cliente': nome_cliente,
            'telefone': telefone,
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
