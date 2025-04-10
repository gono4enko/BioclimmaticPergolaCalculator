"""
Модуль для добавления кода Яндекс.Метрики и отправки событий
"""
import streamlit as st

def add_yandex_metrika():
    """
    Добавляет код счетчика Яндекс.Метрики на страницу и настраивает отправку событий.
    Также добавляет глобальную функцию sendYandexEvent для удобного отправления событий из JavaScript.
    """
    st.markdown("""
    <!-- Яндекс.Метрика -->
    <script type="text/javascript">
      // Инициализация Яндекс.Метрики
      (function(m,e,t,r,i,k,a){ m[i]=m[i]||function(){ (m[i].a=m[i].a||[]).push(arguments) };
      m[i].l=1*new Date(); k=e.createElement(t), a=e.getElementsByTagName(t)[0];
      k.async=1; k.src=r; a.parentNode.insertBefore(k,a) })
      (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

      ym(65714473, "init", {
          clickmap:true,
          trackLinks:true,
          accurateTrackBounce:true
      });
      
      // Глобальная функция для отправки событий в Яндекс.Метрику
      window.sendYandexEvent = function(eventName) {
        if (typeof ym !== 'undefined') {
          ym(65714473, 'reachGoal', eventName);
          console.log('Событие ' + eventName + ' отправлено в Яндекс.Метрику');
          return true;
        } else {
          console.error('Яндекс.Метрика не загружена, событие ' + eventName + ' не отправлено');
          return false;
        }
      };
      
      // Глобальное хранилище для отложенной отправки событий
      window.yaMetrikaEvents = window.yaMetrikaEvents || [];
      
      // Слушаем события из localStorage для межоконной коммуникации
      window.addEventListener('storage', function(e) {
        if (e.key === 'ya_metrika_event') {
          try {
            const eventData = JSON.parse(e.newValue);
            if (eventData && eventData.name) {
              sendYandexEvent(eventData.name);
            }
          } catch (err) {
            console.error('Ошибка при обработке события из localStorage:', err);
          }
        }
      });
      
      // Проверяем, есть ли запланированные события
      document.addEventListener('DOMContentLoaded', function() {
        if (window.yaMetrikaEvents && window.yaMetrikaEvents.length > 0) {
          setTimeout(function() {
            console.log('Отправка отложенных событий в Яндекс.Метрику', window.yaMetrikaEvents);
            window.yaMetrikaEvents.forEach(function(eventName) {
              sendYandexEvent(eventName);
            });
            window.yaMetrikaEvents = [];
          }, 1500); // Даем достаточно времени для загрузки метрики
        }
      });
    </script>
    <noscript><div><img src="https://mc.yandex.ru/watch/65714473" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
    <!-- /Яндекс.Метрика -->
    """, unsafe_allow_html=True)

def send_calc_success_event():
    """
    Отправляет событие успешного расчета в Яндекс.Метрику.
    Сохраняет событие в localStorage для надежного срабатывания даже при перезагрузке страницы.
    """
    st.markdown("""
    <script type="text/javascript">
      // Сохраняем событие в localStorage для межоконной коммуникации
      try {
        localStorage.setItem('ya_metrika_event', JSON.stringify({
          name: 'calc_success',
          timestamp: Date.now()
        }));
      } catch (e) {
        console.error('Ошибка при сохранении события в localStorage:', e);
      }
      
      // Добавляем событие в очередь на отправку
      if (window.yaMetrikaEvents) {
        window.yaMetrikaEvents.push('calc_success');
      } else {
        window.yaMetrikaEvents = ['calc_success'];
      }
      
      // Отправляем событие сразу, если функция доступна
      if (typeof window.sendYandexEvent === 'function') {
        window.sendYandexEvent('calc_success');
        console.log('Запланировано событие calc_success для Яндекс.Метрики');
      } else {
        console.log('Функция sendYandexEvent не найдена, событие calc_success добавлено в очередь');
        
        // Пробуем отправить напрямую через ym, если доступно
        if (typeof ym !== 'undefined') {
          ym(65714473, 'reachGoal', 'calc_success');
          console.log('Событие calc_success отправлено в Яндекс.Метрику напрямую');
        }
      }
      
      // Ставим отложенную отправку для уверенности
      setTimeout(function() {
        if (typeof ym !== 'undefined') {
          ym(65714473, 'reachGoal', 'calc_success');
          console.log('Событие calc_success отправлено в Яндекс.Метрику (по таймауту)');
        }
      }, 1000);
    </script>
    """, unsafe_allow_html=True)