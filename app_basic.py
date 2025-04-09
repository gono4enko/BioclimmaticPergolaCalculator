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
    text-align: left !important;
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

/* Для выравнивания цен по правому краю */
table td:nth-child(2) {
    text-align: right !important;
}

/* Стилизация кнопки расчета */
.stButton>button {
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
.stRadio > div[role="radiogroup"] label {
    background-color: white !important;
}

/* Заголовки результатов расчета */
h2 {
    color: #3f6daa !important;
    font-size: 1.75rem !important;
    font-weight: bold !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1rem !important;
}

h3 {
    color: #3f6daa !important;
    font-size: 1.4rem !important;
    font-weight: bold !important;
    margin-top: 1.2rem !important;
    margin-bottom: 0.7rem !important;
}

h4 {
    color: #333333 !important;
    font-size: 1.1rem !important;
    font-weight: bold !important;
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important;
}

/* Убираем лишние отступы */
div.block-container {
    padding-top: 2rem;
    max-width: 1000px;
    padding-bottom: 2rem;
}

/* Убираем отступы в радио-кнопках */
.stRadio > div {
    margin-bottom: 0.3rem !important;
}

/* Стили для примечаний */
.caption {
    font-size: 0.8rem !important;
    color: #666666 !important;
    margin-top: 0.3rem !important;
}
</style>
""", unsafe_allow_html=True)

# Функция для выполнения расчета
def perform_calculation(dimensions, options):
    """Выполнить расчет стоимости перголы"""
    width_m = dimensions["width"]
    length_m = dimensions["length"]
    height_m = dimensions["height"]
    pergola_type = options["pergola_type"]
    lamella_type = options["lamella_type"]
    lighting_type = options["lighting_type"]
    installation = options.get("installation", "no_install")
    
    # Преобразуем размеры в мм для некоторых расчетов
    width_mm = width_m * 1000
    length_mm = length_m * 1000
    
    # Рассчитываем количество модулей в зависимости от ширины
    # Максимальная ширина модуля около 3.375 метра
    if width_m <= 3.375:
        modules = 1
    elif width_m <= 6.75:
        modules = 2
    elif width_m <= 10.125:
        modules = 3
    else:
        modules = 4
    
    # Базовая цена в зависимости от типа перголы и размера
    # Упрощенная формула для демонстрации
    base_prices = {
        "B500NEW": 7500,
        "B700NEW": 8500,
        "B600": 6500
    }
    base_price = base_prices.get(pergola_type, 7000)
    
    # Коэффициент размера (упрощенно)
    size_factor = width_m * length_m / 10
    
    # Рассчитываем базовую стоимость перголы
    pergola_cost = base_price * size_factor
    
    # Учитываем тип ламелей
    if "25" in lamella_type:
        pergola_cost *= 1.15  # Надбавка 15% для ламелей 250 мм
    
    # Учитываем тип подсветки
    lighting_cost = 0
    lighting_components = []
    
    if lighting_type == "white":
        perimeter = 2 * (width_m + length_m)  # Периметр перголы
        lighting_cost = 20 * perimeter + 300 * modules  # 20€/м ленты + 300€ за блок управления на модуль
        lighting_components = [
            f"LED лента белая - {perimeter:.2f} м",
            f"Блок управления Somfy RTS Dimmer - {modules} шт."
        ]
    elif lighting_type == "rgb":
        perimeter = 2 * (width_m + length_m)
        lighting_cost = 30 * perimeter + 300 * modules  # 30€/м RGB ленты + 300€ за блок управления на модуль
        lighting_components = [
            f"RGB лента - {perimeter:.2f} м",
            f"Блок управления Somfy RTS Dimmer - {modules} шт."
        ]
    elif lighting_type == "rgbw":
        perimeter = 2 * (width_m + length_m)
        lighting_cost = 40 * perimeter + 300 * modules  # 40€/м RGBW ленты + 300€ за блок управления на модуль
        lighting_components = [
            f"RGBW лента - {perimeter:.2f} м",
            f"Блок управления Somfy RTS Dimmer - {modules} шт."
        ]
    
    # Определяем тип автоматизации и стоимость в зависимости от типа перголы и размеров
    automation_components = []
    if pergola_type == "B500NEW":
        # Для B500NEW используем привод Bansbach
        if width_m > 3.5 and length_m > 5.5:
            automation_type = "Bansbach Tandem"
            automation_cost = 1250  # Усиленный привод Bansbach Tandem
            automation_components = [
                "Привод Bansbach easyE-lift-50 Tandem - 1 шт.",
                "Блок управления Bansbach - 1 шт.",
                "Приемник - 1 шт.",
                "Пульт ДУ Simu 1K - 1 шт."
            ]
        else:
            automation_type = "Bansbach T1"
            automation_cost = 700  # Стандартный привод Bansbach T1
            automation_components = [
                "Привод Bansbach easyE-lift-50 - 1 шт.",
                "Блок управления Bansbach - 1 шт.",
                "Приемник - 1 шт.",
                "Пульт ДУ Simu 1K - 1 шт."
            ]
    elif pergola_type == "B700NEW":
        # Для B700NEW используем привод Somfy
        if width_m > 3.5 and length_m > 6.0:
            automation_type = "Somfy M2 TANDEM"
            automation_cost = 1000  # Усиленный привод Somfy M2 TANDEM
            automation_components = [
                "Привод Somfy M2 TANDEM - 1 шт.",
                "Блок управления для двух двигателей - 1 шт.",
                "Приемник - 1 шт.",
                "Пульт ДУ Simu 1K - 1 шт."
            ]
        else:
            automation_type = "Somfy M1"
            automation_cost = 300  # Стандартный привод Somfy M1
            automation_components = [
                "Привод Somfy M1 - 1 шт.",
                "Блок управления - 1 шт.",
                "Приемник - 1 шт.",
                "Пульт ДУ Simu 1K - 1 шт."
            ]
    else:
        # Для B600 и других типов
        automation_type = "Стандартный привод"
        automation_cost = 500
        automation_components = [
            "Стандартный привод - 1 шт.",
            "Блок управления - 1 шт.",
            "Пульт ДУ Simu 1K - 1 шт."
        ]
    
    # Добавляем стоимость пульта ДУ (25 евро за Simu 1K)
    automation_cost += 25
    
    # Учитываем установку
    installation_cost = 0
    if installation == "with_install":
        installation_cost = pergola_cost * 0.15  # 15% от стоимости перголы
    
    # Итоговая стоимость
    total_cost = pergola_cost + lighting_cost + automation_cost + installation_cost
    
    # Формируем результат
    results = {
        "total_cost": round(total_cost, 0),
        "details": {
            "pergola_cost": round(pergola_cost, 0),
            "pergola_type": pergola_type,
            "lighting_cost": round(lighting_cost, 0),
            "lighting_components": lighting_components,
            "automation_cost": round(automation_cost, 0),
            "automation_type": automation_type,
            "automation_components": automation_components,
            "installation_cost": round(installation_cost, 0),
            "modules": modules
        },
        "dimensions": {
            "width_m": width_m,
            "length_m": length_m,
            "height_m": height_m
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
        
        # Сохраняем размеры (высота фиксированная - 3.0 м)
        dimensions = {
            "width": width,
            "length": length,
            "height": 3.0
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
        st.markdown("## Результаты расчета")
        
        # Отображаем спецификацию перголы
        st.markdown("### Спецификация перголы")
        
        # Основные характеристики перголы
        basic_specs = [
            ["Тип перголы", PERGOLA_TYPES.get(options["pergola_type"], options["pergola_type"])],
            ["Тип ламелей", LAMELLA_TYPES.get(options["lamella_type"], options["lamella_type"])],
            ["Ширина", f"{results['dimensions']['width_m']} м"],
            ["Вынос", f"{results['dimensions']['length_m']} м"],
            ["Высота", f"{results['dimensions']['height_m']} м"],
            ["Количество модулей", f"{results['details']['modules']}"]
        ]
        
        # Добавляем информацию об автоматизации
        basic_specs.append(["Автоматизация", results["details"]["automation_type"]])
        
        # Создаем DataFrame для базовой спецификации
        spec_df = pd.DataFrame(basic_specs, columns=["Параметр", "Значение"])
        st.table(spec_df)
        
        # Если есть подсветка, выводим ее компоненты
        if options["lighting_type"] != "none" and results['details']['lighting_components']:
            st.markdown("#### Компоненты подсветки")
            lighting_components = [[comp] for comp in results['details']['lighting_components']]
            lighting_df = pd.DataFrame(lighting_components, columns=["Наименование"])
            st.table(lighting_df)
        
        # Выводим компоненты автоматизации
        st.markdown("#### Компоненты автоматизации")
        automation_components = [[comp] for comp in results['details']['automation_components']]
        automation_df = pd.DataFrame(automation_components, columns=["Наименование"])
        st.table(automation_df)
        
        # Отображаем стоимость
        st.markdown("### Стоимость")
        
        # Информация о стоимости
        cost_items = []
        cost_items.append(["Базовая стоимость перголы", f"{results['details']['pergola_cost']:.0f}"])
        
        # Добавляем информацию о стоимости автоматизации
        if results['details']['automation_cost'] > 0:
            cost_items.append(["Система автоматизации", f"{results['details']['automation_cost']:.0f}"])
        
        # Добавляем информацию о стоимости освещения
        if results['details']['lighting_cost'] > 0:
            cost_items.append(["Светодиодная подсветка", f"{results['details']['lighting_cost']:.0f}"])
        
        # Добавляем информацию о стоимости установки
        if results['details']['installation_cost'] > 0:
            cost_items.append(["Установка", f"{results['details']['installation_cost']:.0f}"])
        
        # Итоговая стоимость
        cost_items.append(["**Итоговая стоимость**", f"**{results['total_cost']:.0f}**"])
        
        # Создаем DataFrame для стоимости
        cost_df = pd.DataFrame(cost_items, columns=["Компонент", "Стоимость, €"])
        st.table(cost_df)
        
        # Добавляем примечание о том, что все цены указаны в евро
        st.caption("Все цены указаны в евро. Цены на перголы зависят от выбранных размеров и опций.")

if __name__ == "__main__":
    main()