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
    unidade_medida TEXT NOT NULL DEFAULT 'UN', -- 'UN' (Unidade) ou 'KG' (Quilo)
    imagem_url TEXT,
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
