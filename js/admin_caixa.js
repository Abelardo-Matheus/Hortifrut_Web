// ==========================================
// Módulo Frente de Caixa e Fiado
// ==========================================

let carrinho = [];
let clientes = [];
let comprasFiadoAbertas = [];
let clienteSelecionadoFiado = null;

// DOM Caixa
const buscaCaixa = document.getElementById('buscaCaixa');
const gridCaixaProdutos = document.getElementById('gridCaixaProdutos');
const listaCarrinho = document.getElementById('listaCarrinho');
const totalCaixa = document.getElementById('totalCaixa');
const pagamentoCaixa = document.getElementById('pagamentoCaixa');
const divFiadoCliente = document.getElementById('divFiadoCliente');
const clienteFiadoCaixa = document.getElementById('clienteFiadoCaixa');
const btnFinalizarVenda = document.getElementById('btnFinalizarVenda');
const valorPagoCaixa = document.getElementById('valorPagoCaixa');
const txtTroco = document.getElementById('txtTroco');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    fetchClientes();
});

// Quando os produtos forem carregados
document.addEventListener('produtosCarregados', () => {
    renderCaixaProdutos(adminProducts);
    renderSelectProdutoFiado(adminProducts);
});

// Renderizar produtos no POS
function renderCaixaProdutos(produtos) {
    gridCaixaProdutos.innerHTML = '';
    produtos.forEach(p => {
        const card = document.createElement('div');
        card.className = 'st-card';
        card.style.cursor = 'pointer';
        
        let imgHtml = p.imagem_url 
            ? `<div style="display:flex;justify-content:center;height:80px;align-items:center;margin-bottom:5px;"><img src="${p.imagem_url}" style="max-width:100%;max-height:80px;object-fit:contain;border-radius:5px;"></div>`
            : `<div style="height:80px;display:flex;align-items:center;justify-content:center;opacity:0.4;font-size:12px;">Sem foto</div>`;

        let estoqueStatus = '';
        const isEsgotado = p.quantidade_estoque <= 0 && p.categoria !== 'Horta (Ilimitado)' && !p.producao_propria;
        
        if(isEsgotado) {
            estoqueStatus = `<div style="text-align:center;color:#e74c3c;font-size:12px;font-weight:bold;margin-bottom:10px;">Esgotado</div>`;
        } else {
            const numEstoque = p.quantidade_estoque % 1 === 0 ? p.quantidade_estoque : Number(p.quantidade_estoque).toFixed(3);
            estoqueStatus = p.producao_propria 
                ? `<div style="text-align:center;color:#27ae60;font-size:12px;font-weight:bold;margin-bottom:5px;">Estoque: Disponível</div>`
                : `<div style="text-align:center;color:#27ae60;font-size:12px;font-weight:bold;margin-bottom:5px;">Estoque: ${numEstoque} ${p.unidade_medida === 'Un' ? 'Unidade' : p.unidade_medida === 'Kg' ? 'Kilos' : p.unidade_medida || 'Unidade'}</div>`;
        }

        const addBtn = isEsgotado 
            ? `<button class="st-button" disabled style="width:100%; opacity:0.5;">Esgotado</button>`
            : `<button class="st-button" style="width:100%; background-color:#ff4b4b; color:white; border:none;" onclick='adicionarAoCarrinho(${JSON.stringify(p)})'>➕ Add</button>`;

        card.innerHTML = `
            ${imgHtml}
            <div style="text-align:center;font-size:13px;font-weight:bold;margin-bottom:5px;line-height:1.2;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;" title="${p.nome}">${p.nome}</div>
            <div style="margin-top:auto;text-align:center;font-size:14px;color:#27ae60;font-weight:bold;margin-bottom:5px;">R$ ${Number(p.preco_venda).toFixed(2)}</div>
            ${estoqueStatus}
            ${addBtn}
        `;
        gridCaixaProdutos.appendChild(card);
    });
}

// Filtro Caixa
buscaCaixa.addEventListener('input', (e) => {
    const t = e.target.value.toLowerCase();
    const filtrados = adminProducts.filter(p => p.nome.toLowerCase().includes(t) || (p.codigo_barras && p.codigo_barras.toLowerCase().includes(t)));
    renderCaixaProdutos(filtrados);
});

// Carrinho de Compras
let produtoTempAdicionar = null;

window.fecharModalAddCarrinho = function() {
    const modal = document.getElementById('modalAddCarrinho');
    if(modal) modal.classList.remove('active');
    produtoTempAdicionar = null;
}

