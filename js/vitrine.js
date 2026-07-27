// ==========================================
// Lógica da Vitrine Pública
// ==========================================

let allProducts = [];

// Elementos da DOM
const vitrineGrid = document.getElementById('vitrineGrid');
const searchInput = document.getElementById('searchInput');

// Função de inicialização
async function carregarProdutos() {
    try {
        const { data, error } = await supabase
            .from('produtos')
            .select('*')
            .order('nome', { ascending: true });

        if (error) {
            console.error("Erro ao buscar produtos:", error);
            vitrineGrid.innerHTML = `<p style="color:red; text-align:center; width:100%;">Erro ao carregar produtos. Tente recarregar a página.</p>`;
            return;
        }

        allProducts = data;
        renderizarProdutos(allProducts);
    } catch (err) {
        console.error("Erro inesperado:", err);
    }
}

// Renderiza a lista de produtos na grade
function renderizarProdutos(produtos) {
    if (produtos.length === 0) {
        vitrineGrid.innerHTML = `<p style="text-align:center; width:100%; color:var(--text-secondary);">Nenhum produto encontrado.</p>`;
        return;
    }

    vitrineGrid.innerHTML = '';
    
    produtos.forEach(p => {
        const card = document.createElement('div');
        card.className = 'vitrine-card';

        // Imagem HTML
        let imgHtml = '';
        if (p.imagem_url) {
            imgHtml = `<img src="${p.imagem_url}" class="blend-img" loading="lazy" alt="${p.nome}">`;
        } else {
            imgHtml = `<div class="sem-imagem">Sem Foto</div>`;
        }

        // Preço formatado
        const precoFormatado = Number(p.preco_venda).toFixed(2).replace('.', ',');

        // Estoque HTML
        let estoqueHtml = '';
        if (p.producao_propria) {
            if (p.quantidade_estoque > 0) {
                estoqueHtml = `<div class="vitrine-estoque disp">Disponível <br><span style="font-size:10px; opacity:0.7">(Prod. Própria)</span></div>`;
            } else {
                estoqueHtml = `<div class="vitrine-estoque esgot">Não Disponível <br><span style="font-size:10px; opacity:0.7">(Prod. Própria)</span></div>`;
            }
        } else {
            if (p.quantidade_estoque > 0) {
                const numEstoque = p.quantidade_estoque % 1 === 0 ? p.quantidade_estoque : Number(p.quantidade_estoque).toFixed(3);
                estoqueHtml = `<div class="vitrine-estoque disp">Estoque: ${numEstoque} ${p.unidade_medida || 'Un'}</div>`;
            } else {
                estoqueHtml = `<div class="vitrine-estoque esgot">Esgotado</div>`;
            }
        }

        card.innerHTML = `
            <div class="vitrine-img-container">${imgHtml}</div>
            <div class="vitrine-nome">${p.nome}</div>
            <div class="vitrine-preco">R$ ${precoFormatado} <span>/${p.unidade_medida || 'Un'}</span></div>
            ${estoqueHtml}
        `;
        
        vitrineGrid.appendChild(card);
    });
}

// Filtro de Busca
searchInput.addEventListener('input', (e) => {
    const termo = e.target.value.toLowerCase();
    const filtrados = allProducts.filter(p => 
        p.nome.toLowerCase().includes(termo) || 
        (p.codigo_barras && p.codigo_barras.toLowerCase().includes(termo))
    );
    renderizarProdutos(filtrados);
});

// Inicializa a vitrine ao carregar a página
document.addEventListener('DOMContentLoaded', carregarProdutos);
