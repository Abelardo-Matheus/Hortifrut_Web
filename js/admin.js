// ==========================================
// Lógica Global do Painel Admin (Abas)
// ==========================================

const navBtns = document.querySelectorAll('.st-tab-btn:not(.logout)');
const tabContents = document.querySelectorAll('.tab-content');

navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class de todos
        navBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(tc => tc.classList.remove('active'));

        // Adiciona no clicado
        btn.classList.add('active');
        const tabId = btn.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});
