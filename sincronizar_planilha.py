import pandas as pd
import re
import datetime
import math
from database import supabase

file_path = r"c:\Users\Usuario\Downloads\BALANÇO MÊS Planilha Hotifruti J&M junho-26 (2).xlsx"

print("Lendo a planilha...")
df = pd.read_excel(file_path, header=None)

# Extrair os produtos do banco de dados atual
print("Buscando produtos do banco de dados...")
db_produtos = supabase.table("produtos").select("*").execute().data
db_map = {p['nome'].lower().strip(): p for p in db_produtos}

sucessos = 0
criados = 0

for idx in range(4, len(df)):
    row = df.iloc[idx]
    
    nome = str(row[0]).strip()
    if pd.isna(row[0]) or nome == 'nan' or nome == '' or nome.startswith('TOTAL') or nome.startswith('Estoque') or nome.startswith('Retirada') or nome.startswith('CAPITAL'):
        continue
        
    data_compra_raw = row[1]
    data_compra = ""
    if pd.notna(data_compra_raw):
        if isinstance(data_compra_raw, datetime.datetime):
            data_compra = data_compra_raw.strftime('%d/%m/%Y')
        else:
            data_compra = str(data_compra_raw).split()[0]
            
    try:
        preco_custo = float(row[6]) if pd.notna(row[6]) else 0.0
    except:
        preco_custo = 0.0
        
    try:
        preco_venda = float(row[7]) if pd.notna(row[7]) else 0.0
    except:
        preco_venda = 0.0
        
    estoque_str = str(row[14])
    quantidade = 0.0
    if pd.notna(row[14]) and estoque_str != 'nan':
        # Extrai apenas os números
        nums = re.findall(r'\d+', estoque_str)
        if nums:
            quantidade = float(nums[0])
            
    # Procura se o produto já existe
    nome_key = nome.lower()
    
    if nome_key in db_map:
        # Atualiza o produto existente
        prod_id = db_map[nome_key]['id']
        update_data = {
            'preco_custo': preco_custo,
            'preco_venda': preco_venda,
            'quantidade_estoque': quantidade,
            'data_compra': data_compra
        }
        supabase.table("produtos").update(update_data).eq("id", prod_id).execute()
        sucessos += 1
        print(f"[ATUALIZADO] {nome} -> Venda: R${preco_venda} | Estoque: {quantidade} | Data: {data_compra}")
    else:
        # Cria um novo produto
        insert_data = {
            'nome': nome,
            'codigo_barras': '',
            'categoria': 'Mercearia', # Categoria genérica para os da planilha
            'preco_custo': preco_custo,
            'preco_venda': preco_venda,
            'quantidade_estoque': quantidade,
            'data_compra': data_compra,
            'imagem_url': ''
        }
        supabase.table("produtos").insert(insert_data).execute()
        criados += 1
        print(f"[CRIADO] {nome} -> Venda: R${preco_venda} | Estoque: {quantidade} | Data: {data_compra}")

print("=======================================")
print(f"Migração concluída!")
print(f"Produtos atualizados: {sucessos}")
print(f"Produtos criados: {criados}")
print("=======================================")
