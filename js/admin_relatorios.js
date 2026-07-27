// ==========================================
// Aba: Resumo de Vendas (Relatórios)
// ==========================================

const btnRelGeral = document.getElementById('btnRelGeral');
const btnRelPP = document.getElementById('btnRelPP');
const relGeral = document.getElementById('relGeral');
const relPP = document.getElementById('relPP');

// Alternar Sub-abas
btnRelGeral.addEventListener('click', () => {
    btnRelGeral.classList.add('active');
    btnRelPP.classList.remove('active');
    relGeral.style.display = 'block';
    relPP.style.display = 'none';
});

btnRelPP.addEventListener('click', () => {
    btnRelPP.classList.add('active');
    btnRelGeral.classList.remove('active');
    relPP.style.display = 'block';
    relGeral.style.display = 'none';
});

// Elementos DOM
const metricTotalHoje = document.getElementById('metricTotalHoje');
const metricLucroHoje = document.getElementById('metricLucroHoje');
const metricQtdHoje = document.getElementById('metricQtdHoje');
const listaVendasGeral = document.getElementById('listaVendasGeral');

const metricPptotal = document.getElementById('metricPptotal');
const metricPplucro = document.getElementById('metricPplucro');
const metricPpQtd = document.getElementById('metricPpQtd');

// Inicialização: Escutar clique na aba principal de relatórios
document.querySelector('[data-tab="tab-balanco"]').addEventListener('click', () => {
    fetchRelatorios();
    fetchProducaoPropria();
});

async function fetchRelatorios() {
    try {
        const { data: vendas, error } = await window.supabase
            .from('vendas')
            .select('*')
            .order('data_venda', { ascending: false });

        if(error) throw error;

        // Filtra vendas de hoje
        const hoje = new Date().toLocaleDateString('pt-BR');
        let totalHoje = 0;
        let lucroHoje = 0;
        let qtdHoje = 0;

        vendas.forEach(v => {
            const dataVenda = new Date(v.data_venda).toLocaleDateString('pt-BR');
            if (dataVenda === hoje) {
                totalHoje += v.valor_total;
                lucroHoje += v.lucro_total;
                qtdHoje++;
            }
        });

        metricTotalHoje.textContent = `R$ ${totalHoje.toFixed(2)}`;
        metricLucroHoje.textContent = `R$ ${lucroHoje.toFixed(2)}`;
        metricQtdHoje.textContent = qtdHoje;

        // Renderiza lista das últimas 100
        listaVendasGeral.innerHTML = '';
        if(vendas.length === 0) {
            listaVendasGeral.innerHTML = `<div style="color:var(--text-secondary);">Ainda não há histórico de vendas registrado no banco.</div>`;
            return;
        }

        const ultimas100 = vendas.slice(0, 100);
        ultimas100.forEach(v => {
            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.marginBottom = '10px';
            
            const dateFmt = new Date(v.data_venda).toLocaleString('pt-BR', { dateStyle:'short', timeStyle:'short' });

            row.innerHTML = `
                <div style="flex:2;">📅 ${dateFmt}</div>
                <div style="flex:1;">Pag: ${v.forma_pagamento}</div>
                <div style="flex:1;">💰 <strong>R$ ${v.valor_total.toFixed(2)}</strong></div>
                <button class="st-button" style="padding:5px; border-color:#e74c3c; color:#e74c3c;" onclick="excluirVenda(${v.id})">🗑️</button>
            `;
            listaVendasGeral.appendChild(row);
        });

    } catch (err) {
        console.error("Erro ao buscar relatórios:", err);
    }
}

window.excluirVenda = async function(id) {
    if(confirm("Excluir esta venda? O estoque não será revertido automaticamente nesta versão simples (somente registro financeiro será apagado). Deseja continuar?")) {
        try {
            await window.supabase.from('vendas').delete().eq('id', id);
            alert("Venda excluída com sucesso.");
            fetchRelatorios();
            fetchProducaoPropria();
        } catch(e) {
            alert("Erro ao excluir venda");
        }
    }
}

async function fetchProducaoPropria() {
    try {
        const now = new Date();
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
        
        // Busca todos os itens de venda que pertencem ao mês atual e que têm producao_propria = true
        // Para simplificar, buscamos os itens de venda join com produtos e join com vendas
        const { data, error } = await window.supabase
            .from('itens_venda')
            .select(`
                *,
                produtos!inner(*),
                vendas!inner(*)
            `)
            .eq('produtos.producao_propria', true)
            .gte('vendas.data_venda', startOfMonth);

        if(error) throw error;

        let totalVendido = 0;
        let totalLucro = 0;
        let totalQtd = 0;

        data.forEach(item => {
            totalQtd += item.quantidade;
            totalVendido += item.subtotal;
            const custoItem = item.quantidade * (item.produtos.preco_custo || 0);
            totalLucro += (item.subtotal - custoItem);
        });

        metricPptotal.textContent = `R$ ${totalVendido.toFixed(2)}`;
        metricPplucro.textContent = `R$ ${totalLucro.toFixed(2)}`;
        metricPpQtd.textContent = totalQtd.toFixed(2);

    } catch(err) {
        console.error("Erro ao buscar relatório de PP:", err);
    }
}
