/**
 * Основные JavaScript-функции для приложения калькулятора пергол
 */

document.addEventListener('DOMContentLoaded', function() {
    // Активация текущего пункта меню
    activateCurrentMenuItem();

    // Инициализация всплывающих подсказок, если они есть
    initializeTooltips();
    
    // Инициализация интерактивных элементов
    initializeInteractiveElements();
});

/**
 * Активирует текущий пункт меню на основе URL
 */
function activateCurrentMenuItem() {
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('nav a');
    
    menuItems.forEach(item => {
        // Удаляем класс active со всех элементов
        item.classList.remove('active');
        
        // Проверяем, соответствует ли href текущему пути
        const href = item.getAttribute('href');
        if (href === currentPath || 
            (href !== '/' && currentPath.startsWith(href))) {
            item.classList.add('active');
        }
    });
}

/**
 * Инициализирует всплывающие подсказки
 */
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseover', function() {
            const text = this.getAttribute('data-tooltip');
            
            // Создаем элемент подсказки
            const tooltipElement = document.createElement('div');
            tooltipElement.className = 'tooltip';
            tooltipElement.textContent = text;
            
            // Позиционируем элемент
            document.body.appendChild(tooltipElement);
            
            const rect = this.getBoundingClientRect();
            const tooltipRect = tooltipElement.getBoundingClientRect();
            
            tooltipElement.style.left = (rect.left + rect.width / 2 - tooltipRect.width / 2) + 'px';
            tooltipElement.style.top = (rect.top - tooltipRect.height - 10) + 'px';
            
            // Запоминаем элемент для удаления
            this._tooltipElement = tooltipElement;
        });
        
        tooltip.addEventListener('mouseout', function() {
            if (this._tooltipElement) {
                this._tooltipElement.remove();
                this._tooltipElement = null;
            }
        });
    });
}

/**
 * Инициализирует интерактивные элементы на странице
 */
function initializeInteractiveElements() {
    // Настраиваем поля ввода с ограничениями
    const numericInputs = document.querySelectorAll('input[type="number"]');
    
    numericInputs.forEach(input => {
        input.addEventListener('input', function() {
            const min = parseFloat(this.getAttribute('min') || -Infinity);
            const max = parseFloat(this.getAttribute('max') || Infinity);
            const step = parseFloat(this.getAttribute('step') || 1);
            
            let value = parseFloat(this.value);
            
            if (!isNaN(value)) {
                // Округляем значение до ближайшего шага
                const stepDecimalPlaces = (step.toString().split('.')[1] || '').length;
                const factor = Math.pow(10, stepDecimalPlaces);
                
                value = Math.round(value * factor) / factor;
                
                // Ограничиваем значение
                value = Math.max(min, Math.min(max, value));
                
                this.value = value;
            }
        });
    });
    
    // Обработка клика по контейнеру с radio/checkbox для улучшения UX
    const clickableContainers = document.querySelectorAll('.pergola-type, .lamella-size, .option');
    
    clickableContainers.forEach(container => {
        container.addEventListener('click', function(e) {
            // Игнорируем клик непосредственно по input
            if (e.target.tagName !== 'INPUT') {
                const input = this.querySelector('input');
                
                if (input) {
                    if (input.type === 'radio') {
                        input.checked = true;
                        // Вызываем событие изменения для обработки зависимостей
                        input.dispatchEvent(new Event('change'));
                    } else if (input.type === 'checkbox') {
                        input.checked = !input.checked;
                        input.dispatchEvent(new Event('change'));
                    }
                }
            }
        });
    });
}

/**
 * Функция для анимированной прокрутки к элементу
 * @param {string} elementId - ID элемента, к которому нужно прокрутить
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Форматирует число в денежный формат с разделителями
 * @param {number} amount - Сумма для форматирования
 * @returns {string} Форматированная строка
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Включает/выключает индикатор загрузки
 * @param {boolean} show - Показать или скрыть индикатор
 * @param {string} targetId - ID элемента, в котором показывать индикатор
 */
function toggleLoader(show, targetId) {
    const target = document.getElementById(targetId);
    
    if (!target) return;
    
    let loader = target.querySelector('.loader');
    
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.className = 'loader';
            loader.innerHTML = '<div class="spinner"></div><p>Загрузка...</p>';
            target.appendChild(loader);
        }
    } else {
        if (loader) {
            loader.remove();
        }
    }
}