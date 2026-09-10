// ==========================================
// Lógica Global do Painel Admin (Navegação)
// ==========================================

const navBtns = document.querySelectorAll('.nav-btn');
const tabSections = document.querySelectorAll('.tab-section');

// Dispara o carregamento de dados quando o usuário abre uma aba pela
// primeira vez (evita várias chamadas ao Supabase logo no load).
const tabLoaders = {
    vendas: () => window.fetchDashboardVendas && window.fetchDashboardVendas(),
    fiados: () => window.fetchResumoFiados && window.fetchResumoFiados(),
    solicitacoes: () => typeof fetchSolicitacoes === 'function' && fetchSolicitacoes(),
};
const tabsJaCarregadas = new Set(['vendas']); // vendas já carrega no DOMContentLoaded

navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');

        navBtns.forEach(b => b.classList.remove('active'));
        tabSections.forEach(tc => tc.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(`${tabId}-tab`).classList.add('active');

        if (!tabsJaCarregadas.has(tabId) && tabLoaders[tabId]) {
            tabLoaders[tabId]();
            tabsJaCarregadas.add(tabId);
        }
    });
});
