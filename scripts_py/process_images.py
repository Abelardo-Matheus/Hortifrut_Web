import sqlite3
import os
import sys
import io
import urllib.parse
from PIL import Image

sys.path.append(r"c:\Users\Usuario\Documents\Hortifrut_Web")
from database import supabase

try:
    from rembg import remove
except ImportError:
    print("rembg não instalado. Execute pip install rembg primeiro.")
    sys.exit(1)

def main():
    # 1. Fetch all products from Supabase that have an image_url
    print("Buscando produtos no Supabase...")
    res = supabase.table("produtos").select("id, nome, imagem_url").neq("imagem_url", "").execute()
    produtos = res.data
    
    print(f"Encontrados {len(produtos)} produtos com imagem.")
    
    pasta_imagens = r"c:\Users\Usuario\Documents\Hortifrut\imagens"
    
    for p in produtos:
        url = p['imagem_url']
        if not url: continue
        
        # O nome do arquivo no final da URL
        filename_encoded = url.split('/')[-1].split('?')[0]
        filename = urllib.parse.unquote(filename_encoded)
        
        caminho_local = os.path.join(pasta_imagens, filename)
        
        if not os.path.exists(caminho_local):
            print(f"Aviso: Imagem local não encontrada para {p['nome']} -> {filename}")
            continue
            
        print(f"\nProcessando imagem de: {p['nome']} ({filename})")
        
        # Novo nome
        name_no_ext = os.path.splitext(filename)[0]
        new_filename = f"{name_no_ext}_nobg.png"
        
        try:
            # Carregar, remover fundo e salvar em memória
            input_image = Image.open(caminho_local)
            output_image = remove(input_image)
            
            img_byte_arr = io.BytesIO()
            output_image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Upload para Supabase
            print("Fazendo upload para o Supabase...")
            # Tenta remover caso já exista
            try:
                supabase.storage.from_("produtos").remove([new_filename])
            except:
                pass
                
            supabase.storage.from_("produtos").upload(
                path=new_filename,
                file=img_byte_arr.read(),
                file_options={"content-type": "image/png"}
            )
            
            url_publica = supabase.storage.from_("produtos").get_public_url(new_filename)
            
            # Atualiza banco
            supabase.table("produtos").update({"imagem_url": url_publica}).eq("id", p['id']).execute()
            print(f"OK! {p['nome']} atualizado com sucesso com fundo transparente.")
            
        except Exception as e:
            print(f"Erro ao processar {p['nome']}: {e}")

if __name__ == "__main__":
    main()
