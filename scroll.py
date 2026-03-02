"""
Модуль для плавного скроллинга к элементам страницы
"""
import streamlit as st 
from streamlit.components.v1 import html

def smooth_scroll_to(target_id, fixed_y_position=None):
    """
    Выполняет плавный скролл к элементу с указанным ID.
    Работает через window.parent для доступа к DOM Streamlit из iframe html().
    Пробует несколько скроллируемых контейнеров Streamlit.
    """
    scroll_code = f"""
    <script type="text/javascript">
        (function() {{
            try {{
                var doc = window.parent.document;
                
                var findTarget = function() {{
                    var target = doc.getElementById("{target_id}");
                    if (target) return target;
                    
                    var headers = doc.querySelectorAll('h1, h2, h3, h4');
                    for (var i = 0; i < headers.length; i++) {{
                        if (headers[i].textContent.indexOf('Результаты расчета') !== -1) {{
                            return headers[i];
                        }}
                    }}
                    return null;
                }};
                
                var doScroll = function(attempt) {{
                    if (attempt > 20) return;
                    
                    var target = findTarget();
                    if (!target) {{
                        setTimeout(function() {{ doScroll(attempt + 1); }}, 300);
                        return;
                    }}
                    
                    var containers = [
                        doc.querySelector('[data-testid="stAppViewContainer"]'),
                        doc.querySelector('section.main'),
                        doc.querySelector('.main'),
                        doc.querySelector('[data-testid="stVerticalBlock"]'),
                        doc.documentElement
                    ];
                    
                    var scrolled = false;
                    for (var i = 0; i < containers.length; i++) {{
                        var c = containers[i];
                        if (c && c.scrollHeight > c.clientHeight) {{
                            var rect = target.getBoundingClientRect();
                            var newTop = c.scrollTop + rect.top - 100;
                            c.scrollTo({{top: newTop, behavior: 'smooth'}});
                            scrolled = true;
                            break;
                        }}
                    }}
                    
                    if (!scrolled) {{
                        target.scrollIntoView({{behavior: 'smooth', block: 'start'}});
                    }}
                    
                    try {{
                        window.parent.scrollTo({{
                            top: target.getBoundingClientRect().top + window.parent.pageYOffset - 100,
                            behavior: 'smooth'
                        }});
                    }} catch(e) {{}}
                }};
                
                setTimeout(function() {{ doScroll(1); }}, 500);
                setTimeout(function() {{ doScroll(1); }}, 1500);
            }} catch(e) {{}}
        }})();
    </script>
    """
    html(scroll_code, height=0)
