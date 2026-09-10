// ==========================================
// CRUD de Produtos (Aba Estoque)
// ==========================================

let adminProducts = [];
const buscaInput = document.getElementById('buscaProdutoAdmin');
const modalProduto = document.getElementById('modalProduto');
const formProduto = document.getElementById('formProduto');

const ESTOQUE_CRITICO_LIMITE = 5;

function unidadeLabel(p) {
    return p.unidade_medida === 'Un' ? 'Unidade' : p.unidade_medida === 'Kg' ? 'Kilos' : (p.unidade_medida || 'Unidade');
}

function isEstoqueIlimitado(p) {
    return p.producao_propria || p.categoria === 'Horta (Ilimitado)';
}

// Busca produtos ao iniciar
async function fetchAdminProdutos() {
    try {
        const { data, error } = await supabase.from('produtos').select('*').order('nome');
        if (error) throw error;
        adminProducts = data;
        renderAdminTable(adminProducts);
        renderEstoquesCriticos(adminProducts);
        document.dispatchEvent(new Event('produtosCarregados'));
    } catch (err) {
        console.error("Erro ao buscar produtos admin:", err);
        const body = document.getElementById('estoqueBody');
        if (body) body.innerHTML = `<tr><td colspan="6" class="empty" style="color:#e74c3c;">Erro ao carregar banco de dados.</td></tr>`;
    }
}