window.adicionarAoCarrinho = function(produto) {
    produtoTempAdicionar = produto;
    document.getElementById('modalAddCarrinhoTitle').textContent = `Adicionar: ${produto.nome}`;
    
    const isKg = produto.unidade_medida && (produto.unidade_medida.toLowerCase() === 'kg' || produto.unidade_medida.toLowerCase() === 'kilos');
    document.getElementById('lblAddCarrinhoQtd').textContent = isKg ? 'Peso (Kilos)' : 'Quantidade (Unidade)';
    document.getElementById('addCarrinhoQtd').value = isKg ? '0.50' : '1';
    document.getElementById('addCarrinhoPreco').value = Number(produto.preco_venda).toFixed(2);
    
    const estoqueNum = produto.quantidade_estoque % 1 === 0 ? produto.quantidade_estoque : Number(produto.quantidade_estoque).toFixed(3);
    document.getElementById('modalAddCarrinhoDesc').textContent = 
        produto.producao_propria ? 'Produção Própria (Ilimitado)' : `Estoque atual: ${estoqueNum} ${produto.unidade_medida === 'Un' ? 'Unidade' : produto.unidade_medida === 'Kg' ? 'Kilos' : produto.unidade_medida || 'Unidade'}`;

    document.getElementById('modalAddCarrinho').classList.add('active');
}

document.addEventListener('DOMContentLoaded', () => {
    const formAddCarrinho = document.getElementById('formAddCarrinho');
    if(formAddCarrinho) {
        formAddCarrinho.addEventListener('submit', (e) => {
            e.preventDefault();
            if(!produtoTempAdicionar) return;

            const qtdAdd = parseFloat(document.getElementById('addCarrinhoQtd').value);
            const precoVendaEditado = parseFloat(document.getElementById('addCarrinhoPreco').value);

            if(isNaN(qtdAdd) || qtdAdd <= 0) return alert("Quantidade inválida!");
            if(isNaN(precoVendaEditado) || precoVendaEditado < 0) return alert("Preço inválido!");

            const existe = carrinho.find(item => item.produto_id === produtoTempAdicionar.id);
            if(existe) {
                existe.quantidade += qtdAdd;
                existe.preco_unitario = precoVendaEditado;
                existe.subtotal = existe.quantidade * existe.preco_unitario;
            } else {
                carrinho.push({
                    produto_id: produtoTempAdicionar.id,
                    nome: produtoTempAdicionar.nome,
                    preco_unitario: precoVendaEditado,
                    preco_custo: produtoTempAdicionar.preco_custo,
                    quantidade: qtdAdd,
                    subtotal: qtdAdd * precoVendaEditado,
                    estoque_atual: produtoTempAdicionar.quantidade_estoque,
                    producao_propria: produtoTempAdicionar.producao_propria,
                    unidade_medida: produtoTempAdicionar.unidade_medida === 'Un' ? 'Unidade' : produtoTempAdicionar.unidade_medida === 'Kg' ? 'Kilos' : produtoTempAdicionar.unidade_medida || 'Unidade'
                });
            }
            
            const msg = document.getElementById('msgCaixa');
            msg.style.display = 'block';
            msg.style.backgroundColor = 'rgba(39, 174, 96, 0.1)';
            msg.style.color = '#27ae60';
            msg.style.border = '1px solid #27ae60';
            msg.textContent = `✅ ${produtoTempAdicionar.nome} adicionado!`;
            setTimeout(() => msg.style.display = 'none', 3000);

            renderCarrinho();
            window.fecharModalAddCarrinho();
        });
    }
});

window.removerDoCarrinho = function(index) {
    carrinho.splice(index, 1);
    renderCarrinho();
}

