"""
Калькулятор стоимости пергол - базовая версия без сложных стилей и модификаций
Максимально простой подход с использованием стандартных компонентов Streamlit

Версия 3.7 (стабильная)
Последнее обновление: 10.04.2025

ИНСТРУКЦИИ ПО ОБСЛУЖИВАНИЮ:
- Всегда вести себя как профессионал при внесении изменений
- Достигать результатов максимально быстро и эффективно
- Не нарушать существующую логику работы приложения
- Сохранять единый стиль форматирования для всех элементов
- Сохранять оригинальное содержание текстов и документации
- Приоритизировать оптимизацию UI для лучшей читаемости и удобства пользователей
- При оптимизации таблиц обеспечивать полную видимость числовых значений
- Ценить время пользователя и стремиться к максимальной производительности
"""
import streamlit as st
import pandas as pd
import os
import math
import csv
import time
import tempfile
import base64
from pdf_generator_fpdf_rus import generate_commercial_offer, format_pergola_data_for_pdf
from config.pergola_descriptions import (
    get_pergola_description,
    get_modular_system_description,
    get_drainage_system_description,
    get_bansbach_description,
    get_pergola_images,
    get_pergola_image_caption
)

# Создадим отсутствующие функции для совместимости
def get_bioclimatic_install_description():
    return """
    <h3 style='font-size: 1.2rem; margin-top: 30px; text-align: center;'>Биоклиматические перголы: идеальный симбиоз стиля, функциональности и свободы выбора</h3>
    <p style='margin-bottom: 15px; font-style: italic; text-align: center;'>
    (Как превратить любое пространство в зону комфорта, защищенную от капризов природы)
    </p>
    
    <div style='margin-bottom: 15px;'>
    <h4 style='font-size: 1.1rem; margin-top: 20px;'>Варианты установки: от сада до небоскреба</h4>
    <p style='margin-bottom: 10px;'>Биоклиматическая пергола — это не просто навес, а архитектурный элемент, который адаптируется под ваши потребности. Выберите свой сценарий:</p>
    <ol style='margin-bottom: 10px; padding-left: 20px;'>
        <li><strong>Отдельностоящая</strong> Идеальна для садов, бассейнов, открытых террас. Создает островок уюта в центре ландшафта.
            <ul style='padding-left: 20px;'>
                <li>Пример: Пергола над зоной барбекю, где дождь не прервет вечеринку, а солнце не испортит стейки.</li>
            </ul>
        </li>
        <li><strong>Пристенная</strong> Продлевает жилое пространство дома. Замените скучный козырек на элегантную террасу с видом на сад.
            <ul style='padding-left: 20px;'>
                <li>Фишка: Интеграция с фасадным остеклением — стирает границы между домом и природой.</li>
            </ul>
        </li>
        <li><strong>Подвесная</strong> Для сложных проектов: над внутренними двориками, между этажами или как часть промзоны.
            <ul style='padding-left: 20px;'>
                <li>Технология: Алюминиевые балки выдерживают вес снега и ветровые нагрузки до 70 кг/м².</li>
            </ul>
        </li>
        <li><strong>Интегрированная</strong> Станьте автором уникального дизайна! Комбинируйте перголу с беседками, зимними садами, зонами СПА.
            <ul style='padding-left: 20px;'>
                <li>Для вдохновения: Пергола-трансформер, которая днем — навес у бассейна, а вечером — кинотеатр под звездами.</li>
            </ul>
        </li>
    </ol>
    </div>
    
    <div style='margin-bottom: 15px;'>
    <h4 style='font-size: 1.1rem; margin-top: 20px;'>Вертикальные системы остекления: когда стены становятся умными</h4>
    <p style='margin-bottom: 10px;'>Защитите пространство от ветра, дождя и солнца, не жертвуя светом и видами.</p>
    <ol style='margin-bottom: 10px; padding-left: 20px;'>
        <li><strong>Гильотинное остекление W-серия</strong>
            <ul style='padding-left: 20px;'>
                <li>Как работает: Стеклянные панели поднимаются вертикально, как окна-гильотины.</li>
                <li>Плюсы:
                    <ul style='padding-left: 20px;'>
                        <li>Максимальная герметичность.</li>
                        <li>Выбор: энергоэффективные стеклопакеты толщиной 28мм или закаленное стекло толщиной до 10 мм.</li>
                    </ul>
                </li>
                <li>Для кого: Рестораны с панорамным видом, дома в горах, где важно сохранить тепло.</li>
            </ul>
        </li>
        <li><strong>Раздвижное остекление S-серия</strong>
            <ul style='padding-left: 20px;'>
                <li>Как работает: Панели сдвигаются вбок, превращая перголу в открытую веранду за 30 секунд.</li>
                <li>Плюсы:
                    <ul style='padding-left: 20px;'>
                        <li>Бесшумные направляющие.</li>
                        <li>Возможность объединить до 6 панелей в одну систему.</li>
                    </ul>
                </li>
                <li>Для кого: Летние кафе, квартиры с выходом на террасу, частные дома с террасами либо веранды.</li>
            </ul>
        </li>
        <li><strong>Подъемный ZIP / Screen</strong>
            <ul style='padding-left: 20px;'>
                <li>Как работает: Прочное полотно из акриловой ткани в виде экрана поднимаются по направляющим, создавая тень и защиту от ветра.</li>
                <li>Плюсы:
                    <ul style='padding-left: 20px;'>
                        <li>Солнцезащитные полотна с системой автоматизации.</li>
                        <li>Управление через приложение: регулируйте прозрачность в зависимости от солнца.</li>
                    </ul>
                </li>
                <li>Для кого: Дома у моря, детские площадки под перголой.</li>
            </ul>
        </li>
    </ol>
    </div>
    
    <div style='margin-bottom: 15px;'>
    <h4 style='font-size: 1.1rem; margin-top: 20px;'>Почему это выгодно?</h4>
    <ul style='margin-bottom: 10px; padding-left: 20px;'>
        <li>Адаптивность: Одно решение для дождя, снега, ветра и палящего солнца.</li>
        <li>Дизайн-трансформер: Меняйте конфигурацию остекления и солнцезащиты хоть каждый день.</li>
        <li>Европейская надежность: Автоматика Bansbach и Somfy (до 50 000 циклов!) работают даже в экстремальных условиях.</li>
    </ul>
    </div>
    
    <div style='margin-bottom: 25px;'>
        <p style='margin-bottom: 15px; font-weight: bold;'>Вы готовы выйти за рамки стандартов? Биоклиматическая пергола — это не «навес», а ваш личный климатический контролер. Оставьте заявку, и наши инженеры создадут проект, где каждая деталь будет работать на ваш комфорт.</p>
        <div style="margin: 20px auto; text-align: center;">
            <img src="attached_assets/install_design_system.png" style="max-width: 100%; height: auto;" alt="Система установки и проектирования пергол">
        </div>
    </div>
    """

def get_lamella_engineering_description(pergola_type=None):
    return """
    <div style='padding: 0 20px;'>
    <h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Инженерный взгляд на биоклиматические перголы: как ламели выдерживают снег, ливни и сохраняют тепло</h3>
    <p style='margin-bottom: 15px; font-style: italic; text-align: center;'>
    (Технические секреты, которые делают ваш комфорт непогрешимым)
    </p>
    
    <div style='margin-bottom: 15px;'>
    <h4 style='font-size: 1.1rem; margin-top: 20px;'>Прогиб ламелей: где точность встречает надежность</h4>
    <p style='margin-bottom: 10px;'>Ламели — это «скелет» перголы, и их прочность определяет, как конструкция поведет себя под нагрузками. Мы протестировали каждую модель в экстремальных условиях. Вот что важно знать:</p>
    
    <p style='margin-bottom: 10px;'><strong>Ламель 250×53 NEW</strong></p>
    <ul style='margin-bottom: 10px; padding-left: 20px;'>
        <li>Масса: 4,684 кг/м | Шаг: 250 мм</li>
        <li>Прогиб под нагрузкой:
            <ul style='padding-left: 20px;'>
                <li>Рабочая (масса ламели + 50%): 12 мм при ширине 4,5 м.</li>
                <li>Снеговая (50 кг/м²): 30 мм при ширине 4,5 м.</li>
            </ul>
        </li>
        <li>Макс. снеговая нагрузка: 50 кг/м² (эквивалент 40-50 см свежего снега).</li>
    </ul>
    
    <p style='margin-bottom: 10px;'><strong>Ламель 200×56 NEW</strong></p>
    <ul style='margin-bottom: 10px; padding-left: 20px;'>
        <li>Масса: 4,375 кг/м | Шаг: 200 мм</li>
        <li>Прогиб под нагрузкой:
            <ul style='padding-left: 20px;'>
                <li>Рабочая: 10 мм при ширине 5,0 м.</li>
                <li>Снеговая: 22 мм при ширине 5,0 м.</li>
            </ul>
        </li>
        <li>Макс. снеговая нагрузка: 70 кг/м² (до 60 см снега).</li>
    </ul>
    
    <p style='margin-bottom: 10px;'>Почему это важно? Минимальный прогиб сохраняет геометрию крыши даже в экстремальных условиях. Для сравнения: у конкурентов аналогичные ламели прогибаются на 50-70 мм под теми же нагрузками.</p>
    </div>
    
    <div style='margin-bottom: 15px;'>
    <h4 style='font-size: 1.1rem; margin-top: 20px;'>Герметичность: когда внутри сухо, даже если снаружи потоп</h4>
    <p style='margin-bottom: 10px;'>Алюминиевые ламели перголы — это не просто «крыша», а герметичный кокон. Вот как мы этого добиваемся:</p>
    <ol style='margin-bottom: 10px; padding-left: 20px;'>
        <li><strong>Двойное уплотнение EPDM:</strong>
            <ul style='padding-left: 20px;'>
                <li>Уплотнители между ламелями и в лотках выдерживают давление водяного столба до 600 Па (ливень интенсивностью 100 мм/час).</li>
                <li>Для сравнения: стандартные системы держат только 300-400 Па.</li>
            </ul>
        </li>
        <li><strong>Наклон ламелей + дренажные каналы:</strong> Вода стекает в лотки, не задерживаясь на поверхности. Даже при сильном ветре капли не просачиваются через стыки.</li>
        <li><strong>Тест на герметичность:</strong> Мы заливаем крышу перголы водой под давлением 600 Па в течение 1 часа. Результат: 0 протечек.</li>
    </ol>
    </div>
    
    <div style='margin-bottom: 15px;'>
    <h4 style='font-size: 1.1rem; margin-top: 20px;'>Теплоизоляция: почему под перголой тепло зимой и прохладно летом</h4>
    <ul style='margin-bottom: 10px; padding-left: 20px;'>
        <li><strong>Терморазрыв в профиле:</strong> Алюминиевые ламели с изолирующими вставками из нейлона снижают теплопотери на 40%.</li>
        <li><strong>Эффект «воздушной подушки»:</strong> При закрытых ламелях между ними образуется прослойка воздуха, которая работает как естественный изолятор.</li>
        <li><strong>Температурный комфорт:</strong>
            <ul style='padding-left: 20px;'>
                <li>Зимой: под перголой на 5-7°C теплее, чем снаружи.</li>
                <li>Летом: на 10-12°C прохладнее благодаря тени и вентиляции.</li>
            </ul>
        </li>
    </ul>
    </div>
    
    <div style='margin-bottom: 15px;'>
    <h4 style='font-size: 1.1rem; margin-top: 20px;'>Сравнительная таблица: какая ламель подходит вам?</h4>
    <table style='width: 100%; border-collapse: collapse; margin-bottom: 15px;'>
        <tr>
            <th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Параметр</th>
            <th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Ламель 250×53 NEW</th>
            <th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Ламель 200×56 NEW</th>
        </tr>
        <tr>
            <td style='border: 1px solid #ddd; padding: 8px;'>Снеговая нагрузка</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>50 кг/м²</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>70 кг/м²</td>
        </tr>
        <tr>
            <td style='border: 1px solid #ddd; padding: 8px;'>Прогиб под снегом</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>30 мм (4,5 м)</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>22 мм (5,0 м)</td>
        </tr>
        <tr>
            <td style='border: 1px solid #ddd; padding: 8px;'>Шаг ламелей</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>250 мм</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>200 мм (плотнее защита)</td>
        </tr>
        <tr>
            <td style='border: 1px solid #ddd; padding: 8px;'>Ветровая стойкость</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>До 25 м/с</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>До 30 м/с</td>
        </tr>
        <tr>
            <td style='border: 1px solid #ddd; padding: 8px;'>Идеальный сценарий</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>Умеренный климат</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>Северные регионы</td>
        </tr>
    </table>
    </div>
    
    <div style='margin-bottom: 15px;'>
    <h4 style='font-size: 1.1rem; margin-top: 20px;'>Почему это выгодно?</h4>
    <ul style='margin-bottom: 10px; padding-left: 20px;'>
        <li><strong>Экономия на отоплении/кондиционировании:</strong> Терморазрыв и герметичность снижают затраты на энергию.</li>
        <li><strong>Гарантия 10 лет:</strong> На ламели и уплотнители — потому что мы уверены в каждом миллиметре.</li>
        <li><strong>Адаптивность:</strong> Комбинируйте ламели с остеклением или ZIP-экранами для полного контроля над климатом.</li>
    </ul>
    </div>
    
    <div style='margin-bottom: 25px;'>
        <p style='margin-bottom: 15px; font-weight: bold;'>Финал: Биоклиматическая пергола — это не «навес», а инженерная система, которая считает каждую каплю дождя и снежинку. Выбирайте ламели, которые работают как швейцарские часы — тихо, точно, без компромиссов.</p>
        <div style="margin: 20px auto; text-align: center;">
            <img src="attached_assets/aluminum slats.png" style="max-width: 100%; height: auto;" alt="Алюминиевые ламели для пергол">
        </div>
    </div>
    """

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

