"""
Модуль для плавного скроллинга к элементам страницы
"""
import streamlit as st 
from streamlit.components.v1 import html

def smooth_scroll_to(target_id, fixed_y_position=None):
    """
    Выполняет плавный скролл к элементу с указанным ID.
    Использует window.parent для корректной работы внутри iframe Streamlit.
    """
    if fixed_y_position is not None:
        scroll_code = f"""
        <script type="text/javascript">
            (function() {{
                var doc = window.parent.document;
                var attempts = [300, 700, 1200];
                attempts.forEach(function(delay) {{
                    setTimeout(function() {{
                        try {{
                            var mainSection = doc.querySelector('section.main');
                            if (mainSection) {{
                                mainSection.scrollTo({{top: {fixed_y_position}, behavior: 'smooth'}});
                            }}
                        }} catch(e) {{}}
                    }}, delay);
                }});
            }})();
        </script>
        """
        html(scroll_code, height=0)
        return

    scroll_code = f"""
    <script type="text/javascript">
        (function() {{
            var doc = window.parent.document;
            var TARGET_ID = "{target_id}";
            
            var tryScroll = function(attempt) {{
                if (attempt > 15) return;
                
                var target = doc.getElementById(TARGET_ID);
                if (!target) {{
                    var headers = doc.querySelectorAll('h1, h2, h3, h4');
                    for (var i = 0; i < headers.length; i++) {{
                        if (headers[i].textContent.indexOf('Результаты расчета') !== -1) {{
                            target = headers[i];
                            break;
                        }}
                    }}
                }}
                
                if (target) {{
                    var mainSection = doc.querySelector('section.main');
                    if (mainSection) {{
                        var targetRect = target.getBoundingClientRect();
                        var scrollTop = mainSection.scrollTop;
                        var offset = targetRect.top + scrollTop - 80;
                        mainSection.scrollTo({{top: offset, behavior: 'smooth'}});
                    }} else {{
                        target.scrollIntoView({{behavior: 'smooth', block: 'start'}});
                    }}
                }} else {{
                    setTimeout(function() {{ tryScroll(attempt + 1); }}, 300);
                }}
            }};
            
            setTimeout(function() {{ tryScroll(1); }}, 500);
        }})();
    </script>
    """
    html(scroll_code, height=0)
