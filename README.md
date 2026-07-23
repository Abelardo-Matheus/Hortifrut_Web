# Hortifruti Online (Streamlit + Supabase)

Este é o guia completo para colocar o seu sistema de Hortifruti no ar, acessível de qualquer lugar, 100% gratuito e hospedado na nuvem.

## Passo 1: Configurando o Banco de Dados (Supabase)

O Supabase é um banco de dados poderoso e gratuito.
1. Acesse [supabase.com](https://supabase.com) e crie uma conta (pode usar o seu GitHub).
2. Clique em **"New Project"**, dê o nome de "HortifrutDB", coloque uma senha forte e escolha a região mais próxima (ex: São Paulo). Aguarde alguns minutos para o banco ser criado.
3. No menu lateral esquerdo do Supabase, clique em **"SQL Editor"** e depois em **"New Query"**.
4. Abra o arquivo `schema.sql` (que está nesta pasta), copie todo o texto dentro dele, cole no SQL Editor do Supabase e clique em **"Run"**.
   - *Isso vai criar as tabelas `produtos`, `vendas`, `itens_venda` e as regras de segurança automaticamente.*
5. Agora pegue suas senhas: vá em **Project Settings -> API**. Copie a `URL` do projeto e a `anon key`.

---

## Passo 2: Testando o Projeto no seu Computador (Local)

1. Crie uma cópia do arquivo `.env.example` e renomeie apenas para `.env`.
2. Abra o `.env` no bloco de notas e cole a sua URL e KEY copiadas no passo anterior.
3. Abra o terminal na pasta `Hortifrut_Web` e instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Rode a aplicação:
   ```bash
   streamlit run app.py
   ```
5. O navegador vai abrir o sistema. Faça alguns cadastros para garantir que conectou certinho com o banco de dados.

---

## Passo 3: Colocando o Código no GitHub

Para que o site fique 100% online, ele precisa estar no GitHub.
1. Crie uma conta no [GitHub](https://github.com).
2. Crie um novo repositório (ex: `hortifruti-web`).
3. Envie TODOS os arquivos desta pasta `Hortifrut_Web` para o seu repositório no GitHub (não envie o `.env`).

---

## Passo 4: Colocando no Ar (Streamlit Community Cloud)

O Streamlit Cloud vai ler o seu GitHub e gerar um site oficial.
1. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com a sua conta do GitHub.
2. Clique em **"New app"**.
3. Selecione o repositório que você acabou de criar (`hortifruti-web`).
4. Selecione `app.py` como o *Main file path*.
5. **ATENÇÃO:** Clique em **"Advanced settings"** (Configurações Avançadas).
   - Lembra que você não enviou o `.env` para o GitHub? Aqui é onde você vai colocar os segredos. 
   - No campo de *Secrets*, cole:
     ```toml
     SUPABASE_URL="sua-url-do-supabase-aqui"
     SUPABASE_KEY="sua-chave-anon-aqui"
     ```
6. Clique em **"Deploy!"**

**Pronto!** Em 2 minutos, o Streamlit vai te dar um link (ex: `https://seu-hortifruti.streamlit.app`). Você pode salvar esse link no computador antigo dos seus pais, e eles poderão usar o caixa perfeitamente pelo navegador. Quando você quiser atualizar o sistema, basta mudar o código e enviar para o GitHub, que o site atualiza sozinho!