# Правила для добавления дополнительных колонн в зависимости от размера выноса
ADDITIONAL_COLUMNS_RULES = {
    "B500NEW": {
        "250": 6.5,  # Для ламелей 250мм - если вынос > 6.5м, нужны доп. колонны
        "200": 6.85  # Для ламелей 200мм - если вынос > 6.85м, нужны доп. колонны
    },
    "B700NEW": {
        "250": 6.5,  # Для ламелей 250мм - если вынос > 6.5м, нужны доп. колонны
        "200": 6.85  # Для ламелей 200мм - если вынос > 6.85м, нужны доп. колонны
    },
    "B600": {
        "PIR": 6.5   # Для PIR панелей - если вынос > 6.5м, нужны доп. колонны
    }
}

# Стоимость дополнительных колонн в зависимости от количества модулей
COLUMNS_PRICES = {
    1: 653,  # 1 модуль - 2 колонны - 653 евро
    2: 980,  # 2 модуля - 3 колонны - 980 евро
    3: 1306  # 3 модуля - 4 колонны - 1306 евро
}

# Усилитель лотка добавляется автоматически при выносе > 6.5м
GUTTER_INSERT_THRESHOLD = 6.5
GUTTER_INSERT_PRICE_PER_METER = 80  # Цена усилителя лотка 80 евро за погонный метр

# Наценки за доставку и установку (в процентах от базовой стоимости)
DELIVERY_MARKUP_PERCENT = 10  # 10% наценка за доставку (добавляется автоматически)
INSTALLATION_MARKUP_PERCENT = 10  # 10% наценка за установку (опционально)

# Курс евро в рублях
EURO_RATE = 110  # 1 евро = 110 рублей

# Правила для выбора привода Bansbach для B500NEW
BANSBACH_DRIVE_RULES = {
    1: [  # 1 модуль
        {"width": 2.5, "length": 8.0, "tandem": False},  # До 2.5м ширины и до 8м выноса - T1
        {"width": 3.0, "length": 6.5, "tandem": True},   # > 2.5м и > 6.5м выноса - Tandem (для 3.0x8.0 тоже нужен Tandem!)
        {"width": 3.5, "length": 5.5, "tandem": True},   # > 3.0м и > 5.5м выноса - Tandem
        {"width": 4.0, "length": 5.0, "tandem": True},   # > 3.5м и > 5.0м выноса - Tandem
        {"width": float('inf'), "length": 5.0, "tandem": True}  # > 4.0м и > 5.0м выноса - Tandem
    ],
    2: [  # 2 модуля
        {"width": 5.0, "length": 8.0, "tandem": False},  # До 5м ширины и до 8м выноса - T1
        {"width": 6.0, "length": 7.5, "tandem": True},   # > 5м и > 7.5м выноса - Tandem
        {"width": 7.0, "length": 6.5, "tandem": True},   # > 6м и > 6.5м выноса - Tandem
        {"width": 8.0, "length": 5.5, "tandem": True},   # > 7м и > 5.5м выноса - Tandem
        {"width": float('inf'), "length": 5.0, "tandem": True}  # > 8м и > 5.0м выноса - Tandem
    ],
    3: [  # 3 модуля
        {"width": 7.5, "length": 8.0, "tandem": False},  # До 7.5м ширины и до 8м выноса - T1
        {"width": 9.0, "length": 7.5, "tandem": True},   # > 7.5м и > 7.5м выноса - Tandem
        {"width": 10.5, "length": 6.5, "tandem": True},  # > 9м и > 6.5м выноса - Tandem
        {"width": 12.0, "length": 5.5, "tandem": True},  # > 10.5м и > 5.5м выноса - Tandem
        {"width": float('inf'), "length": 5.0, "tandem": True}  # > 12м и > 5.0м выноса - Tandem
    ]
}

# Правила для выбора привода Somfy для B700NEW
SOMFY_DRIVE_RULES = {
    1: [  # 1 модуль
        {"width": 3.0, "length": 7.0, "tandem": True},   # до 3м ширины и > 7м выноса - Tandem
        {"width": 3.5, "length": 6.0, "tandem": True},   # до 3.5м ширины и > 6м выноса - Tandem
        {"width": float('inf'), "length": float('inf'), "tandem": False}  # По умолчанию - M1
    ],
    2: [  # 2 модуля
        {"width": 6.0, "length": 7.0, "tandem": True},   # > 6м ширины и > 7м выноса - Tandem
        {"width": 7.0, "length": 6.0, "tandem": True},   # > 7м ширины и > 6м выноса - Tandem
        {"width": float('inf'), "length": float('inf'), "tandem": False}  # По умолчанию - M1
    ],
    3: [  # 3 модуля
        {"width": 9.0, "length": 7.0, "tandem": True},   # > 9м ширины и > 7м выноса - Tandem
        {"width": 10.5, "length": 6.0, "tandem": True},  # > 10.5м ширины и > 6м выноса - Tandem
        {"width": float('inf'), "length": float('inf'), "tandem": False}  # По умолчанию - M1
    ]
}

# Цены на приводы
DRIVE_PRICES = {
    "B500NEW": {
        "standard": 700,     # Bansbach T1 - 700 евро
        "tandem": 1250       # Bansbach Tandem - 1250 евро
    },
    "B700NEW": {
        "standard": 300,     # Somfy M1 - 300 евро
        "tandem": 1000       # Somfy M2 TANDEM - 1000 евро
    }
}

# Функция для правильного склонения слова "канал"
def get_channel_suffix(count):
    """
    Возвращает правильное склонение слова "канал" в зависимости от числа
    
    Args:
        count (int): Количество каналов
    
    Returns:
        str: Правильное склонение слова "канал" ("канал", "канала", "каналов")
    """
    if count % 10 == 1 and count % 100 != 11:
        return "канал"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return "канала"
    else:
        return "каналов"

# Пульты дистанционного управления
REMOTE_CONTROL_TYPES = {
    1: {"name": "Simu 1K", "price": 25},    # 1 канал - 25 евро
    5: {"name": "Simu 5K", "price": 40},    # 5 каналов - 40 евро
    15: {"name": "Simu 15K", "price": 90}   # 15 каналов - 90 евро
}

# Освещение
LIGHTING_PRICES = {
    "controller": 300,       # Блок управления Somfy RTS Dimmer - 300 евро
    "white_led": 20,         # Сверхъяркая LED лента - 20 евро/м
    "rgb_led": 20            # Сверхъяркая RGB лента - 20 евро/м
}

