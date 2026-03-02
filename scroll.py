"""
Модуль для плавного скроллинга к элементам страницы в Streamlit.
Использует html() компонент (iframe) с доступом к window.parent.document.
"""
import streamlit as st 
from streamlit.components.v1 import html


def smooth_scroll_to(target_id, offset_px=80):
    code = """<div style="height:0;overflow:hidden;">
    <script>
    (function(){
        var pdoc = window.parent.document;
        var attempts = 0;
        function go() {
            attempts++;
            if (attempts > 20) return;
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
                    var off = t.getBoundingClientRect().top - p.getBoundingClientRect().top + p.scrollTop - """ + str(offset_px) + """;
                    p.scrollTo({top: off, behavior: 'smooth'});
                    return;
                }
                p = p.parentElement;
            }
            t.scrollIntoView({behavior: 'smooth', block: 'start'});
        }
        setTimeout(go, 500);
    })();
    </script></div>"""
    html(code, height=1)
