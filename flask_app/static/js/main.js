/**
 * Основной файл JavaScript для приложения калькулятора пергол
 * Содержит утилиты и общие функции, используемые на всех страницах
 */

// Инициализация документа
document.addEventListener('DOMContentLoaded', function() {
  // Активация всех подсказок Bootstrap
  initializeTooltips();
  
  // Настройка плавной прокрутки
  setupSmoothScrolling();
  
  // Активация активного элемента в навигации
  highlightActiveNavItem();
  
  // Инициализация Яндекс.Метрики
  setupYandexMetrika();
  
  // Обработка параметров URL
  processUrlParams();
});

/**
 * Инициализирует все подсказки Bootstrap на странице
 */
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Настраивает плавную прокрутку для всех якорных ссылок на странице
 */
function setupSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

/**
 * Подсвечивает активный элемент в навигационном меню
 */
function highlightActiveNavItem() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
  
  navLinks.forEach(link => {
    const linkPath = link.getAttribute('href');
    
    // Проверяем, соответствует ли путь ссылки текущему пути
    if (linkPath && (
      linkPath === currentPath || 
      (linkPath !== '/' && currentPath.startsWith(linkPath))
    )) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

/**
 * Настраивает отправку событий в Яндекс.Метрику
 */
function setupYandexMetrika() {
  // Добавляем обработчики для кнопок с атрибутом data-ym-event
  document.querySelectorAll('[data-ym-event]').forEach(el => {
    el.addEventListener('click', function() {
      const category = this.getAttribute('data-ym-category') || 'Взаимодействие';
      const action = this.getAttribute('data-ym-event');
      const label = this.getAttribute('data-ym-label') || '';
      
      sendYandexEvent(category, action, label);
    });
  });
  
  // Отслеживаем отправку форм
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
      const formName = this.getAttribute('name') || this.getAttribute('id') || 'Форма';
      sendYandexEvent('Формы', 'Отправка', formName);
    });
  });
}

/**
 * Отправляет событие в Яндекс.Метрику (если она доступна)
 * 
 * @param {string} category - Категория события
 * @param {string} action - Действие
 * @param {string} label - Метка (опционально)
 */
function sendYandexEvent(category, action, label) {
  // Проверяем, инициализирована ли Яндекс.Метрика
  if (typeof ym !== 'undefined') {
    ym(12345678, 'reachGoal', action, {
      category: category,
      label: label
    });
    console.log(`Отправлено событие в Яндекс.Метрику: ${category} / ${action} / ${label}`);
  } else {
    console.log(`Яндекс.Метрика не доступна. Событие: ${category} / ${action} / ${label}`);
    
    // Сохраняем событие для последующей отправки
    if (typeof window.pendingMetrikaEvents === 'undefined') {
      window.pendingMetrikaEvents = [];
    }
    
    window.pendingMetrikaEvents.push({
      category,
      action,
      label
    });
  }
}

/**
 * Обрабатывает параметры URL для контроля состояния приложения
 */
function processUrlParams() {
  const urlParams = new URLSearchParams(window.location.search);
  
  // Обработка импорта данных из PDF
  if (urlParams.has('import') && urlParams.get('import') === 'true') {
    const importedData = localStorage.getItem('importedPdfData');
    
    if (importedData) {
      const dataObj = JSON.parse(importedData);
      console.log('Импортировано из PDF:', dataObj);
      
      // Генерируем событие для уведомления приложения об импорте данных
      const importEvent = new CustomEvent('pdf-data-imported', { detail: dataObj });
      document.dispatchEvent(importEvent);
      
      // Очищаем сохраненные данные
      localStorage.removeItem('importedPdfData');
    }
  }
  
  // Обработка других параметров URL
  // ...
}

/**
 * Форматирует число в денежный формат с валютой
 * 
 * @param {number} price - Число для форматирования
 * @param {string} currency - Валюта (по умолчанию: ₽)
 * @returns {string} Отформатированная строка с валютой
 */
function formatPrice(price, currency = '₽') {
  return new Intl.NumberFormat('ru-RU', {
    style: 'decimal', 
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price) + ' ' + currency;
}

/**
 * Показывает уведомление пользователю
 * 
 * @param {string} message - Сообщение для отображения
 * @param {string} type - Тип уведомления (success, error, warning, info)
 * @param {number} duration - Продолжительность отображения в мс (по умолчанию: 3000)
 */
function showNotification(message, type = 'info', duration = 3000) {
  // Проверяем, существует ли контейнер для уведомлений
  let notificationContainer = document.getElementById('notification-container');
  
  if (!notificationContainer) {
    notificationContainer = document.createElement('div');
    notificationContainer.id = 'notification-container';
    notificationContainer.style.position = 'fixed';
    notificationContainer.style.top = '1rem';
    notificationContainer.style.right = '1rem';
    notificationContainer.style.zIndex = '9999';
    document.body.appendChild(notificationContainer);
  }
  
  // Создаем элемент уведомления
  const notification = document.createElement('div');
  notification.className = `alert alert-${type} alert-dismissible fade show`;
  notification.role = 'alert';
  
  // Добавляем иконку
  let icon = 'info-circle';
  switch (type) {
    case 'success': icon = 'check-circle'; break;
    case 'warning': icon = 'exclamation-triangle'; break;
    case 'error': case 'danger': icon = 'exclamation-circle'; type = 'danger'; break;
  }
  
  notification.innerHTML = `
    <i class="bi bi-${icon} me-2"></i>
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Добавляем анимацию и стили
  notification.style.minWidth = '250px';
  notification.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
  notification.style.marginBottom = '0.5rem';
  notification.style.transform = 'translateX(100%)';
  notification.style.transition = 'transform 0.3s ease-out';
  
  // Добавляем уведомление в контейнер
  notificationContainer.appendChild(notification);
  
  // Запускаем анимацию появления
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 10);
  
  // Автоматическое скрытие уведомления
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)';
    notification.addEventListener('transitionend', () => {
      notification.remove();
    });
  }, duration);
  
  // Обработчик кнопки закрытия
  notification.querySelector('.btn-close').addEventListener('click', () => {
    notification.style.transform = 'translateX(100%)';
    notification.addEventListener('transitionend', () => {
      notification.remove();
    });
  });
}