# Функция для загрузки данных о ценах из CSV файлов
def load_price_data(pergola_type, lamella_size):
    """
    Загружает данные о ценах из соответствующего CSV файла
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        
    Returns:
        dict: Словарь с ценами для разных размеров перголы
    """
    # Определяем соответствие типов пергол и имен файлов
    # Ищем как русские, так и английские версии файлов
    file_mapping = {
        ("B500NEW", "200"): ["attached_assets/Price_B500-20.csv", "attached_assets/Прайс_В500-20.csv"],
        ("B500NEW", "250"): ["attached_assets/Price_B500-25.csv", "attached_assets/Прайс_В500-25.csv"],
        ("B700NEW", "200"): ["attached_assets/Price_B700-20.csv", "attached_assets/Прайс_B700-20.csv"],
        ("B700NEW", "250"): ["attached_assets/Price_B700-25.csv", "attached_assets/Прайс_B700-25.csv"],
        ("B600", "PIR"): ["attached_assets/Price_B600_PIR.csv", "attached_assets/Прайс_В600_PIR.csv"]
    }
    
    key = (pergola_type, lamella_size)
    if key not in file_mapping:
        print(f"Ошибка: Комбинация {pergola_type} и {lamella_size} не найдена в маппинге файлов")
        return {}
    
    # Получаем пути к файлам прайса (поддерживаем и английскую, и русскую версию)
    file_paths = file_mapping[key]
    
    # Проверяем, существует ли хотя бы один из файлов
    existing_file_path = None
    for path in file_paths:
        if os.path.exists(path):
            existing_file_path = path
            break
    
    if not existing_file_path:
        print(f"Ошибка: Файлы прайса {file_paths} не найдены")
        return {}
    
    # Используем найденный файл
    file_path = existing_file_path
    
    print(f"Загрузка прайс-листа из файла: {file_path}")
    
    prices = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Определяем разделитель CSV (точка с запятой или запятая)
            first_line = file.readline().strip()
            if ';' in first_line:
                delimiter = ';'
            else:
                delimiter = ','
            
            print(f"Обнаружен разделитель: '{delimiter}'")
            
            # Перематываем файл в начало
            file.seek(0)
            
            reader = csv.reader(file, delimiter=delimiter)
            
            # Пропускаем первую строку (если она содержит информацию о модулях)
            first_row = next(reader)
            if "модуль" in ' '.join(first_row).lower():
                print("Обнаружена строка с информацией о модулях, пропускаем")
                header = next(reader)  # Берем следующую строку как заголовок
            else:
                header = first_row  # Если первая строка не о модулях, она и есть заголовок
            
            print(f"Заголовок: {header}")
            
            # Извлекаем значения длины из заголовка
            length_values = []
            for val in header[1:]:  # Пропускаем первую колонку
                if val.strip():
                    try:
                        # Обрабатываем разные форматы чисел
                        cleaned_val = val.replace(',', '.').strip()
                        length_values.append(float(cleaned_val))
                    except ValueError:
                        print(f"Предупреждение: Не удалось преобразовать '{val}' в число")
                        continue  # Пропускаем, если не удалось преобразовать в число
            
            print(f"Значения длины из заголовка: {length_values}")
            
            # Обрабатываем строки с данными
            for row in reader:
                if not row or len(row) <= 1:
                    continue
                
                try:
                    # Получаем ширину из первой колонки
                    width_str = row[0].strip()
                    if not width_str:
                        continue
                    
                    width = float(width_str.replace(',', '.'))
                    
                    # Обрабатываем цены
                    for i, price_str in enumerate(row[1:]):
                        if i < len(length_values) and price_str.strip():
                            length = length_values[i]
                            try:
                                # Преобразуем строку цены в число
                                # Убираем пробелы и меняем запятую на точку для десятичных чисел
                                price = float(price_str.replace(' ', '').replace(',', '.'))
                                if width not in prices:
                                    prices[width] = {}
                                prices[width][length] = price
                            except ValueError:
                                print(f"Предупреждение: Не удалось преобразовать '{price_str}' в цену")
                                continue  # Пропускаем, если не удалось преобразовать в число
                except (ValueError, IndexError) as e:
                    print(f"Ошибка при обработке строки {row}: {str(e)}")
                    continue
        
        print(f"Загружено {len(prices)} значений ширины с ценами")
        
        # Выводим загруженные данные для отладки
        for width in sorted(prices.keys())[:3]:  # Показываем только 3 первых значения для краткости
            print(f"Ширина {width} м: {prices[width]}")
        
        return prices
    except Exception as e:
        print(f"Ошибка загрузки прайс-листа {file_path}: {str(e)}")
        return {}

def calculate_lighting_perimeter(width_m, length_m, modules=1):
    """
    Расчет периметра подсветки по правилам.
    Для 1 модуля - просто периметр.
    Для нескольких модулей - сумма периметров всех модулей.
    
    Args:
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
        
    Returns:
        float: Длина периметра для светодиодной ленты
    """
    if modules <= 1:
        return 2 * (width_m + length_m)
    
    # Для многомодульных пергол
    module_width = width_m / modules
    module_perimeter = 2 * (module_width + length_m)
    return module_perimeter * modules

def adjust_length_for_lamella_size(length_m, lamella_size_mm):
    """
    Корректирует размер выноса перголы до ближайшего целого числа ламелей
    
    Args:
        length_m (float): Вынос перголы в метрах
        lamella_size_mm (int): Размер ламели в миллиметрах (200 или 250)
        
    Returns:
        float: Скорректированный размер выноса перголы
    """
    lamella_size_m = lamella_size_mm / 1000  # Перевод из мм в метры
    num_lamellas = length_m / lamella_size_m
    
    # Округляем до ближайшего целого числа ламелей в большую сторону
    num_lamellas_rounded = math.ceil(num_lamellas)
    
    # Вычисляем скорректированную длину
    adjusted_length = num_lamellas_rounded * lamella_size_m
    
    return adjusted_length

def get_base_price(pergola_type, lamella_size, width_m, length_m):
    """
    Получает базовую стоимость перголы из прайс-листа, используя точное соответствие
    шириной и длиной (выносом) из таблицы прайса
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600)
        lamella_size (str): Размер ламели (200, 250, PIR)
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        
    Returns:
        float: Базовая стоимость перголы
    """
    prices = load_price_data(pergola_type, lamella_size)
    if not prices:
        raise ValueError(f"Не удалось загрузить данные о ценах для {pergola_type} с ламелями {lamella_size}")
    
    # Логирование для отладки
    print(f"Поиск цены для {pergola_type} с ламелями {lamella_size}, размер {width_m}x{length_m}м")
    
    # Получаем доступные размеры
    available_widths = sorted(prices.keys())
    available_lengths = set()
    for width_data in prices.values():
        available_lengths.update(width_data.keys())
    available_lengths = sorted(available_lengths)
    
    # Логирование доступных размеров для отладки
    print(f"Доступные ширины: {available_widths}")
    print(f"Доступные длины: {available_lengths}")
    
    # В CSV файле цены указаны в формате "вынос (строка) x ширина (столбец)"
    # Но в калькуляторе параметры указаны как "ширина x вынос" 
    # Поэтому меняем местами параметры при поиске цены
    width_orig, length_orig = width_m, length_m
    
    # Находим точный размер или ближайший больший размер
    # В CSV файле цены указаны в формате "вынос (строка) x ширина (столбец)"
    # Но в калькуляторе параметры указаны как "ширина x вынос"
    # Поэтому для поиска в прайсе меняем местами ширину и вынос
    lookup_width = length_m  # Используем длину как ширину в прайсе
    lookup_length = width_m  # Используем ширину как длину в прайсе
    
    # Ищем точное совпадение по ширине (в прайсе это вынос)
    if lookup_width in available_widths:
        width_match = lookup_width
    else:
        # Если точного совпадения нет, ищем ближайшую большую ширину
        width_match = next((w for w in available_widths if w > lookup_width), max(available_widths))
    
    # Ищем точное совпадение по длине (в прайсе это ширина)
    if lookup_length in available_lengths:
        length_match = lookup_length
    else:
        # Если точного совпадения нет, ищем ближайшую большую длину
        length_match = next((l for l in available_lengths if l > lookup_length), max(available_lengths))
    
    # Проверяем, есть ли цена для найденной комбинации ширины и длины
    if width_match in prices and length_match in prices[width_match]:
        price = prices[width_match][length_match]
        print(f"Найдена цена для размера {width_match}x{length_match}м: {price} евро")
        return price
    
    # Если цены нет, ищем минимальную цену среди всех подходящих размеров
    # (размеров, которые больше или равны заданным)
    min_price = None
    min_width = None
    min_length = None
    
    for width in available_widths:
        if width >= lookup_width:  # Используем lookup_width вместо width_m
            for length in available_lengths:
                if length >= lookup_length:  # Используем lookup_length вместо length_m
                    if width in prices and length in prices[width]:
                        price = prices[width][length]
                        if min_price is None or price < min_price:
                            min_price = price
                            min_width = width
                            min_length = length
    
    if min_price is None:
        # Если не нашли ни одной подходящей цены, это ошибка
        raise ValueError(f"Не удалось найти цену для перголы {pergola_type} с размерами {width_m}x{length_m}м")
    
    print(f"Найдена ближайшая цена для размера {min_width}x{min_length}м: {min_price} евро")
    return min_price

def needs_additional_columns(pergola_type, lamella_size, length_m):
    """
    Проверяет, нужны ли дополнительные колонны
    
    Args:
        pergola_type (str): Тип перголы
        lamella_size (str): Размер ламели
        length_m (float): Вынос перголы в метрах
        
    Returns:
        bool: True если нужны дополнительные колонны
    """
    threshold = ADDITIONAL_COLUMNS_RULES.get(pergola_type, {}).get(lamella_size)
    if threshold is None:
        return False
    
    return length_m > threshold

def calculate_gutter_insert_price(length_m, modules):
    """
    Рассчитывает стоимость усилителя лотка по формуле:
    Стоимость = цена за метр * длина выноса * количество лотков
    
    В перголах с 1 модулем - 2 лотка
    В перголах с 2 модулями - 3 лотка
    В перголах с 3 модулями - 4 лотка
    
    Args:
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
    
    Returns:
        tuple: (нужен ли усилитель, стоимость усилителя, количество лотков, общая длина лотков)
    """
    # Проверяем, нужен ли усилитель лотка (вынос > 6.5м)
    needs_insert = length_m > GUTTER_INSERT_THRESHOLD
    
    # Если не нужен усилитель, возвращаем нули
    if not needs_insert:
        return (False, 0, 0, 0)
    
    # Определяем количество лотков в зависимости от модулей
    gutters_count = 0
    if modules == 1:
        gutters_count = 2
    elif modules == 2:
        gutters_count = 3
    elif modules == 3:
        gutters_count = 4
    else:
        gutters_count = modules + 1  # По умолчанию - на 1 больше чем модулей
    
    # Общая длина лотков = вынос * количество лотков
    total_gutter_length = length_m * gutters_count
    
    # Общая стоимость = цена за метр * общая длина
    total_price = GUTTER_INSERT_PRICE_PER_METER * total_gutter_length
    
    return (True, total_price, gutters_count, total_gutter_length)


def needs_gutter_insert(length_m):
    """
    Проверяет, нужен ли усилитель лотка
    
    Args:
        length_m (float): Вынос перголы в метрах
        
    Returns:
        bool: True если нужен усилитель лотка
    """
    return length_m > GUTTER_INSERT_THRESHOLD

def get_drive_price(pergola_type, width_m, length_m, modules):
    """
    Определяет тип и стоимость привода для перголы
    
    Args:
        pergola_type (str): Тип перголы
        width_m (float): Ширина перголы в метрах
        length_m (float): Вынос перголы в метрах
        modules (int): Количество модулей
        
    Returns:
        tuple: (название привода, цена привода, нужен ли танем-привод)
    """
    if pergola_type == "B500NEW":
        rules = BANSBACH_DRIVE_RULES.get(modules, [])
        # Специальный случай для размера 3x8 (нужен Tandem)
        if abs(width_m - 3.0) < 0.01 and abs(length_m - 8.0) < 0.01:
            return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
            
        # Проверяем правила
        for rule in rules:
            # При большом выносе (> 6м) всегда нужен Tandem, даже если ширина небольшая
            if length_m > 6.0:
                return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
            
            if width_m > rule["width"] and length_m > rule["length"]:
                if rule["tandem"]:
                    return "Bansbach Tandem, Germany", DRIVE_PRICES["B500NEW"]["tandem"], True
                else:
                    return "Bansbach Т1, Germany", DRIVE_PRICES["B500NEW"]["standard"], False
        
        # По умолчанию - стандартный привод
        return "Bansbach Т1, Germany", DRIVE_PRICES["B500NEW"]["standard"], False
    
    elif pergola_type == "B700NEW":
        rules = SOMFY_DRIVE_RULES.get(modules, [])
        for rule in rules:
            # Для 1 модуля: проверяем, что ширина <= указанной, для других модулей: ширина > указанной
            width_check = width_m <= rule["width"] if modules == 1 else width_m > rule["width"]
            
            if width_check and length_m > rule["length"]:
                if rule["tandem"]:
                    return "Somfy M2 TANDEM", DRIVE_PRICES["B700NEW"]["tandem"], True
                else:
                    return "Somfy M1", DRIVE_PRICES["B700NEW"]["standard"], False
        
        # По умолчанию - стандартный привод
        return "Somfy M1", DRIVE_PRICES["B700NEW"]["standard"], False
    
    return "", 0, False

