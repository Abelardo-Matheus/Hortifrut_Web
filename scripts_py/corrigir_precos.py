import pandas as pd
import re
from database import supabase

file_path = r"c:\Users\Usuario\Downloads\BALANÇO MÊS Planilha Hotifruti J&M junho-26 (2).xlsx"
df = pd.read_excel(file_path, header=None)

db_produtos = supabase.table("produtos").select("*").execute().data
db_map = {p['nome'].lower().strip(): p for p in db_produtos}

def parse_price(val):
    if pd.isna(val): return 0.0
    val_str = str(val).strip().lower()
    
    # Ex: "6 p/1,00" ou "5 p/1,00"
    match = re.match(r'(\d+)\s*p/([0-9.,]+)', val_str)
    if match:
        qtd = float(match.group(1))
        preco_str = match.group(2).replace(',', '.')
        # Corrige apenas casos como ".0,50" -> "0.50"
        if preco_str.startswith('.'):
            preco_str = '0' + preco_str
        try:
            preco_total = float(preco_str)
            return round(preco_total / qtd, 2)
        except Exception as e:
            pass
            
    # Remove textos extras
    val_str = val_str.replace('p/unid.', '').replace('p/porção', '').replace(',', '.').replace('p/1.00', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

def parse_qty(val):
    if pd.isna(val): return 0.0
    val_str = str(val)
    if val_str == 'nan': return 0.0
    
    nums = re.findall(r'\d+', val_str)
    if nums:
        return float(nums[0])
    return 0.0

sucessos = 0
for idx in range(4, len(df)):
    row = df.iloc[idx]
    
    nome = str(row[0]).strip()
    if pd.isna(row[0]) or nome == 'nan' or nome == '' or nome.startswith('TOTAL') or nome.startswith('Estoque') or nome.startswith('Retirada') or nome.startswith('CAPITAL'):
        continue
        
    preco_custo = parse_price(row[6])
    preco_venda = parse_price(row[7])
    quantidade = parse_qty(row[14])
            
    nome_key = nome.lower()
    
    if nome_key in db_map:
        prod_id = db_map[nome_key]['id']
        update_data = {
            'preco_custo': preco_custo,
            'preco_venda': preco_venda,
            'quantidade_estoque': quantidade
        }
        supabase.table("produtos").update(update_data).eq("id", prod_id).execute()
        sucessos += 1
        print(f"[CORRIGIDO] {nome} -> Custo: {preco_custo} | Venda: R${preco_venda} | Estoque: {quantidade}")

print(f"Total corrigidos novamente: {sucessos}")
