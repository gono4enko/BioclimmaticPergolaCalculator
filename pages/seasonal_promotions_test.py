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
selected_season = st.selectbox(
    "Выберите сезон для симуляции:",
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
    simulated_promo = {
        "id": f"{selected_season_code}_sale_{datetime.date.today().year}",
        **promotions.generate_seasonal_promotion(5)
    }
    
    st.write("### Симулированная акция")
    promotion_display.display_urgent_discount_panel(simulated_promo)

# Отображаем кнопку для обновления страницы
if st.button("Обновить страницу", type="primary"):
    st.rerun()