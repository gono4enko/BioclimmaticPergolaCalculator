/**
 * Основной JavaScript файл для функциональности приложения
 */

document.addEventListener('DOMContentLoaded', function() {
    // Проверка, запущен ли JavaScript
    console.log('Main.js loaded successfully');
    
    // Добавляем класс для запуска CSS-анимаций
    document.body.classList.add('js-enabled');
    
    // Плавная прокрутка для якорных ссылок
    setupSmoothScrolling();
    
    // Инициализация всплывающих подсказок Bootstrap, если они используются
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Отправка событий в Яндекс.Метрику, если она подключена
    setupYandexMetrikaEvents();
    
    // Обработка параметров URL, если страница - калькулятор
    if (window.location.pathname.includes('calculator')) {
        processUrlParams();
    }
});

/**
 * Настройка плавной прокрутки для якорных ссылок
 */
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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
 * Настройка событий Яндекс.Метрики
 */
function setupYandexMetrikaEvents() {
    // Отслеживание событий калькулятора
    const calculateButton = document.querySelector('button[type="submit"]');
    if (calculateButton) {
        calculateButton.addEventListener('click', function() {
            sendYandexEvent('calculator', 'click', 'calculate');
        });
    }
    
    // Отслеживание событий экспорта PDF
    const exportPdfButton = document.getElementById('exportPDF');
    if (exportPdfButton) {
        exportPdfButton.addEventListener('click', function() {
            sendYandexEvent('calculator', 'click', 'export_pdf');
        });
    }
    
    // Отслеживание переходов по каталогу
    const catalogLinks = document.querySelectorAll('.catalog-item a');
    catalogLinks.forEach(link => {
        link.addEventListener('click', function() {
            sendYandexEvent('catalog', 'click', this.getAttribute('href'));
        });
    });
}

/**
 * Отправка события в Яндекс.Метрику
 * @param {string} category - Категория события
 * @param {string} action - Действие
 * @param {string} label - Метка
 */
function sendYandexEvent(category, action, label) {
    try {
        if (typeof ym !== 'undefined') {
            ym(89136431, 'reachGoal', action, {
                category: category,
                label: label
            });
            console.log(`Yandex.Metrika event sent: ${category} / ${action} / ${label}`);
        } else {
            console.log(`Yandex.Metrika not available. Event would be: ${category} / ${action} / ${label}`);
        }
    } catch (e) {
        console.error('Error sending Yandex.Metrika event:', e);
    }
}

/**
 * Обработка параметров URL для калькулятора
 */
function processUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Заполнение типа перголы
    if (urlParams.has('type')) {
        const type = urlParams.get('type');
        const typeRadio = document.querySelector(`input[name="pergola_type"][value="${type}"]`);
        if (typeRadio) {
            typeRadio.checked = true;
            const event = new Event('change');
            typeRadio.dispatchEvent(event);
            
            // Выделяем карточку
            const card = typeRadio.closest('.option-card');
            if (card) {
                // Снимаем выделение с других карточек
                document.querySelectorAll('.option-card[data-option="pergola-type"]').forEach(c => {
                    c.classList.remove('selected');
                });
                card.classList.add('selected');
            }
        }
    }
    
    // Заполнение размера ламелей
    if (urlParams.has('lamella')) {
        const lamella = urlParams.get('lamella');
        const lamellaRadio = document.querySelector(`input[name="lamella_size"][value="${lamella}"]`);
        if (lamellaRadio) {
            lamellaRadio.checked = true;
            const event = new Event('change');
            lamellaRadio.dispatchEvent(event);
            
            // Выделяем карточку
            const card = lamellaRadio.closest('.option-card');
            if (card) {
                // Снимаем выделение с других карточек
                document.querySelectorAll('.option-card[data-option="lamella-size"]').forEach(c => {
                    c.classList.remove('selected');
                });
                card.classList.add('selected');
            }
        }
    }
    
    // Заполнение модулей
    if (urlParams.has('modules')) {
        const modules = urlParams.get('modules');
        // Здесь нет прямого поля для модулей, но можно рассчитать на основе ширины
        // Приблизительный расчет: до 4м - 1 модуль, до 7м - 2 модуля, больше - 3 модуля
        const width = parseInt(modules) * 2 + 1; // Примерная формула
        const widthInput = document.getElementById('width');
        if (widthInput && width > 0) {
            widthInput.value = Math.min(width, 7); // Ограничиваем максимальной шириной
        }
    }
    
    // Включение LED подсветки
    if (urlParams.has('led') && urlParams.get('led') === 'true') {
        const ledCheckbox = document.getElementById('ledLighting');
        if (ledCheckbox) {
            ledCheckbox.checked = true;
            
            // Выделяем карточку
            const card = ledCheckbox.closest('.option-card');
            if (card) {
                card.classList.add('selected');
            }
        }
    }
    
    // Другие параметры можно обрабатывать аналогично
}

/**
 * Форматирование числа как цены
 * @param {number} price - Число для форматирования
 * @returns {string} - Отформатированная строка
 */
function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU').format(Math.round(price));
}