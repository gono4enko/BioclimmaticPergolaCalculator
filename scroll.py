"""
Модуль для плавного скроллинга к элементам страницы в Streamlit.
Использует <img onload> внутри st.markdown(unsafe_allow_html=True),
что выполняет JS в контексте основного документа Streamlit (без iframe).
Если st.markdown блокирует onload, fallback на html() с height=1.
"""
import streamlit as st 
from streamlit.components.v1 import html


def smooth_scroll_to(target_id, offset_px=80):
    js = _build_scroll_js(target_id, offset_px)

    st.markdown(
        f'<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" '
        f'onload="{js}" style="display:none;height:0;width:0;" />',
        unsafe_allow_html=True,
    )

    _scroll_via_html(target_id, offset_px)


def _build_scroll_js(target_id, offset_px):
    return (
        "var d=document;"
        f"var t=d.getElementById('{target_id}');"
        "if(!t){{var h=d.querySelectorAll('h2,h3,h4');"
        "for(var i=0;i<h.length;i++){{if(h[i].textContent.indexOf('Результаты')>=0){{t=h[i];break;}}}}}}"
        "if(t){{"
        "var p=t;while(p&&p!==d.documentElement){{"
        "var s=getComputedStyle(p);"
        "if((s.overflowY==='auto'||s.overflowY==='scroll')&&p.scrollHeight>p.clientHeight+5){{"
        f"p.scrollTo({{top:p.scrollTop+t.getBoundingClientRect().top-p.getBoundingClientRect().top-{offset_px},behavior:'smooth'}});"
        "break;}}p=p.parentElement;}}"
        "if(!p||p===d.documentElement){{t.scrollIntoView({{behavior:'smooth',block:'start'}})}}"
        "}}"
    )


def _scroll_via_html(target_id, offset_px):
    code = """<script>
    (function(){
        var pdoc = window.parent.document;
        var attempts = 0;
        function go() {
            attempts++;
            if (attempts > 15) return;
            var t = pdoc.getElementById('""" + target_id + """');
            if (!t) {
                var h = pdoc.querySelectorAll('h2,h3,h4');
                for (var i = 0; i < h.length; i++) {
                    if (h[i].textContent.indexOf('Результаты') >= 0) { t = h[i]; break; }
                }
            }
            if (!t) { setTimeout(go, 300); return; }

            var p = t;
            while (p && p !== pdoc.documentElement) {
                var s = window.parent.getComputedStyle(p);
                if ((s.overflowY === 'auto' || s.overflowY === 'scroll') && p.scrollHeight > p.clientHeight + 5) {
                    p.scrollTo({top: p.scrollTop + t.getBoundingClientRect().top - p.getBoundingClientRect().top - """ + str(offset_px) + """, behavior: 'smooth'});
                    return;
                }
                p = p.parentElement;
            }
            t.scrollIntoView({behavior: 'smooth', block: 'start'});
        }
        setTimeout(go, 500);
    })();
    </script>"""
    html(code, height=1)
