// ==========================================
// Aba: Retiradas para Casa
// ==========================================

const buscaProdutoRetirada = document.getElementById('buscaProdutoRetirada');
const selectProdutoRetirada = document.getElementById('selectProdutoRetirada');
const qtdRetirada = document.getElementById('qtdRetirada');
const custoEstimadoRetirada = document.getElementById('custoEstimadoRetirada');
const btnRegistrarRetirada = document.getElementById('btnRegistrarRetirada');
const listaRetiradasMes = document.getElementById('listaRetiradasMes');
const tituloMesRetirada = document.getElementById('tituloMesRetirada');
const custoTotalRetiradas = document.getElementById('custoTotalRetiradas');

let retiradasMes = [];

// Quando os produtos forem carregados
document.addEventListener('produtosCarregados', () => {
    renderSelectProdutoRetirada(adminProducts);
    fetchRetiradasMes();
});

function renderSelectProdutoRetirada(produtos) {
    selectProdutoRetirada.innerHTML = '';
    produtos.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.nome;
        opt.dataset.custo = p.preco_custo;
        opt.dataset.iskg = (p.unidade_medida || '').toLowerCase() === 'kg';
        selectProdutoRetirada.appendChild(opt);
    });
    calcularCustoEstimado();
}

buscaProdutoRetirada.addEventListener('input', (e) => {
    const t = e.target.value.toLowerCase();
    const filtrados = adminProducts.filter(p => p.nome.toLowerCase().includes(t));
    renderSelectProdutoRetirada(filtrados);
});

function calcularCustoEstimado() {
    const opt = selectProdutoRetirada.options[selectProdutoRetirada.selectedIndex];
    if(opt) {
        const custo = parseFloat(opt.dataset.custo) || 0;
        const qtd = parseFloat(qtdRetirada.value) || 0;
        custoEstimadoRetirada.textContent = `R$ ${(custo * qtd).toFixed(2)}`;
    }
}

selectProdutoRetirada.addEventListener('change', calcularCustoEstimado);
qtdRetirada.addEventListener('input', calcularCustoEstimado);

btnRegistrarRetirada.addEventListener('click', async () => {
    const opt = selectProdutoRetirada.options[selectProdutoRetirada.selectedIndex];
    if(!opt) return alert("Selecione um produto.");
    
    const produtoId = opt.value;
    const custo = parseFloat(opt.dataset.custo);
    const qtd = parseFloat(qtdRetirada.value);
    const p = adminProducts.find(x => x.id == produtoId);

    if(!qtd || qtd <= 0) return alert("Quantidade inválida.");

    try {
        await window.supabase.from('retiradas_casa').insert([{
            produto_id: produtoId,
            quantidade: qtd,
            custo_unitario: custo
        }]);

        // Atualiza estoque se não for produção própria/ilimitado
        if(!p.producao_propria && p.categoria !== 'Horta (Ilimitado)') {
            const novo_estoque = Math.max(0, p.quantidade_estoque - qtd);
            await window.supabase.from('produtos').update({ quantidade_estoque: novo_estoque }).eq('id', produtoId);
        }

        alert("Retirada registrada com sucesso!");
        qtdRetirada.value = "1";
        calcularCustoEstimado();
        
        fetchAdminProdutos(); // Recarrega produtos (estoque) e as retiradas
    } catch(e) {
        console.error(e);
        alert("Erro ao registrar retirada.");
    }
});

async function fetchRetiradasMes() {
    try {
        const now = new Date();
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
        
        tituloMesRetirada.textContent = `Retiradas em ${String(now.getMonth()+1).padStart(2,'0')}/${now.getFullYear()}`;

        const { data, error } = await window.supabase
            .from('retiradas_casa')
            .select('*, produtos(*)')
            .gte('data_hora', startOfMonth)
            .order('data_hora', { ascending: false });

        if(error) throw error;
        retiradasMes = data;
        
        listaRetiradasMes.innerHTML = '';
        let totalMes = 0;

        if(data.length === 0) {
            listaRetiradasMes.innerHTML = `<div style="background: rgba(39, 174, 96, 0.1); border: 1px solid #27ae60; color:#27ae60; padding: 15px; border-radius: 5px;">Nenhuma retirada registrada neste mês.</div>`;
            custoTotalRetiradas.textContent = `Custo Total Retirado no Mês: R$ 0,00`;
            return;
        }

        data.forEach(r => {
            const subtotal = r.quantidade * r.custo_unitario;
            totalMes += subtotal;

            let dateFmt = new Date(r.data_hora).toLocaleString('pt-BR', { dateStyle:'short', timeStyle:'short' });
            let nomeProd = r.produtos ? r.produtos.nome : 'Produto Excluído';
            let unMedida = r.produtos ? r.produtos.unidade_medida : '';

            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.marginBottom = '10px';
            
            row.innerHTML = `
                <div style="flex:2;">📅 ${dateFmt} - <strong>${nomeProd}</strong></div>
                <div style="flex:1;">${r.quantidade} ${unMedida}</div>
                <div style="flex:1;">📉 <strong>R$ ${subtotal.toFixed(2)}</strong></div>
                <button class="st-button" style="padding:5px;" onclick='editarRetirada(${JSON.stringify(r)})' title="Editar Retirada">✏️</button>
                <button class="st-button" style="padding:5px; border-color:#e74c3c; color:#e74c3c;" onclick="excluirRetirada(${r.id})">🗑️</button>
            `;
            listaRetiradasMes.appendChild(row);
        });

        custoTotalRetiradas.textContent = `Custo Total Retirado no Mês: R$ ${totalMes.toFixed(2)}`;

    } catch(err) {
        console.error(err);
    }
}

window.excluirRetirada = async function(id) {
    if(confirm("Excluir esta retirada?")) {
        try {
            await window.supabase.from('retiradas_casa').delete().eq('id', id);
            alert("Retirada excluída!");
            fetchRetiradasMes();
        } catch(e) { alert("Erro ao excluir. Verifique permissões."); }
    }
}

window.editarRetirada = function(r) {
    document.getElementById('editRetiradaId').value = r.id;
    document.getElementById('editRetiradaQtd').value = r.quantidade;
    document.getElementById('editRetiradaCusto').value = r.custo_unitario;
    document.getElementById('modalEditRetirada').classList.add('active');
}

document.addEventListener('DOMContentLoaded', () => {
    const formEditRetirada = document.getElementById('formEditRetirada');
    if(formEditRetirada) {
        formEditRetirada.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('editRetiradaId').value;
            const qtd = parseFloat(document.getElementById('editRetiradaQtd').value);
            const custo = parseFloat(document.getElementById('editRetiradaCusto').value);

            try {
                await window.supabase.from('retiradas_casa').update({
                    quantidade: qtd,
                    custo_unitario: custo
                }).eq('id', id);
                document.getElementById('modalEditRetirada').classList.remove('active');
                fetchRetiradasMes();
                alert("Retirada editada com sucesso!");
            } catch(err) {
                alert("Erro ao editar retirada. Verifique permissões.");
            }
        });
    }
});
