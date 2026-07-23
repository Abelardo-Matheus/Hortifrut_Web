import sqlite3
import os
import sys

# Adiciona o diretório atual ao path para importar o módulo database.py que tem a conexão do supabase
sys.path.append(r"c:\Users\Usuario\Documents\Hortifrut_Web")
from database import supabase

def migrar_banco():
    db_path = r"c:\Users\Usuario\Documents\Hortifrut\mercearia.db"
    
    if not os.path.exists(db_path):
        print(f"Erro: Banco local {db_path} não encontrado.")
        return
        
    print(f"Conectando ao banco local SQLite: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ==========================================
    # 1. Migração de Produtos
    # ==========================================
    print("Iniciando migração de Produtos...")
    cursor.execute("SELECT * FROM produtos")
    produtos_sqlite = cursor.fetchall()
    
    produtos_batch = []
    id_map_produtos = {} # Mapeia ID antigo do SQLite (INT) para novo ID do Supabase (UUID)
    
    for p in produtos_sqlite:
        categoria = 'Outros'
        if p['is_horta']: 
            categoria = 'Horta (Ilimitado)'
            
        unidade_medida = 'KG' if p['vendido_por_peso'] else 'UN'
        
        produtos_batch.append({
            "nome": p['nome'],
            "codigo_barras": p['codigo_barras'],
            "categoria": categoria,
            "preco_custo": float(p['preco_compra']),
            "preco_venda": float(p['preco_venda']),
            "quantidade_estoque": float(p['quantidade_estoque']),
            "unidade_medida": unidade_medida
        })
        
    if produtos_batch:
        try:
            # Insere em lote (batch) para ser mais rápido
            resp_prod = supabase.table("produtos").insert(produtos_batch).execute()
            print(f"{len(resp_prod.data)} produtos inseridos no Supabase.")
            
            # Constroi o mapa de IDs baseado na ordem retornada
            for i, p_db in enumerate(resp_prod.data):
                old_id = produtos_sqlite[i]['id']
                id_map_produtos[old_id] = p_db['id']
                
        except Exception as e:
            print(f"Erro ao inserir produtos: {e}")
            return
    else:
        print("Nenhum produto para migrar.")

    # ==========================================
    # 2. Migração de Vendas
    # ==========================================
    print("Iniciando migração de Vendas...")
    cursor.execute("SELECT * FROM vendas")
    vendas_sqlite = cursor.fetchall()
    
    vendas_batch = []
    id_map_vendas = {} # Mapeia ID de venda do SQLite para Supabase
    
    for v in vendas_sqlite:
        # SQLite datetime format is usually compatible with PostgreSQL
        vendas_batch.append({
            "data_venda": v['data_hora'],
            "valor_total": float(v['total_venda']),
            "lucro_total": float(v['lucro_venda']),
            "forma_pagamento": "Dinheiro (Migrado)"
        })
        
    # Chunking para vendas (caso sejam muitas, enviamos de 500 em 500)
    chunk_size = 500
    for i in range(0, len(vendas_batch), chunk_size):
        chunk = vendas_batch[i:i + chunk_size]
        chunk_orig_sqlite = vendas_sqlite[i:i + chunk_size]
        
        try:
            resp_vendas = supabase.table("vendas").insert(chunk).execute()
            print(f"Lote de {len(resp_vendas.data)} vendas inserido.")
            
            for j, v_db in enumerate(resp_vendas.data):
                old_id = chunk_orig_sqlite[j]['id']
                id_map_vendas[old_id] = v_db['id']
        except Exception as e:
            print(f"Erro ao inserir lote de vendas: {e}")
            
    # ==========================================
    # 3. Migração de Itens da Venda
    # ==========================================
    print("Iniciando migração de Itens de Venda...")
    cursor.execute("SELECT * FROM itens_venda")
    itens_sqlite = cursor.fetchall()
    
    itens_batch = []
    for it in itens_sqlite:
        old_venda_id = it['venda_id']
        old_produto_id = it['produto_id']
        
        new_venda_id = id_map_vendas.get(old_venda_id)
        new_produto_id = id_map_produtos.get(old_produto_id)
        
        # Só insere se ambos os pais existirem (Evita FK Violation)
        if new_venda_id and new_produto_id:
            qtd = float(it['quantidade'])
            preco_un = float(it['preco_unitario'])
            itens_batch.append({
                "venda_id": new_venda_id,
                "produto_id": new_produto_id,
                "quantidade": qtd,
                "preco_unitario": preco_un,
                "subtotal": qtd * preco_un
            })
            
    for i in range(0, len(itens_batch), chunk_size):
        chunk = itens_batch[i:i + chunk_size]
        try:
            resp_itens = supabase.table("itens_venda").insert(chunk).execute()
            print(f"Lote de {len(resp_itens.data)} itens de venda inserido.")
        except Exception as e:
            print(f"Erro ao inserir lote de itens: {e}")

    conn.close()
    print("==========================================")
    print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("==========================================")

if __name__ == "__main__":
    migrar_banco()