function renderCarrinho() {
    if(carrinho.length === 0) {
        listaCarrinho.innerHTML = `
            <div style="background: rgba(41, 128, 185, 0.1); border: 1px solid rgba(41, 128, 185, 0.3); padding: 15px; border-radius: 5px; color: #3498db; font-size: 14px;">
                Carrinho vazio.<br>Busque e selecione um produto à esquerda.
            </div>`;
        totalCaixa.textContent = 'R$ 0.00';
        atualizarTroco();
        return;
    }

    listaCarrinho.innerHTML = '';
    let total = 0;

    carrinho.forEach((item, index) => {
        total += item.subtotal;
        const div = document.createElement('div');
        div.style.display = 'flex';
        div.style.justifyContent = 'space-between';
        div.style.alignItems = 'center';
        div.style.marginBottom = '15px';
        div.style.fontSize = '14px';

        div.innerHTML = `
            <div style="flex:1;">
                <strong>${item.nome}</strong><br>
                <code style="background:rgba(255,255,255,0.1); padding:2px 5px; border-radius:3px;">${item.quantidade.toFixed(2)} ${item.unidade_medida}</code> × R$ ${Number(item.preco_unitario).toFixed(2)} = <strong>R$ ${Number(item.subtotal).toFixed(2)}</strong>
            </div>
            <button class="st-button" style="padding: 5px 10px;" onclick="removerDoCarrinho(${index})">✕</button>
        `;
        listaCarrinho.appendChild(div);
    });

    totalCaixa.textContent = `R$ ${total.toFixed(2)}`;
    valorPagoCaixa.value = total.toFixed(2);
    atualizarTroco();
}

pagamentoCaixa.addEventListener('change', (e) => {
    divFiadoCliente.style.display = e.target.value === 'Fiado (Anotar)' ? 'block' : 'none';
});

valorPagoCaixa.addEventListener('input', atualizarTroco);

function atualizarTroco() {
    const total = carrinho.reduce((acc, item) => acc + item.subtotal, 0);
    const pago = parseFloat(valorPagoCaixa.value) || 0;
    if(pago > total && total > 0) {
        txtTroco.textContent = `💵 Troco: R$ ${(pago - total).toFixed(2)}`;
        txtTroco.style.display = 'block';
    } else {
        txtTroco.style.display = 'none';
    }
}

// Finalizar Venda
btnFinalizarVenda.addEventListener('click', async () => {
    if(carrinho.length === 0) return alert('Adicione produtos ao carrinho!');
    
    const forma = pagamentoCaixa.value;
    const clienteId = clienteFiadoCaixa.value;

    if(forma === 'Fiado (Anotar)' && !clienteId) {
        return alert('Selecione um cliente para anotar o fiado!');
    }

    btnFinalizarVenda.textContent = 'Processando...';
    btnFinalizarVenda.disabled = true;

    try {
        let valor_total = 0;
        let custo_total = 0;
        
        carrinho.forEach(i => {
            valor_total += i.subtotal;
            custo_total += (i.preco_custo * i.quantidade);
        });
        
        const lucro_total = valor_total - custo_total;

        if(forma !== 'Fiado (Anotar)') {
            // Venda normal
            const { data: vendaData, error: erroVenda } = await window.supabase
                .from('vendas')
                .insert([{ valor_total, lucro_total, forma_pagamento: forma }])
                .select();
            if(erroVenda) throw erroVenda;
            
            const venda_id = vendaData[0].id;
            const itensInsert = carrinho.map(i => ({
                venda_id,
                produto_id: i.produto_id,
                quantidade: i.quantidade,
                preco_unitario: i.preco_unitario,
                subtotal: i.subtotal
            }));
            await window.supabase.from('itens_venda').insert(itensInsert);
        } else {
            // Fiado Anotado
            const itensFiado = carrinho.map(i => ({
                cliente_id: clienteId,
                produto_id: i.produto_id,
                quantidade: i.quantidade,
                preco_unitario: i.preco_unitario,
                pago: false
            }));
            await window.supabase.from('compras_anotadas').insert(itensFiado);
        }

        // Dedução de Estoque Batch
        for(const item of carrinho) {
            if(!item.producao_propria) {
                const novo_estoque = Math.max(0, item.estoque_atual - item.quantidade);
                await window.supabase.from('produtos').update({ quantidade_estoque: novo_estoque }).eq('id', item.produto_id);
            }
        }

        alert('🎉 Venda registrada com sucesso!');
        carrinho = [];
        renderCarrinho();
        fetchAdminProdutos(); // Recarrega para pegar estoque atualizado
        if(clienteSelecionadoFiado) loadContaCliente(clienteSelecionadoFiado);
        
    } catch (err) {
        console.error(err);
        alert('Erro ao finalizar venda.');
    } finally {
        btnFinalizarVenda.textContent = '✅ FINALIZAR VENDA';
        btnFinalizarVenda.disabled = false;
    }
});


// ==========================================
// Módulo Fiado (Aba 3)
// ==========================================
const btnToggleNovoCliente = document.getElementById('btnToggleNovoCliente');
const divNovoCliente = document.getElementById('divNovoCliente');
const btnSalvarNovoCliente = document.getElementById('btnSalvarNovoCliente');
const selectClienteFiado = document.getElementById('selectClienteFiado');
const contaClienteDetalhe = document.getElementById('contaClienteDetalhe');
const contaClienteVazia = document.getElementById('contaClienteVazia');

