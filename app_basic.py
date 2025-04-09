"""
Калькулятор стоимости пергол - базовая версия без сложных стилей и модификаций
Максимально простой подход с использованием стандартных компонентов Streamlit
"""
import streamlit as st
import pandas as pd
# Используем прямое определение структур данных для упрощения
# Типы пергол
PERGOLA_TYPES = {
    "B500NEW": "В500 - с поворотными ламелями",
    "B700NEW": "В700 - с поворотно-сдвижными ламелями",
    "B600": "В600 PIR - со стационарными панелями"
}

# Описания типов пергол
PERGOLA_TYPE_DESCRIPTIONS = {
    "B500NEW": "Современная пергола с поворотными алюминиевыми ламелями.",
    "B700NEW": "Премиальная пергола с поворотно-сдвижными ламелями.",
    "B600": "Пергола со стационарной крышей из PIR сэндвич-панелей."
}

# Типы ламелей
LAMELLA_TYPES = {
    "B500-20NEW": "Ламели 200 мм (усиленные)",
    "B500-25NEW": "Ламели 250 мм (стандарт)",
    "B700-20NEW": "Ламели 200 мм (усиленные)",
    "B700-25NEW": "Ламели 250 мм (стандарт)",
    "B600": "PIR-панель"
}

# Устанавливаем заголовок страницы
st.set_page_config(
    page_title="Калькулятор пергол", 
    page_icon="🏠",
    initial_sidebar_state="collapsed"
)