def get_remote_control(devices_count):
    """
    Определяет тип и стоимость пульта управления на основе количества управляемых устройств.
    Выбор происходит по следующим правилам:
    - Если устройств 1, выбирается одноканальный пульт Simu 1K
    - Если устройств 2-3, выбирается пятиканальный пульт Simu 5K
    - Если устройств 4-5, выбирается пятиканальный пульт Simu 5K
    - Если устройств более 5, выбирается пятнадцатиканальный пульт Simu 15K
    
    Args:
        devices_count (int): Количество устройств для управления
        
    Returns:
        tuple: (название пульта, цена пульта)
    """
    if devices_count == 1:
        return REMOTE_CONTROL_TYPES[1]["name"], REMOTE_CONTROL_TYPES[1]["price"]
    elif 2 <= devices_count <= 5:
        return REMOTE_CONTROL_TYPES[5]["name"], REMOTE_CONTROL_TYPES[5]["price"]
    else:
        return REMOTE_CONTROL_TYPES[15]["name"], REMOTE_CONTROL_TYPES[15]["price"]

def perform_calculation(dimensions, options):
    """Выполнить расчет стоимости перголы"""
    try:
        # Извлекаем данные из ввода пользователя
        width_m = float(dimensions.get("width", 0))
        length_m = float(dimensions.get("length", 0))
        pergola_type = options.get("pergola_type", "")
        lamella_type = options.get("lamella_type", "")
        modules = get_modules_by_dimensions(width_m, length_m, pergola_type)  # Автоматически определяем модули по размерам
        lighting_options = options.get("lighting", [])
        installation = options.get("installation", False)  # Опция установки
        
        # Определяем размер ламели в миллиметрах
        lamella_size = "PIR" if "PIR" in lamella_type else ("200" if "200" in lamella_type else "250")
        
        # Корректируем размер выноса в соответствии с размером ламелей для B500NEW и B700NEW
        if pergola_type in ["B500NEW", "B700NEW"]:
            lamella_size_mm = 200 if lamella_size == "200" else 250
            original_length = length_m
            length_m = adjust_length_for_lamella_size(length_m, lamella_size_mm)
            # Рассчитываем количество ламелей
            lamellas_count = math.ceil(length_m / (lamella_size_mm / 1000))
        
        # Определяем базовую стоимость перголы из прайс-листа
        base_price = get_base_price(pergola_type, lamella_size, width_m, length_m)
        
        # Инициализируем результаты расчета
        results = {
            "dimensions": {
                "width": width_m,
                "length": length_m,
                "modules": modules
            },
            "options": {
                "pergola_type": pergola_type,
                "lamella_type": lamella_type,
                "lighting": lighting_options,
                "installation": installation
            },
            "base_price": base_price,
            "items": [],
            "total_price": base_price
        }
        
        # Проверяем, нужны ли дополнительные колонны
        need_columns = needs_additional_columns(pergola_type, lamella_size, length_m)
        if need_columns:
            columns_price = COLUMNS_PRICES.get(modules, 0)
            results["additional_columns"] = {
                "required": True,
                "count": modules + 1,  # Количество колонн зависит от модулей
                "price": columns_price
            }
            results["items"].append({
                "name": f"Дополнительные колонны ({modules + 1} шт.)",
                "price": columns_price
            })
            results["total_price"] += columns_price
        else:
            results["additional_columns"] = {"required": False}
        
        # Проверяем, нужен ли усилитель лотка и рассчитываем его стоимость
        gutter_needed, gutter_price, gutters_count, total_gutter_length = calculate_gutter_insert_price(length_m, modules)
        if gutter_needed:
            results["gutter_insert"] = {
                "required": True,
                "gutters_count": gutters_count,
                "length": total_gutter_length,
                "price_per_meter": GUTTER_INSERT_PRICE_PER_METER,
                "total_price": gutter_price
            }
            results["items"].append({
                "name": f"Усилитель лотка ({gutters_count} лотка, {total_gutter_length:.2f} м)",
                "price": gutter_price
            })
            results["total_price"] += gutter_price
        else:
            results["gutter_insert"] = {"required": False}
        
        # Определяем тип и стоимость привода
        if pergola_type in ["B500NEW", "B700NEW"]:
            drive_name, drive_price, is_tandem = get_drive_price(pergola_type, width_m, length_m, modules)
            drive_count = modules  # Один привод на каждый модуль
            total_drive_price = drive_price * drive_count
            
            results["drive"] = {
                "name": drive_name,
                "count": drive_count,
                "is_tandem": is_tandem,
                "price": drive_price,
                "total_price": total_drive_price
            }
            
            results["items"].append({
                "name": f"Привод {drive_name} (для {drive_count} модулей)",
                "price": total_drive_price
            })
            
            results["total_price"] += total_drive_price
            
            # Количество устройств для пульта ДУ (привод + освещение)
            devices_count = drive_count
            if "white_led" in lighting_options or "rgb_led" in lighting_options:
                devices_count += 1  # Добавляем блок управления освещением
            
            # Определяем тип и стоимость пульта ДУ
            remote_name, remote_price = get_remote_control(devices_count)
            
            results["remote_control"] = {
                "name": remote_name,
                "devices_count": devices_count,
                "price": remote_price
            }
            
            results["items"].append({
                "name": f"Пульт ДУ {remote_name} ({devices_count} {get_channel_suffix(devices_count)})",
                "price": remote_price
            })
            
            results["total_price"] += remote_price
        
        # Расчет стоимости освещения
        has_lighting = "white_led" in lighting_options or "rgb_led" in lighting_options
        if has_lighting:
            lighting_perimeter = calculate_lighting_perimeter(width_m, length_m, modules)
            
            lighting_cost = 0
            led_types = []
            
            # Блок управления освещением - по 1 блоку на каждый модуль
            # Количество блоков управления зависит от количества модулей
            controllers_count = modules
            total_controller_price = LIGHTING_PRICES["controller"] * controllers_count
            lighting_cost += total_controller_price
            results["items"].append({
                "name": f"Блок управления освещением Somfy RTS Dimmer ({controllers_count} шт.)",
                "price": total_controller_price
            })
            
            # Белая светодиодная лента
            if "white_led" in lighting_options:
                white_led_cost = LIGHTING_PRICES["white_led"] * lighting_perimeter
                lighting_cost += white_led_cost
                led_types.append("белая")
                results["items"].append({
                    "name": f"Светодиодная лента белая ({lighting_perimeter:.2f} м)",
                    "price": white_led_cost
                })
            
            # RGB светодиодная лента
            if "rgb_led" in lighting_options:
                rgb_led_cost = LIGHTING_PRICES["rgb_led"] * lighting_perimeter
                lighting_cost += rgb_led_cost
                led_types.append("RGB")
                results["items"].append({
                    "name": f"Светодиодная лента RGB ({lighting_perimeter:.2f} м)",
                    "price": rgb_led_cost
                })
                
            # Для B600 добавляем пульт управления освещением
            if pergola_type == "B600":
                # Для B600 нужен отдельный пульт для освещения
                # Количество устройств = количество блоков освещения (по одному на каждый модуль)
                lighting_devices_count = controllers_count  
                remote_name, remote_price = get_remote_control(lighting_devices_count)
                
                results["lighting_remote"] = {
                    "name": remote_name,
                    "devices_count": lighting_devices_count,
                    "price": remote_price
                }
                
                results["items"].append({
                    "name": f"Пульт ДУ {remote_name} для освещения ({lighting_devices_count} {get_channel_suffix(lighting_devices_count)})",
                    "price": remote_price
                })
                
                lighting_cost += remote_price
            
            results["lighting"] = {
                "types": led_types,
                "perimeter": lighting_perimeter,
                "total_price": lighting_cost
            }
            
            results["total_price"] += lighting_cost
        
        # Добавляем информацию о спецификации (без цен)
        specification = []
        
        # Определяем тип ламелей и их количество
        lamella_info = ""
        if pergola_type in ["B500NEW", "B700NEW"]:
            lamella_info = LAMELLA_TYPES.get(lamella_type, lamella_type).lower()
            # Корректное склонение в зависимости от числа ламелей (четное/нечетное)
            lamellas_suffix = "ламель" if lamellas_count % 2 != 0 else "ламелей"
            lamellas_count_text = f", {lamellas_count} {lamellas_suffix}" if 'lamellas_count' in locals() else ""
        else:
            lamellas_count_text = ""
                
        # Корректируем текст для описания ламелей в единственном числе
        if "ламели" in lamella_info.lower():
            lamella_info = lamella_info.replace("Ламели", "ламелью").replace("ламели", "ламелью")
                
        # Основная пергола
        specification.append({
            "name": f"Пергола {PERGOLA_TYPES.get(pergola_type, pergola_type)} {width_m:.2f}×{length_m:.2f} м с {lamella_info}{lamellas_count_text}",
            "count": f"{modules} {'модуль' if modules == 1 else 'модуля' if modules < 5 else 'модулей'}",
            "price": ""
        })
        
        # Дополнительные колонны и усилитель лотка
        if need_columns:
            specification.append({
                "name": "Дополнительные колонны",
                "count": f"{modules + 1} шт.",
                "price": ""
            })
        
        if gutter_needed:
            # Правильное склонение для "лоток"
            gutter_suffix = "лоток" if gutters_count % 10 == 1 and gutters_count % 100 != 11 else "лотка" if 2 <= gutters_count % 10 <= 4 and (gutters_count % 100 < 10 or gutters_count % 100 >= 20) else "лотков"
            specification.append({
                "name": "Усилитель лотка",
                "count": f"{total_gutter_length:.2f} м ({gutters_count} {gutter_suffix})",
                "price": ""
            })
        
        # Привод
        if pergola_type in ["B500NEW", "B700NEW"]:
            drive_name, _, _ = get_drive_price(pergola_type, width_m, length_m, modules)
            specification.append({
                "name": f"Привод {drive_name}",
                "count": f"{modules} шт.",
                "price": ""
            })
            
            # Пульт ДУ
            remote_name, _ = get_remote_control(devices_count)
            specification.append({
                "name": f"Пульт ДУ {remote_name}",
                "count": "1 шт.",
                "price": ""
            })
        
        # Освещение
        if has_lighting:
            # Добавляем блок управления освещением - по 1 блоку на каждый модуль
            specification.append({
                "name": "Блок управления освещением Somfy RTS Dimmer",
                "count": f"{modules} шт.",
                "price": ""
            })
            
            # Увеличиваем счетчик устройств для определения типа пульта
            lighting_devices_count = modules  # По 1 блоку управления на каждый модуль
            
            if "white_led" in lighting_options:
                specification.append({
                    "name": "Светодиодная лента белая",
                    "count": f"{lighting_perimeter:.2f} м",
                    "price": ""
                })
            
            if "rgb_led" in lighting_options:
                specification.append({
                    "name": "Светодиодная лента RGB",
                    "count": f"{lighting_perimeter:.2f} м",
                    "price": ""
                })
            
            # Добавляем пульт для управления освещением
            # Если уже есть пульт от привода перголы (B500/B700), выбираем пульт с большим числом каналов
            # Если перголы B600 без привода, добавляем пульт для освещения
            if pergola_type in ["B500NEW", "B700NEW"]:
                # Обновляем devices_count для выбора пульта с большим числом каналов
                devices_count += lighting_devices_count
                
                # Обновляем информацию о пульте в спецификации
                for i, item in enumerate(specification):
                    if "Пульт ДУ" in item["name"]:
                        remote_name, _ = get_remote_control(devices_count)
                        specification[i] = {
                            "name": f"Пульт ДУ {remote_name}",
                            "count": "1 шт.",
                            "price": ""
                        }
                        break
            else:
                # Для B600 добавляем отдельный пульт для освещения
                remote_name, _ = get_remote_control(lighting_devices_count)
                specification.append({
                    "name": f"Пульт ДУ {remote_name} для освещения",
                    "count": f"1 шт. ({lighting_devices_count} {get_channel_suffix(lighting_devices_count)})",
                    "price": ""
                })
        
        results["specification"] = specification
        
        # Базовая стоимость (без наценок)
        base_total_price = results["total_price"]
        
        # Добавляем наценку за доставку (10% автоматически)
        delivery_price = round(base_total_price * 0.1, 2)
        results["delivery"] = {
            "percentage": 10,
            "price": delivery_price
        }
        results["items"].append({
            "name": "Доставка (10%)",
            "price": delivery_price
        })
        results["total_price"] += delivery_price
        
        # Добавляем наценку за установку (10%, если выбрана опция)
        if installation:
            installation_price = round(base_total_price * 0.1, 2)
            results["installation"] = {
                "selected": True,
                "percentage": 10,
                "price": installation_price
            }
            results["items"].append({
                "name": "Установка (10%)",
                "price": installation_price
            })
            results["total_price"] += installation_price
        else:
            results["installation"] = {
                "selected": False,
                "price": 0
            }
        
        # Обновляем итоговую стоимость в спецификации
        specification.append({
            "name": "Доставка",
            "count": "10%",
            "price": ""
        })
        
        if installation:
            specification.append({
                "name": "Установка",
                "count": "10%",
                "price": ""
            })
        
        # Округляем общую стоимость
        results["total_price"] = round(results["total_price"], 2)
        
        # Отладочная информация
        results["debug"] = {
            "length_corrected": length_m,
            "width": width_m,
            "modules": modules,
            "need_columns": need_columns,
            "need_gutter": gutter_needed,
            "pergola_type": pergola_type,
            "lamella_type": lamella_type,
            "lamella_size": lamella_size,
            "lamellas_count": lamellas_count if 'lamellas_count' in locals() else 0,
            "installation": installation
        }
        
        return results
    
    except Exception as e:
        error_msg = f"Ошибка при расчете: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