btnToggleNovoCliente.addEventListener('click', () => {
    divNovoCliente.style.display = divNovoCliente.style.display === 'none' ? 'block' : 'none';
});

async function fetchClientes() {
    try {
        const { data, error } = await window.supabase.from('clientes').select('*').order('nome');
        if(error) throw error;
        clientes = data;
        
        selectClienteFiado.innerHTML = '<option value="">-- Selecione --</option>';
        clienteFiadoCaixa.innerHTML = ''; // Popula select do Caixa

        clientes.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.nome;
            selectClienteFiado.appendChild(opt);

            const optCaixa = opt.cloneNode(true);
            clienteFiadoCaixa.appendChild(optCaixa);
        });
    } catch (err) {
        console.error(err);
    }
}

btnSalvarNovoCliente.addEventListener('click', async () => {
    const nome = document.getElementById('novoClienteNome').value;
    const telefone = document.getElementById('novoClienteTel').value;
    if(!nome) return alert('Nome obrigatório!');

    try {
        const { error } = await window.supabase.from('clientes').insert([{ nome, telefone }]);
        if(error) throw error;
        document.getElementById('novoClienteNome').value = '';
        document.getElementById('novoClienteTel').value = '';
        divNovoCliente.style.display = 'none';
        alert('Cliente salvo!');
        await fetchClientes();
    } catch(err) {
        alert("Erro ao adicionar cliente. O nome já pode existir.");
    }
});

selectClienteFiado.addEventListener('change', (e) => {
    const id = e.target.value;
    if(!id) {
        contaClienteDetalhe.style.display = 'none';
        contaClienteVazia.style.display = 'block';
        clienteSelecionadoFiado = null;
        return;
    }
    const cliente = clientes.find(c => c.id == id);
    if(cliente) {
        clienteSelecionadoFiado = cliente;
        loadContaCliente(cliente);
    }
});

async function loadContaCliente(cliente) {
    contaClienteVazia.style.display = 'none';
    contaClienteDetalhe.style.display = 'block';
    
    document.getElementById('nomeContaCliente').textContent = `Conta de: ${cliente.nome}`;
    document.getElementById('telContaCliente').textContent = cliente.telefone ? `📞 ${cliente.telefone}` : '';

    try {
        const { data, error } = await window.supabase
            .from('compras_anotadas')
            .select('*, produtos(*)')
            .eq('cliente_id', cliente.id)
            .eq('pago', false)
            .order('data_hora', { ascending: false });
        if(error) throw error;
        
        comprasFiadoAbertas = data;
        let dividaTotal = 0;
        const lista = document.getElementById('listaItensFiado');
        lista.innerHTML = '';

        if(data.length === 0) {
            document.getElementById('dividaTotalFiado').textContent = `Dívida Total: R$ 0.00`;
            lista.innerHTML = `<div style="color:var(--text-secondary);">O cliente não possui dívidas.</div>`;
            return;
        }

        data.forEach(c => {
            const subtotal = c.quantidade * c.preco_unitario;
            dividaTotal += subtotal;

            let dateFmt = new Date(c.data_hora).toLocaleString('pt-BR', { dateStyle:'short', timeStyle:'short' });
            let nomeProd = (!c.produto_id && c.preco_unitario < 0) ? "Pagamento Parcial" : (c.produtos ? c.produtos.nome : 'Produto Excluído');
            let unMedida = c.produtos ? c.produtos.unidade_medida : '';

            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.marginBottom = '10px';
            
            let valHtml = '';
            if(c.preco_unitario < 0) {
                valHtml = `💰 <strong style="color:#27ae60;">- R$ ${Math.abs(subtotal).toFixed(2)}</strong>`;
            } else {
                valHtml = `${c.quantidade} ${unMedida} x R$ ${c.preco_unitario.toFixed(2)} &nbsp;&nbsp; 💰 <strong>R$ ${subtotal.toFixed(2)}</strong>`;
            }

            row.innerHTML = `
                <div style="flex:2;">📅 ${dateFmt} - <strong>${nomeProd}</strong></div>
                <div style="flex:2;">${valHtml}</div>
                <div style="flex:1; display:flex; gap:5px; justify-content:flex-end;">
                    <button class="st-button" style="padding:5px;" onclick="pagarItemUnico(${c.id})" title="Pagar este item">💲</button>
                    <button class="st-button" style="padding:5px;" onclick='editarCompraFiado(${JSON.stringify(c)})' title="Editar item">✏️</button>
                    <button class="st-button" style="padding:5px; border-color:#e74c3c; color:#e74c3c;" onclick="excluirCompraFiado(${c.id})" title="Excluir item">🗑️</button>
                </div>
            `;
            lista.appendChild(row);
        });

        document.getElementById('dividaTotalFiado').textContent = `Dívida Total: R$ ${dividaTotal.toFixed(2)}`;

    } catch(err) {
        console.error(err);
    }
}

