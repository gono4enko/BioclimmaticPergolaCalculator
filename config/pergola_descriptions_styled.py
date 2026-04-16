"""
Модуль с описаниями пергол различных типов.
Отделяем описания от основного кода для облегчения будущих модификаций.
Применен единый стиль оформления для всех типов пергол.
"""

# Инициализация словаря описаний
PERGOLA_DESCRIPTIONS = {}

# Описание перголы B500NEW
B500_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Серия B500NEW (с поворотными ламелями)</h3>
<p style='margin-bottom: 15px;'>
Пергола с поворотными ламелями, вращающимися вокруг нижней оси. Идеальна для зон отдыха, террас и уличных площадок.
</p>

<section style='margin-bottom: 15px;'>
<strong>Ламели:</strong><br/>
250x53 мм (NEW): Угол поворота 105°, шаг 250 мм, масса 4,684 кг/м.<br/>
200x56 мм (NEW): Угол поворота 112°, шаг 200 мм, масса 4,375 кг/м.
</section>

<section style='margin-bottom: 15px;'>
<strong>Преимущества:</strong><br/>
• Высокая герметичность благодаря двойному уплотнению.<br/>
• Интегрированная дренажная система с лотком 164x280 мм.<br/>
• Быстрый монтаж (до 4 часов на модуль).<br/>
• LED/RGB подсветка по периметру (опция).<br/>
• Максимальный пролет до 8 м.
</section>

<section style='margin-bottom: 15px;'>
<strong>Узлы:</strong><br/>
• Несущая балка: Алюминиевая конструкция с двойным сливным лотком (322x280 мм).<br/>
• Колонна: 164x164 мм, усиленная 7 анкерами для устойчивости.<br/>
• Система вращения: Немецкий двигатель Bansbach easylift (IP65), синхронизация TANDEM для больших конструкций.
</section>
"""

# Описание перголы B700NEW
B700_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Серия B700NEW (со сдвижными ламелями)</h3>
<p style='margin-bottom: 15px;'>
Пергола с ламелями, сдвигающимися в горизонтальной плоскости. Идеальна для больших пространств и экстремальных ветровых нагрузок.
</p>

<section style='margin-bottom: 15px;'>
<strong>Ламели:</strong><br/>
250x46 мм: Сдвиг с углом 107°, шаг 250 мм, масса 4,144 кг/м.<br/>
200x56 мм (NEW): Сдвиг с углом 107°, шаг 200 мм, масса 4,375 кг/м.
</section>

<section style='margin-bottom: 15px;'>
<strong>Преимущества:</strong><br/>
• Высокая ветровая устойчивость (до 50 кг/м² снеговой нагрузки).<br/>
• Французские двигатели Somfy с защитой IP65.<br/>
• Возможность интеграции с панорамным остеклением.
</section>

<section style='margin-bottom: 15px;'>
<strong>Узлы:</strong><br/>
• Несущая балка: Двойной лоток 322x280 мм для отвода воды.<br/>
• Колонна: Усиленная конструкция с дренажными отверстиями.<br/>
• Система сдвига: Замок Roof-Lock для герметичности.
</section>
"""

# Описание перголы B600
B600_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Серия B600 (с сэндвич-панелями PIR)</h3>
<p style='margin-bottom: 15px;'>
Пергола с неподвижными сэндвич-панелями PIR. Оптимальна для северных регионов с высокими снеговыми нагрузками.
</p>

<section style='margin-bottom: 15px;'>
<strong>Характеристики:</strong><br/>
• Панели PIR: Толщина 100 мм, замок Rolf-Lock, RAL 9003/7024.<br/>
• Максимальный пролет: До 8 м.
</section>

<section style='margin-bottom: 15px;'>
<strong>Преимущества:</strong><br/>
• Снеговая нагрузка до 100 кг/м².<br/>
• Термоизоляция и защита от шума.<br/>
• Экологичность и устойчивость к УФ-излучению.
</section>