function renderAdminTable(produtos) {
    const body = document.getElementById('estoqueBody');
    if (!body) return;

    if (produtos.length === 0) {
        body.innerHTML = `<tr><td colspan="6" class="empty">Nenhum produto cadastrado.</td></tr>`;
        return;
    }

    body.innerHTML = produtos.map(p => {
        const margem = p.preco_venda > 0 ? (((p.preco_venda - p.preco_custo) / p.preco_venda) * 100).toFixed(1) : '0.0';
        const estoqueTxt = isEstoqueIlimitado(p)
            ? (p.quantidade_estoque > 0 ? 'Disponível' : 'Não Disponível')
            : `${Number(p.quantidade_estoque) % 1 === 0 ? p.quantidade_estoque : Number(p.quantidade_estoque).toFixed(3)} ${unidadeLabel(p)}`;
        const imgHtml = p.imagem_url
            ? `<img src="${p.imagem_url}" class="td-img" alt="${p.nome}">`
            : `<div class="td-img" style="display:flex;align-items:center;justify-content:center;font-size:16px;">🥬</div>`;

        return `
            <tr>
                <td style="display:flex; align-items:center; gap:10px;">${imgHtml}<span>${p.nome}</span></td>
                <td class="center">${estoqueTxt}</td>
                <td class="center">R$ ${Number(p.preco_custo).toFixed(2)}</td>
                <td class="center">R$ ${Number(p.preco_venda).toFixed(2)}</td>
                <td class="center">${margem}%</td>
                <td class="center">
                    <button class="a-btn a-btn-outline a-btn-sm" onclick='abrirModalEdicao(${JSON.stringify(p)})'>✏️</button>
                    <button class="a-btn a-btn-danger a-btn-sm" onclick="excluirProduto('${p.id}')">🗑️</button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderEstoquesCriticos(produtos) {
    const container = document.getElementById('estoquesCriticos');
    if (!container) return;

    const criticos = produtos.filter(p => !isEstoqueIlimitado(p) && Number(p.quantidade_estoque) < ESTOQUE_CRITICO_LIMITE);

    if (criticos.length === 0) {
        container.innerHTML = `
            <div class="a-success-box" style="grid-column:1/-1;">
                <strong>✅ Estoque Ok</strong><br>Nenhum produto abaixo do mínimo (${ESTOQUE_CRITICO_LIMITE}).
            </div>`;
        return;
    }

    container.innerHTML = criticos.map(p => `
        <div class="a-critical-card">
            <div class="name">${p.nome}</div>
            <div class="stock">Estoque: <strong>${p.quantidade_estoque} ${unidadeLabel(p)}</strong></div>
            <button class="a-btn a-btn-sm" style="background:#ff9800;" onclick='abrirModalEdicao(${JSON.stringify(p)})'>Repor Estoque</button>
        </div>
    `).join('');
}

// Filtro Admin
if (buscaInput) {
    buscaInput.addEventListener('input', (e) => {
        const t = e.target.value.toLowerCase();
        const filtrados = adminProducts.filter(p =>
            p.nome.toLowerCase().includes(t) ||
            (p.codigo_barras && p.codigo_barras.toLowerCase().includes(t))
        );
        renderAdminTable(filtrados);
    });
}

// Modal Actions
document.getElementById('btnNovoProduto').addEventListener('click', () => {
    formProduto.reset();
    document.getElementById('prodId').value = '';
    document.getElementById('modalProdutoTitle').textContent = 'Novo Produto';
    modalProduto.classList.add('active');
});

function fecharModalProduto() {
    modalProduto.classList.remove('active');
}

function abrirModalEdicao(p) {
    formProduto.reset();
    document.getElementById('modalProdutoTitle').textContent = 'Editar Produto';
    document.getElementById('prodId').value = p.id;
    document.getElementById('prodNome').value = p.nome;
    document.getElementById('prodCodigo').value = p.codigo_barras || '';
    document.getElementById('prodCat').value = p.categoria;
    document.getElementById('prodMedida').value = (p.unidade_medida === 'Un' ? 'Unidade' : p.unidade_medida === 'Kg' ? 'Kilos' : p.unidade_medida) || 'Unidade';
    document.getElementById('prodCusto').value = p.preco_custo;
    document.getElementById('prodVenda').value = p.preco_venda;
    document.getElementById('prodEstoque').value = p.quantidade_estoque;
    document.getElementById('prodPropria').checked = p.producao_propria;
    modalProduto.classList.add('active');
}

// Salvar / Atualizar
formProduto.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btnSalvar = formProduto.querySelector('.btn-save');
    btnSalvar.textContent = 'Salvando...';
    btnSalvar.disabled = true;

    try {
        const id = document.getElementById('prodId').value;
        const arquivoFoto = document.getElementById('prodFoto').files[0];

        const dados = {
            nome: document.getElementById('prodNome').value,
            codigo_barras: document.getElementById('prodCodigo').value,
            categoria: document.getElementById('prodCat').value,
            unidade_medida: document.getElementById('prodMedida').value,
            preco_custo: parseFloat(document.getElementById('prodCusto').value),
            preco_venda: parseFloat(document.getElementById('prodVenda').value),
            quantidade_estoque: parseFloat(document.getElementById('prodEstoque').value),
            producao_propria: document.getElementById('prodPropria').checked
        };

        if (!id) {
            dados.data_compra = new Date().toISOString();
        }

        let produtoSalvo;

        if (id) {
            const { data, error } = await supabase.from('produtos').update(dados).eq('id', id).select();
            if (error) throw error;
            produtoSalvo = data[0];
        } else {
            const { data, error } = await supabase.from('produtos').insert([dados]).select();
            if (error) throw error;
            produtoSalvo = data[0];
        }

        if (arquivoFoto && produtoSalvo) {
            const fileExt = arquivoFoto.name.split('.').pop();
            const fileName = `${produtoSalvo.id}_${Date.now()}.${fileExt}`;

            const { error: uploadError } = await supabase.storage
                .from('produtos')
                .upload(fileName, arquivoFoto, { upsert: true });

            if (!uploadError) {
                const { data: { publicUrl } } = supabase.storage.from('produtos').getPublicUrl(fileName);
                await supabase.from('produtos').update({ imagem_url: publicUrl }).eq('id', produtoSalvo.id);
            }
        }

        fecharModalProduto();
        fetchAdminProdutos();

    } catch (err) {
        console.error("Erro ao salvar produto:", err);
        alert("Erro ao salvar o produto.");
    } finally {
        btnSalvar.textContent = 'Salvar';
        btnSalvar.disabled = false;
    }
});

// Excluir Produto
async function excluirProduto(id) {
    if (confirm("Tem certeza que deseja excluir este produto?")) {
        try {
            const { error } = await supabase.from('produtos').delete().eq('id', id);
            if (error) throw error;
            fetchAdminProdutos();
        } catch (err) {
            console.error(err);
            alert("Erro ao excluir o produto. Ele pode estar atrelado a histórico de vendas.");
        }
    }
}

document.addEventListener('DOMContentLoaded', fetchAdminProdutos);
