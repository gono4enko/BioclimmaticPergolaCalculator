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
    "B600-PIR": "PIR сэндвич-панель",
    "lamella-200": "Ламели 200 мм (усиленные)",
    "lamella-250": "Ламели 250 мм (стандарт)"
}

# Максимально допустимые размеры для каждого типа пергол
MAX_DIMENSIONS = {
    "B500NEW": {"width": 15.0, "length": 8.0},
    "B700NEW": {"width": 15.0, "length": 7.25},
    "B600": {"width": 13.5, "length": 8.0}
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

/* Для выравнивания только цен в таблице стоимости по правому краю */
.cost-table td:nth-child(2) {
    text-align: right !important;
}

/* Для выравнивания всех остальных таблиц по левому краю */
table td {
    text-align: left !important;
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
    
    # Рассчитываем количество модулей в зависимости от ширины и типа перголы
    # Согласно прайсам B500-20, B500-25, B700-25
    if pergola_type == "B500NEW" or pergola_type == "B700NEW":
        if width_m <= 4.5:
            modules = 1
        elif width_m <= 9.0:  # В прайсах до 9.0 идет 2 модуля
            modules = 2
        elif width_m <= 13.5:  # В прайсах до 13.5 идет 3 модуля
            modules = 3
        else:
            modules = 4
    else:
        # Для B600 используем данные из прайса B600 PIR
        if width_m <= 4.5:
            modules = 1
        elif width_m <= 9.0:  # В прайсе до 9.0 идет 2 модуля
            modules = 2
        else:
            modules = 3
    
    # Определяем тип ламелей по коду
    # Для B500NEW и B700NEW преобразуем упрощенные коды в коды из прайса
    real_lamella_type = lamella_type
    if pergola_type == "B500NEW":
        if lamella_type == "lamella-200":
            real_lamella_type = "B500-20NEW"
        elif lamella_type == "lamella-250":
            real_lamella_type = "B500-25NEW"
    elif pergola_type == "B700NEW":
        if lamella_type == "lamella-200":
            real_lamella_type = "B700-20NEW"
        elif lamella_type == "lamella-250":
            real_lamella_type = "B700-25NEW"
    
    # Получаем базовую цену из прайса в зависимости от типа перголы, ширины и длины
    # Это более точный метод, чем просто использовать коэффициент
    # Данные цен получены из прайс-листов (упрощенная реализация)
    pergola_cost = 0
    
    # Получаем цену из соответствующего прайса
    if pergola_type == "B500NEW":
        if "20" in real_lamella_type:
            # Для B500-20NEW
            # Ищем ближайшие значения из прайса (B500-20)
            # Ширина (м): 3.0, 3.5, 4.0, 4.5, 6.0, 7.0, 8.0, 9.0, 10.0, 9.0, 10.5, 12.0, 13.5, 15.0
            # Вынос (м): 2.45, 2.85, 3.25, 3.65, 4.05, 4.45, 4.85, 5.25, 5.65, 6.05, 6.45, 6.85, 7.25, 7.65, 8.05
            
            # Базовые цены из прайса
            if width_m <= 3.0 and length_m <= 2.45:
                pergola_cost = 6245
            elif width_m <= 3.5 and length_m <= 2.45:
                pergola_cost = 6810
            elif width_m <= 4.0 and length_m <= 2.45:
                pergola_cost = 7375
            elif width_m <= 4.5 and length_m <= 2.45:
                pergola_cost = 7940
            elif width_m <= 3.0 and length_m <= 2.85:
                pergola_cost = 6866
            elif width_m <= 3.0 and length_m <= 3.25:
                pergola_cost = 7487
            elif width_m <= 3.0 and length_m <= 3.65:
                pergola_cost = 8108
            elif width_m <= 3.0 and length_m <= 4.05:
                pergola_cost = 8729
            else:
                # Для других размеров по-прежнему используем приближенную формулу
                pergola_cost = 6245 * (width_m * length_m) / (3.0 * 2.45)
        else:
            # Для B500-25NEW
            # Ищем ближайшие значения из прайса (B500-25)
            # Ширина (м): 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 7.5, 9.0, 10.5, 12.0, 13.5
            # Вынос (м): 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0
            
            # Базовые цены из прайса B500-25
            if width_m <= 2.5 and length_m <= 2.5:
                pergola_cost = 5431
            elif width_m <= 3.0 and length_m <= 2.5:
                pergola_cost = 5945
            elif width_m <= 3.5 and length_m <= 2.5:
                pergola_cost = 6460
            elif width_m <= 4.0 and length_m <= 2.5:
                pergola_cost = 6974
            elif width_m <= 4.5 and length_m <= 2.5:
                pergola_cost = 7488
            elif width_m <= 3.0 and length_m <= 3.0:
                pergola_cost = 6638
            elif width_m <= 3.0 and length_m <= 3.5:
                pergola_cost = 7330
            elif width_m <= 3.0 and length_m <= 4.0:
                pergola_cost = 8022
            elif width_m <= 3.0 and length_m <= 4.5:
                pergola_cost = 8714
            elif width_m <= 3.0 and length_m <= 5.0:
                pergola_cost = 9406
            else:
                # Для других размеров используем приближенную формулу
                pergola_cost = 5431 * (width_m * length_m) / (2.5 * 2.5)
    
    elif pergola_type == "B700NEW":
        if "20" in real_lamella_type:
            # Для B700-20NEW
            # Ищем ближайшие значения из прайса (B700-20)
            # Ширина (м): 3.0, 3.5, 4.0, 4.5, 6.0, 7.0, 8.0, 9.0, 10.0, 9.0, 10.5, 12.0, 13.5, 15.0
            # Вынос (м): 2.45, 2.85, 3.25, 3.65, 4.05, 4.45, 4.85, 5.25, 5.65, 6.05, 6.45, 6.85, 7.25
            
            # Базовые цены из прайса B700-20
            if width_m <= 3.0 and length_m <= 2.45:
                pergola_cost = 6878
            elif width_m <= 3.5 and length_m <= 2.45:
                pergola_cost = 7451
            elif width_m <= 4.0 and length_m <= 2.45:
                pergola_cost = 8023
            elif width_m <= 4.5 and length_m <= 2.45:
                pergola_cost = 8596
            elif width_m <= 3.0 and length_m <= 2.85:
                pergola_cost = 7529
            elif width_m <= 3.0 and length_m <= 3.25:
                pergola_cost = 8179
            elif width_m <= 3.0 and length_m <= 3.65:
                pergola_cost = 8830
            elif width_m <= 3.0 and length_m <= 4.05:
                pergola_cost = 9480
            elif width_m <= 3.0 and length_m <= 4.45:
                pergola_cost = 10130
            elif width_m <= 3.0 and length_m <= 4.85:
                pergola_cost = 10781
            else:
                # Для других размеров используем приближенную формулу
                pergola_cost = 6878 * (width_m * length_m) / (3.0 * 2.45)
        else:
            # Для B700-25NEW
            # Ищем ближайшие значения из прайса (B700-25)
            # Ширина (м): 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 7.5, 9.0, 10.5, 12.0, 13.5
            # Вынос (м): 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0
            
            # Базовые цены из прайса B700-25
            if width_m <= 2.5 and length_m <= 2.5:
                pergola_cost = 6048
            elif width_m <= 3.0 and length_m <= 2.5:
                pergola_cost = 6570
            elif width_m <= 3.5 and length_m <= 2.5:
                pergola_cost = 7092
            elif width_m <= 4.0 and length_m <= 2.5:
                pergola_cost = 7613
            elif width_m <= 4.5 and length_m <= 2.5:
                pergola_cost = 8135
            elif width_m <= 3.0 and length_m <= 3.0:
                pergola_cost = 7297
            elif width_m <= 3.0 and length_m <= 3.5:
                pergola_cost = 8023
            elif width_m <= 3.0 and length_m <= 4.0:
                pergola_cost = 8750
            elif width_m <= 3.0 and length_m <= 4.5:
                pergola_cost = 9476
            elif width_m <= 3.0 and length_m <= 5.0:
                pergola_cost = 10203
            else:
                # Для других размеров используем приближенную формулу
                pergola_cost = 6048 * (width_m * length_m) / (2.5 * 2.5)
    
    elif pergola_type == "B600":
        # Для B600 (PIR панели)
        # Используем данные из прайса В600_PIR
        # Ширина (м): 2.5, 3.0, 3.5, 4.0, 4.5, 6.0, 7.0, 8.0, 9.0, 10.5, 12.0, 13.5
        # Вынос (м): 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0
        
        # Базовые цены из прайса B600 PIR
        if width_m <= 2.5 and length_m <= 2.5:
            pergola_cost = 4500
        elif width_m <= 3.0 and length_m <= 2.5:
            pergola_cost = 4866
        elif width_m <= 3.5 and length_m <= 2.5:
            pergola_cost = 5232
        elif width_m <= 4.0 and length_m <= 2.5:
            pergola_cost = 5599
        elif width_m <= 4.5 and length_m <= 2.5:
            pergola_cost = 5965
        elif width_m <= 2.5 and length_m <= 3.0:
            pergola_cost = 4678
        elif width_m <= 3.0 and length_m <= 3.0:
            pergola_cost = 5045
        elif width_m <= 3.5 and length_m <= 3.0:
            pergola_cost = 5411
        elif width_m <= 4.0 and length_m <= 3.0:
            pergola_cost = 5777
        elif width_m <= 4.5 and length_m <= 3.0:
            pergola_cost = 6144
        elif width_m <= 2.5 and length_m <= 3.5:
            pergola_cost = 5230
        elif width_m <= 3.0 and length_m <= 3.5:
            pergola_cost = 5659
        elif width_m <= 3.5 and length_m <= 3.5:
            pergola_cost = 6087
        else:
            # Для других размеров используем приближенную формулу
            pergola_cost = 4500 * (width_m * length_m) / (2.5 * 2.5)
    
    # Учитываем тип подсветки
    lighting_cost = 0
    lighting_components = []
    
    if lighting_type == "white":
        # Расчет периметра подсветки согласно инструкции
        if modules == 1:
            # Для одного модуля - просто периметр
            perimeter = 2 * (width_m + length_m)
        else:
            # Для нескольких модулей считаем периметр для каждого модуля
            module_width = width_m / modules
            perimeter = modules * 2 * (module_width + length_m)
            
        led_price_per_meter = 20  # Цена за метр сверхъяркой LED ленты согласно инструкции
        controller_price = 300  # Блок управления Somfy RTS Dimmer согласно инструкции
        
        lighting_cost = led_price_per_meter * perimeter + controller_price
        
        # Добавляем только один блок управления LED на всю перголу
        lighting_components = [
            f"Сверхъяркая LED лента белая - {perimeter:.2f} м",
            "Блок управления освещением Somfy RTS Dimmer - 1 шт."
        ]
    elif lighting_type == "rgb":
        # Расчет периметра подсветки согласно инструкции
        if modules == 1:
            # Для одного модуля - просто периметр
            perimeter = 2 * (width_m + length_m)
        else:
            # Для нескольких модулей считаем периметр для каждого модуля
            module_width = width_m / modules
            perimeter = modules * 2 * (module_width + length_m)
            
        led_price_per_meter = 20  # Цена за метр сверхъяркой RGB ленты согласно инструкции
        controller_price = 300  # Блок управления Somfy RTS Dimmer согласно инструкции
        
        lighting_cost = led_price_per_meter * perimeter + controller_price
        
        # Добавляем только один блок управления LED на всю перголу
        lighting_components = [
            f"Сверхъяркая RGB лента - {perimeter:.2f} м",
            "Блок управления освещением Somfy RTS Dimmer - 1 шт."
        ]
    elif lighting_type == "rgbw":
        # Расчет периметра подсветки согласно инструкции
        if modules == 1:
            # Для одного модуля - просто периметр
            perimeter = 2 * (width_m + length_m)
        else:
            # Для нескольких модулей считаем периметр для каждого модуля
            module_width = width_m / modules
            perimeter = modules * 2 * (module_width + length_m)
            
        # Для RGBW используем обе ленты - и LED, и RGB согласно инструкции
        led_price_per_meter = 20 + 20  # Сумма цен за метр LED и RGB ленты
        controller_price = 300  # Блок управления Somfy RTS Dimmer согласно инструкции
        
        lighting_cost = led_price_per_meter * perimeter + controller_price
        
        # Добавляем обе ленты и один блок управления
        lighting_components = [
            f"Сверхъяркая LED лента белая - {perimeter:.2f} м",
            f"Сверхъяркая RGB лента - {perimeter:.2f} м",
            "Блок управления освещением Somfy RTS Dimmer - 1 шт."
        ]
    
    # Проверяем нужны ли дополнительные колонны
    additional_columns = False
    additional_columns_cost = 0
    additional_columns_components = []
    
    # По правилам из инструкции
    if pergola_type == "B500NEW":
        if "250" in real_lamella_type and length_m > 6.5:
            additional_columns = True
        elif "200" in real_lamella_type and length_m > 6.85:
            additional_columns = True
    elif pergola_type == "B700NEW":
        if "250" in real_lamella_type and length_m > 6.5:
            additional_columns = True
        elif "200" in real_lamella_type and length_m > 6.85:
            additional_columns = True
    elif pergola_type == "B600" and length_m > 6.5:
        additional_columns = True
        
    # Отладочная информация для проверки
    st.sidebar.write(f"Тип перголы: {pergola_type}")
    st.sidebar.write(f"Вынос: {length_m} м")
    st.sidebar.write(f"Требуются доп. колонны: {additional_columns}")
    st.sidebar.write(f"Тип ламелей: {real_lamella_type}")
        
    # Добавляем стоимость дополнительных колонн
    if additional_columns:
        if modules == 1:
            additional_columns_cost = 653  # 2 колонны
            additional_columns_components = [
                "Усилитель лотка для большого выноса - 1 шт.",
                "Дополнительные колонны - 2 шт."
            ]
        elif modules == 2:
            additional_columns_cost = 980  # 3 колонны
            additional_columns_components = [
                "Усилитель лотка для большого выноса - 1 шт.",
                "Дополнительные колонны - 3 шт."
            ]
        elif modules >= 3:
            additional_columns_cost = 1306  # 4 колонны
            additional_columns_components = [
                "Усилитель лотка для большого выноса - 1 шт.",
                "Дополнительные колонны - 4 шт."
            ]
    
    # Определяем тип автоматизации и стоимость в зависимости от типа перголы и размеров
    automation_components = []
    
    if pergola_type == "B500NEW":
        # Для B500NEW используем привод Bansbach по правилам из инструкции
        
        # Проверка критериев для использования Bansbach Tandem
        need_tandem = False
        
        # Если 1 модуль
        if modules == 1:
            if width_m <= 2.5 and length_m > 8.0:
                need_tandem = True
            elif width_m > 2.5 and length_m > 7.5:
                need_tandem = True
            elif width_m > 3.0 and length_m > 6.5:
                need_tandem = True
            elif width_m > 3.5 and length_m > 5.5:
                need_tandem = True
            elif width_m > 4.0 and length_m > 5.0:
                need_tandem = True
        # Если 2 модуля
        elif modules == 2:
            if width_m > 5.0 and length_m > 7.5:
                need_tandem = True
            elif width_m > 6.0 and length_m > 6.5:
                need_tandem = True
            elif width_m > 7.0 and length_m > 5.5:
                need_tandem = True
            elif width_m > 8.0 and length_m > 5.0:
                need_tandem = True
        # Если 3 модуля
        elif modules == 3:
            if width_m > 7.5 and length_m > 7.5:
                need_tandem = True
            elif width_m > 9.0 and length_m > 6.5:
                need_tandem = True
            elif width_m > 10.5 and length_m > 5.5:
                need_tandem = True
            elif width_m > 12.0 and length_m > 5.0:
                need_tandem = True
        
        if need_tandem:
            automation_type = "Bansbach Tandem"
            automation_cost = 1250  # Усиленный привод Bansbach Tandem
            automation_components = [
                "Двигатель easyE-lift-50 Bansbach - 2 шт.",
                "Блок управления для 2-х двигателей + блок питания - 1 шт.",
                "Приемник - 1 шт."
            ]
        else:
            automation_type = "Bansbach T1"
            automation_cost = 700  # Стандартный привод Bansbach T1
            automation_components = [
                "Двигатель easyE-lift-50 Bansbach - 1 шт.",
                "Блок управления для 1-го двигателя + блок питания - 1 шт.",
                "Приемник - 1 шт."
            ]
    
    elif pergola_type == "B700NEW":
        # Для B700NEW используем привод Somfy по правилам из инструкции
        
        # Проверка критериев для использования Somfy M2 TANDEM
        need_tandem = False
        
        # Если 1 модуль
        if modules == 1:
            if width_m <= 3.0 and length_m > 7.0:
                need_tandem = True
            elif width_m <= 3.5 and length_m > 6.0:
                need_tandem = True
        # Если 2 модуля
        elif modules == 2:
            if width_m > 6.0 and length_m > 7.0:
                need_tandem = True
            elif width_m > 7.0 and length_m > 6.0:
                need_tandem = True
        
        if need_tandem:
            automation_type = "Somfy M2 TANDEM"
            automation_cost = 1000  # Усиленный привод Somfy M2 TANDEM
            automation_components = [
                "Привод Somfy Altus RTS 120/12 - 2 шт.",
                "Блок управления Somfy для двух двигателей - 1 шт."
            ]
        else:
            automation_type = "Somfy M1"
            automation_cost = 300  # Стандартный привод Somfy M1 согласно инструкции
            automation_components = [
                "Привод Somfy Altus RTS 120/12 - 1 шт.",
                "Блок управления Somfy - 1 шт."
            ]
    
    else:
        # Для B600 и других типов
        automation_type = "Стандартный привод для PIR-панелей"
        automation_cost = 580
        automation_components = [
            "Стандартный привод для PIR-панелей - 1 шт.",
            "Блок управления - 1 шт."
        ]
    
    # Определяем какой пульт нужен в зависимости от количества устройств
    # Считаем количество устройств: привод + освещение (если есть)
    num_devices = 1  # Минимум привод
    
    # Если есть освещение, добавляем еще устройство
    if lighting_type != "none":
        num_devices += 1
    
    # Выбираем пульт на основе количества устройств
    if num_devices <= 1:
        remote_type = "Simu 1K"
        remote_cost = 25
        automation_components.append(f"Пульт {remote_type} (1 канал) - 1 шт.")
    elif num_devices <= 5:
        remote_type = "Simu 5K"
        remote_cost = 40
        automation_components.append(f"Пульт {remote_type} (5 каналов) - 1 шт.")
    else:
        remote_type = "Simu 15K"
        remote_cost = 90
        automation_components.append(f"Пульт {remote_type} (15 каналов) - 1 шт.")
    
    # Добавляем стоимость пульта к стоимости автоматики
    automation_cost += remote_cost
    
    # Добавляем стоимость дополнительных колонн отдельно
    additional_columns_cost_for_results = 0
    additional_columns_components_for_results = []
    
    if additional_columns:
        additional_columns_cost_for_results = additional_columns_cost
        additional_columns_components_for_results = additional_columns_components.copy()
        # Не добавляем компоненты к автоматике, оставляем их отдельно
        # Раньше: automation_components.extend(additional_columns_components)
        # Теперь отображаем их отдельной секцией
        
        # Отладочная информация
        st.sidebar.write(f"Доп. колонны стоимость: {additional_columns_cost}")
        st.sidebar.write(f"Доп. колонны компоненты: {additional_columns_components}")
    
    # Учитываем установку
    installation_cost = 0
    if installation == "with_install":
        installation_cost = pergola_cost * 0.15  # 15% от стоимости перголы
    
    # Итоговая стоимость
    total_cost = pergola_cost + lighting_cost + automation_cost + installation_cost
    
    # Округляем все цены до целых чисел
    pergola_cost = round(pergola_cost)
    lighting_cost = round(lighting_cost)
    automation_cost = round(automation_cost)
    installation_cost = round(installation_cost)
    total_cost = round(total_cost)
    
    # Формируем результат
    results = {
        "total_cost": total_cost,
        "details": {
            "pergola_cost": pergola_cost,
            "pergola_type": pergola_type,
            "real_lamella_type": real_lamella_type,
            "lighting_cost": lighting_cost,
            "lighting_components": lighting_components,
            "automation_cost": automation_cost,
            "automation_type": automation_type,
            "automation_components": automation_components,
            "installation_cost": installation_cost,
            "modules": modules,
            "additional_columns_cost": additional_columns_cost_for_results,
            "additional_columns_components": additional_columns_components_for_results
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
        
        # Для ограничения размеров в зависимости от типа перголы
        pergola_type_key = st.session_state.get('pergola_type', 'B500NEW')
        max_width = MAX_DIMENSIONS.get(pergola_type_key, {}).get('width', 15.0)
        max_length = MAX_DIMENSIONS.get(pergola_type_key, {}).get('length', 10.0)
        
        width = st.number_input("Ширина (м)", min_value=1.0, max_value=max_width, value=3.0, step=0.5)
        length = st.number_input("Вынос (м)", min_value=1.0, max_value=max_length, value=4.0, step=0.5)
        
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
        # Выбор типа ламелей (только для B500NEW и B700NEW)
        st.subheader("Тип ламелей")
        
        # Для B600 не показываем выбор ламелей, так как там PIR-панели
        if pergola_type == "B600":
            lamella_type = "B600-PIR"
            st.info("Для перголы B600 используются PIR сэндвич-панели (фиксированная крыша).")
        else:
            # Для B500NEW и B700NEW показываем только 2 варианта ламелей
            lamella_options = ["lamella-200", "lamella-250"]
            lamella_type = st.radio(
                "Выберите тип ламелей",
                options=lamella_options,
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
        
        # Добавляем информацию о количестве ламелей (для пергол с ламелями)
        if options["pergola_type"] != "B600":
            # Расчет количества ламелей
            lamella_size_m = options["lamella_step"] / 1000  # переводим в метры
            num_lamellas = int(results["dimensions"]["length_m"] / lamella_size_m) + (1 if (results["dimensions"]["length_m"] % lamella_size_m) > 0 else 0)
            basic_specs.append(["Количество ламелей", f"{num_lamellas} шт."])
        
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
        
        # Добавляем информацию о дополнительных колоннах, если они есть
        if results['details']['additional_columns_cost'] > 0 and results['details']['additional_columns_components']:
            cost_items.append(["Усилитель лотка и дополнительные колонны", f"{results['details']['additional_columns_cost']:.0f}"])
            
            # Также добавляем их отдельной секцией в спецификацию, если ещё не добавили
            if results['details']['additional_columns_components']:
                st.markdown("#### Дополнительные компоненты")
                additional_columns = [[comp] for comp in results['details']['additional_columns_components']]
                additional_columns_df = pd.DataFrame(additional_columns, columns=["Наименование"])
                st.table(additional_columns_df)
        
        # Добавляем информацию о стоимости установки
        if results['details']['installation_cost'] > 0:
            cost_items.append(["Установка", f"{results['details']['installation_cost']:.0f}"])
        
        # Итоговая стоимость
        cost_items.append(["**Итоговая стоимость**", f"**{results['total_cost']:.0f}**"])
        
        # Создаем DataFrame для стоимости и добавляем CSS класс для правильного выравнивания
        cost_df = pd.DataFrame(cost_items, columns=["Компонент", "Стоимость, €"])
        st.markdown('<div class="cost-table">', unsafe_allow_html=True)
        st.table(cost_df)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Добавляем примечание о том, что все цены указаны в евро
        st.caption("Все цены указаны в евро. Цены на перголы зависят от выбранных размеров и опций.")

if __name__ == "__main__":
    main()