window.pagarItemUnico = async function(id) {
    try {
        await window.supabase.from('compras_anotadas').update({ pago: true }).eq('id', id);
        alert("Item pago com sucesso!");
        loadContaCliente(clienteSelecionadoFiado);
    } catch(e) { alert("Erro ao pagar item"); }
}

window.excluirCompraFiado = async function(id) {
    if(confirm("Excluir este item anotado? (Devolverá o estoque)")) {
        try {
            await window.supabase.from('compras_anotadas').delete().eq('id', id);
            alert("Item excluído!");
            loadContaCliente(clienteSelecionadoFiado);
        } catch(e) { alert("Erro ao excluir. Verifique as permissões no banco."); }
    }
}

window.editarCompraFiado = function(c) {
    document.getElementById('editFiadoId').value = c.id;
    document.getElementById('editFiadoQtd').value = c.quantidade;
    document.getElementById('editFiadoPreco').value = c.preco_unitario;
    document.getElementById('modalEditFiado').classList.add('active');
}

document.addEventListener('DOMContentLoaded', () => {
    // Editar Fiado
    const formEditFiado = document.getElementById('formEditFiado');
    if(formEditFiado) {
        formEditFiado.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('editFiadoId').value;
            const qtd = parseFloat(document.getElementById('editFiadoQtd').value);
            const preco = parseFloat(document.getElementById('editFiadoPreco').value);

            try {
                await window.supabase.from('compras_anotadas').update({
                    quantidade: qtd,
                    preco_unitario: preco
                }).eq('id', id);
                document.getElementById('modalEditFiado').classList.remove('active');
                loadContaCliente(clienteSelecionadoFiado);
                alert("Anotado editado com sucesso!");
            } catch(err) {
                alert("Erro ao editar o anotado. Verifique as permissões no banco.");
            }
        });
    }

    // Editar e Excluir Cliente
    const btnEditCliente = document.getElementById('btnEditCliente');
    const btnDeleteCliente = document.getElementById('btnDeleteCliente');
    const formEditCliente = document.getElementById('formEditCliente');

    if(btnEditCliente) {
        btnEditCliente.addEventListener('click', () => {
            if(!clienteSelecionadoFiado) return;
            document.getElementById('editClienteId').value = clienteSelecionadoFiado.id;
            document.getElementById('editClienteNome').value = clienteSelecionadoFiado.nome;
            document.getElementById('editClienteTel').value = clienteSelecionadoFiado.telefone || '';
            document.getElementById('modalEditCliente').classList.add('active');
        });
    }

    if(btnDeleteCliente) {
        btnDeleteCliente.addEventListener('click', async () => {
            if(!clienteSelecionadoFiado) return;
            if(confirm(`Tem certeza que deseja excluir o cliente ${clienteSelecionadoFiado.nome}?\nISSO APAGARÁ TODO O HISTÓRICO DELE! (Caso as permissões do banco permitam cascade)`)) {
                try {
                    await window.supabase.from('clientes').delete().eq('id', clienteSelecionadoFiado.id);
                    alert("Cliente excluído com sucesso!");
                    
                    document.getElementById('selectClienteFiado').value = '';
                    document.getElementById('contaClienteDetalhe').style.display = 'none';
                    document.getElementById('contaClienteVazia').style.display = 'block';
                    clienteSelecionadoFiado = null;
                    
                    fetchClientes();
                } catch(err) {
                    alert("Erro ao excluir o cliente. Verifique permissões ou se ele tem compras vinculadas e o banco não permite cascade.");
                }
            }
        });
    }

    if(formEditCliente) {
        formEditCliente.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('editClienteId').value;
            const nome = document.getElementById('editClienteNome').value;
            const tel = document.getElementById('editClienteTel').value;

            try {
                await window.supabase.from('clientes').update({
                    nome: nome,
                    telefone: tel
                }).eq('id', id);
                document.getElementById('modalEditCliente').classList.remove('active');
                
                // Atualiza info no select
                clienteSelecionadoFiado.nome = nome;
                clienteSelecionadoFiado.telefone = tel;
                document.getElementById('nomeContaCliente').textContent = `Conta de: ${nome}`;
                document.getElementById('telContaCliente').textContent = tel ? `📞 ${tel}` : '';
                
                fetchClientes();
                alert("Cliente editado com sucesso!");
            } catch(err) {
                alert("Erro ao editar o cliente. Verifique as permissões no banco.");
            }
        });
    }
});

