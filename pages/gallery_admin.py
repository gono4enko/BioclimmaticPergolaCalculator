"""
Страница администрирования галереи

Позволяет включать и исключать изображения из галереи,
обнаруживать дубликаты и управлять отображением фотографий.
"""

import streamlit as st
import os
import sys

# Импортируем компоненты
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components import gallery_admin
from components.admin_auth import admin_required, check_admin_auth, admin_login_form

# Настройка страницы
st.set_page_config(
    page_title="Администрирование галереи",
    page_icon="🖼️",
    layout="wide",
)

# Заголовок страницы
st.title("Администрирование галереи")

# Проверяем права доступа администратора
is_authenticated = check_admin_auth()

if not is_authenticated:
    st.warning("⚠️ Для доступа к администрированию галереи требуется авторизация")
    
    # Отображаем форму входа
    if admin_login_form(location="main"):
        st.rerun()
else:
    # Показываем интерфейс администрирования только после аутентификации
    # Описание функциональности
    st.markdown("""
    ### Страница администрирования галереи фотографий
    
    На этой странице вы можете:
    - Включать и исключать изображения из галереи
    - Находить и устранять дубликаты
    - Управлять отображением фотографий
    """)
    
    # Директория с изображениями
    IMAGES_DIR = "attached_assets"
    
    # Отображаем интерфейс администрирования
    gallery_admin.render_gallery_admin_interface(IMAGES_DIR)

# Добавляем кнопку для возврата к основному приложению
if st.button("Вернуться к калькулятору"):
    st.switch_page("app.py")