"""
Модуль для аутентификации администратора и защиты административных функций.
Предоставляет компоненты для аутентификации и проверки прав доступа.
"""
import streamlit as st
import hashlib
import time
from functools import wraps

# Фиксированный пароль администратора (хранится в хешированном виде)
ADMIN_PASSWORD_HASH = "a05a8083f4d3dac9c2935b94ec7b870a61b981ed3c1f6d4ee1a66a7445993384"  # хеш для 'andrew009'


def hash_password(password):
    """
    Хеширует пароль с использованием SHA-256
    
    Args:
        password (str): Пароль для хеширования
        
    Returns:
        str: Хеш пароля в виде шестнадцатеричной строки
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash=ADMIN_PASSWORD_HASH):
    """
    Проверяет соответствие пароля хешу
    
    Args:
        password (str): Пароль для проверки
        password_hash (str): Хеш для сравнения (по умолчанию используется ADMIN_PASSWORD_HASH)
        
    Returns:
        bool: True если пароль соответствует хешу, иначе False
    """
    return hash_password(password) == password_hash


def check_admin_auth():
    """
    Проверяет, авторизован ли пользователь как администратор
    
    Returns:
        bool: True если пользователь авторизован, иначе False
    """
    return st.session_state.get("admin_authenticated", False)


def admin_login_form(location="sidebar"):
    """
    Отображает форму авторизации администратора
    
    Args:
        location (str): Местоположение формы - 'sidebar' или 'main'
        
    Returns:
        bool: True если пользователь авторизован, иначе False
    """
    # Инициализируем состояние аутентификации, если оно еще не установлено
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
        st.session_state.auth_error = False
        st.session_state.login_attempts = 0
        st.session_state.last_attempt_time = 0
    
    # Проверяем, был ли пользователь заблокирован из-за неудачных попыток входа
    current_time = time.time()
    if st.session_state.login_attempts >= 5:
        # Блокировка на 5 минут после 5 неудачных попыток
        if current_time - st.session_state.last_attempt_time < 300:
            remaining_time = int(300 - (current_time - st.session_state.last_attempt_time))
            if location == "sidebar":
                st.sidebar.error(f"Слишком много неудачных попыток. Попробуйте снова через {remaining_time} секунд.")
            else:
                st.error(f"Слишком много неудачных попыток. Попробуйте снова через {remaining_time} секунд.")
            return False
        else:
            # Сбрасываем счетчик попыток после истечения времени блокировки
            st.session_state.login_attempts = 0
    
    # Если пользователь уже авторизован, показываем кнопку выхода
    if st.session_state.admin_authenticated:
        if location == "sidebar":
            if st.sidebar.button("Выйти из режима администратора"):
                st.session_state.admin_authenticated = False
                st.rerun()
        else:
            if st.button("Выйти из режима администратора"):
                st.session_state.admin_authenticated = False
                st.rerun()
        return True
    
    # Отображаем форму входа
    if location == "sidebar":
        with st.sidebar.expander("Вход для администратора", expanded=False):
            password = st.text_input("Пароль", type="password", key="admin_password_sidebar")
            login_button = st.button("Войти", key="login_button_sidebar")
            
            if st.session_state.auth_error:
                st.error("Неверный пароль. Попробуйте снова.")
                
            if login_button:
                st.session_state.last_attempt_time = current_time
                if verify_password(password):
                    st.session_state.admin_authenticated = True
                    st.session_state.auth_error = False
                    st.session_state.login_attempts = 0
                    st.rerun()
                else:
                    st.session_state.auth_error = True
                    st.session_state.login_attempts += 1
                    st.error("Неверный пароль. Попробуйте снова.")
    else:
        password = st.text_input("Пароль администратора", type="password", key="admin_password_main")
        login_button = st.button("Войти", key="login_button_main")
        
        if st.session_state.auth_error:
            st.error("Неверный пароль. Попробуйте снова.")
            
        if login_button:
            st.session_state.last_attempt_time = current_time
            if verify_password(password):
                st.session_state.admin_authenticated = True
                st.session_state.auth_error = False
                st.session_state.login_attempts = 0
                st.rerun()
            else:
                st.session_state.auth_error = True
                st.session_state.login_attempts += 1
                st.error("Неверный пароль. Попробуйте снова.")
    
    return st.session_state.admin_authenticated


def admin_required(func):
    """
    Декоратор для функций, требующих аутентификации администратора
    
    Args:
        func: Функция, которую нужно защитить
        
    Returns:
        function: Обертка, которая проверяет аутентификацию перед выполнением функции
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if check_admin_auth():
            return func(*args, **kwargs)
        else:
            st.error("Для доступа к этой функции требуются права администратора")
            admin_login_form("main")
            return None
    return wrapper


def create_admin_panel(title="Панель администратора", location="sidebar", expanded=False):
    """
    Создает сворачивающуюся панель администратора
    
    Args:
        title (str): Заголовок панели
        location (str): Местоположение панели - 'sidebar' или 'main'
        expanded (bool): Развернута ли панель по умолчанию
        
    Returns:
        tuple: (is_authenticated, expander) - статус аутентификации и объект expander
    """
    is_authenticated = check_admin_auth()
    
    if location == "sidebar":
        if not is_authenticated:
            admin_login_form("sidebar")
            expander = st.sidebar.expander(title, expanded=False)
        else:
            expander = st.sidebar.expander(title, expanded=expanded)
    else:
        if not is_authenticated:
            admin_login_form("main")
            expander = st.expander(title, expanded=False)
        else:
            expander = st.expander(title, expanded=expanded)
    
    return is_authenticated, expander