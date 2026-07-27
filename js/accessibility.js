// Acessibilidade - Controle de Zoom Global
document.addEventListener('DOMContentLoaded', () => {
    const widget = document.createElement('div');
    widget.style.position = 'fixed';
    widget.style.top = '50%';
    widget.style.right = '20px';
    widget.style.transform = 'translateY(-50%)';
    widget.style.display = 'flex';
    widget.style.flexDirection = 'column';
    widget.style.gap = '10px';
    widget.style.zIndex = '99999';

    const btnConfigs = [
        { id: 'btnZoomIn', text: 'A+', title: 'Aumentar Visualização', step: 0.1, isZoom: true },
        { id: 'btnZoomOut', text: 'A-', title: 'Diminuir Visualização', step: -0.1, isZoom: true },
        { id: 'btnTheme', text: '🌞', title: 'Alternar Tema', isTheme: true },
        { id: 'btnContrast', text: '🌗', title: 'Alto Contraste', isZoom: false }
    ];

    let currentZoom = parseFloat(localStorage.getItem('userZoom')) || 1;
    let highContrast = localStorage.getItem('userContrast') === 'true';
    let isLightMode = localStorage.getItem('userTheme') === 'light';

    function applyZoom() {
        document.body.style.zoom = currentZoom;
        localStorage.setItem('userZoom', currentZoom);
    }
    
    function applyContrast() {
        if (highContrast) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
        localStorage.setItem('userContrast', highContrast);
    }

    function applyTheme() {
        if (isLightMode) {
            document.body.classList.add('light-theme');
            const themeBtn = document.getElementById('btnTheme');
            if (themeBtn) themeBtn.innerHTML = '🌙';
        } else {
            document.body.classList.remove('light-theme');
            const themeBtn = document.getElementById('btnTheme');
            if (themeBtn) themeBtn.innerHTML = '🌞';
        }
        localStorage.setItem('userTheme', isLightMode ? 'light' : 'dark');
    }

    applyZoom();
    applyContrast();
    applyTheme();

    btnConfigs.forEach(config => {
        const btn = document.createElement('button');
        btn.id = config.id;
        btn.innerHTML = config.text;
        btn.title = config.title;
        btn.style.width = '45px';
        btn.style.height = '45px';
        btn.style.borderRadius = '50%';
        btn.style.background = '#262730';
        btn.style.border = '2px solid #27ae60';
        btn.style.color = '#f8f9fa';
        btn.style.cursor = 'pointer';
        btn.style.fontWeight = 'bold';
        btn.style.fontSize = '18px';
        btn.style.boxShadow = '0 4px 10px rgba(0,0,0,0.5)';
        btn.style.transition = 'all 0.2s';
        
        btn.onmouseover = () => btn.style.transform = 'scale(1.1)';
        btn.onmouseout = () => btn.style.transform = 'scale(1)';

        btn.addEventListener('click', () => {
            if (config.isZoom) {
                let newZoom = currentZoom + config.step;
                if(newZoom >= 0.8 && newZoom <= 1.5) {
                    currentZoom = newZoom;
                    applyZoom();
                }
            } else if (config.isTheme) {
                isLightMode = !isLightMode;
                applyTheme();
            } else {
                highContrast = !highContrast;
                applyContrast();
            }
        });
        
        widget.appendChild(btn);
    });

    document.body.appendChild(widget);
});