# Базовые стили
st.markdown("""
<style>
/* Устанавливаем белый фон для всей страницы */
.stApp {
    background-color: white;
}

/* Стилизация таблиц */
table {
    width: 100%;
    font-size: 0.9rem;
}

table th {
    text-align: left;
    padding: 8px 10px;
    background-color: #f1f1f1;
    color: #000000;
    font-weight: 500;
}

table td {
    padding: 8px 10px;
    border-bottom: 1px solid #eee;
    color: #000000;
}

/* Стилизация кнопки расчета */
.calculate-btn {
    background-color: #ff7a2f !important;
    color: white !important;
    font-weight: bold !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    font-size: 1.2rem !important;
    border-radius: 0.5rem !important;
    cursor: pointer !important;
    width: 100% !important;
    margin-top: 1rem !important;
    margin-bottom: 1rem !important;
}

/* Скрытие голубой заливки */
.stRadio > div[role="radiogroup"] div[data-checked="true"] {
    background-color: #FFFFFF !important;
}

/* Убираем лишние отступы */
div.block-container {
    padding-top: 2rem;
    max-width: 1000px;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Функция для выполнения расчета
def perform_calculation(dimensions, options):
    """Выполнить расчет стоимости перголы"""
    # Заглушка для базовой версии - используем фиксированную цену 
    # для демонстрации работы приложения
    width_m = dimensions["width"]
    length_m = dimensions["length"]
    pergola_type = options["pergola_type"]
    
    # Базовая цена в зависимости от типа перголы
    base_prices = {
        "B500NEW": 7500,
        "B700NEW": 8500,
        "B600": 6500
    }
    base_price = base_prices.get(pergola_type, 7000)
    
    # Коэффициент размера
    size_factor = width_m * length_m / 10
    
    # Рассчитываем базовую стоимость перголы
    pergola_cost = base_price * size_factor
    
    # Учитываем тип ламелей
    lamella_type = options["lamella_type"]
    if "25" in lamella_type:
        pergola_cost *= 1.15  # Надбавка 15% для ламелей 250 мм
    
    # Учитываем тип подсветки
    lighting_type = options["lighting_type"]
    lighting_cost = 0
    if lighting_type == "white":
        lighting_cost = 500 * (width_m + length_m) * 2  # Периметр перголы
    elif lighting_type == "rgb":
        lighting_cost = 750 * (width_m + length_m) * 2
    elif lighting_type == "rgbw":
        lighting_cost = 1000 * (width_m + length_m) * 2
    
    # Учитываем установку
    installation_cost = 0
    if options.get("installation") == "with_install":
        installation_cost = pergola_cost * 0.15  # 15% от стоимости перголы
    
    # Автоматизация определяется типом перголы и размерами
    automation_type = "Стандартный привод"
    automation_cost = pergola_cost * 0.1  # 10% от стоимости перголы
    
    # Итоговая стоимость
    total_cost = pergola_cost + lighting_cost + installation_cost + automation_cost
    
    # Формируем результат
    results = {
        "total_cost": round(total_cost, 0),
        "details": {
            "pergola_cost": round(pergola_cost, 0),
            "lighting_cost": round(lighting_cost, 0),
            "automation_cost": round(automation_cost, 0),
            "installation_cost": round(installation_cost, 0),
            "automation_type": automation_type
        },
        "dimensions": {
            "width_m": width_m,
            "length_m": length_m,
            "height_m": dimensions["height"]
        }
    }
    
    return results

def main():
    """Основная функция приложения"""
    
    # Заголовок и описание
    st.title("Калькулятор пергол")
    st.markdown("Рассчитайте стоимость перголы с учетом размеров и опций")
    
    # Используем колонки для компактного отображения
    col1, col2 = st.columns(2)
    
    with col1:
        # Форма для ввода размеров перголы
        st.subheader("Размеры перголы")
        width = st.number_input("Ширина (м)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
        length = st.number_input("Вынос (м)", min_value=1.0, max_value=10.0, value=4.0, step=0.5)
        height = st.number_input("Высота (м)", min_value=2.0, max_value=5.0, value=3.0, step=0.1)
        
        # Сохраняем размеры
        dimensions = {
            "width": width,
            "length": length,
            "height": height
        }
        
        # Выбор типа перголы
        st.subheader("Тип перголы")
        pergola_type = st.radio(
            "Выберите тип перголы",
            options=list(PERGOLA_TYPES.keys()),
            format_func=lambda x: PERGOLA_TYPES.get(x, x),
            key="pergola_type"
        )
        
        # Показываем описание выбранного типа перголы
        if pergola_type in PERGOLA_TYPE_DESCRIPTIONS:
            st.caption(PERGOLA_TYPE_DESCRIPTIONS[pergola_type])
        
    with col2:
        # Выбор типа ламелей (зависит от типа перголы)
        st.subheader("Тип ламелей")
        # Получаем доступные типы ламелей для выбранной перголы
        available_lamella_types = [k for k in LAMELLA_TYPES.keys() if k.startswith(pergola_type[:-3])]
        
        # Если нет доступных типов ламелей, используем значение по умолчанию
        if not available_lamella_types:
            available_lamella_types = ["Standard"]
        
        lamella_type = st.radio(
            "Выберите тип ламелей",
            options=available_lamella_types,
            format_func=lambda x: LAMELLA_TYPES.get(x, x),
            key="lamella_type"
        )
        
        # Определяем шаг ламелей (извлекаем из названия типа)
        lamella_step = 200
        if "25" in lamella_type:
            lamella_step = 250
        
        # Выбор типа подсветки
        st.subheader("Подсветка (LED по периметру)")
        lighting_options = ["none", "white", "rgb", "rgbw"]
        lighting_labels = {
            "none": "Без подсветки",
            "white": "Белая (5000K)",
            "rgb": "RGB",
            "rgbw": "RGBW"
        }
        lighting_descriptions = {
            "none": "Без подсветки (светодиодная лента не устанавливается)",
            "white": "Белая подсветка по периметру перголы (5000K)",
            "rgb": "RGB подсветка с изменением цвета и яркости",
            "rgbw": "RGBW подсветка с полным управлением цветовой температурой"
        }
        
        lighting_type = st.radio(
            "Выберите тип подсветки",
            options=lighting_options,
            format_func=lambda x: f"{lighting_labels.get(x, x)} - {lighting_descriptions.get(x, '')}",
            key="lighting_type"
        )
        
        # Выбор установки
        st.subheader("Установка")
        install_options = ["no_install", "with_install"]
        install_labels = {
            "no_install": "Без установки",
            "with_install": "С установкой"
        }
        install_descriptions = {
            "no_install": "Только оборудование, без монтажа",
            "with_install": "Полный комплекс: оборудование + монтаж"
        }
        
        installation = st.radio(
            "Выберите вариант установки",
            options=install_options,
            format_func=lambda x: f"{install_labels.get(x, x)} - {install_descriptions.get(x, '')}",
            key="installation"
        )
    
    # Собираем все опции
    options = {
        "pergola_type": pergola_type,
        "lamella_type": lamella_type,
        "lamella_step": lamella_step,
        "lighting_type": lighting_type,
        "installation": installation
    }
    
    # Кнопка расчета
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    calc_button = st.button("Рассчитать стоимость", type="primary")
    
    # Если кнопка нажата, выполняем расчет
    if calc_button:
        with st.spinner("Выполняется расчет..."):
            # Проверяем, что у нас есть данные для расчета
            if dimensions and options:
                # Выполняем расчет
                results = perform_calculation(dimensions, options)
                
                # Сохраняем результаты в состоянии сессии
                st.session_state.results = results
    
    # Отображаем результаты расчета, если они есть
    if "results" in st.session_state:
        results = st.session_state.results
        
        st.markdown("---")
        st.subheader("Результаты расчета")
        
        # Отображаем спецификацию перголы
        st.markdown("### Спецификация перголы")
        
        # Создаем DataFrame для спецификации
        spec_data = {
            "Параметр": [
                "Тип перголы", 
                "Тип ламелей", 
                "Ширина", 
                "Вынос",
                "Высота",
                "Тип подсветки",
                "Автоматизация"
            ],
            "Значение": [
                PERGOLA_TYPES.get(options["pergola_type"], options["pergola_type"]),
                LAMELLA_TYPES.get(options["lamella_type"], options["lamella_type"]),
                f"{results['dimensions']['width_m']} м",
                f"{results['dimensions']['length_m']} м",
                f"{results['dimensions']['height_m']} м",
                lighting_labels.get(options["lighting_type"], options["lighting_type"]),
                results["details"]["automation_type"]
            ]
        }
        spec_df = pd.DataFrame(spec_data)
        st.table(spec_df)
        
        # Отображаем стоимость
        st.markdown("### Стоимость")
        
        # Создаем DataFrame для стоимости
        cost_data = {
            "Компонент": [
                "Базовая стоимость перголы",
                "Система автоматизации",
                "Светодиодная подсветка",
                "Установка",
                "**Итоговая стоимость**"
            ],
            "Сумма, €": [
                f"{results['details']['pergola_cost']:.0f}",
                f"{results['details']['automation_cost']:.0f}",
                f"{results['details']['lighting_cost']:.0f}",
                f"{results['details']['installation_cost']:.0f}",
                f"**{results['total_cost']:.0f}**"
            ]
        }
        cost_df = pd.DataFrame(cost_data)
        st.table(cost_df)

if __name__ == "__main__":
    main()