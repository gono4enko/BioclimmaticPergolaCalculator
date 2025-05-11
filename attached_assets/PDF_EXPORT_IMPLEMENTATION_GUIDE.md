# Руководство по реализации PDF-экспорта с корректным именованием файлов

Данный документ описывает механизм генерации и выгрузки PDF-файлов с правильным именованием, который можно использовать в любых проектах на Flask с JavaScript-интерфейсом.

## Общая архитектура

Реализация состоит из трех основных компонентов:

1. **Backend (Flask)**: Генерирует PDF и устанавливает HTTP-заголовки для правильного именования файла
2. **JavaScript-клиент**: Обрабатывает ответ сервера и предоставляет пользователю файл с корректным именем
3. **Система хранения PDF**: Сохраняет созданные PDF в отдельной директории для отладки и архивирования

## 1. Backend (Flask)

### Маршрут для генерации PDF

```python
@app.route('/export_pdf_new', methods=['GET'])
def export_pdf_new():
    """
    Новый маршрут для экспорта PDF с использованием simplified_pdf_generator
    и данных из API.
    """
    try:
        # Получаем ID последнего расчета из параметра запроса или используем последний
        calculation_id = request.args.get('id', None)
        
        # Загружаем данные расчета из хранилища
        calculation_data = load_calculation_data(calculation_id)
        
        if not calculation_data:
            return jsonify({
                "success": False,
                "error": "Данные расчета не найдены"
            }), 404
        
        # Генерируем PDF с использованием simplified_pdf_generator
        from simplified_pdf_generator import generate_pdf
        
        # Собираем информацию для формирования имени файла
        construction_type = calculation_data.get('constructionType', 'unknown')
        model = calculation_data.get('model', 'unknown')
        width = calculation_data.get('width', 0)
        depth = calculation_data.get('depth', 0)
        
        # Создаем информативное имя файла
        file_name = f"КП тентовая пергола {construction_type} {model} {width} м × {depth} м {datetime.now().strftime('%d.%m.%Y')}.pdf"
        
        # Генерируем PDF
        pdf_data = generate_pdf(calculation_data)
        
        # Сохраняем файл в директорию для отладки
        debug_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug_pdfs')
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        
        debug_file_path = os.path.join(debug_dir, file_name)
        with open(debug_file_path, 'wb') as f:
            f.write(pdf_data)
        
        # Подготавливаем ответ с PDF
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="KP_tentovaya_pergola.pdf"; filename*=UTF-8\'\'{quote(file_name)}'
        response.headers['Content-Length'] = len(pdf_data)
        
        return response
        
    except Exception as e:
        app.logger.error(f"Ошибка при создании PDF: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
```

### Ключевые моменты в серверной части

1. **Формирование имени файла**: Имя включает тип конструкции, модель, размеры и дату.
2. **HTTP-заголовки**:
   - Используется комбинация простого имени файла (`filename="KP_tentovaya_pergola.pdf"`) для старых браузеров
   - И расширенного параметра (`filename*=UTF-8''...`) для современных браузеров, поддерживающих Unicode
3. **URL-кодирование**: Имя файла URL-кодируется с помощью функции `quote(file_name)` для совместимости со всеми браузерами

## 2. JavaScript-клиент

### Обработка ответа сервера и скачивание файла

