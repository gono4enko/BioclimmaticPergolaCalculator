"""
Тестовая страница для проверки логики сезонных акций.
Позволяет подтвердить правильность переключения между сезонами и работы счетчика.
"""
import streamlit as st
import datetime
from config import promotions
from components import promotion_display

# Настройка страницы
st.set_page_config(
    page_title="Тестирование сезонных акций",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Заголовок приложения
st.title("Тестирование сезонных акций")

# Информация о текущем времени и сезоне
st.subheader("Текущее время и сезон")
current_time = datetime.datetime.now()
current_season = promotions.get_current_season()
season_name_ru = promotions.get_season_name_in_russian(current_season)

st.write(f"Текущая дата: **{current_time.strftime('%d.%m.%Y %H:%M:%S')}**")
st.write(f"Текущий сезон: **{season_name_ru}** (код: {current_season})")

# Создаем сезонную акцию
seasonal_promo = promotions.generate_seasonal_promotion(5)
st.subheader("Информация о сезонной акции")
start_date, end_date = None, None
for condition in seasonal_promo.get("conditions", []):
    if condition.get("type") == promotions.CONDITION_DATE_RANGE:
        start_date = condition.get("start_date")
        end_date = condition.get("end_date")
        break

if start_date and end_date:
    st.write(f"Начало акции: **{start_date.strftime('%d.%m.%Y')}**")
    st.write(f"Окончание акции: **{end_date.strftime('%d.%m.%Y')}**")
    
    # Сколько дней осталось до конца акции
    days_left = (end_date - datetime.date.today()).days
    st.write(f"Осталось дней: **{days_left}**")
    
    # Форматированный таймер
    formatted_time = promotions.format_countdown_time(end_date)
    st.write(f"Таймер: **{formatted_time}**")

# Демонстрация автоматической смены сезонов
st.subheader("Моделирование сезонов")

# Симуляция разных дат и получение сезонов
test_dates = [
    datetime.date(2025, 1, 15),  # зима
    datetime.date(2025, 4, 10),  # весна
    datetime.date(2025, 7, 20),  # лето
    datetime.date(2025, 10, 5),  # осень
    datetime.date(2025, 12, 25), # зима
]

# Создаем таблицу с примерами дат и сезонов
data = []
for date in test_dates:
    month = date.month
    season = ""
    if 3 <= month <= 5:
        season = "Весна"
    elif 6 <= month <= 8: 
        season = "Лето"
    elif 9 <= month <= 11:
        season = "Осень"
    else:
        season = "Зима"
    
    start_date, end_date = None, None
    if 3 <= month <= 5:  # Весна
        start_date = datetime.date(date.year, 3, 1)
        end_date = datetime.date(date.year, 5, 31)
    elif 6 <= month <= 8:  # Лето
        start_date = datetime.date(date.year, 6, 1)
        end_date = datetime.date(date.year, 8, 31)
    elif 9 <= month <= 11:  # Осень
        start_date = datetime.date(date.year, 9, 1)
        end_date = datetime.date(date.year, 11, 30)
    elif month == 12:  # Зима (декабрь)
        start_date = datetime.date(date.year, 12, 1)
        end_date = datetime.date(date.year + 1, 2, 28)
    else:  # Зима (январь, февраль)
        start_date = datetime.date(date.year - 1, 12, 1)
        end_date = datetime.date(date.year, 2, 28)
    
    data.append([
        date.strftime("%d.%m.%Y"),
        season,
        start_date.strftime("%d.%m.%Y"),
        end_date.strftime("%d.%m.%Y"),
        f"{(end_date - date).days} дней"
    ])

# Отображаем таблицу
st.table({
    "Дата": [row[0] for row in data],
    "Сезон": [row[1] for row in data],
    "Начало акции": [row[2] for row in data],
    "Конец акции": [row[3] for row in data],
    "Осталось": [row[4] for row in data]
})

# Отображаем панель акции
st.subheader("Отображение панели акции")

# Создаем контрольную конфигурацию для тестирования отображения акции
fake_options = {}
fake_promo = {
    "id": f"{current_season}_sale_{datetime.date.today().year}",
    **promotions.generate_seasonal_promotion(5),
}

promotion_display.display_urgent_discount_panel(fake_promo)

# Отображаем разные сезонные цвета
st.subheader("Цвета сезонов")
season_colors = {
    "Весна (spring)": promotions.SEASON_COLORS[promotions.SEASON_SPRING],
    "Лето (summer)": promotions.SEASON_COLORS[promotions.SEASON_SUMMER],
    "Осень (autumn)": promotions.SEASON_COLORS[promotions.SEASON_AUTUMN],
    "Зима (winter)": promotions.SEASON_COLORS[promotions.SEASON_WINTER]
}

for season_name, color in season_colors.items():
    st.markdown(f"""
    <div style="background-color: {color}; padding: 10px; color: white; border-radius: 5px; margin-bottom: 10px;">
        {season_name}: {color}
    </div>
    """, unsafe_allow_html=True)

# Симуляция переключения между сезонами
st.subheader("Симуляция смены сезонов")

# Добавляем проверку определения сезона по дате
st.write("### Проверка определения сезона по дате")
col1, col2, col3 = st.columns(3)
with col1:
    test_day = st.number_input("День", min_value=1, max_value=31, value=15)
with col2:
    test_month = st.number_input("Месяц", min_value=1, max_value=12, value=datetime.date.today().month)
with col3:
    test_year = st.number_input("Год", min_value=2020, max_value=2030, value=datetime.date.today().year)

# Создаем тестовую дату
try:
    test_date = datetime.date(test_year, test_month, test_day)
    
    # Функция для определения сезона по дате
    def get_season_for_date(date):
        month = date.month
        if 3 <= month <= 5:
            return "Весна", promotions.SEASON_SPRING
        elif 6 <= month <= 8:
            return "Лето", promotions.SEASON_SUMMER
        elif 9 <= month <= 11:
            return "Осень", promotions.SEASON_AUTUMN
        else:
            return "Зима", promotions.SEASON_WINTER
    
    # Определяем сезон для тестовой даты
    season_ru, season_code = get_season_for_date(test_date)
    
    # Отображаем результат в цветном блоке
    season_color = promotions.SEASON_COLORS[season_code]
    st.markdown(f"""
    <div style="background-color: {season_color}; padding: 15px; color: white; border-radius: 8px; margin: 15px 0;">
        <h3 style="margin: 0;">Дата {test_date.strftime('%d.%m.%Y')}</h3>
        <p style="font-size: 18px; margin-top: 10px;">Сезон: <b>{season_ru}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Получаем даты начала и окончания акции для этого сезона
    start_date, end_date = promotions.get_season_date_range(season_code, test_date.year)
    
    # Отображаем информацию о периоде акции
    st.write(f"Начало акции: **{start_date.strftime('%d.%m.%Y')}**")
    st.write(f"Окончание акции: **{end_date.strftime('%d.%m.%Y')}**")
    st.write(f"Дней до окончания акции: **{(end_date - test_date).days}**")
    
except ValueError:
    st.error("Указана некорректная дата. Пожалуйста, проверьте, существует ли такая дата в календаре.")

# Симуляция акций по сезонам
st.write("### Симуляция акций для разных сезонов")
selected_season = st.selectbox(
    "Выберите сезон для симуляции акции:",
    ["Текущий", "Весна", "Лето", "Осень", "Зима"]
)

if selected_season != "Текущий":
    season_map = {
        "Весна": promotions.SEASON_SPRING,
        "Лето": promotions.SEASON_SUMMER,
        "Осень": promotions.SEASON_AUTUMN,
        "Зима": promotions.SEASON_WINTER
    }
    
    selected_season_code = season_map[selected_season]
    
    # Функция для создания симулированной акции для выбранного сезона
    def generate_simulated_promo(season_code):
        """Создает акцию для выбранного сезона с подменой текущего сезона"""
        
        # Сохраняем исходную функцию
        original_get_current_season = promotions.get_current_season
        
        # Заменяем функцию определения текущего сезона на нашу, возвращающую выбранный сезон
        def simulated_get_current_season():
            return season_code
        
        # Подменяем функцию
        promotions.get_current_season = simulated_get_current_season
        
        # Создаем акцию для симулируемого сезона
        promo = {
            "id": f"{season_code}_sale_{datetime.date.today().year}",
            **promotions.generate_seasonal_promotion(5)
        }
        
        # Восстанавливаем оригинальную функцию
        promotions.get_current_season = original_get_current_season
        
        return promo
    
    # Создаем симуляцию акции для выбранного сезона
    simulated_promo = generate_simulated_promo(selected_season_code)
    
    # Отображаем информацию о симулированной акции
    st.write(f"### Симулированная акция для сезона: {selected_season}")
    
    # Отображаем даты акции
    start_date, end_date = None, None
    for condition in simulated_promo.get("conditions", []):
        if condition.get("type") == promotions.CONDITION_DATE_RANGE:
            start_date = condition.get("start_date")
            end_date = condition.get("end_date")
            break
    
    if start_date and end_date:
        st.write(f"Начало акции: **{start_date.strftime('%d.%m.%Y')}**")
        st.write(f"Окончание акции: **{end_date.strftime('%d.%m.%Y')}**")
    
    # Отображаем панель акции
    promotion_display.display_urgent_discount_panel(simulated_promo)

# Отображаем кнопку для обновления страницы
if st.button("Обновить страницу", type="primary"):
    st.rerun()