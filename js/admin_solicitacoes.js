// ==========================================
// Aba: Solicitações de Clientes
// ==========================================

const listaSolicitacoes = document.getElementById('listaSolicitacoes');

document.querySelector('[data-tab="tab-solicitacoes"]').addEventListener('click', () => {
    fetchSolicitacoes();
});

async function fetchSolicitacoes() {
    try {
        const { data, error } = await window.supabase
            .from('solicitacoes')
            .select('*')
            .order('data_solicitacao', { ascending: false });

        if(error) throw error;

        listaSolicitacoes.innerHTML = '';

        if(data.length === 0) {
            listaSolicitacoes.innerHTML = `<div style="background: rgba(41, 128, 185, 0.1); border: 1px solid #3498db; color: #3498db; padding: 15px; border-radius: 5px;">Nenhuma solicitação no momento.</div>`;
            return;
        }

        data.forEach(r => {
            const row = document.createElement('div');
            row.className = 'st-card';
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.padding = '15px';
            
            const dateFmt = new Date(r.data_solicitacao).toLocaleString('pt-BR', { dateStyle:'short', timeStyle:'short' });
            
            let statusColor = '#f39c12';
            if(r.status === 'Atendido') statusColor = '#27ae60';
            if(r.status === 'Recusado') statusColor = '#e74c3c';

            let actionBtns = '';
            if(r.status === 'Pendente') {
                actionBtns = `
                    <button class="st-button" style="background-color:#ff4b4b; color:white; border:none; margin-bottom:5px; width:100%;" onclick="updateSolicitacaoStatus(${r.id}, 'Atendido')">Atendido</button>
                    <button class="st-button" style="width:100%; margin-bottom:5px;" onclick="updateSolicitacaoStatus(${r.id}, 'Recusado')">Recusado</button>
                `;
                
                if(r.receber_whatsapp && r.telefone) {
                    let num = r.telefone.replace(/\D/g, '');
                    if(!num.startsWith('55') && num.length >= 10) num = '55' + num;
                    const msg = encodeURIComponent(`Olá ${r.nome_cliente}! O produto '${r.nome_produto}' que você pediu acabou de chegar no Hortifruti! 🎉`);
                    const wppLink = `https://api.whatsapp.com/send?phone=${num}&text=${msg}`;
                    
                    actionBtns += `<a href="${wppLink}" target="_blank" style="text-decoration:none;"><button class="st-button" style="background-color:#25D366; color:white; border:none; width:100%;">📱 Enviar WhatsApp</button></a>`;
                }
            }

            row.innerHTML = `
                <div style="flex:3;">
                    <div style="margin-bottom:5px;"><strong>Produto:</strong> ${r.nome_produto}</div>
                    <div style="margin-bottom:5px;"><strong>Cliente:</strong> ${r.nome_cliente} (Tel: ${r.telefone})</div>
                    ${r.receber_whatsapp ? `<div style="font-size:13px; color:#25D366;">💬 <strong>Avisar no WhatsApp</strong></div>` : ''}
                </div>
                <div style="flex:2; text-align:center;">
                    <div style="color:var(--text-secondary); font-size:13px; margin-bottom:5px;">Data: ${dateFmt}</div>
                    <div><strong>Status:</strong> <span style="color:${statusColor}">${r.status}</span></div>
                </div>
                <div style="flex:1; display:flex; flex-direction:column; gap:5px;">
                    ${actionBtns}
                </div>
            `;
            listaSolicitacoes.appendChild(row);
        });

    } catch(err) {
        console.error(err);
        listaSolicitacoes.innerHTML = `<div style="color:red;">Erro ao buscar solicitações.</div>`;
    }
}

window.updateSolicitacaoStatus = async function(id, status) {
    try {
        await window.supabase.from('solicitacoes').update({ status }).eq('id', id);
        fetchSolicitacoes();
    } catch(e) {
        alert("Erro ao atualizar status");
    }
}
