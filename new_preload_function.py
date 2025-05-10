def preload_images_js():
    """
    Возвращает JavaScript-код для оптимизированной предварительной загрузки изображений.
    Ускоряет начальную загрузку страницы с минимальными необходимыми ресурсами.
    """
    # Создаем список путей ко всем основным изображениям пергол
    critical_image_paths = [
        # Только самые важные изображения для первой загрузки
        "attached_assets/b500_rotation.png",
        "attached_assets/linear_drive_b500.png"
    ]
    
    secondary_image_paths = [
        "attached_assets/b700_sliding.png", 
        "attached_assets/b600_sandwich.png",
        "attached_assets/somfy_pergola_b700.jpg",
        "attached_assets/pir_sandwich_panel_b600.png",
    ]
    
    tertiary_image_paths = [
        "attached_assets/Линейный привод-2.png",
        "attached_assets/Линейный привод.png",
        "attached_assets/Somfy Pergola.jpg",
        "attached_assets/Снимок экрана 2025-04-16 в 00.35.39.png"
    ]
    
    # Генерируем Base64 данные только для критически важных изображений
    critical_images = []
    for path in critical_image_paths:
        if os.path.exists(path):
            mime_type, base64_data = get_image_base64(path)
            critical_images.append(f"data:{mime_type};base64,{base64_data}")
            logger.info(f"Подготовлено критическое изображение: {path}")
        else:
            logger.warning(f"Не найдено критическое изображение: {path}")
    
    # Готовим пути для вторичных и третичных изображений (без base64 для экономии памяти)
    secondary_images = [path for path in secondary_image_paths if os.path.exists(path)]
    tertiary_images = [path for path in tertiary_image_paths if os.path.exists(path)]
    
    # Кодируем списки в JSON
    critical_json = json.dumps(critical_images)
    secondary_json = json.dumps(secondary_images)
    tertiary_json = json.dumps(tertiary_images)
    
    return f"""
    <script>
        // Функция для предварительной загрузки критически важных изображений (немедленно)
        function preloadCriticalImages() {{
            // Список критически важных изображений для немедленной загрузки
            const criticalImages = {critical_json};
            
            // Сразу загружаем критически важные изображения
            criticalImages.forEach(src => {{
                const link = document.createElement('link');
                link.rel = 'preload';
                link.href = src;
                link.as = 'image';
                link.importance = 'high'; 
                link.fetchpriority = 'high';
                document.head.appendChild(link);
            }});
            
            console.log("🚀 Загружены " + criticalImages.length + " критически важных изображений");
        }}
        
        // Функция для загрузки вторичных изображений (после загрузки страницы)
        function preloadSecondaryImages() {{
            // Вторичные изображения для загрузки после основной страницы
            const secondaryImages = {secondary_json};
            
            // Загружаем с низким приоритетом после загрузки страницы
            secondaryImages.forEach(src => {{
                const img = new Image();
                img.src = src;
                img.importance = 'low';
                img.fetchpriority = 'low';
                img.loading = 'lazy';
                img.style.position = 'absolute';
                img.style.opacity = '0';
                img.style.width = '1px';
                img.style.height = '1px';
                img.style.zIndex = '-1000';
                document.body.appendChild(img);
            }});
            
            console.log("📦 Загружены " + secondaryImages.length + " вторичных изображений");
        }}
        
        // Функция для загрузки третичных изображений (когда браузер простаивает)
        function preloadTertiaryImages() {{
            // Третичные изображения для загрузки в момент простоя
            const tertiaryImages = {tertiary_json};
            
            // Используем requestIdleCallback или setTimeout для минимального влияния на производительность
            const loadMethod = window.requestIdleCallback || 
                ((callback) => setTimeout(callback, 3000));
            
            loadMethod(() => {{
                tertiaryImages.forEach(src => {{
                    setTimeout(() => {{
                        const img = new Image();
                        img.src = src;
                        img.importance = 'low';
                        img.fetchpriority = 'low';
                        img.loading = 'lazy';
                    }}, 100); // Небольшая задержка между загрузками
                }});
                
                console.log("🔄 Загружены " + tertiaryImages.length + " дополнительных изображений");
            }});
        }}
        
        // Запускаем критическую предзагрузку немедленно
        preloadCriticalImages();
        
        // Добавляем кэширующие заголовки через мета-теги
        const metaCache = document.createElement('meta');
        metaCache.httpEquiv = 'Cache-Control';
        metaCache.content = 'public, max-age=31536000, immutable';
        document.head.appendChild(metaCache);
        
        // Добавляем мета-тег для отключения масштабирования на мобильных устройствах
        const metaViewport = document.createElement('meta');
        metaViewport.name = 'viewport';
        metaViewport.content = 'width=device-width, initial-scale=1, maximum-scale=1';
        document.head.appendChild(metaViewport);
        
        // Запускаем остальные загрузки постепенно
        window.addEventListener('load', function() {{
            // Задержка для загрузки вторичных изображений
            setTimeout(preloadSecondaryImages, 300);
            
            // Еще большая задержка для третичных изображений
            setTimeout(preloadTertiaryImages, 1500);
        }});
    </script>
    """