document.getElementById('btnPagarContaInteira').addEventListener('click', async () => {
    if(!clienteSelecionadoFiado || comprasFiadoAbertas.length === 0) return;
    if(confirm("Deseja quitar toda a conta deste cliente?")) {
        try {
            const ids = comprasFiadoAbertas.map(c => c.id);
            await window.supabase.from('compras_anotadas').update({ pago: true }).in('id', ids);
            
            // Registra a quitação em Vendas para entrar no fluxo de caixa (opcional, como no py)
            const dividaTotal = comprasFiadoAbertas.reduce((acc, c) => acc + (c.quantidade * c.preco_unitario), 0);
            await window.supabase.from('vendas').insert([{ valor_total: dividaTotal, lucro_total: 0, forma_pagamento: 'Pagamento Fiado' }]);

            alert("Conta paga com sucesso! 🎉");
            loadContaCliente(clienteSelecionadoFiado);
        } catch(err) { alert("Erro ao quitar"); }
    }
});

document.getElementById('btnRegistrarPagamentoParcial').addEventListener('click', async () => {
    const val = parseFloat(document.getElementById('valorParcialFiado').value);
    if(!val || val <= 0) return;
    
    try {
        await window.supabase.from('compras_anotadas').insert([{
            cliente_id: clienteSelecionadoFiado.id,
            preco_unitario: -Math.abs(val),
            quantidade: 1,
            pago: false
        }]);
        await window.supabase.from('vendas').insert([{ valor_total: val, lucro_total: 0, forma_pagamento: 'Pagamento Fiado Parcial' }]);
        
        document.getElementById('valorParcialFiado').value = '';
        alert("Pagamento parcial registrado!");
        loadContaCliente(clienteSelecionadoFiado);
    } catch(err) { alert("Erro ao registrar parcial"); }
});

// Anotar nova compra
function renderSelectProdutoFiado(produtos) {
    const sel = document.getElementById('selectProdutoFiado');
    sel.innerHTML = '';
    produtos.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.nome;
        opt.dataset.preco = p.preco_venda;
        opt.dataset.iskg = (p.unidade_medida || '').toLowerCase() === 'kg' || (p.unidade_medida || '').toLowerCase() === 'kilos';
        sel.appendChild(opt);
    });
}

document.getElementById('buscaProdutoFiado').addEventListener('input', (e) => {
    const t = e.target.value.toLowerCase();
    const f = adminProducts.filter(p => p.nome.toLowerCase().includes(t));
    renderSelectProdutoFiado(f);
});

document.getElementById('selectProdutoFiado').addEventListener('change', (e) => {
    const opt = e.target.options[e.target.selectedIndex];
    if(opt) {
        document.getElementById('precoNovaCompraFiado').value = opt.dataset.preco;
        document.getElementById('lblQtdFiado').textContent = opt.dataset.iskg === 'true' ? "Peso (Kilos)" : "Quantidade";
    }
});

document.getElementById('btnAnotarNovaCompra').addEventListener('click', async () => {
    const prodSel = document.getElementById('selectProdutoFiado');
    if(!prodSel.value) return;
    
    const opt = prodSel.options[prodSel.selectedIndex];
    const qtd = parseFloat(document.getElementById('qtdNovaCompraFiado').value);
    const preco = parseFloat(document.getElementById('precoNovaCompraFiado').value);
    const iskg = opt.dataset.iskg === 'true';

    if(!qtd || qtd <= 0) return alert("Preencha a quantidade");

    try {
        await window.supabase.from('compras_anotadas').insert([{
            cliente_id: clienteSelecionadoFiado.id,
            produto_id: prodSel.value,
            quantidade: qtd,
            preco_unitario: preco,
            pago: false
        }]);
        alert("Compra anotada com sucesso!");
        loadContaCliente(clienteSelecionadoFiado);
        document.getElementById('qtdNovaCompraFiado').value = '1';
    } catch(e) { alert("Erro ao anotar compra"); }
});
