// ==========================================
// Aba: Vendas (Dashboard + Relatórios)
// ==========================================

let dashboardVendasPeriodo = [];
let dashboardItensPeriodo = [];

function getInicioPeriodo(periodo) {
    const now = new Date();
    switch (periodo) {
        case 'hoje':
            return new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString();
        case 'semana': {
            const d = new Date(now);
            const diaSemana = d.getDay(); // 0=domingo
            d.setDate(d.getDate() - diaSemana);
            d.setHours(0, 0, 0, 0);
            return d.toISOString();
        }
        case 'ano':
            return new Date(now.getFullYear(), 0, 1).toISOString();
        case 'tudo':
            return '1970-01-01T00:00:00.000Z';
        case 'mes':
        default:
            return new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
    }
}

function fmtMoeda(v) {
    return `R$ ${Number(v || 0).toFixed(2)}`;
}

// ---------- Métricas fixas de "Hoje" (independem do filtro de período) ----------
async function atualizarMetricasHoje() {
    try {
        const inicioHoje = new Date(new Date().setHours(0, 0, 0, 0)).toISOString();
        const { data: vendasHoje, error } = await window.supabase
            .from('vendas')
            .select('*')
            .gte('data_venda', inicioHoje);
        if (error) throw error;

        const totalHoje = vendasHoje.reduce((a, v) => a + Number(v.valor_total), 0);
        const lucroHoje = vendasHoje.reduce((a, v) => a + Number(v.lucro_total), 0);

        document.getElementById('metricVendasHoje').textContent = fmtMoeda(totalHoje);
        document.getElementById('metricTransacoesHoje').textContent = `${vendasHoje.length} transações`;
        document.getElementById('metricLucroHoje').textContent = fmtMoeda(lucroHoje);
        document.getElementById('metricMargemHoje').textContent = totalHoje > 0 ? `${((lucroHoje / totalHoje) * 100).toFixed(1)}%` : '0%';
    } catch (err) {
        console.error('Erro ao buscar métricas de hoje:', err);
    }
}

// ---------- Métricas de estoque (depende dos produtos já carregados) ----------
function atualizarMetricasEstoque() {
    if (typeof adminProducts === 'undefined' || !adminProducts) return;
    document.getElementById('metricEstoqueTotal').textContent = adminProducts.length;
    const baixos = adminProducts.filter(p =>
        !(p.producao_propria || p.categoria === 'Horta (Ilimitado)') &&
        Number(p.quantidade_estoque) < (typeof ESTOQUE_CRITICO_LIMITE !== 'undefined' ? ESTOQUE_CRITICO_LIMITE : 5)
    ).length;
    document.getElementById('metricProdutosBaixos').textContent = baixos;

    const estoqueFinalEl = document.getElementById('estoqueFinalTotal');
    if (estoqueFinalEl) {
        const totalEstoque = adminProducts.reduce((a, p) => a + (p.producao_propria || p.categoria === 'Horta (Ilimitado)' ? 0 : Number(p.quantidade_estoque)), 0);
        estoqueFinalEl.textContent = `${totalEstoque % 1 === 0 ? totalEstoque : totalEstoque.toFixed(2)}`;
    }
}
document.addEventListener('produtosCarregados', atualizarMetricasEstoque);

// ---------- Carrega vendas + itens do período selecionado ----------
async function fetchDashboardVendas() {
    const periodo = document.getElementById('periodoVendas').value;
    const inicio = getInicioPeriodo(periodo);

    atualizarMetricasHoje();
    atualizarMetricasEstoque();

    try {
        const { data: vendas, error: errVendas } = await window.supabase
            .from('vendas')
            .select('*')
            .gte('data_venda', inicio)
            .order('data_venda', { ascending: false });
        if (errVendas) throw errVendas;
        dashboardVendasPeriodo = vendas || [];

        const { data: itens, error: errItens } = await window.supabase
            .from('itens_venda')
            .select('*, produtos(*), vendas!inner(*)')
            .gte('vendas.data_venda', inicio);
        if (errItens) throw errItens;
        dashboardItensPeriodo = itens || [];

        renderDashboardVendas();
    } catch (err) {
        console.error('Erro ao buscar dashboard de vendas:', err);
        document.getElementById('tabelaVendasTotais').innerHTML = `<tr><td colspan="7" class="empty" style="color:#e74c3c;">Erro ao carregar vendas.</td></tr>`;
    }
}
window.fetchDashboardVendas = fetchDashboardVendas;