# Новая функция для минимизации загрузки данных в форме
def get_minimal_form_js():
    """
    Предоставляет JavaScript код для ускорения загрузки и отображения формы.
    Ускоряет отображение критически важных элементов формы.
    """
    
    return """
    <script>
        // Функция для оптимизации загрузки форм
        function optimizeFormLoading() {
            // Устанавливаем обновление высоты iframe при изменении размеров 
            // элементов формы, для лучшей работы во внешнем iframe
            function updateIframeHeight() {
                const height = document.body.scrollHeight;
                if (window.parent && window !== window.parent) {
                    window.parent.postMessage({type: 'set-iframe-height', height: height + 20}, '*');
                }
            }

            // Устанавливаем приоритеты загрузки и рендеринга элементов формы
            const prioritizeForm = () => {
                // Находим ввод размеров - это наиболее важная часть
                const dimensionInputs = document.querySelectorAll('input[type="number"]');
                dimensionInputs.forEach(input => {
                    input.style.display = 'block';
                    input.style.opacity = '1';
                });
                
                // Находим кнопку расчета и выделяем ее визуально
                const calcButtons = document.querySelectorAll('button:not(.streamlit-expanderHeader)');
                calcButtons.forEach(button => {
                    if (button.innerText.includes('Рассчитать')) {
                        button.style.boxShadow = '0 0 5px #3f6daa';
                        button.style.transform = 'scale(1.02)';
                    }
                });
                
                // Обновляем высоту iframe для корректного отображения
                updateIframeHeight();
            };
            
            // Запускаем приоритизацию элементов формы сразу после загрузки DOM
            document.addEventListener('DOMContentLoaded', prioritizeForm);
            
            // Обновляем высоту iframe при изменении размеров
            window.addEventListener('resize', updateIframeHeight);
            
            // Добавляем возможность быстрой навигации по форме с клавиатуры
            document.addEventListener('keydown', function(e) {
                // Tab + Alt для перемещения между секциями
                if (e.key === 'Tab' && e.altKey) {
                    e.preventDefault();
                    const sections = document.querySelectorAll('.stForm, .stSelectbox, .stNumberInput');
                    const currentFocused = document.activeElement;
                    let nextFocus = null;
                    
                    // Ищем следующий элемент формы для фокуса
                    for (let i = 0; i < sections.length; i++) {
                        if (sections[i].contains(currentFocused) && i < sections.length - 1) {
                            nextFocus = sections[i+1].querySelector('input, select, button');
                            break;
                        }
                    }
                    
                    // Если нашли следующий элемент, фокусируемся на нем
                    if (nextFocus) {
                        nextFocus.focus();
                    }
                }
            });
        }
        
        // Запускаем функцию оптимизации загрузки форм
        optimizeFormLoading();
    </script>
    """
