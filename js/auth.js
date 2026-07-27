// ==========================================
// Lógica de Autenticação
// ==========================================

const loginForm = document.getElementById('loginForm');
const errorMsg = document.getElementById('errorMsg');

// Se já estiver logado, manda pro admin
if (window.location.pathname.includes('login.html')) {
    if (localStorage.getItem('hortifrut_admin_auth') === 'true') {
        window.location.href = 'admin.html';
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const user = document.getElementById('username').value;
        const pass = document.getElementById('password').value;
        const btn = loginForm.querySelector('button');
        
        btn.textContent = 'Verificando...';
        btn.disabled = true;
        errorMsg.style.display = 'none';

        try {
            const { data, error } = await supabase
                .from('usuarios')
                .select('*')
                .eq('usuario', user)
                .eq('senha', pass);

            if (data && data.length > 0) {
                // Sucesso!
                localStorage.setItem('hortifrut_admin_auth', 'true');
                window.location.href = 'admin.html';
            } else {
                // Falha
                errorMsg.style.display = 'block';
                btn.textContent = 'Entrar';
                btn.disabled = false;
            }
        } catch (err) {
            console.error('Erro de login:', err);
            errorMsg.textContent = 'Erro de conexão com o banco.';
            errorMsg.style.display = 'block';
            btn.textContent = 'Entrar';
            btn.disabled = false;
        }
    });
}

// Proteger rotas que exigem login (como admin.html)
function checkAuth() {
    if (!localStorage.getItem('hortifrut_admin_auth')) {
        window.location.href = 'login.html';
    }
}

// Função de logout global
function logout() {
    localStorage.removeItem('hortifrut_admin_auth');
    window.location.href = 'login.html';
}