def get_modules_by_dimensions(width, length, pergola_type=None):
    """
    Определяет количество модулей в зависимости от размеров перголы и ее типа.
    Учитывает как ширину, так и вынос (длину) перголы.
    
    Args:
        width (float): Ширина перголы в метрах
        length (float): Вынос (длина) перголы в метрах
        pergola_type (str, optional): Тип перголы
        
    Returns:
        int: Количество модулей
    """
    # Особые правила для больших выносов
    if length > 6.0:
        if width <= 4.5:
            return 2  # Для выноса > 6.0м даже при малой ширине нужно 2 модуля
        elif width <= 9.0:
            return 2  # Для ширины 5-9м - 2 модуля
        else:
            return 3  # Для ширины 9.5м и более - 3 модуля
    
    # Стандартные правила по ширине
    if width <= 4.5:
        return 1  # Для ширины до 4.5м - 1 модуль
    elif width <= 9.0:
        return 2  # Для ширины 5-9м - 2 модуля
    else:
        return 3  # Для ширины 9.5м и более - 3 модуля
        
def get_modules_by_width(width):
    """
    Устаревшая функция, оставлена для совместимости.
    Используйте get_modules_by_dimensions вместо нее.
    
    Args:
        width (float): Ширина перголы в метрах
        
    Returns:
        int: Количество модулей
    """
    return get_modules_by_dimensions(width, 4.0)  # Используем стандартный вынос 4.0

def render_dimensions_form():
    """
    Отображает форму для ввода размеров перголы
    
    Returns:
        dict: Словарь с введенными размерами
    """
    st.markdown("<h2 class='section-header' style='text-align: center;'>Размеры перголы</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        width = st.number_input(
            "Ширина (м)",
            min_value=2.0,
            max_value=15.0,
            value=3.0,
            step=0.5,
            format="%.2f",
            help="Ширина перголы в метрах (2.0 - 15.0 м)"
        )
    
    with col2:
        length = st.number_input(
            "Вынос (м)",
            min_value=2.0,
            max_value=8.0,
            value=4.0,
            step=0.5,
            format="%.2f",
            help="Глубина (вынос) перголы в метрах (2.0 - 8.0 м)"
        )
    
    # Определяем количество модулей автоматически по обоим параметрам - ширине и выносу
    modules = get_modules_by_dimensions(width, length)
    
    # Показываем информацию о модулях (только для отображения)
    if modules > 1:
        # Правильное склонение для модулей
        modules_suffix = "модуля" if modules < 5 else "модулей"
        st.info(f"При размере {width:.2f}×{length:.2f} м будет автоматически использовано {modules} {modules_suffix}")
    
    return {
        "width": width,
        "length": length,
        "modules": modules
    }

def render_options_form():
    """
    Отображает форму для выбора опций перголы в плиточном дизайне
    
    Returns:
        dict: Словарь с выбранными опциями
    """
    st.markdown("<h2 class='section-header' style='text-align: center;'>Параметры перголы</h2>", unsafe_allow_html=True)
    
    # Тип перголы
    pergola_type = st.radio(
        "Выберите тип перголы",
        options=list(PERGOLA_TYPES.keys()),
        format_func=lambda x: PERGOLA_TYPES.get(x, x),
        horizontal=True
    )
    
    # Тип ламелей - зависит от выбранного типа перголы
    lamella_options = []
    if pergola_type == "B500NEW":
        lamella_options = ["B500-25NEW", "B500-20NEW"]  # Стандартные 250 мм первыми
    elif pergola_type == "B700NEW":
        lamella_options = ["B700-25NEW", "B700-20NEW"]  # Стандартные 250 мм первыми
    elif pergola_type == "B600":
        lamella_options = ["B600-PIR"]
    
    lamella_type = st.radio(
        "Выберите тип ламелей",
        options=lamella_options,
        format_func=lambda x: LAMELLA_TYPES.get(x, x),
        horizontal=True
    )
    
    # Освещение
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight: 500; margin-bottom: 5px;'>Освещение</p>", unsafe_allow_html=True)
    
    lighting_options = []
    col1, col2 = st.columns(2)
    
    with col1:
        if st.checkbox("Белая светодиодная лента", value=False):
            lighting_options.append("white_led")
    
    with col2:
        if st.checkbox("RGB светодиодная лента", value=False):
            lighting_options.append("rgb_led")
    
    # Установка
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight: 500;'>Установка</p>", unsafe_allow_html=True)
    
    installation = st.checkbox("С установкой (+10% к стоимости)", value=True)
    
    # Возвращаем выбранные опции (не включаем модули, т.к. они рассчитываются автоматически)
    return {
        "pergola_type": pergola_type,
        "lamella_type": lamella_type,
        "lighting": lighting_options,
        "installation": installation
    }

def create_pdf_download_link(pdf_path, link_text="Скачать коммерческое предложение в PDF"):
    """
    Создает HTML-ссылку для скачивания сгенерированного PDF-файла
    
    Args:
        pdf_path (str): Путь к PDF-файлу
        link_text (str): Текст ссылки
        
    Returns:
        str: HTML-код ссылки для скачивания
    """
    with open(pdf_path, "rb") as file:
        pdf_data = file.read()
    
    # Кодируем данные PDF в base64
    b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    
    # Создаем ссылку для скачивания
    # Используем чистый HTML вместо st.download_button для большей гибкости стиля
    download_filename = os.path.basename(pdf_path)
    href = f"""
    <a href="data:application/octet-stream;base64,{b64_pdf}" 
       download="{download_filename}" 
       style="display: inline-block; 
              background-color: #4CAF50; 
              color: white; 
              padding: 10px 20px; 
              text-align: center; 
              text-decoration: none; 
              font-size: 16px; 
              margin: 15px 0; 
              border-radius: 4px;">
        <i class="fas fa-file-pdf"></i> {link_text}
    </a>
    """
    
    return href

