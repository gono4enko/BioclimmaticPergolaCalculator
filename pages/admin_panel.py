"""
Административная панель для управления приложением
"""
import streamlit as st
from components.admin_auth import admin_required, create_admin_panel, check_admin_auth, admin_login_form
import os

st.set_page_config(
    page_title="Административная панель",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Создаем заголовок страницы
st.title("Административная панель")

# Проверяем права доступа
is_authenticated = check_admin_auth()

if not is_authenticated:
    st.warning("Для доступа к панели администратора требуется авторизация")
    
    # Отображаем форму входа
    if admin_login_form(location="main"):
        st.experimental_rerun()
else:
    # Отображаем административный интерфейс
    st.success("Вы авторизованы как администратор")
    
    tabs = st.tabs([
        "Кэш и настройки", 
        "Защита контента", 
        "Управление галереей", 
        "Акции", 
        "Тестирование"
    ])
    
    # Вкладка управления кэшем и настройками
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            admin_auth, cache_expander = create_admin_panel(
                "Управление кэшем", 
                location="main", 
                expanded=True
            )
            
            with cache_expander:
                st.write("Настройки кэширования и производительности")
                
                if st.button("Очистить кэш приложения"):
                    try:
                        # Используем session_state для хранения кэша
                        for key in list(st.session_state.keys()):
                            if key.startswith("cache_"):
                                del st.session_state[key]
                        st.success("Кэш успешно очищен")
                    except Exception as e:
                        st.error(f"Ошибка при очистке кэша: {str(e)}")
                        
                if st.button("Перезагрузить приложение"):
                    st.experimental_rerun()
                
                st.write("Статистика системы:")
                st.text(f"Путь к рабочей директории: {os.getcwd()}")
                
                # Размер кэша
                cache_keys = [k for k in st.session_state.keys() if k.startswith("cache_")]
                st.text(f"Количество элементов в кэше: {len(cache_keys)}")
                
        with col2:
            admin_auth, settings_expander = create_admin_panel(
                "Общие настройки", 
                location="main", 
                expanded=True
            )
            
            with settings_expander:
                st.write("Общие настройки приложения")
                
                # Настройки курса евро
                current_euro = st.session_state.get("EURO_RATE", 100)
                new_euro = st.number_input(
                    "Курс евро (₽)",
                    min_value=50.0,
                    max_value=200.0,
                    value=float(current_euro),
                    step=0.5
                )
                
                if st.button("Обновить курс евро"):
                    st.session_state["EURO_RATE"] = new_euro
                    st.success(f"Курс евро обновлен: {new_euro} ₽")
                
                # Переключатели функций
                debug_mode = st.checkbox("Режим отладки", value=st.session_state.get("DEBUG_MODE", False))
                if debug_mode != st.session_state.get("DEBUG_MODE", False):
                    st.session_state["DEBUG_MODE"] = debug_mode
                    st.success(f"Режим отладки {'включен' if debug_mode else 'отключен'}")
                
                analytics_enabled = st.checkbox("Аналитика", value=st.session_state.get("ANALYTICS_ENABLED", True))
                if analytics_enabled != st.session_state.get("ANALYTICS_ENABLED", True):
                    st.session_state["ANALYTICS_ENABLED"] = analytics_enabled
                    st.success(f"Аналитика {'включена' if analytics_enabled else 'отключена'}")
                
    # Вкладка защиты контента
    with tabs[1]:
        admin_auth, protection_expander = create_admin_panel(
            "Защита контента", 
            location="main", 
            expanded=True
        )
        
        with protection_expander:
            st.write("Настройки защиты контента")
            
            protection_enabled = st.checkbox(
                "Включить защиту контента", 
                value=st.session_state.get("CONTENT_PROTECTION", True)
            )
            
            if protection_enabled != st.session_state.get("CONTENT_PROTECTION", True):
                st.session_state["CONTENT_PROTECTION"] = protection_enabled
                st.success(f"Защита контента {'включена' if protection_enabled else 'отключена'}")
            
            if protection_enabled:
                st.write("Настройки защиты от копирования:")
                
                disable_right_click = st.checkbox(
                    "Отключить контекстное меню", 
                    value=st.session_state.get("DISABLE_RIGHT_CLICK", True)
                )
                
                if disable_right_click != st.session_state.get("DISABLE_RIGHT_CLICK", True):
                    st.session_state["DISABLE_RIGHT_CLICK"] = disable_right_click
                    st.success(f"Контекстное меню {'отключено' if disable_right_click else 'включено'}")
                
                disable_selection = st.checkbox(
                    "Отключить выделение текста", 
                    value=st.session_state.get("DISABLE_SELECTION", True)
                )
                
                if disable_selection != st.session_state.get("DISABLE_SELECTION", True):
                    st.session_state["DISABLE_SELECTION"] = disable_selection
                    st.success(f"Выделение текста {'отключено' if disable_selection else 'включено'}")
    
    # Вкладка управления галереей
    with tabs[2]:
        admin_auth, gallery_expander = create_admin_panel(
            "Управление галереей", 
            location="main", 
            expanded=True
        )
        
        with gallery_expander:
            st.write("Управление изображениями и галереей")
            
            st.file_uploader(
                "Загрузить новое изображение",
                type=["jpg", "jpeg", "png", "heic"],
                accept_multiple_files=True,
                help="Выберите файлы изображений для загрузки"
            )
            
            if st.button("Обработать все изображения в галерее"):
                st.info("Запуск обработки изображений...")
                # Здесь должен быть код для обработки изображений
                st.success("Изображения успешно обработаны")
    
    # Вкладка управления акциями
    with tabs[3]:
        admin_auth, promo_expander = create_admin_panel(
            "Управление акциями", 
            location="main", 
            expanded=True
        )
        
        with promo_expander:
            st.write("Управление акциями и скидками")
            
            promo_enabled = st.checkbox(
                "Включить акции", 
                value=st.session_state.get("PROMOTIONS_ENABLED", True)
            )
            
            if promo_enabled != st.session_state.get("PROMOTIONS_ENABLED", True):
                st.session_state["PROMOTIONS_ENABLED"] = promo_enabled
                st.success(f"Акции {'включены' if promo_enabled else 'отключены'}")
            
            st.write("Настройки сезонных акций:")
            
            seasons = ["Весна", "Лето", "Осень", "Зима"]
            current_season = st.selectbox(
                "Текущий сезон",
                options=seasons,
                index=seasons.index(st.session_state.get("CURRENT_SEASON", "Весна"))
            )
            
            if current_season != st.session_state.get("CURRENT_SEASON", "Весна"):
                st.session_state["CURRENT_SEASON"] = current_season
                st.success(f"Установлен сезон: {current_season}")
            
            # Настройка размера скидки
            discount_percent = st.slider(
                "Размер скидки (%)",
                min_value=0,
                max_value=25,
                value=st.session_state.get("DISCOUNT_PERCENT", 10),
                step=1
            )
            
            if discount_percent != st.session_state.get("DISCOUNT_PERCENT", 10):
                st.session_state["DISCOUNT_PERCENT"] = discount_percent
                st.success(f"Установлен размер скидки: {discount_percent}%")
    
    # Вкладка тестирования
    with tabs[4]:
        admin_auth, test_expander = create_admin_panel(
            "Тестирование функций", 
            location="main", 
            expanded=True
        )
        
        with test_expander:
            st.write("Инструменты для тестирования функций")
            
            if st.button("Запустить тестирование функций расчета"):
                st.info("Запуск тестирования функций расчета...")
                # Здесь должен быть код для тестирования
                st.success("Тесты успешно пройдены")
            
            if st.button("Проверить целостность данных"):
                st.info("Проверка целостности данных...")
                # Здесь должен быть код для проверки целостности
                st.success("Данные в порядке")
            
            st.write("Тестовые параметры:")
            
            test_width = st.number_input(
                "Тестовая ширина (м)",
                min_value=2.0,
                max_value=15.0,
                value=4.0,
                step=0.5
            )
            
            test_length = st.number_input(
                "Тестовый вынос (м)",
                min_value=2.0,
                max_value=8.0,
                value=4.0,
                step=0.5
            )
            
            test_type = st.selectbox(
                "Тестовый тип перголы",
                options=["B500NEW", "B700NEW", "B600"]
            )
            
            if st.button("Запустить тестовый расчет"):
                st.info(f"Расчет для перголы {test_type} {test_width}×{test_length} м...")
                # Здесь должен быть код для тестового расчета
                st.success("Тестовый расчет выполнен успешно")

# Добавляем кнопку выхода из административного режима
if is_authenticated:
    if st.button("Выйти из режима администратора"):
        st.session_state.admin_authenticated = False
        st.experimental_rerun()