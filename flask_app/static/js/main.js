/**
 * Основной JavaScript файл для калькулятора пергол.
 * Содержит функции для интерактивного взаимодействия с пользователем.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Обновление текущего года в футере
    updateCopyrightYear();
    
    // Прокрутка к якорям при клике на навигационные ссылки
    setupSmoothScrolling();
});

/**
 * Обновляет год в копирайте футера.
 */
function updateCopyrightYear() {
    const currentYear = new Date().getFullYear();
    const copyrightElements = document.querySelectorAll('.copyright-year');
    
    copyrightElements.forEach(elem => {
        elem.textContent = currentYear;
    });
}

/**
 * Настраивает плавную прокрутку к якорям на странице.
 */
function setupSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
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
 * Форматирует числовое значение как денежную сумму.
 * 
 * @param {number} price - Цена для форматирования
 * @returns {string} Отформатированная строка с ценой
 */
function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU').format(Math.round(price));
}

/**
 * Показывает сообщение пользователю.
 * 
 * @param {string} message - Сообщение для отображения
 * @param {string} type - Тип сообщения (success, warning, error)
 */
function showMessage(message, type = 'info') {
    // Создаем элемент сообщения
    const messageElement = document.createElement('div');
    messageElement.className = `alert alert-${type}`;
    messageElement.textContent = message;
    
    // Контейнер для сообщений
    let messagesContainer = document.querySelector('.messages');
    
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'messages';
        document.querySelector('main').prepend(messagesContainer);
    }
    
    // Добавляем сообщение
    messagesContainer.appendChild(messageElement);
    
    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
        messageElement.remove();
        
        // Если контейнер пустой, удаляем его
        if (messagesContainer.children.length === 0) {
            messagesContainer.remove();
        }
    }, 5000);
}

/**
 * Загружает и отображает изображение перголы.
 * 
 * @param {string} pergolaType - Тип перголы
 */
function loadPergolaImage(pergolaType) {
    const imageContainer = document.getElementById('pergolaImage');
    if (!imageContainer) return;
    
    const imagePath = `/static/images/${pergolaType.toLowerCase()}_main.jpg`;
    
    // Добавляем анимацию для плавной смены изображения
    imageContainer.style.opacity = '0';
    
    setTimeout(() => {
        imageContainer.src = imagePath;
        imageContainer.style.opacity = '1';
    }, 300);
}

/**
 * Обновляет доступные размеры ламелей в зависимости от выбранного типа перголы.
 * 
 * @param {string} pergolaType - Выбранный тип перголы
 */
function updateLamellaSizes(pergolaType) {
    const lamellaSizes = document.querySelectorAll('.lamella-size');
    
    // Показать все размеры ламелей
    lamellaSizes.forEach(elem => {
        elem.style.display = 'block';
    });
    
    // Для B600 доступны только PIR панели
    if (pergolaType === 'B600') {
        lamellaSizes.forEach(elem => {
            const input = elem.querySelector('input');
            if (input.value !== 'PIR') {
                elem.style.display = 'none';
            } else {
                input.checked = true;
            }
        });
    }
}

/**
 * Обновляет ограничения размеров перголы в зависимости от выбранного типа и размера ламелей.
 * 
 * @param {string} pergolaType - Выбранный тип перголы
 * @param {string} lamellaSize - Выбранный размер ламелей
 */
function updateDimensionLimits(pergolaType, lamellaSize) {
    const widthInput = document.getElementById('width');
    const lengthInput = document.getElementById('length');
    
    if (!widthInput || !lengthInput) return;
    
    // Установка ограничений по умолчанию
    let maxWidth = 15.0;
    let maxLength = 8.0;
    
    // Корректировка ограничений в зависимости от типа перголы и размера ламелей
    if (pergolaType === 'B500NEW' || pergolaType === 'B700NEW') {
        if (lamellaSize === '250') {
            maxWidth = 13.5;
        }
    } else if (pergolaType === 'B600') {
        maxWidth = 13.5;
    }
    
    // Обновляем атрибуты ввода
    widthInput.setAttribute('max', maxWidth);
    lengthInput.setAttribute('max', maxLength);
    
    // Корректируем значения, если они превышают новые ограничения
    if (parseFloat(widthInput.value) > maxWidth) {
        widthInput.value = maxWidth;
    }
    
    if (parseFloat(lengthInput.value) > maxLength) {
        lengthInput.value = maxLength;
    }
}

/**
 * Экспортирует результаты расчета в PDF.
 * 
 * @param {Object} calculationData - Данные расчета для экспорта
 */
function exportToPdf(calculationData) {
    // Показываем индикатор загрузки
    showMessage('Генерация PDF...', 'info');
    
    fetch('/api/export-pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(calculationData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Перенаправляем на скачивание PDF
            window.location.href = data.pdf_url;
            showMessage('PDF успешно сгенерирован', 'success');
        } else {
            showMessage('Ошибка при генерации PDF: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showMessage('Произошла ошибка при экспорте в PDF', 'error');
    });
}