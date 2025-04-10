"""
Модуль для добавления кода Яндекс.Метрики и отправки событий
"""
import streamlit as st

def add_yandex_metrika():
    """
    Добавляет код счетчика Яндекс.Метрики на страницу
    """
    st.markdown("""
    <!-- Яндекс.Метрика -->
    <script type="text/javascript">
      (function(m,e,t,r,i,k,a){ m[i]=m[i]||function(){ (m[i].a=m[i].a||[]).push(arguments) };
      m[i].l=1*new Date(); k=e.createElement(t), a=e.getElementsByTagName(t)[0];
      k.async=1; k.src=r; a.parentNode.insertBefore(k,a) })
      (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

      ym(65714473, "init", {
          clickmap:true,
          trackLinks:true,
          accurateTrackBounce:true
      });
    </script>
    <noscript><div><img src="https://mc.yandex.ru/watch/65714473" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
    <!-- /Яндекс.Метрика -->
    """, unsafe_allow_html=True)

def send_calc_success_event():
    """
    Отправляет событие успешного расчета в Яндекс.Метрику
    """
    st.markdown("""
    <script type="text/javascript">
      // Проверяем, что функция ym доступна
      if (typeof ym !== 'undefined') {
        // Отправляем событие в Яндекс.Метрику
        ym(65714473, 'reachGoal', 'calc_success');
        console.log('Событие calc_success отправлено в Яндекс.Метрику');
      } else {
        console.log('Яндекс.Метрика не загружена, событие не отправлено');
      }
    </script>
    """, unsafe_allow_html=True)