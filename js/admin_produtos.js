// ==========================================
// CRUD de Produtos (Admin)
// ==========================================

let adminProducts = [];
const buscaInput = document.getElementById('buscaProdutoAdmin');
const modalProduto = document.getElementById('modalProduto');
const formProduto = document.getElementById('formProduto');

// Busca produtos ao iniciar
async function fetchAdminProdutos() {
    try {
        const { data, error } = await supabase.from('produtos').select('*').order('nome');
        if (error) throw error;
        adminProducts = data;
        renderAdminTable(adminProducts);
        document.dispatchEvent(new Event('produtosCarregados'));
    } catch (err) {
        console.error("Erro ao buscar produtos admin:", err);
        const grid = document.getElementById('gridAdminProdutos');
        grid.innerHTML = `<p style="color:red; text-align:center; width:100%;">Erro ao carregar banco de dados.</p>`;
    }
}

function renderAdminTable(produtos) {
    const grid = document.getElementById('gridAdminProdutos');
    if(produtos.length === 0) {
        grid.innerHTML = `<p style="text-align:center; width:100%;">Nenhum produto cadastrado.</p>`;
        return;
    }

    grid.innerHTML = '';
    produtos.forEach(p => {
        const card = document.createElement('div');
        card.className = 'st-card';
        
        let imgHtml = p.imagem_url 
            ? `<div style="display: flex; justify-content: center; height: 100px; align-items: center; margin-bottom: 5px;"><img src="${p.imagem_url}" style="max-width: 100%; max-height: 100px; object-fit: contain; border-radius: 5px;"></div>` 
            : `<div style="height: 105px; display:flex; align-items:center; justify-content:center; border-radius:5px; opacity: 0.5;">Sem Foto</div>`;

        let estoqueHtml = p.producao_propria
            ? `Estoque: ${p.quantidade_estoque > 0 ? 'Disponível' : 'Não Disponível'} (Prod. Própria)`
            : `Estoque: ${p.quantidade_estoque} ${p.unidade_medida || 'Un'}`;

        card.innerHTML = `
            ${imgHtml}
            <div style="text-align:center;font-size:15px;font-weight:bold;margin-bottom:5px;line-height:1.2;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;" title="${p.nome}">${p.nome}</div>
            <div style="margin-top:auto;font-size: 14px; margin-bottom: 5px; text-align: center;"><b>R$ ${Number(p.preco_venda).toFixed(2).replace('.', ',')}</b></div>
            <div style="font-size: 13px; opacity: 0.7; margin-bottom: 10px; text-align: center;">${estoqueHtml}</div>
            <button class="st-button btn-full-width" onclick='abrirModalEdicao(${JSON.stringify(p)})'>✏️ Editar</button>
            <button class="st-button btn-full-width" style="margin-top:5px; border-color: rgba(231,76,60,0.5); color:#e74c3c;" onclick="excluirProduto(${p.id})">🗑️ Excluir</button>
        `;
        grid.appendChild(card);
    });
}

// Filtro Admin
buscaInput.addEventListener('input', (e) => {
    const t = e.target.value.toLowerCase();
    const filtrados = adminProducts.filter(p => 
        p.nome.toLowerCase().includes(t) || 
        (p.codigo_barras && p.codigo_barras.toLowerCase().includes(t))
    );
    renderAdminTable(filtrados);
});

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
    document.getElementById('prodMedida').value = p.unidade_medida || 'Un';
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

        // 1. Salvar dados no banco (Upsert ou Insert/Update)
        if (id) {
            const { data, error } = await supabase.from('produtos').update(dados).eq('id', id).select();
            if (error) throw error;
            produtoSalvo = data[0];
        } else {
            const { data, error } = await supabase.from('produtos').insert([dados]).select();
            if (error) throw error;
            produtoSalvo = data[0];
        }

        // 2. Upload de Foto se existir
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
    if(confirm("Tem certeza que deseja excluir este produto?")) {
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