function renderDashboardVendas() {
    const termo = (document.getElementById('buscaVendas').value || '').toLowerCase();

    // Mapa venda_id -> soma de quantidade de itens (para a coluna "Qtd Itens")
    const qtdPorVenda = {};
    const produtoPorVenda = {}; // venda_id -> set de nomes de produto (para busca)
    dashboardItensPeriodo.forEach(i => {
        qtdPorVenda[i.venda_id] = (qtdPorVenda[i.venda_id] || 0) + Number(i.quantidade);
        if (!produtoPorVenda[i.venda_id]) produtoPorVenda[i.venda_id] = [];
        if (i.produtos) produtoPorVenda[i.venda_id].push(i.produtos.nome.toLowerCase());
    });

    // ===== VIEW: TOTAIS =====
    const vendasFiltradas = dashboardVendasPeriodo.filter(v => {
        if (!termo) return true;
        const nomes = produtoPorVenda[v.id] || [];
        return nomes.some(n => n.includes(termo)) || (v.forma_pagamento || '').toLowerCase().includes(termo);
    });

    const tabelaVendasTotais = document.getElementById('tabelaVendasTotais');
    if (vendasFiltradas.length === 0) {
        tabelaVendasTotais.innerHTML = `<tr><td colspan="7" class="empty">Nenhuma venda encontrada no período.</td></tr>`;
    } else {
        tabelaVendasTotais.innerHTML = vendasFiltradas.map(v => {
            const dateFmt = new Date(v.data_venda).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
            const qtd = qtdPorVenda[v.id] || 0;
            return `
                <tr>
                    <td>${dateFmt}</td>
                    <td>Balcão</td>
                    <td class="center">${qtd % 1 === 0 ? qtd : qtd.toFixed(2)}</td>
                    <td class="right" style="font-weight:600;">${fmtMoeda(v.valor_total)}</td>
                    <td class="right" style="color:#27ae60; font-weight:600;">${fmtMoeda(v.lucro_total)}</td>
                    <td class="center"><span class="a-badge">${v.forma_pagamento}</span></td>
                    <td class="center">
                        <button class="a-btn a-btn-outline a-btn-sm" onclick='editarVenda(${JSON.stringify(v)})'>✏️</button>
                        <button class="a-btn a-btn-danger a-btn-sm" onclick="excluirVenda('${v.id}')">🗑️</button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    const faturamentoTotal = vendasFiltradas.reduce((a, v) => a + Number(v.valor_total), 0);
    const lucroTotalPeriodo = vendasFiltradas.reduce((a, v) => a + Number(v.lucro_total), 0);
    const qtdVendidaTotal = dashboardItensPeriodo.reduce((a, i) => a + Number(i.quantidade), 0);

    document.getElementById('qtdVendidaTotal').textContent = qtdVendidaTotal % 1 === 0 ? qtdVendidaTotal : qtdVendidaTotal.toFixed(2);
    document.getElementById('faturamentoTotal').textContent = fmtMoeda(faturamentoTotal);
    document.getElementById('lucroTotalPeriodo').textContent = fmtMoeda(lucroTotalPeriodo);
    document.getElementById('margemTotalPeriodo').textContent = faturamentoTotal > 0 ? `${((lucroTotalPeriodo / faturamentoTotal) * 100).toFixed(1)}%` : '0%';

    // ===== VIEW: COMPRADOS (produtos revendidos, não produção própria) =====
    const compradosRows = dashboardItensPeriodo.filter(i => i.produtos && !i.produtos.producao_propria &&
        (!termo || i.produtos.nome.toLowerCase().includes(termo)));
    renderTabelaItens('tabelaVendasCompradas', compradosRows);

    const qtdVendidaComp = compradosRows.reduce((a, i) => a + Number(i.quantidade), 0);
    const totalComp = compradosRows.reduce((a, i) => a + Number(i.subtotal), 0);
    const custoComp = compradosRows.reduce((a, i) => a + (Number(i.quantidade) * Number(i.produtos.preco_custo || 0)), 0);
    const lucroComp = totalComp - custoComp;

    document.getElementById('qtdVendidaComp').textContent = qtdVendidaComp % 1 === 0 ? qtdVendidaComp : qtdVendidaComp.toFixed(2);
    document.getElementById('faturamentoComp').textContent = fmtMoeda(totalComp);
    document.getElementById('lucroComp').textContent = fmtMoeda(lucroComp);
    document.getElementById('margemComp').textContent = totalComp > 0 ? `${((lucroComp / totalComp) * 100).toFixed(1)}%` : '0%';

    // ===== VIEW: PRODUÇÃO PRÓPRIA =====
    const propriaRows = dashboardItensPeriodo.filter(i => i.produtos && i.produtos.producao_propria &&
        (!termo || i.produtos.nome.toLowerCase().includes(termo)));
    renderTabelaItens('tabelaVendasPropria', propriaRows);

    const qtdVendidaProp = propriaRows.reduce((a, i) => a + Number(i.quantidade), 0);
    const totalProp = propriaRows.reduce((a, i) => a + Number(i.subtotal), 0);
    const custoProp = propriaRows.reduce((a, i) => a + (Number(i.quantidade) * Number(i.produtos.preco_custo || 0)), 0);
    const lucroProp = totalProp - custoProp;

    document.getElementById('qtdVendidaProp').textContent = qtdVendidaProp % 1 === 0 ? qtdVendidaProp : qtdVendidaProp.toFixed(2);
    document.getElementById('faturamentoProp').textContent = fmtMoeda(totalProp);
    document.getElementById('lucroProp').textContent = fmtMoeda(lucroProp);
    document.getElementById('margemProp').textContent = totalProp > 0 ? `${((lucroProp / totalProp) * 100).toFixed(1)}%` : '0%';
}

function renderTabelaItens(tbodyId, rows) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty">Nenhum item encontrado no período.</td></tr>`;
        return;
    }
    tbody.innerHTML = rows.map(i => {
        const dateFmt = new Date(i.vendas.data_venda).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
        const custoUnit = Number(i.produtos.preco_custo || 0);
        const lucro = Number(i.subtotal) - (Number(i.quantidade) * custoUnit);
        return `
            <tr>
                <td>${dateFmt}</td>
                <td>${i.produtos.nome}</td>
                <td class="center">${i.quantidade}</td>
                <td class="right">${fmtMoeda(i.preco_unitario)}</td>
                <td class="right" style="font-weight:600;">${fmtMoeda(i.subtotal)}</td>
                <td class="right">${fmtMoeda(custoUnit)}</td>
                <td class="right" style="color:#27ae60; font-weight:600;">${fmtMoeda(lucro)}</td>
            </tr>
        `;
    }).join('');
}

// ---------- Editar / Excluir Venda ----------
window.excluirVenda = async function (id) {
    if (confirm("Excluir esta venda? O estoque não será revertido automaticamente. Deseja continuar?")) {
        try {
            await window.supabase.from('vendas').delete().eq('id', id);
            alert("Venda excluída com sucesso.");
            fetchDashboardVendas();
        } catch (e) {
            alert("Erro ao excluir venda. Verifique as permissões.");
        }
    }
};

window.editarVenda = function (v) {
    document.getElementById('editVendaId').value = v.id;
    document.getElementById('editVendaValor').value = v.valor_total;
    document.getElementById('editVendaLucro').value = v.lucro_total;
    document.getElementById('editVendaPagamento').value = v.forma_pagamento;
    document.getElementById('modalEditVenda').classList.add('active');
};

document.addEventListener('DOMContentLoaded', () => {
    const formEditVenda = document.getElementById('formEditVenda');
    if (formEditVenda) {
        formEditVenda.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('editVendaId').value;
            const valor = parseFloat(document.getElementById('editVendaValor').value);
            const lucro = parseFloat(document.getElementById('editVendaLucro').value);
            const forma = document.getElementById('editVendaPagamento').value;

            try {
                await window.supabase.from('vendas').update({
                    valor_total: valor,
                    lucro_total: lucro,
                    forma_pagamento: forma
                }).eq('id', id);
                document.getElementById('modalEditVenda').classList.remove('active');
                fetchDashboardVendas();
                alert("Venda editada com sucesso!");
            } catch (err) {
                alert("Erro ao editar a venda. Verifique as permissões.");
            }
        });
    }

    // Filtros
    document.getElementById('periodoVendas').addEventListener('change', fetchDashboardVendas);
    document.getElementById('btnAplicarFiltroVendas').addEventListener('click', fetchDashboardVendas);
    document.getElementById('buscaVendas').addEventListener('input', renderDashboardVendas);

    // Sub-abas de visualização
    document.querySelectorAll('.a-subtab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.a-subtab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.vendas-view').forEach(v => v.style.display = 'none');
            btn.classList.add('active');
            document.getElementById(`view-${btn.dataset.view}`).style.display = 'block';
        });
    });

    // Carga inicial (a aba Vendas já vem ativa por padrão)
    fetchDashboardVendas();
});


