"""
Модуль для отображения формы выбора опций перголы.
"""
import streamlit as st

def render_options_form():
    """
    Отображает форму для выбора опций перголы в плиточном дизайне
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="color: #0066cc; font-size: 2.0rem; font-weight: 600; margin-bottom: 1rem;">Опции перголы</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Тип перголы
    st.subheader("Тип перголы")
    pergola_type = st.radio(
        "Выберите тип перголы:",
        ["B500NEW", "B700NEW", "B600"],
        index=0,
        horizontal=True,
        help="B500NEW - с вращением ламелей, B700NEW - со сдвижением ламелей, B600 - с сэндвич-панелями"
    )
    
    # Размер ламели
    st.subheader("Размер ламели")
    # Для B600 доступны только ламели PIR
    if pergola_type == "B600":
        lamella_size = "PIR"
        st.info("Для перголы B600 доступны только сэндвич-панели PIR.")
    else:
        lamella_size = st.radio(
            "Выберите размер ламели:",
            ["200", "250"],
            index=1,
            horizontal=True,
            help="Размер ламели в миллиметрах"
        )
    
    # Освещение
    st.subheader("Подсветка")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        led_lighting = st.checkbox("LED подсветка", value=False)
    
    with col2:
        rgb_lighting = st.checkbox("RGB подсветка", value=False)
    
    with col3:
        led_rgb_lighting = st.checkbox("LED + RGB", value=False)
    
    # Дополнительные опции
    st.subheader("Дополнительные опции")
    col1, col2 = st.columns(2)
    
    with col1:
        delivery = st.checkbox("Доставка", value=True)
    
    with col2:
        installation = st.checkbox("Монтаж", value=False)
    
    # Определяем тип освещения на основе выбранных опций
    lighting_type = "none"
    if led_lighting:
        lighting_type = "led"
    elif rgb_lighting:
        lighting_type = "rgb"
    elif led_rgb_lighting:
        lighting_type = "led_rgb"
    
    # Возвращаем выбранные опции как словарь
    return {
        "pergola_type": pergola_type,
        "lamella_size": lamella_size,
        "lighting_type": lighting_type,
        "led_lighting": led_lighting,
        "rgb_lighting": rgb_lighting,
        "led_rgb_lighting": led_rgb_lighting,
        "delivery": delivery,
        "installation": installation
    }