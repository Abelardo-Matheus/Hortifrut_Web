import sqlite3
import os
import sys

# Adiciona o diretório atual ao path para importar o módulo database.py
sys.path.append(r"c:\Users\Usuario\Documents\Hortifrut_Web")
from database import supabase

def migrar_imagens():
    db_path = r"c:\Users\Usuario\Documents\Hortifrut\mercearia.db"
    
    if not os.path.exists(db_path):
        print(f"Erro: Banco local {db_path} não encontrado.")
        return
        
    print(f"Conectando ao banco local SQLite: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produtos WHERE caminho_imagem IS NOT NULL AND caminho_imagem != ''")
    produtos_com_imagem = cursor.fetchall()

    print(f"Encontrados {len(produtos_com_imagem)} produtos com imagem no SQLite local.")

    for p in produtos_com_imagem:
        caminho_local = p['caminho_imagem']
        caminho_absoluto = os.path.join(r"c:\Users\Usuario\Documents\Hortifrut", caminho_local)

        if not os.path.exists(caminho_absoluto):
            print(f"Aviso: Imagem não encontrada localmente: {caminho_absoluto}")
            continue
        
        nome_arquivo = os.path.basename(caminho_absoluto)
        print(f"\nProcessando imagem: {nome_arquivo}")
        
        try:
            # 1. Enviar para Supabase Storage
            # Se der erro de duplicate, cai no except e apenas pegamos a URL
            res = supabase.storage.from_("produtos").upload(
                path=nome_arquivo,
                file=caminho_absoluto,
                file_options={"content-type": "image/jpeg"} 
            )
            
            url_publica = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
            print(f"Upload concluído. URL Pública: {url_publica}")

            # 2. Atualizar produto correspondente no Supabase
            nome_produto = p['nome']
            codigo_barras = p['codigo_barras']

            if codigo_barras:
                supabase.table("produtos").update({"imagem_url": url_publica}).eq("codigo_barras", codigo_barras).execute()
            else:
                supabase.table("produtos").update({"imagem_url": url_publica}).eq("nome", nome_produto).execute()

            print(f"Produto '{nome_produto}' atualizado no Supabase com a nova imagem.")
            
        except Exception as e:
            # Verifica se já existe ou ocorreu outro erro
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower() or "409" in str(e):
                print(f"A imagem {nome_arquivo} já existe no Supabase. Atualizando banco com a URL existente...")
                url_publica = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                nome_produto = p['nome']
                codigo_barras = p['codigo_barras']

                if codigo_barras:
                    supabase.table("produtos").update({"imagem_url": url_publica}).eq("codigo_barras", codigo_barras).execute()
                else:
                    supabase.table("produtos").update({"imagem_url": url_publica}).eq("nome", nome_produto).execute()
                print(f"Produto '{nome_produto}' atualizado com a URL existente.")
            else:
                print(f"Erro ao processar {nome_arquivo}: {e}")

if __name__ == "__main__":
    migrar_imagens()
