-- ==========================================
-- Hortifrut Web - Supabase Schema
-- ==========================================

-- 1. Criação das Tabelas

-- Tabela de Produtos
CREATE TABLE produtos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    codigo_barras TEXT,
    categoria TEXT DEFAULT 'Outros',
    preco_custo NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    preco_venda NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    quantidade_estoque NUMERIC(10, 3) NOT NULL DEFAULT 0.000,
    data_compra TEXT,
    imagem_url TEXT,
    unidade_medida TEXT DEFAULT 'Un',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Vendas
CREATE TABLE vendas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_venda TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valor_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    lucro_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    forma_pagamento TEXT DEFAULT 'Dinheiro'
);

-- Tabela de Itens da Venda
CREATE TABLE itens_venda (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id UUID REFERENCES vendas(id) ON DELETE CASCADE,
    produto_id UUID REFERENCES produtos(id) ON DELETE SET NULL,
    quantidade NUMERIC(10, 3) NOT NULL,
    preco_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
);

-- Tabela de Clientes (Fiado/Anotado)
CREATE TABLE clientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL UNIQUE,
    telefone TEXT,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Compras Anotadas (Fiado)
CREATE TABLE compras_anotadas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES clientes(id) ON DELETE CASCADE,
    produto_id UUID REFERENCES produtos(id) ON DELETE SET NULL,
    quantidade NUMERIC(10, 3) NOT NULL,
    preco_unitario NUMERIC(10, 2) NOT NULL,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pago BOOLEAN NOT NULL DEFAULT FALSE
);

-- Tabela de Retiradas para Casa
CREATE TABLE retiradas_casa (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    produto_id UUID REFERENCES produtos(id) ON DELETE SET NULL,
    quantidade NUMERIC(10, 3) NOT NULL,
    custo_unitario NUMERIC(10, 2) NOT NULL
);

-- Tabela de Balanço Mensal
CREATE TABLE balanco_mensal (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mes INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    estoque_inicial NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    estoque_final NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    UNIQUE(mes, ano)
);

-- Tabela de Usuários (Admins)
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- 2. Configurações de Segurança RLS 
-- (Row Level Security)
-- ==========================================
-- Por padrão, vamos permitir leitura e escrita pública anônima. 
-- ATENÇÃO: Para um sistema real em produção aberto na internet, 
-- é recomendado implementar Autenticação (Supabase Auth). 
-- Como este sistema será acessado apenas pelos donos do hortifruti 
-- e não terá dados super sigilosos na primeira versão, vamos habilitar acesso anônimo seguro 
-- baseado nas chaves (anon key).

ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas ENABLE ROW LEVEL SECURITY;
ALTER TABLE itens_venda ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE compras_anotadas ENABLE ROW LEVEL SECURITY;
ALTER TABLE retiradas_casa ENABLE ROW LEVEL SECURITY;
ALTER TABLE balanco_mensal ENABLE ROW LEVEL SECURITY;

-- Políticas para Produtos
CREATE POLICY "Permitir leitura pública de produtos" ON produtos FOR SELECT USING (true);
CREATE POLICY "Permitir inserção de produtos" ON produtos FOR INSERT WITH CHECK (true);
CREATE POLICY "Permitir atualização de produtos" ON produtos FOR UPDATE USING (true);
CREATE POLICY "Permitir deleção de produtos" ON produtos FOR DELETE USING (true);

-- Políticas para Vendas
CREATE POLICY "Permitir leitura de vendas" ON vendas FOR SELECT USING (true);
CREATE POLICY "Permitir inserção de vendas" ON vendas FOR INSERT WITH CHECK (true);

-- Políticas para Itens da Venda
CREATE POLICY "Permitir leitura de itens de venda" ON itens_venda FOR SELECT USING (true);
CREATE POLICY "Permitir inserção de itens de venda" ON itens_venda FOR INSERT WITH CHECK (true);

-- Políticas Básicas (Permitir CRUD completo anonimamente para agilizar o PDV local)
CREATE POLICY "Permitir tudo em clientes" ON clientes FOR ALL USING (true);
CREATE POLICY "Permitir tudo em compras_anotadas" ON compras_anotadas FOR ALL USING (true);
CREATE POLICY "Permitir tudo em retiradas_casa" ON retiradas_casa FOR ALL USING (true);
CREATE POLICY "Permitir tudo em balanco_mensal" ON balanco_mensal FOR ALL USING (true);

-- ==========================================================

-- ==========================================================
-- SOLICITAÇÕES DE PRODUTOS
-- ==========================================================
CREATE TABLE IF NOT EXISTS public.solicitacoes (
    id SERIAL PRIMARY KEY,
    nome_produto VARCHAR(255) NOT NULL,
    nome_cliente VARCHAR(255) NOT NULL,
    telefone VARCHAR(50),
    receber_whatsapp BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'Pendente' CHECK (status IN ('Pendente', 'Atendido', 'Recusado')),
    data_solicitacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