<section style='margin-bottom: 15px;'>
<strong>Узлы:</strong><br/>
• Сэндвич-панели: Трехслойная конструкция с пенополиизоциануратом.<br/>
• Колонна: 164x164 мм с жестким креплением.<br/>
• Дренаж: Интегрированный лоток по периметру.
</section>
"""

# Описание модульной системы - для всех типов пергол
MODULAR_SYSTEM_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Масштабируемость пергол: модульная система без границ</h3>
<p style='margin-bottom: 15px;'>
Благодаря модульной конструкции перголы серий B500NEW, B700NEW и B600 можно объединять в любых направлениях, создавая конструкции практически неограниченной длины и ширины.
</p>

<section style='margin-bottom: 15px;'>
<strong>Ключевые особенности:</strong><br/>
• Общие колонны на стыке модулей: При соединении 2-4 модулей используется одна усиленная колонна.<br/>
• Простота монтажа: Конструкции поставляются в готовых сборочных узлах.<br/>
• Интеграция разных элементов: Возможно комбинирование разных типов пергол в рамках одной системы.<br/>
• Сохранение характеристик: Герметичность и нагрузочная способность остаются неизменными.
</section>

<section style='margin-bottom: 15px;'>
<strong>Примеры применения:</strong><br/>
• Большие открытые террасы ресторанов.<br/>
• Крытые переходы между зданиями.<br/>
• Частные дворы с зонами отдыха и бассейнами.
</section>
"""

# Словарь с путями к изображениям
PERGOLA_IMAGES = {
    "B500NEW": [
        "attached_assets/IMG_1001.jpeg",
        "attached_assets/b500_rotation.png",
        "attached_assets/Снимок экрана 2025-04-09 в 13.57.24.png"
    ],
    "B700NEW": [
        "attached_assets/IMG_1002.jpeg",
        "attached_assets/b700_sliding.png",
        "attached_assets/Снимок экрана 2025-04-09 в 13.51.02.png"
    ],
    "B600": [
        "attached_assets/IMG_1003.png",
        "attached_assets/b600_sandwich.png",
        "attached_assets/Снимок экрана 2025-04-09 в 13.39.51.png"
    ],
    "MODULAR": [
        "attached_assets/Модульная система пергол.jpeg"
    ],
    "DRAINAGE": [
        "attached_assets/Система водоотведения.jpeg",
        "attached_assets/Снимок экрана 2025-04-09 в 18.55.21.png"
    ],
    "INSTALL_SYSTEM": [
        "attached_assets/install_design_system.png",
        "attached_assets/Instal and design Sistem.png"
    ],
    "LAMELLA_ENGINEERING": [
        "attached_assets/aluminum_slats.png",
        "attached_assets/aluminum slats.png"
    ],
    "BANSBACH": [
        "attached_assets/Lin gate.jpg",
        "attached_assets/Линейный привод.jpeg"
    ],
    "SOMFY": [
        "attached_assets/Somfy Pergola.jpeg"
    ]
}

# Подписи к изображениям
PERGOLA_IMAGE_CAPTIONS = {
    "B500NEW": "Пергола B500 с поворотными ламелями",
    "B700NEW": "Пергола B700 со сдвижными ламелями",
    "B600": "Пергола B600 с PIR-панелями",
    "MODULAR": "Принцип модульной системы пергол",
    "INSTALL_SYSTEM": "Система установки и проектирования пергол",
    "LAMELLA_ENGINEERING": "Технические характеристики ламелей",
    "DRAINAGE": "Система водоотведения Decolife", 
    "BANSBACH": "Линейный привод Bansbach для пергол В500",
    "SOMFY": "Автоматика Somfy для пергол B700"
}

# Описание привода Bansbach
BANSBACH_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Bansbach: Автоматика для перголы B500</h3>
<p style='margin-bottom: 15px;'>
Двигатели Bansbach созданы для экстремальных нагрузок с крутящим моментом 4500 Нм. Идеальное решение для управления поворотными ламелями в любых погодных условиях.
</p>

<section style='margin-bottom: 15px;'>
<strong>Характеристики:</strong><br/>
• Мощность: 4500 Нм крутящего момента.<br/>
• Ресурс: 100 000 циклов открытия/закрытия.<br/>
• Класс защиты: IP65 (пыле- и влагозащита).
</section>

<section style='margin-bottom: 15px;'>
<strong>Управление:</strong><br/>
• Дистанционное: Пульт, смартфон или голосовой помощник.<br/>
• Умная защита: Автоматическое закрытие при дожде через климатические датчики.<br/>
• Синхронизация TANDEM: Для больших пергол (от 8 м) используются два синхронизированных двигателя.
</section>

