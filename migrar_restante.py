import sqlite3
import os
import sys

sys.path.append(r"c:\Users\Usuario\Documents\Hortifrut_Web")
from database import supabase

def migrar_banco_restante():
    db_path = r"c:\Users\Usuario\Documents\Hortifrut\mercearia.db"
    
    if not os.path.exists(db_path):
        print(f"Erro: Banco local {db_path} não encontrado.")
        return
        
    print(f"Conectando ao banco local SQLite: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Mapeamento de Produtos (necessário para as chaves estrangeiras)
    print("Recuperando mapa de produtos...")
    cursor.execute("SELECT id, nome FROM produtos")
    produtos_sqlite = cursor.fetchall()
    
    resp_prod = supabase.table("produtos").select("id, nome").execute()
    prod_supa_map = {p['nome']: p['id'] for p in resp_prod.data}
    
    id_map_produtos = {} # Mapeia ID antigo do SQLite (INT) para ID do Supabase (UUID)
    for p in produtos_sqlite:
        if p['nome'] in prod_supa_map:
            id_map_produtos[p['id']] = prod_supa_map[p['nome']]

    # ==========================================
    # 1. Migração de Clientes
    # ==========================================
    print("Iniciando migração de Clientes...")
    cursor.execute("SELECT * FROM clientes")
    clientes_sqlite = cursor.fetchall()
    
    clientes_batch = []
    id_map_clientes = {} 
    
    for c in clientes_sqlite:
        clientes_batch.append({
            "nome": c['nome'],
            "telefone": c['telefone']
        })
        
    if clientes_batch:
        try:
            resp_cli = supabase.table("clientes").insert(clientes_batch).execute()
            print(f"{len(resp_cli.data)} clientes inseridos no Supabase.")
            for i, c_db in enumerate(resp_cli.data):
                old_id = clientes_sqlite[i]['id']
                id_map_clientes[old_id] = c_db['id']
        except Exception as e:
            print(f"Erro ao inserir clientes: {e}")
            return
            
    # ==========================================
    # 2. Migração de Compras Anotadas (Fiado)
    # ==========================================
    print("Iniciando migração de Compras Anotadas...")
    cursor.execute("SELECT * FROM compras_anotadas")
    compras_sqlite = cursor.fetchall()
    
    compras_batch = []
    for c in compras_sqlite:
        new_cli_id = id_map_clientes.get(c['cliente_id'])
        new_prod_id = id_map_produtos.get(c['produto_id'])
        
        if new_cli_id and new_prod_id:
            compras_batch.append({
                "cliente_id": new_cli_id,
                "produto_id": new_prod_id,
                "quantidade": float(c['quantidade']),
                "preco_unitario": float(c['preco_unitario']),
                "data_hora": c['data_hora'],
                "pago": bool(c['pago'])
            })
            
    if compras_batch:
        chunk_size = 500
        for i in range(0, len(compras_batch), chunk_size):
            chunk = compras_batch[i:i + chunk_size]
            try:
                resp = supabase.table("compras_anotadas").insert(chunk).execute()
                print(f"Lote de {len(resp.data)} compras anotadas inserido.")
            except Exception as e:
                print(f"Erro ao inserir compras anotadas: {e}")

    # ==========================================
    # 3. Migração de Retiradas para Casa
    # ==========================================
    print("Iniciando migração de Retiradas para Casa...")
    cursor.execute("SELECT * FROM retiradas_casa")
    retiradas_sqlite = cursor.fetchall()
    
    ret_batch = []
    for r in retiradas_sqlite:
        new_prod_id = id_map_produtos.get(r['produto_id'])
        if new_prod_id:
            ret_batch.append({
                "data_hora": r['data_hora'],
                "produto_id": new_prod_id,
                "quantidade": float(r['quantidade']),
                "custo_unitario": float(r['custo_unitario'])
            })
            
    if ret_batch:
        chunk_size = 500
        for i in range(0, len(ret_batch), chunk_size):
            chunk = ret_batch[i:i + chunk_size]
            try:
                resp = supabase.table("retiradas_casa").insert(chunk).execute()
                print(f"Lote de {len(resp.data)} retiradas inserido.")
            except Exception as e:
                print(f"Erro ao inserir retiradas: {e}")

    # ==========================================
    # 4. Migração de Balanço Mensal
    # ==========================================
    print("Iniciando migração de Balanço Mensal...")
    cursor.execute("SELECT * FROM balanco_mensal")
    balanco_sqlite = cursor.fetchall()
    
    bal_batch = []
    for b in balanco_sqlite:
        bal_batch.append({
            "mes": b['mes'],
            "ano": b['ano'],
            "estoque_inicial": float(b['estoque_inicial']),
            "estoque_final": float(b['estoque_final'])
        })
        
    if bal_batch:
        try:
            resp = supabase.table("balanco_mensal").insert(bal_batch).execute()
            print(f"{len(resp.data)} balanços mensais inseridos.")
        except Exception as e:
            print(f"Erro ao inserir balanços: {e}")

    conn.close()
    print("==========================================")
    print("MIGRAÇÃO DE FIADO E RETIRADAS CONCLUÍDA!")
    print("==========================================")

if __name__ == "__main__":
    migrar_banco_restante()
