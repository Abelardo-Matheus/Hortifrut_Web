import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('# ── Portal visual')
if idx == -1:
    print('Not found')
    sys.exit(1)

# Remove the bad part
good_content = content[:idx]

# Append the correct portal JS
correct_portal = '''# ── Portal visual — box fixa superior ───────────────────────────────
import streamlit.components.v1 as _components

if st.session_state.show_admin:
    _admin_icon = "🔓"
else:
    _admin_icon = "⚙️" if st.session_state.logged_in else "🔐"
_tema_icon_js = "🌙" if st.session_state.light_mode else "☀️"

_components.html(f"""
<script>
(function() {{
    var doc = window.parent.document;
    
    // 1. Encontra e esconde o container dos botões originais do Streamlit
    var marker = doc.getElementById('hf-hidden-btns-marker');
    if (marker) {{
        var stContainer = marker.closest('[data-testid="stVerticalBlock"]');
        if (stContainer) {{
            stContainer.style.display = 'none';
        }}
    }}
    
    // 2. Remove TODOS os portais visuais anteriores para evitar duplicatas
    var oldPortals = doc.querySelectorAll('#hf-btn-portal');
    oldPortals.forEach(function(p) {{ p.remove(); }});

    // 3. Cria a box do portal com os dois botões
    var portal = doc.createElement('div');
    portal.id = 'hf-btn-portal';
    portal.innerHTML =
        '<button id="hf-btn-admin" title="Admin">{_admin_icon}</button>' +
        '<button id="hf-btn-tema"  title="Tema">{_tema_icon_js}</button>';
    
    doc.body.appendChild(portal);

    // 4. Lógica de clique que aciona os botões ocultos
    function clickSt(n) {{
        if (marker) {{
            var stContainer = marker.closest('[data-testid="stVerticalBlock"]');
            if (stContainer) {{
                var btns = stContainer.querySelectorAll('button');
                if (btns && btns[n]) btns[n].click();
            }}
        }}
    }}

    doc.getElementById('hf-btn-admin').onclick = function() {{ clickSt(0); }};
    doc.getElementById('hf-btn-tema').onclick  = function() {{ clickSt(1); }};
    
    // 5. Lógica de estado do Vídeo Logo (Tocar só uma vez)
    var logoVid = doc.querySelector('.logo-video');
    if (logoVid) {{
        if (sessionStorage.getItem('hf_video_played')) {{
            // Se já tocou nessa sessão, pausa e pula pro final
            logoVid.removeAttribute('autoplay');
            logoVid.pause();
            
            if (logoVid.readyState >= 1) {{
                logoVid.currentTime = logoVid.duration || 999;
            }} else {{
                logoVid.addEventListener('loadedmetadata', function() {{
                    logoVid.currentTime = logoVid.duration || 999;
                }});
            }}
        }} else {{
            // Marca como tocado quando terminar
            logoVid.addEventListener('ended', function() {{
                sessionStorage.setItem('hf_video_played', 'true');
            }});
        }}
    }}
}})();
</script>
""", height=0, width=0)
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(good_content + correct_portal)