<section style='margin-bottom: 15px;'>
<strong>Преимущества:</strong><br/>
• Сделано в Германии: Точность и надежность.<br/>
• Работа при температурах от -30°C до +70°C.<br/>
• Низкий уровень шума: 45 дБ.<br/>
• Гарантия 5 лет от производителя.
</section>
"""

# Описание привода Somfy для перголы B700NEW
SOMFY_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Somfy: Французский интеллект для перголы B700</h3>
<p style='margin-bottom: 15px;'>
Привод Somfy J4 io разработан специально для горизонтальных конструкций. Обеспечивает плавное скольжение ламелей даже при больших размерах перголы.
</p>

<section style='margin-bottom: 15px;'>
<strong>Характеристики:</strong><br/>
• Крутящий момент: 6 Нм с плавным стартом/остановкой.<br/>
• Ресурс: Более 10 000 полных циклов открытия/закрытия.<br/>
• Уровень шума: Менее 38 дБ (тише, чем шепот).<br/>
• Защита: IP 54, работа от -20°C до +60°C.
</section>

<section style='margin-bottom: 15px;'>
<strong>Smart-управление:</strong><br/>
• Технология io-homecontrol с обратной связью.<br/>
• Интеграция с Amazon Alexa, Google Home, Apple HomeKit.<br/>
• Метеостанция TaHoma: автоматическая реакция на погодные условия.<br/>
• Потребление в режиме ожидания: менее 0,5 Вт.
</section>

<section style='margin-bottom: 15px;'>
<strong>Дополнительно:</strong><br/>
• Самодиагностика привода через приложение.<br/>
• Ручное управление при отключении электричества.<br/>
• Идеально подходит для технофилов и владельцев умных домов.
</section>
"""

# Описание инженерных характеристик ламелей
LAMELLA_ENGINEERING_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Инженерный взгляд на биоклиматические перголы</h3>
<p style='margin-bottom: 15px;'>
Технические характеристики ламелей определяют надежность перголы при снеговых нагрузках, ливнях и экстремальных температурах.
</p>

<section style='margin-bottom: 15px;'>
<strong>Прочность и надежность:</strong><br/>
• Ламель 250×53 NEW: Масса 4,684 кг/м, шаг 250 мм, прогиб 30 мм при снеговой нагрузке 50 кг/м².<br/>
• Ламель 200×56 NEW: Масса 4,375 кг/м, шаг 200 мм, прогиб 22 мм при снеговой нагрузке 70 кг/м².<br/>
• Минимальный прогиб сохраняет геометрию крыши даже в экстремальных условиях.
</section>

<section style='margin-bottom: 15px;'>
<strong>Герметичность:</strong><br/>
• Двойное уплотнение EPDM выдерживает давление водяного столба до 600 Па.<br/>
• Интеллектуальная геометрия ламелей направляет воду в дренажные каналы.<br/>
• Наклон ламелей + специальные лотки обеспечивают защиту даже при сильном ветре.
</section>

<section style='margin-bottom: 15px;'>
<strong>Теплоизоляция:</strong><br/>
• B500/B700: Теплопередача 2,1 Вт/(м²·К), летом под перголой на 8-10°C прохладнее.<br/>
• B600 (PIR-панели): Теплопередача 0,54 Вт/(м²·К), разница с внешней средой 15-20°C.<br/>
• Звукоизоляция: до 25 дБ для B500/B700, до 32 дБ для B600.
</section>
"""

# Описание системы водоотведения
DRAINAGE_SYSTEM_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Интегрированная система водоотведения</h3>
<p style='margin-bottom: 15px;'>
Водосточный лоток встроен прямо в несущую балку перголы без дополнительных внешних элементов, обеспечивая эстетичность и функциональность.
</p>

<section style='margin-bottom: 15px;'>
<strong>Варианты исполнения:</strong><br/>
• Стандартный лоток 164×280 мм: Пропускная способность 15 л/с (для большинства регионов).<br/>
• Усиленный лоток 322×280 мм: Пропускная способность 30 л/с (для тропических ливней).<br/>
• Материал: Анодированный алюминий толщиной 3 мм с ребрами жесткости.
</section>

<section style='margin-bottom: 15px;'>
<strong>Колонны:</strong><br/>
• Сечение: 164×164 мм для оптимального отвода воды.<br/>
• Скрытый дренаж: Вода уходит через внутренний канал колонны.<br/>
• Крепление: 7 усиленных анкеров с EPDM-уплотнителями.
</section>

<section style='margin-bottom: 15px;'>
<strong>Преимущества:</strong><br/>
• Справляется с осадками интенсивностью до 50 мм/час.<br/>
• Алюминиевые лотки снижают шум дождя на 40%.<br/>
• Уплотнители EPDM служат более 15 лет без деформаций.<br/>
• Модульная конструкция позволяет масштабировать систему.
</section>
"""