```javascript
function generatePdf(url, generatorType) {
    // Получаем данные из формы калькулятора или из последнего расчета
    const calculationData = window.latestCalculationData || {};
    
    if (!calculationData || Object.keys(calculationData).length === 0) {
        showAlert('Внимание!', 'Пожалуйста, выполните расчет перед созданием PDF.');
        return;
    }
    
    // Показываем индикатор загрузки
    showLoading(true, 'Создание PDF документа...');
    
    // Сначала сохраняем данные расчета через API
    fetch('/api/calculations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(calculationData)
    })
    .then(response => response.json())
    .then(saveResult => {
        // Отправляем запрос на генерацию PDF
        const method = generatorType === 'new' ? 'GET' : 'POST';
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        // Для стандартного генератора добавляем данные в тело запроса
        if (method === 'POST') {
            options.body = JSON.stringify(calculationData);
        }
        
        // Отправляем запрос на создание PDF
        return fetch(url, options);
    })
    .then(response => {
        // Получаем имя файла из заголовка Content-Disposition, если он есть
        const contentDisposition = response.headers.get('content-disposition');
        let fileName = 'КП тентовая пергола.pdf'; // Значение по умолчанию
        
        if (contentDisposition) {
            // Сначала пробуем извлечь из параметра filename*=UTF-8''...
            const fileNameUtf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
            if (fileNameUtf8Match && fileNameUtf8Match[1]) {
                // Декодируем URL-encoded имя файла
                try {
                    fileName = decodeURIComponent(fileNameUtf8Match[1]);
                    console.log(`Извлечено UTF-8 имя файла: ${fileName}`);
                } catch (e) {
                    console.warn(`Ошибка при декодировании UTF-8 имени файла: ${e.message}`);
                }
            } else {
                // Если нет filename*, пробуем обычный filename
                const fileNameMatch = contentDisposition.match(/filename=["']?([^"';\s]+)/i);
                if (fileNameMatch && fileNameMatch[1]) {
                    fileName = fileNameMatch[1];
                    console.log(`Извлечено обычное имя файла: ${fileName}`);
                }
            }
        }
        
        console.log(`Итоговое имя файла для сохранения: ${fileName}`);
        
        // Проверяем тип содержимого
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
            // Возвращаем объект с блобом и именем файла
            return response.blob().then(blob => {
                return { blob, fileName };
            });
        } else {
            throw new Error('Сервер не вернул PDF документ.');
        }
    })
    .then(data => {
        // Извлекаем блоб и имя файла
        const { blob, fileName } = data;
        
        // Создаем URL для скачивания
        const pdfUrl = URL.createObjectURL(blob);
        
        // Создаем ссылку для скачивания
        const downloadLink = document.createElement('a');
        downloadLink.href = pdfUrl;
        
        // Используем имя файла, полученное от сервера
        downloadLink.download = fileName;
        
        console.log(`Скачивание файла с именем: ${fileName}`);
        
        // Добавляем элемент на страницу и запускаем скачивание
        document.body.appendChild(downloadLink);
        downloadLink.click();
        
        // Удаляем элемент и освобождаем ресурсы
        setTimeout(() => {
            document.body.removeChild(downloadLink);
            URL.revokeObjectURL(pdfUrl);
        }, 100);
        
        // Показываем дополнительную кнопку для открытия в браузере
        const alertMessage = document.createElement('div');
        alertMessage.className = 'pdf-alert';
        alertMessage.innerHTML = `
            <div class="pdf-alert-content">
                <p>PDF документ скачивается автоматически.</p>
                <button class="open-in-browser-btn">Открыть в браузере</button>
            </div>
        `;
        document.body.appendChild(alertMessage);
        
        // Добавляем обработчик для кнопки открытия в браузере
        const openBrowserBtn = alertMessage.querySelector('.open-in-browser-btn');
        if (openBrowserBtn) {
            openBrowserBtn.addEventListener('click', function() {
                // Открываем PDF в новой вкладке
                window.open(pdfUrl, '_blank');
                // Скрываем сообщение
                alertMessage.style.display = 'none';
            });
        }
        
        // Скрываем сообщение через 5 секунд
        setTimeout(() => {
            if (alertMessage.parentNode) {
                document.body.removeChild(alertMessage);
            }
        }, 5000);
        
        // Убираем индикатор загрузки
        showLoading(false);
    })
    .catch(error => {
        console.error('Ошибка при обработке PDF:', error);
        showAlert('Ошибка', error.message || 'Не удалось создать PDF. Попробуйте позже.');
        showLoading(false);
    });
}
```

### Ключевые моменты в клиентской части

1. **Извлечение имени файла**: Код сначала пытается получить имя файла из параметра `filename*=UTF-8''...`, который поддерживает Unicode, затем из обычного параметра `filename`.
2. **Скачивание файла**: Создается временная скрытая ссылка с атрибутом `download` и программно кликается, что вызывает скачивание файла с правильным именем.
3. **Дополнительный просмотр**: Пользователю предоставляется опция "Открыть в браузере", которая открывает PDF в новой вкладке.

## 3. Отладка и тестирование

1. **Сохранение локальных копий**: Все сгенерированные PDF сохраняются в директорию `debug_pdfs` для отладки и архивирования.
2. **Логирование**: Логирование всех этапов генерации и выгрузки PDF для определения возможных проблем.
3. **Обработка ошибок**: Подробное логирование ошибок и информативные сообщения для пользователя.

## Рекомендации по интеграции в другие проекты

### Бэкенд (Flask)

1. Импортируйте необходимые библиотеки:
```python
from flask import make_response, jsonify, request
from urllib.parse import quote
from datetime import datetime
import os
```

2. Настройте маршрут для генерации PDF.
3. Сформируйте информативное имя файла, включающее ключевые параметры.
4. Используйте комбинацию заголовков для максимальной совместимости:
```python
response.headers['Content-Disposition'] = f'inline; filename="simple_name.pdf"; filename*=UTF-8\'\'{quote(detailed_file_name)}'
```

### Фронтенд (JavaScript)

1. Извлеките имя файла из заголовка ответа:
```javascript
const contentDisposition = response.headers.get('content-disposition');
const fileNameUtf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
if (fileNameUtf8Match && fileNameUtf8Match[1]) {
    fileName = decodeURIComponent(fileNameUtf8Match[1]);
}
```

2. Создайте механизм программного скачивания файла:
```javascript
const downloadLink = document.createElement('a');
downloadLink.href = URL.createObjectURL(blob);
downloadLink.download = fileName;
document.body.appendChild(downloadLink);
downloadLink.click();
document.body.removeChild(downloadLink);
```

3. Предоставьте пользователю возможность выбора между скачиванием и просмотром.

## Заключение

Данная реализация обеспечивает надежный механизм скачивания PDF-файлов с корректными именами, включающими специфическую информацию о документе. Система совместима с большинством браузеров, поддерживает Unicode-символы и предоставляет хороший пользовательский опыт с выбором между скачиванием и просмотром файла.