// ==========================================
// Resumo de Fiados (topo da aba Fiados)
// ==========================================
async function fetchResumoFiados() {
    const body = document.getElementById('fiadosResumoBody');
    if (!body) return;
    body.innerHTML = `<tr><td colspan="4" class="empty">Carregando...</td></tr>`;

    try {
        const { data, error } = await window.supabase
            .from('compras_anotadas')
            .select('*, clientes(*)')
            .eq('pago', false)
            .order('data_hora', { ascending: false });
        if (error) throw error;

        if (!data || data.length === 0) {
            body.innerHTML = `<tr><td colspan="4" class="empty">Nenhum fiado em aberto.</td></tr>`;
            return;
        }

        const porCliente = {};
        data.forEach(c => {
            const id = c.cliente_id;
            if (!id) return;
            if (!porCliente[id]) {
                porCliente[id] = { nome: c.clientes ? c.clientes.nome : 'Cliente Excluído', total: 0, itens: 0, ultimo: c.data_hora };
            }
            porCliente[id].total += Number(c.quantidade) * Number(c.preco_unitario);
            porCliente[id].itens += 1;
            if (new Date(c.data_hora) > new Date(porCliente[id].ultimo)) porCliente[id].ultimo = c.data_hora;
        });

        const linhas = Object.values(porCliente).sort((a, b) => b.total - a.total);

        if (linhas.length === 0) {
            body.innerHTML = `<tr><td colspan="4" class="empty">Nenhum fiado em aberto.</td></tr>`;
            return;
        }

        body.innerHTML = linhas.map(l => `
            <tr>
                <td>${l.nome}</td>
                <td class="center" style="font-weight:600; color:#e74c3c;">${fmtMoeda(l.total)}</td>
                <td class="center">${l.itens}</td>
                <td class="center">${new Date(l.ultimo).toLocaleDateString('pt-BR')}</td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Erro ao buscar resumo de fiados:', err);
        body.innerHTML = `<tr><td colspan="4" class="empty" style="color:#e74c3c;">Erro ao carregar fiados.</td></tr>`;
    }
}
window.fetchResumoFiados = fetchResumoFiados;