# Описание монтажа биоклиматических пергол
BIOCLIMATIC_INSTALL_DESCRIPTION = """
<h3 style='font-size: 1.2rem; margin-top: 20px; text-align: center;'>Варианты установки биоклиматических пергол</h3>
<p style='margin-bottom: 15px;'>
Перголы адаптируются под любые архитектурные решения и могут быть установлены различными способами в зависимости от потребностей.
</p>

<section style='margin-bottom: 15px;'>
<strong>Типы установки:</strong><br/>
• Отдельностоящая: Идеальна для садов, бассейнов, открытых террас.<br/>
• Пристенная: Продлевает жилое пространство дома, заменяя обычный козырек.<br/>
• Встроенная: Интегрируется в архитектуру здания как его неотъемлемая часть.
</section>

<section style='margin-bottom: 15px;'>
<strong>Процесс монтажа:</strong><br/>
• Время установки: От 1 дня для стандартного модуля.<br/>
• Точечное крепление: Минимальные земляные работы без масштабного фундамента.<br/>
• Предварительная сборка: До 80% узлов собирается на производстве.<br/>
• Подробная документация с 3D-визуализацией всех этапов монтажа.
</section>

<section style='margin-bottom: 15px;'>
<strong>Дополнительные системы:</strong><br/>
• Инфракрасные обогреватели в несущих балках.<br/>
• LED-освещение в ламелях и по периметру.<br/>
• Всепогодные аудиосистемы в колоннах.<br/>
• Моторизованные москитные сетки или шторы ZIP-screen.
</section>
"""

# Заполняем словарь описаний пергол
PERGOLA_DESCRIPTIONS.update({
    "B500NEW": B500_DESCRIPTION,
    "B700NEW": B700_DESCRIPTION,
    "B600": B600_DESCRIPTION,
    "SOMFY": SOMFY_DESCRIPTION
})

def get_pergola_description(pergola_type):
    """
    Возвращает описание перголы по ее типу
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600, SOMFY)
        
    Returns:
        str: HTML-описание перголы
    """
    if pergola_type in PERGOLA_DESCRIPTIONS:
        return PERGOLA_DESCRIPTIONS[pergola_type]
    else:
        return "<p>Описание для данного типа перголы отсутствует.</p>"

def get_modular_system_description():
    """
    Возвращает описание модульной системы (для всех типов пергол)
    
    Returns:
        str: HTML-описание модульной системы
    """
    return MODULAR_SYSTEM_DESCRIPTION

def get_drainage_system_description():
    """
    Возвращает описание системы водоотведения (для всех типов пергол)
    
    Returns:
        str: HTML-описание системы водоотведения
    """
    return DRAINAGE_SYSTEM_DESCRIPTION

def get_bansbach_description():
    """
    Возвращает описание привода Bansbach (только для пергол B500)
    
    Returns:
        str: HTML-описание привода Bansbach
    """
    return BANSBACH_DESCRIPTION

def get_pergola_images(pergola_type):
    """
    Возвращает список изображений для перголы указанного типа
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600) или "MODULAR"
        
    Returns:
        list: Список путей к изображениям
    """
    return PERGOLA_IMAGES.get(pergola_type, [])

def get_pergola_image_caption(pergola_type):
    """
    Возвращает подпись к изображению перголы указанного типа
    
    Args:
        pergola_type (str): Тип перголы (B500NEW, B700NEW, B600) или "MODULAR"
        
    Returns:
        str: Подпись к изображению
    """
    return PERGOLA_IMAGE_CAPTIONS.get(pergola_type, "Пергола")
    
def get_bioclimatic_install_description():
    """
    Возвращает описание монтажа биоклиматических пергол
    
    Returns:
        str: HTML-описание системы монтажа
    """
    return BIOCLIMATIC_INSTALL_DESCRIPTION

def get_lamella_engineering_description(pergola_type=None):
    """
    Возвращает техническое описание ламелей для различных типов пергол
    
    Args:
        pergola_type (str, optional): Тип перголы (B500NEW, B700NEW, B600)
        
    Returns:
        str: HTML-описание технических характеристик ламелей
    """
    return LAMELLA_ENGINEERING_DESCRIPTION

def get_somfy_description():
    """
    Возвращает описание привода Somfy (только для пергол B700)
    
    Returns:
        str: HTML-описание привода Somfy
    """
    return SOMFY_DESCRIPTION