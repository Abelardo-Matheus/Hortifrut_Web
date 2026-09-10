// ==========================================
// Aba: Solicitações de Clientes
// ==========================================

const listaSolicitacoes = document.getElementById('listaSolicitacoes');

async function fetchSolicitacoes() {
    try {
        const { data, error } = await window.supabase
            .from('solicitacoes')
            .select('*')
            .order('data_solicitacao', { ascending: false });

        if (error) throw error;

        listaSolicitacoes.innerHTML = '';

        if (data.length === 0) {
            listaSolicitacoes.innerHTML = `<div class="a-info-box">Nenhuma solicitação no momento.</div>`;
            return;
        }

        data.forEach(r => {
            const row = document.createElement('div');
            row.className = 'a-card';
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.flexWrap = 'wrap';
            row.style.gap = '15px';

            const dateFmt = new Date(r.data_solicitacao).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });

            let statusClass = 'orange';
            if (r.status === 'Atendido') statusClass = 'green';
            if (r.status === 'Recusado') statusClass = 'red';

            let actionBtns = '';
            if (r.status === 'Pendente') {
                actionBtns = `
                    <button class="a-btn a-btn-sm" style="width:100%; margin-bottom:5px;" onclick="updateSolicitacaoStatus('${r.id}', 'Atendido')">Atendido</button>
                    <button class="a-btn a-btn-outline a-btn-sm" style="width:100%; margin-bottom:5px;" onclick="updateSolicitacaoStatus('${r.id}', 'Recusado')">Recusado</button>
                `;

                if (r.receber_whatsapp && r.telefone) {
                    let num = r.telefone.replace(/\D/g, '');
                    if (!num.startsWith('55') && num.length >= 10) num = '55' + num;
                    const msg = encodeURIComponent(`Olá ${r.nome_cliente}! O produto '${r.nome_produto}' que você pediu acabou de chegar no Hortifrut! 🎉`);
                    const wppLink = `https://api.whatsapp.com/send?phone=${num}&text=${msg}`;

                    actionBtns += `<a href="${wppLink}" target="_blank" style="text-decoration:none;"><button class="a-btn a-btn-sm" style="width:100%; background:#25D366;">📱 WhatsApp</button></a>`;
                }
            }

            row.innerHTML = `
                <div style="flex:3; min-width:200px;">
                    <div style="margin-bottom:5px;"><strong>Produto:</strong> ${r.nome_produto}</div>
                    <div style="margin-bottom:5px;"><strong>Cliente:</strong> ${r.nome_cliente} (Tel: ${r.telefone || '-'})</div>
                    ${r.receber_whatsapp ? `<div style="font-size:13px; color:#25D366;">💬 <strong>Avisar no WhatsApp</strong></div>` : ''}
                </div>
                <div style="flex:2; text-align:center; min-width:150px;">
                    <div style="color:var(--a-text-secondary); font-size:13px; margin-bottom:5px;">Data: ${dateFmt}</div>
                    <span class="a-badge ${statusClass}">${r.status}</span>
                </div>
                <div style="flex:1; min-width:130px; display:flex; flex-direction:column; gap:5px;">
                    ${actionBtns}
                    <button class="a-btn a-btn-outline a-btn-sm" style="width:100%;" onclick='editarSolicitacao(${JSON.stringify(r)})'>✏️ Editar</button>
                    <button class="a-btn a-btn-danger a-btn-sm" style="width:100%;" onclick="excluirSolicitacao('${r.id}')">🗑️ Excluir</button>
                </div>
            `;
            listaSolicitacoes.appendChild(row);
        });

    } catch (err) {
        console.error(err);
        listaSolicitacoes.innerHTML = `<div class="a-danger-box">Erro ao buscar solicitações.</div>`;
    }
}
window.fetchSolicitacoes = fetchSolicitacoes;

window.updateSolicitacaoStatus = async function (id, status) {
    try {
        await window.supabase.from('solicitacoes').update({ status }).eq('id', id);
        fetchSolicitacoes();
    } catch (e) {
        alert("Erro ao atualizar status");
    }
};

window.excluirSolicitacao = async function (id) {
    if (confirm("Deseja realmente excluir esta solicitação?")) {
        try {
            await window.supabase.from('solicitacoes').delete().eq('id', id);
            alert("Solicitação excluída.");
            fetchSolicitacoes();
        } catch (e) {
            alert("Erro ao excluir. Verifique as permissões.");
        }
    }
};

window.editarSolicitacao = function (s) {
    document.getElementById('editSolicitacaoId').value = s.id;
    document.getElementById('editSolProduto').value = s.nome_produto;
    document.getElementById('editSolCliente').value = s.nome_cliente;
    document.getElementById('editSolTelefone').value = s.telefone || '';
    document.getElementById('editSolWhats').checked = s.receber_whatsapp;
    document.getElementById('modalEditSolicitacao').classList.add('active');
};

document.addEventListener('DOMContentLoaded', () => {
    const formEditSolicitacao = document.getElementById('formEditSolicitacao');
    if (formEditSolicitacao) {
        formEditSolicitacao.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('editSolicitacaoId').value;
            const produto = document.getElementById('editSolProduto').value;
            const cliente = document.getElementById('editSolCliente').value;
            const tel = document.getElementById('editSolTelefone').value;
            const whats = document.getElementById('editSolWhats').checked;

            try {
                await window.supabase.from('solicitacoes').update({
                    nome_produto: produto,
                    nome_cliente: cliente,
                    telefone: tel,
                    receber_whatsapp: whats
                }).eq('id', id);
                document.getElementById('modalEditSolicitacao').classList.remove('active');
                fetchSolicitacoes();
                alert("Solicitação editada com sucesso!");
            } catch (err) {
                alert("Erro ao editar. Verifique permissões.");
            }
        });
    }
});