def render_results(results):
    """
    Отображает результаты расчета стоимости перголы
    
    Args:
        results (dict): Словарь с результатами расчета
    """
    # Создаем якорь для скролла с ID 
    st.markdown('<div id="results" name="results"></div>', unsafe_allow_html=True)
    
    if "error" in results:
        st.error(f"Ошибка при расчете: {results['error']}")
        return
    
    # Основная информация о перголе
    pergola_type = results["options"]["pergola_type"]
    width = results["dimensions"]["width"]
    length = results["dimensions"]["length"]
    modules = results["dimensions"]["modules"]
    base_price = results["base_price"]
    
    # Курс евро для конвертации цен
    euro_rate = EURO_RATE
    total_price = results["total_price"]
    
    # Отладочная информация только в режиме разработки
    if 'debug_mode' in st.session_state and st.session_state['debug_mode']:
        with st.sidebar:
            st.markdown("### Отладочная информация")
            st.json(results["debug"])
    
    # Получаем информацию о ламелях
    lamella_type = results["options"]["lamella_type"]
    lamella_info = LAMELLA_TYPES.get(lamella_type, lamella_type)
    
    # Получаем количество ламелей
    lamellas_count = results["debug"].get("lamellas_count", 0)
    
    # Заголовок результатов
    rub_total = total_price * euro_rate
    # Форматируем цену в бухгалтерском стиле с разделителями тысяч
    formatted_price = "{:,.0f}".format(rub_total).replace(",", " ")
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
        <h2 style='margin-top: 0; color: #0066cc; font-size: 1.4rem;'>Результаты расчета</h2>
        <p style='font-size: 1.1rem; margin-bottom: 5px;'>
            <strong>Пергола:</strong> {PERGOLA_TYPES.get(pergola_type, pergola_type)} {width:.2f}×{length:.2f} м
        </p>
        <p style='font-size: 1.1rem; margin-bottom: 5px;'>
            <strong>Тип ламелей:</strong> {lamella_info}
        </p>
        <p style='font-size: 1.1rem; margin-bottom: 5px;'>
            <strong>Количество модулей:</strong> {modules}
        </p>
        <div style='font-size: 1.4rem; color: #0066cc; font-weight: 700; margin-top: 15px; padding-top: 10px; border-top: 1px solid #e0e0e0; text-align: center;'>
            Итоговая стоимость: <span style='font-size: 1.5rem; color: #0066cc;'>{formatted_price} ₽</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Кнопки PDF временно скрыты 
    # (функциональность будет настроена позже)
    if False:  # Условие, при котором код не будет выполняться
        pdf_col1, pdf_col2 = st.columns([4, 2])
        
        with pdf_col1:
            st.markdown("<p style='margin-top: 15px;'>Создайте коммерческое предложение для вашего клиента:</p>", 
                        unsafe_allow_html=True)
        
        with pdf_col2:
            if st.button("Создать коммерческое предложение", key="create_pdf_btn"):
                with st.spinner("Генерация PDF, пожалуйста подождите..."):
                    try:
                        # Получаем описание перголы из конфигурации
                        pergola_description = get_pergola_description(pergola_type)
                        
                        # Форматируем данные для PDF
                        pergola_data = format_pergola_data_for_pdf(
                            results=results,
                            options=results["options"],
                            dimensions=results["dimensions"],
                            pergola_description=pergola_description
                        )
                        
                        # Создаем PDF и получаем путь к файлу
                        pdf_path = generate_commercial_offer(pergola_data)
                        
                        if pdf_path:
                            # Создаем и отображаем ссылку для скачивания PDF
                            pdf_download_link = create_pdf_download_link(pdf_path)
                            st.markdown(f"<div style='text-align: center;'>{pdf_download_link}</div>", unsafe_allow_html=True)
                            st.success("Коммерческое предложение успешно создано!")
                        else:
                            st.error("Не удалось создать PDF. Проверьте логи сервера.")
                    except Exception as e:
                        st.error(f"Ошибка при создании PDF: {str(e)}")
                        st.info("Проверьте наличие шрифтов в папке fonts/ и права доступа к директории generated_pdf/")
    
    # Отображаем спецификацию перголы
    if "specification" in results:
        st.markdown("<h3 style='font-size: 1.1rem; margin-top: 0; margin-bottom: 10px; text-align: center;'>Спецификация перголы</h3>", unsafe_allow_html=True)
        
        # Создаем таблицу спецификации
        spec_data = []
        for item in results["specification"]:
            spec_data.append([item["name"], item["count"]])
        
        # Преобразуем данные в DataFrame и отображаем
        import pandas as pd
        spec_df = pd.DataFrame(spec_data, columns=["Наименование", "Количество"])
        
        # Создаем уникальный ключ для таблицы спецификации (для применения уникальных стилей)
        spec_table_key = "spec_table_" + str(hash(str(spec_data)))
        
        # Создаем HTML-таблицу напрямую для обхода проблем с шириной
        html_table = '<table style="width:100%; border-collapse:collapse; margin-bottom:20px;">'
        
        # Добавляем заголовки
        html_table += '<tr>'
        html_table += '<th style="text-align:left; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:65%;">Наименование</th>'
        html_table += '<th style="text-align:center; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:35%;">Количество</th>'
        html_table += '</tr>'
        
        # Добавляем строки с данными
        for item in spec_data:
            html_table += '<tr>'
            html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:0.95rem;">{item[0]}</td>'
            html_table += f'<td style="text-align:center; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:0.95rem;">{item[1]}</td>'
            html_table += '</tr>'
        
        html_table += '</table>'
        
        # Выводим HTML-таблицу напрямую через markdown с теми же отступами, как у таблицы стоимости
        st.markdown(f"""
        <div style="width:95%; margin:0 auto; padding-left:15px; padding-right:15px;">
            {html_table}
        </div>
        """, unsafe_allow_html=True)
    
    # Отображаем таблицу стоимости
    st.markdown("<h3 style='font-size: 1.1rem; margin-top: 15px; margin-bottom: 10px; text-align: center;'>Стоимость</h3>", unsafe_allow_html=True)
    
    # Создаем таблицу стоимости
    items_data = []
    
    # Получаем информацию о ламелях
    lamella_info = LAMELLA_TYPES.get(results["options"]["lamella_type"], results["options"]["lamella_type"])
    lamellas_count = results["debug"].get("lamellas_count", 0)
    lamellas_info = f" с ламелью {lamella_info.replace('ламели ', '')}"
    if lamellas_count > 0 and pergola_type in ["B500NEW", "B700NEW"]:
        # Корректное склонение в зависимости от числа ламелей (четное/нечетное)
        lamellas_suffix = "ламель" if lamellas_count % 2 != 0 else "ламелей"
        lamellas_info += f", {lamellas_count} {lamellas_suffix}"
    
    # Функция для форматирования цены в бухгалтерском стиле
    def format_price(price):
        # Всегда используем полный формат без сокращений
        # Форматируем с пробелами между тысячами и символом валюты
        return "{:,.0f} ₽".format(price).replace(",", " ")
    
    # Базовая стоимость перголы - всегда первой строкой
    rub_base_price = base_price * euro_rate
    items_data.append([f"Пергола {PERGOLA_TYPES.get(pergola_type, pergola_type)} {width:.2f}×{length:.2f} м{lamellas_info} ({modules} модуль)", format_price(rub_base_price)])
    
    # Привод и автоматика - второй строкой, если есть
    if pergola_type in ["B500NEW", "B700NEW"]:
        for item in results["items"]:
            if "Привод" in item["name"] or "привод" in item["name"]:
                rub_price = item['price'] * euro_rate
                items_data.append([item["name"], format_price(rub_price)])
    
    # Пульт ДУ - третьей строкой, если есть (для всех типов пергол)
    for item in results["items"]:
        if "Пульт" in item["name"] or "пульт" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
    
    # Освещение - четвертой строкой, если есть
    for item in results["items"]:
        if "освещен" in item["name"].lower() or "лента" in item["name"].lower():
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
    
    # Дополнительные опции - усилитель лотка и колонны
    for item in results["items"]:
        if "Усилитель" in item["name"] or "усилитель" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
        
        if "колон" in item["name"].lower():
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
    
    # Доставка и установка
    for item in results["items"]:
        if "Доставка" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
            
        if "Установка" in item["name"]:
            rub_price = item['price'] * euro_rate
            items_data.append([item["name"], format_price(rub_price)])
    
    # Итоговая строка - просто добавляем строку "Итого" (жирный шрифт применяется через CSS)
    rub_total = total_price * euro_rate
    items_data.append(["Итого", format_price(rub_total)])
    
    # Создаем HTML-таблицу напрямую для обхода проблем с шириной
    html_table = '<table style="width:100%; border-collapse:collapse; margin-bottom:20px;">'
    
    # Добавляем заголовки
    html_table += '<tr>'
    html_table += '<th style="text-align:left; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:65%;">Наименование</th>'
    html_table += '<th style="text-align:right; padding:8px; background-color:#f8f9fa; border-bottom:1px solid #ddd; width:35%;">Стоимость</th>'
    html_table += '</tr>'
    
    # Добавляем строки с данными
    for i, item in enumerate(items_data):
        # Особое форматирование для строки "Итого"
        if i == len(items_data) - 1:
            html_table += '<tr style="background-color:#e0f0ff;">'
            html_table += f'<td style="text-align:left; padding:10px 5px; border-bottom:2px solid #3f6daa; word-wrap:break-word; font-weight:bold; font-size:1.2rem;">{item[0]}</td>'
            html_table += f'<td style="text-align:right; padding:10px 15px; border-bottom:2px solid #3f6daa; font-weight:bold; font-size:1.2rem; color:#0066cc; min-width:120px; white-space:nowrap;">{item[1]}</td>'
            html_table += '</tr>'
        else:
            html_table += '<tr>'
            html_table += f'<td style="text-align:left; padding:8px 5px; border-bottom:1px solid #eee; word-wrap:break-word; font-size:0.95rem;">{item[0]}</td>'
            html_table += f'<td style="text-align:right; padding:8px 15px; border-bottom:1px solid #eee; min-width:150px; white-space:nowrap; font-size:0.95rem;">{item[1]}</td>'
            html_table += '</tr>'
    
    html_table += '</table>'
    
    # Выводим HTML-таблицу напрямую через markdown
    st.markdown(f"""
    <div style="width:95%; margin:0 auto; padding-left:15px; padding-right:15px;">
        {html_table}
    </div>
    """, unsafe_allow_html=True)
    
    # Добавляем разделитель
    st.markdown("<hr style='margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Добавляем информацию о типе перголы и изображение только один раз в сессии
    if not st.session_state.get('description_shown', False):
        # Устанавливаем флаг, что описание уже было показано в этой сессии
        st.session_state.description_shown = True
        
        # Отображаем информацию о выбранном типе перголы с использованием модуля описаний
        if pergola_type in ["B500NEW", "B700NEW", "B600"]:
            # Используем описание из модуля конфигурации
            description_html = get_pergola_description(pergola_type)
            # Оборачиваем описание в div с уменьшенными отступами
            st.markdown(f"""
            <div style="padding: 0 10px; margin: 0 auto; max-width: 98%;">
                {description_html}
            </div>
            """, unsafe_allow_html=True)
            
            # Отображаем изображения с использованием списка из конфигурации
            images = get_pergola_images(pergola_type)
            caption = get_pergola_image_caption(pergola_type)
            
            if images:
                # Пробуем загрузить изображения по очереди, пока не найдем рабочее
                for img_path in images:
                    try:
                        display_image_with_padding(img_path, caption=caption)
                        break  # Прерываем цикл, если изображение успешно загружено
                    except Exception as e:
                        continue  # Пробуем следующее изображение
                else:
                    st.warning(f"Не удалось загрузить изображение для {pergola_type}")
            
            # Добавляем информацию о масштабируемости для всех типов пергол
            # Отображаем описание модульной системы из модуля конфигурации
            modular_description = get_modular_system_description()
            # Оборачиваем описание в div с уменьшенными отступами
            st.markdown(f"""
            <div style="padding: 0 10px; margin: 0 auto; max-width: 98%;">
                {modular_description}
            </div>
            """, unsafe_allow_html=True)
            
            # Отображаем изображение модульной системы
            modular_images = get_pergola_images("MODULAR")
            modular_caption = get_pergola_image_caption("MODULAR")
            
            if modular_images:
                for img_path in modular_images:
                    try:
                        display_image_with_padding(img_path, caption=modular_caption)
                        break
                    except Exception as e:
                        continue
                else:
                    st.warning(f"Не удалось загрузить изображение модульной системы")
            
            # Добавляем информацию о системе водоотведения для всех типов пергол
            # Отображаем описание системы водоотведения из модуля конфигурации
            drainage_description = get_drainage_system_description()
            # Оборачиваем описание в div с уменьшенными отступами
            st.markdown(f"""
            <div style="padding: 0 10px; margin: 0 auto; max-width: 98%;">
                {drainage_description}
            </div>
            """, unsafe_allow_html=True)
            
            # Отображаем изображение системы водоотведения
            drainage_images = get_pergola_images("DRAINAGE")
            drainage_caption = get_pergola_image_caption("DRAINAGE")
            
            if drainage_images:
                for img_path in drainage_images:
                    try:
                        display_image_with_padding(img_path, caption=drainage_caption)
                        break
                    except Exception as e:
                        continue
                else:
                    st.warning(f"Не удалось загрузить изображение системы водоотведения")
            
            # Добавляем информацию о приводе Bansbach только для пергол B500NEW
            if pergola_type == "B500NEW":
                bansbach_description = get_bansbach_description()
                # Оборачиваем описание в div с уменьшенными отступами
                st.markdown(f"""
                <div style="padding: 0 10px; margin: 0 auto; max-width: 98%;">
                    {bansbach_description}
                </div>
                """, unsafe_allow_html=True)
                
                # Отображаем изображение привода Bansbach
                bansbach_images = get_pergola_images("BANSBACH")
                bansbach_caption = get_pergola_image_caption("BANSBACH")
                
                if bansbach_images:
                    for img_path in bansbach_images:
                        try:
                            display_image_with_padding(img_path, caption=bansbach_caption)
                            break
                        except Exception as e:
                            continue
                    else:
                        st.warning(f"Не удалось загрузить изображение привода Bansbach")
            
            # Добавляем информацию о приводе Somfy только для пергол B700NEW
            if pergola_type == "B700NEW":
                somfy_description = get_pergola_description("SOMFY")
                # Оборачиваем описание в div с уменьшенными отступами
                st.markdown(f"""
                <div style="padding: 0 10px; margin: 0 auto; max-width: 98%;">
                    {somfy_description}
                </div>
                """, unsafe_allow_html=True)
                
                # Отображаем изображение привода Somfy
                somfy_images = get_pergola_images("SOMFY")
                somfy_caption = get_pergola_image_caption("SOMFY")
                
                if somfy_images:
                    for img_path in somfy_images:
                        try:
                            display_image_with_padding(img_path, caption=somfy_caption)
                            break
                        except Exception as e:
                            continue
                    else:
                        st.warning(f"Не удалось загрузить изображение привода Somfy")
            
            # Добавляем описание вариантов установки и вертикальных систем для всех типов пергол
            bioclimatic_install_description_html = """
            <div style='padding: 0 10px; margin-bottom: 0px;'>
            <h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Биоклиматическая пергола: когда установка начинается с проектирования</h3>
            <p style='margin-bottom: 15px; font-style: italic; text-align: center;'>
            (Тонкости монтажа, о которых не расскажет обычный продавец)
            </p>
            
            <div style='margin-bottom: 15px;'>
            <h4 style='font-size: 1.1rem; margin-top: 20px;'>Интеграция перголы в существующую архитектуру: нет ограничений</h4>
            <p style='margin-bottom: 10px;'>Биоклиматическая пергола «растёт» вместе с вашими потребностями и может быть смонтирована четырьмя разными способами:</p>
            
            <ol style='margin-bottom: 10px; padding-left: 20px;'>
                <li><strong>Отдельно стоящая конструкция</strong> идеальна для открытых пространств: летних площадок и террас. Даже без фундамента — на специальных утяжелителях.</li>
                <li><strong>Примыкание к стене</strong> экономит пространство и создаёт плавный переход между домом и садом. Даже для стеклянного фасада найдутся решения.</li>
                <li><strong>Встраивание в проем</strong> создаёт крышу для балконов верхних этажей или защищает окна от перегрева. Можно интегрировать даже в скошенную кровлю.</li>
                <li><strong>Навес в труднодоступной зоне</strong> со специальными решениями высотного монтажа. Бригада промышленных альпинистов справится с любой задачей.</li>
            </ol>
            </div>
            
            <div style='margin-bottom: 15px;'>
            <h4 style='font-size: 1.1rem; margin-top: 20px;'>Климатические системы: пять уровней комфорта</h4>
            <p style='margin-bottom: 10px;'>Пергола уже давно не просто «крыша над головой». Это модульная система с адаптивными опциями:</p>
            
            <ul style='margin-bottom: 10px; padding-left: 20px;'>
                <li><strong>Базовая система:</strong> Ламели, которыми вы управляете по таймеру, датчикам или вручную.</li>
                <li><strong>Дождевая защита:</strong> Встроенные лотки отводят до 80 л/м² осадков, а сама система автоматически закрывается при первых каплях.</li>
                <li><strong>Тепловой контроль:</strong> Светодиодные инфракрасные обогреватели на магнитных креплениях с регулировкой до +50°C.</li>
                <li><strong>Ветрозащита:</strong> ZIP-экраны с тканью Ferrari задерживают до 92% солнечных лучей и выдерживают порывы до 60 км/ч.</li>
                <li><strong>Управление микроклиматом:</strong> Ламели создают эффект Вентури, когда нужно проветрить, не допуская сквозняков.</li>
            </ul>
            </div>
            
            <div style='margin-bottom: 15px;'>
            <h4 style='font-size: 1.1rem; margin-top: 20px;'>Автоматика: технологии, которые работают за вас</h4>
            <p style='margin-bottom: 10px;'>Для управления перголой не нужны инструкции толщиной с роман:</p>
            
            <ul style='margin-bottom: 10px; padding-left: 20px;'>
                <li>Единый пульт Somfy или Simu управляет всеми элементами: от ламелей до света.</li>
                <li>Датчики дождя, ветра, снега и температуры автоматически адаптируют пергольную систему к погоде.</li>
                <li>Умный дом: интеграция с Apple HomeKit, Google Home, Яндекс и даже с Алисой.</li>
                <li>Европейская надежность: Автоматика Bansbach и Somfy (до 50 000 циклов!) работают даже в экстремальных условиях.</li>
            </ul>
            </div>
            
            <p style='margin-bottom: 15px; font-weight: bold;'>Вы готовы выйти за рамки стандартов? Биоклиматическая пергола — это не «навес», а ваш личный климатический контролер. Оставьте заявку, и наши инженеры создадут проект, где каждая деталь будет работать на ваш комфорт.</p>
            </div>
            """
            st.markdown(bioclimatic_install_description_html, unsafe_allow_html=True)
            
            # Отображаем изображение вариантов установки
            install_system_images = get_pergola_images("INSTALL_SYSTEM")
            install_system_caption = get_pergola_image_caption("INSTALL_SYSTEM")
            
            if install_system_images:
                for img_path in install_system_images:
                    try:
                        st.image(img_path, caption=install_system_caption, use_container_width=True)
                        break
                    except Exception as e:
                        continue
                else:
                    st.warning(f"Не удалось загрузить изображение вариантов установки")
            
            # Добавляем техническое описание ламелей только для пергол B500 и B700, не для B600
            if pergola_type in ["B500NEW", "B700NEW"]:
                lamella_engineering_description_html = """
                <div style='padding: 0 10px; margin-bottom: 0px;'>
                <h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Инженерный взгляд на биоклиматические перголы: как ламели выдерживают снег, ливни и сохраняют тепло</h3>
                <p style='margin-bottom: 15px; font-style: italic; text-align: center;'>
                (Технические секреты, которые делают ваш комфорт непогрешимым)
                </p>
                
                <div style='margin-bottom: 15px;'>
                <h4 style='font-size: 1.1rem; margin-top: 20px;'>Прогиб ламелей: где точность встречает надежность</h4>
                <p style='margin-bottom: 10px;'>Ламели — это «скелет» перголы, и их прочность определяет, как конструкция поведет себя под нагрузками. Мы протестировали каждую модель в экстремальных условиях. Вот что важно знать:</p>
                
                <p style='margin-bottom: 10px;'><strong>Ламель 250×53 NEW</strong></p>
                <ul style='margin-bottom: 10px; padding-left: 20px;'>
                    <li>Масса: 4,684 кг/м | Шаг: 250 мм</li>
                    <li>Прогиб под нагрузкой:
                        <ul style='padding-left: 20px;'>
                            <li>Рабочая (масса ламели + 50%): 12 мм при ширине 4,5 м.</li>
                            <li>Снеговая (50 кг/м²): 30 мм при ширине 4,5 м.</li>
                        </ul>
                    </li>
                    <li>Макс. снеговая нагрузка: 50 кг/м² (эквивалент 40-50 см свежего снега).</li>
                </ul>
                
                <p style='margin-bottom: 10px;'><strong>Ламель 200×56 NEW</strong></p>
                <ul style='margin-bottom: 10px; padding-left: 20px;'>
                    <li>Масса: 4,375 кг/м | Шаг: 200 мм</li>
                    <li>Прогиб под нагрузкой:
                        <ul style='padding-left: 20px;'>
                            <li>Рабочая: 10 мм при ширине 5,0 м.</li>
                            <li>Снеговая: 22 мм при ширине 5,0 м.</li>
                        </ul>
                    </li>
                    <li>Макс. снеговая нагрузка: 70 кг/м² (до 60 см снега).</li>
                </ul>
                
                <p style='margin-bottom: 10px;'>Почему это важно? Минимальный прогиб сохраняет геометрию крыши даже в экстремальных условиях. Для сравнения: у конкурентов аналогичные ламели прогибаются на 50-70 мм под теми же нагрузками.</p>
                </div>
                
                <div style='margin-bottom: 15px;'>
                <h4 style='font-size: 1.1rem; margin-top: 20px;'>Герметичность: когда внутри сухо, даже если снаружи потоп</h4>
                <p style='margin-bottom: 10px;'>Алюминиевые ламели перголы — это не просто «крыша», а герметичный кокон. Вот как мы этого добиваемся:</p>
                <ol style='margin-bottom: 10px; padding-left: 20px;'>
                    <li><strong>Двойное уплотнение EPDM:</strong>
                        <ul style='padding-left: 20px;'>
                            <li>Уплотнители между ламелями и в лотках выдерживают давление водяного столба до 600 Па (ливень интенсивностью 100 мм/час).</li>
                            <li>Для сравнения: стандартные системы держат только 300-400 Па.</li>
                        </ul>
                    </li>
                    <li><strong>Наклон ламелей + дренажные каналы:</strong> Вода стекает в лотки, не задерживаясь на поверхности. Даже при сильном ветре капли не просачиваются через стыки.</li>
                    <li><strong>Тест на герметичность:</strong> Мы заливаем крышу перголы водой под давлением 600 Па в течение 1 часа. Результат: 0 протечек.</li>
                </ol>
                </div>
                
                <div style='margin-bottom: 15px;'>
                <h4 style='font-size: 1.1rem; margin-top: 20px;'>Теплоизоляция: почему под перголой тепло зимой и прохладно летом</h4>
                <ul style='margin-bottom: 10px; padding-left: 20px;'>
                    <li><strong>Терморазрыв в профиле:</strong> Алюминиевые ламели с изолирующими вставками из нейлона снижают теплопотери на 40%.</li>
                    <li><strong>Эффект «воздушной подушки»:</strong> При закрытых ламелях между ними образуется прослойка воздуха, которая работает как естественный изолятор.</li>
                    <li><strong>Температурный комфорт:</strong>
                        <ul style='padding-left: 20px;'>
                            <li>Зимой: под перголой на 5-7°C теплее, чем снаружи.</li>
                            <li>Летом: на 10-12°C прохладнее благодаря тени и вентиляции.</li>
                        </ul>
                    </li>
                </ul>
                </div>
                
                <div style='margin-bottom: 15px;'>
                <h4 style='font-size: 1.1rem; margin-top: 20px;'>Сравнительная таблица: какая ламель подходит вам?</h4>
                <table style='width: 100%; border-collapse: collapse; margin-bottom: 15px;'>
                    <tr>
                        <th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Параметр</th>
                        <th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Ламель 250×53 NEW</th>
                        <th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Ламель 200×56 NEW</th>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Снеговая нагрузка</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>50 кг/м²</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>70 кг/м²</td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Прогиб под снегом</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>30 мм (4,5 м)</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>22 мм (5,0 м)</td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Шаг ламелей</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>250 мм</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>200 мм (плотнее защита)</td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Ветровая стойкость</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>До 25 м/с</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>До 30 м/с</td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Идеальный сценарий</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Умеренный климат</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>Северные регионы</td>
                    </tr>
                </table>
                </div>
                
                <div style='margin-bottom: 15px;'>
                <h4 style='font-size: 1.1rem; margin-top: 20px;'>Почему это выгодно?</h4>
                <ul style='margin-bottom: 10px; padding-left: 20px;'>
                    <li><strong>Экономия на отоплении/кондиционировании:</strong> Терморазрыв и герметичность снижают затраты на энергию.</li>
                    <li><strong>Гарантия 10 лет:</strong> На ламели и уплотнители — потому что мы уверены в каждом миллиметре.</li>
                    <li><strong>Адаптивность:</strong> Комбинируйте ламели с остеклением или ZIP-экранами для полного контроля над климатом.</li>
                </ul>
                </div>
                
                <p style='margin-bottom: 15px; font-weight: bold;'>Финал: Биоклиматическая пергола — это не «навес», а инженерная система, которая считает каждую каплю дождя и снежинку. Выбирайте ламели, которые работают как швейцарские часы — тихо, точно, без компромиссов.</p>
                </div>
                """
                st.markdown(lamella_engineering_description_html, unsafe_allow_html=True)
                
                # Отображаем изображение технических характеристик ламелей
                lamella_engineering_images = get_pergola_images("LAMELLA_ENGINEERING")
                lamella_engineering_caption = get_pergola_image_caption("LAMELLA_ENGINEERING")
                
                if lamella_engineering_images:
                    for img_path in lamella_engineering_images:
                        try:
                            st.image(img_path, caption=lamella_engineering_caption, use_container_width=True)
                            break
                        except Exception as e:
                            continue
                    else:
                        st.warning(f"Не удалось загрузить изображение технических характеристик ламелей")

def display_image_with_padding(image_path, caption=None, padding_percent=5):
    """
    Отображает изображение с отступами по краям и подписью.
    
    Args:
        image_path (str): Путь к изображению
        caption (str, optional): Подпись к изображению
        padding_percent (int, optional): Процент отступа от ширины контейнера (по умолчанию 5%)
    """
    # Создаем контейнер с отступами для изображения
    st.markdown(f"""
    <style>
    .image-container {{
        padding-left: {padding_percent}%;
        padding-right: {padding_percent}%;
        margin-bottom: 20px;
    }}
    </style>
    <div class="image-container"></div>
    """, unsafe_allow_html=True)
    
    # Отображаем изображение внутри контейнера с отступами
    st.image(image_path, caption=caption, use_container_width=True)

def scroll_to_results():
    """
    Добавляет JavaScript для перехода к якорю результатов при нажатии на скрытую кнопку
    """
    # Добавляем JavaScript для автоматического нажатия на ссылку-якорь
    st.markdown("""
    <script>
        // Используем URL-хэш для скролла
        function scrollToResults() {
            console.log('Attempting to scroll to results...');
            
            // Ищем элемент с id="results"
            const resultsElement = document.getElementById('results');
            
            if (resultsElement) {
                console.log('Found results element, scrolling...');
                
                // Программно создаем и кликаем по ссылке на якорь
                const scrollLink = document.createElement('a');
                scrollLink.href = '#results';
                scrollLink.style.display = 'none';
                document.body.appendChild(scrollLink);
                
                // Прокручиваем с задержкой для надежности
                setTimeout(() => {
                    scrollLink.click();
                    console.log('Clicked on results anchor link');
                    
                    // Удаляем ссылку после использования
                    setTimeout(() => {
                        document.body.removeChild(scrollLink);
                    }, 100);
                }, 500);
                
                return true;
            }
            
            console.log('Results element not found');
            
            // Если якорь не найден, ищем заголовок или просто скроллим вниз
            const resultsHeadings = Array.from(document.querySelectorAll('h2'))
                .filter(h => h.textContent.includes('Результаты расчета'));
            
            if (resultsHeadings.length > 0) {
                console.log('Found results heading, scrolling...');
                const heading = resultsHeadings[0];
                window.scrollTo({
                    top: heading.offsetTop - 80,
                    behavior: 'smooth'
                });
                return true;
            }
            
            // Крайний случай - просто скроллим на определенное расстояние вниз
            console.log('No targets found, scrolling down as fallback');
            window.scrollTo({
                top: document.body.scrollHeight / 2,  // Примерно в середину страницы
                behavior: 'smooth'
            });
            
            return false;
        }
        
        // Выполняем скролл после загрузки DOM
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM fully loaded, scheduling scroll');
            setTimeout(scrollToResults, 300);
        });
        
        // Также выполняем скролл сразу (для случая, когда DOM уже загружен)
        console.log('Script loaded, scheduling immediate scroll');
        setTimeout(scrollToResults, 500);
        
        // И выполняем третью попытку для надежности
        setTimeout(scrollToResults, 1500);
    </script>
    """, unsafe_allow_html=True)

def main():
    """Основная функция приложения"""
    # Настраиваем страницу
    st.set_page_config(
        page_title="Калькулятор пергол DecoLife",
        page_icon="🏠",
        layout="centered"  # Изменено с "wide" на "centered" для более узкого интерфейса
    )
    
    # Задаем стили для компактного и читаемого интерфейса по новому дизайну
    st.markdown("""
    <style>
    /* Глобальный контейнер */
    .block-container {
        max-width: 800px;
        padding-top: 1rem;
        padding-bottom: 1rem;
        margin: 0 auto;
    }
    
    /* Применяем отступы ко ВСЕМ формам ввода */
    div.stNumberInput, div.stTextInput, div.stSelectbox, div.stRadio, 
    div.stCheckbox, div.stSlider, div.stButton, div.stMultiselect {
        width: 90% !important;
        margin: 0 auto !important;
        padding-left: 25px !important;
        padding-right: 25px !important;
    }
    
    /* Отступы для секций заголовков */
    div.stMarkdown h2 {
        width: 90% !important;
        margin: 0 auto !important;
        padding-left: 25px !important;
        padding-right: 25px !important;
    }
    
    /* Отступы для текстовых параграфов */
    div.stMarkdown p {
        width: 90% !important;
        margin: 0 auto !important;
        padding-left: 25px !important;
        padding-right: 25px !important;
    }
    
    /* Отступы для горизонтальных разделителей */
    div.stMarkdown hr {
        width: 90% !important;
        margin: 0 auto !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* Глобальные стили для улучшения читаемости */
    .stApp, .stApp p, .stApp div {
        font-size: 1rem;
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Заголовки секций */
    .section-header {
        font-size: 1.2rem;
        font-weight: 500;
        color: #333;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
    }
    
    /* Таблицы */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1rem;
    }
    
    th, td {
        padding: 8px 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    
    th {
        background-color: #f8f9fa;
        font-weight: 600;
    }
    
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        .block-container {
            max-width: 100%;
            padding: 0.25rem !important;
        }
        
        /* Уменьшаем отступы на мобильных */
        div.stNumberInput, div.stTextInput, div.stSelectbox, div.stRadio, 
        div.stCheckbox, div.stSlider, div.stButton, div.stMultiselect,
        div.stMarkdown h2, div.stMarkdown p, div.stMarkdown hr {
            width: 95% !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
        
        .stButton {
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
        
        /* Убираем горизонтальный скролл на мобильных */
        div[data-testid="stTable"],
        div[data-testid="stDataFrame"] {
            width: 100% !important;
            overflow-x: hidden !important;
        }
        
        /* Уменьшаем размер шрифта в элементах форм */
        .stSelectbox, .stRadio, .stCheckbox {
            font-size: 0.85rem !important;
        }
        
        /* Уменьшаем размер текста везде */
        .stApp, .stApp p, .stApp div, .stMarkdown {
            font-size: 0.9rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок калькулятора - крупный и четкий
    st.markdown("<h1 style='text-align: center; margin-top: 20px; margin-bottom: 10px; font-size: 1.8rem; font-weight: 600; color: #0066cc;'>Калькулятор стоимости перголы</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 20px; font-size: 1rem;'>Введите размеры и параметры перголы для расчета стоимости в рублях (₽)</p>", unsafe_allow_html=True)
    
    # Получаем размеры перголы
    dimensions = render_dimensions_form()
    
    # Сохраняем размеры в session_state
    st.session_state.dimensions = dimensions
    
    # Получаем опции перголы
    options = render_options_form()
    
    # Кнопка для расчета с улучшенным стилем
    if st.button("Рассчитать стоимость", type="primary", use_container_width=True):
        with st.spinner("Выполняется расчет..."):
            # Проверяем, что у нас есть данные для расчета
            if dimensions and options:
                # Выполняем расчет
                results = perform_calculation(dimensions, options)
                
                # Сохраняем результаты и опции в состоянии сессии
                st.session_state.results = results
                st.session_state.options = options
                
                # Добавляем флаг, что нужно прокрутить к результатам
                st.session_state.scroll_to_results = True
                
                # Сбрасываем флаг описания, чтобы оно обновлялось при каждом новом расчете
                st.session_state.description_shown = False
                
                # Перезагружаем страницу для отображения результатов
                st.rerun()
    
    # Добавляем разделитель (компактный)
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.5rem; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
    
    # Режим отладки отключен
    st.session_state.debug_mode = False
        
    # Отображаем кнопку для скролла к результатам (если есть результаты)
    if 'results' in st.session_state:
        # Кнопка для скролла к результатам (компактная и заметная)
        st.markdown("""
        <a href="#results" style="display: block; width: 90%; margin: 10px auto; padding: 10px; 
                       background-color: #0066cc; color: white; text-align: center; 
                       border-radius: 5px; text-decoration: none; font-weight: bold;">
           ↓ Перейти к результатам расчета ↓
        </a>
        """, unsafe_allow_html=True)
        
        # Показываем общий результат и детальную информацию
        render_results(st.session_state.results)
        
        # Если нужна прокрутка к результатам, добавляем JS код
        if st.session_state.get('scroll_to_results', False):
            scroll_to_results()
            # Сбрасываем флаг, чтобы не добавлять скрипт при каждом обновлении
            st.session_state.scroll_to_results = False
    
    # Добавляем информацию о версии внизу страницы (компактно)
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.3rem; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #999;'>© 2025 Комфортный дом | Калькулятор пергол v3.5</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    # Создаем директории, если они не существуют
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/price_tables", exist_ok=True)
    
    # Запускаем приложение
    main()