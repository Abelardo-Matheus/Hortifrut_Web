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

def adicionar_produto(nome, codigo_barras, categoria, preco_custo, preco_venda, estoque, unidade_medida):
    """Adiciona um novo produto ao banco"""
    try:
        data = {
            "nome": nome,
            "codigo_barras": codigo_barras,
            "categoria": categoria,
            "preco_custo": float(preco_custo),
            "preco_venda": float(preco_venda),
            "quantidade_estoque": float(estoque),
            "unidade_medida": unidade_medida
        }
        supabase.table("produtos").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar produto: {e}")
        return False

def atualizar_produto(produto_id, nome, codigo_barras, categoria, preco_custo, preco_venda, estoque, unidade_medida):
    """Atualiza as informações de um produto existente"""
    try:
        data = {
            "nome": nome,
            "codigo_barras": codigo_barras,
            "categoria": categoria,
            "preco_custo": float(preco_custo),
            "preco_venda": float(preco_venda),
            "quantidade_estoque": float(estoque),
            "unidade_medida": unidade_medida
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
