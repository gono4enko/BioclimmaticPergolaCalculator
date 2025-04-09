"""
Модуль для генерации коммерческого предложения в формате PDF
на основе данных из калькулятора перголы.
Использует библиотеку FPDF для корректной работы с кириллицей.
"""
import os
import io
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# Создаем директорию для сохранения сгенерированных PDF
os.makedirs("generated_pdf", exist_ok=True)

# Создаем директорию для обработанных изображений
os.makedirs("processed_images", exist_ok=True)

class PDF(FPDF):
    """
    Расширенный класс FPDF с поддержкой кириллицы и дополнительными функциями
    """
    def __init__(self):
        # Используем конкретные значения из перечисления литералов
        super().__init__(orientation='P', unit='mm', format='A4')
        
        # Устанавливаем мета-информацию PDF (только латиница)
        self.set_title("Kommercheskoe Predlozhenie")
        self.set_author("Pergola Calculator")
        self.set_creator("Pergola Calculator")
        
        # Устанавливаем отступы
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(True, margin=20)
        
        # Добавляем шрифт с поддержкой кириллицы
        # Проверяем наличие файла шрифта
        # В Replit используем копирование вместо символьных ссылок
        # и добавляем отладочную информацию
        print("Проверка наличия шрифтов:")
        print(f"DejaVuSans.ttf: {os.path.exists('fonts/DejaVuSans.ttf')}")
        print(f"DejaVuSans-Bold.ttf: {os.path.exists('fonts/DejaVuSans-Bold.ttf')}")
        print(f"DejaVuSansCondensed.ttf: {os.path.exists('fonts/DejaVuSansCondensed.ttf')}")
        
        # Добавляем шрифты с поддержкой кириллицы
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        
        # Устанавливаем шрифт по умолчанию
        self.set_font('DejaVu', '', 12)
        
        # Счетчик страниц для колонтитула
        self.page_count = 0
        
    def header(self):
        """Создает верхний колонтитул на каждой странице"""
        self.page_count += 1
        # Добавляем синюю плашку с текстом
        self.set_fill_color(63, 109, 170)  # Синий цвет #3f6daa
        self.set_text_color(255, 255, 255)  # Белый текст
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 15, "Компания «Комфортный дом»", 0, 1, "C", fill=True)
        
        # Номер страницы
        self.set_text_color(0, 0, 0)  # Черный текст
        self.set_font("DejaVu", "", 10)
        self.cell(0, 5, f"{self.page_count} из 4", 0, 1, "L")
        
    def footer(self):
        """Создает нижний колонтитул на каждой странице"""
        self.set_y(-15)  # 15 мм от нижнего края
        self.set_font("DejaVu", "", 8)
        self.set_text_color(128, 128, 128)  # Серый текст
        self.cell(0, 10, "© 2025 Комфортный дом | Все права защищены", 0, 0, "C")
        
    def chapter_title(self, title):
        """Добавляет заголовок раздела"""
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(0, 0, 0)  # Черный текст
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(1)  # Небольшой отступ после заголовка
        
    def check_table_fit(self, rows_count, row_height=8):
        """
        Проверяет, поместится ли таблица на текущей странице
        Если не поместится - добавляет новую страницу
        
        Args:
            rows_count (int): Количество строк в таблице
            row_height (int): Высота одной строки в мм
            
        Returns:
            bool: True если таблица помещается, False если добавлена новая страница
        """
        # Получаем текущую позицию Y
        current_y = self.get_y()
        
        # Рассчитываем необходимую высоту
        table_height = rows_count * row_height
        
        # Проверяем, поместится ли таблица
        if current_y + table_height > self.page_break_trigger:
            self.add_page()
            return False
        return True
    
    def table_header(self, headers, widths):
        """Создает заголовок таблицы"""
        self.set_fill_color(173, 216, 230)  # Светло-голубой цвет
        self.set_text_color(0, 0, 0)  # Черный текст
        self.set_font("DejaVu", "B", 10)
        for i, header in enumerate(headers):
            self.cell(widths[i], 8, header, 1, 0, "C", fill=True)
        self.ln()
        
    def table_row(self, data, widths, aligns=None, row_height=7):
        """
        Добавляет строку в таблицу с адаптивным размером шрифта
        
        Args:
            data (list): Данные для ячеек
            widths (list): Ширина каждой ячейки
            aligns (list, optional): Выравнивание для каждой ячейки (L, C, R)
            row_height (int, optional): Высота строки в мм
        """
        if aligns is None:
            aligns = ["L"] * len(data)
        
        self.set_text_color(0, 0, 0)  # Черный текст
        
        # Для каждой ячейки проверяем, помещается ли текст при текущем размере шрифта
        for i, cell in enumerate(data):
            cell_text = str(cell)
            font_size = 10  # Начальный размер шрифта
            
            # Если это ячейка с ценой (обычно последняя), используем меньший шрифт сразу
            if i == len(data) - 1 and "₽" in cell_text:
                font_size = 9
            
            # Цикл уменьшения шрифта, пока текст не поместится
            while font_size >= 7:  # Минимальный размер шрифта 7
                # FPDF принимает только целые числа для размера шрифта
                self.set_font("DejaVu", "", int(font_size))
                text_width = self.get_string_width(cell_text)
                
                # Если текст помещается в ячейку (с небольшим отступом), выходим из цикла
                if text_width <= widths[i] - 3:
                    break
                
                # Уменьшаем размер шрифта
                font_size -= 1  # Уменьшаем на целое число
            
            # Выводим ячейку с адаптированным размером шрифта
            self.cell(widths[i], row_height, cell_text, 1, 0, aligns[i])
        
        self.ln()


def generate_commercial_offer(pergola_data, user_data=None):
    """
    Генерирует коммерческое предложение в формате PDF на основе 
    данных о перголе, полученных из калькулятора.
    
    Args:
        pergola_data (dict): Словарь с данными о перголе, ее размерах, конфигурации и стоимости
        user_data (dict, optional): Словарь с данными пользователя (имя, телефон и т.д.)
        
    Returns:
        str: Путь к сгенерированному PDF-файлу
    """
    try:
        # Очищаем временные файлы обработанных изображений
        for file in os.listdir("processed_images"):
            if file.startswith("resized_"):
                try:
                    os.remove(os.path.join("processed_images", file))
                except:
                    pass
        
        # Создаем уникальное имя файла на основе текущей даты и времени
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Форматируем текущую дату для отображения в документе
        current_date = now.strftime("%d.%m.%Y")
        
        # Определяем путь для сохранения файла
        if user_data and user_data.get('phone'):
            # Если есть телефон, используем его в имени файла (без специальных символов)
            phone = ''.join(filter(str.isdigit, user_data['phone']))
            pdf_filename = f"generated_pdf/KP_Pergola_{phone}_{timestamp}.pdf"
        else:
            pdf_filename = f"generated_pdf/KP_Pergola_{timestamp}.pdf"
        
        # Создаем экземпляр PDF с поддержкой кириллицы
        pdf = PDF()
        
        # Добавляем первую страницу
        pdf.add_page()
        
        # Устанавливаем информацию о текущей дате
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 5, f"г. Москва, {current_date}", 0, 1, "L")
        
        # Добавляем номер коммерческого предложения
        pdf.ln(5)
        pdf.cell(0, 5, f"№ {timestamp[:8]}", 0, 1, "L")
        
        # Добавляем заголовок коммерческого предложения
        pdf.ln(10)
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", 0, 1, "C")
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, "на поставку и монтаж биоклиматической перголы", 0, 1, "C")
        
        # Добавляем информацию о клиенте, если она доступна
        if user_data:
            pdf.ln(5)
            pdf.chapter_title("Информация о клиенте:")
            
            pdf.set_font('DejaVu', '', 10)
            if user_data.get('name'):
                pdf.cell(0, 7, f"Имя: {user_data['name']}", 0, 1)
            
            if user_data.get('phone'):
                pdf.cell(0, 7, f"Телефон: {user_data['phone']}", 0, 1)
            
            if user_data.get('email'):
                pdf.cell(0, 7, f"Email: {user_data['email']}", 0, 1)
        
        # Добавляем информацию о выбранной конфигурации перголы
        pdf.ln(10)
        pdf.chapter_title("Параметры перголы:")
        
        # Извлекаем данные о перголе из словаря
        pergola_type = pergola_data.get('pergola_type', '')
        width = pergola_data.get('width', 0)
        length = pergola_data.get('length', 0)
        lamella_type = pergola_data.get('lamella_type', '')
        modules = pergola_data.get('modules', 1)
        total_cost = pergola_data.get('total_cost', 0)
        
        # Подсчитываем количество строк в таблице параметров
        parameters_rows = 5  # Базовые параметры
        
        # Если есть опции, учитываем их в количестве строк
        options = pergola_data.get('options', {})
        if options:
            if 'lighting_type' in options and options['lighting_type'] != 'none':
                parameters_rows += 1
            if options.get('installation', False):
                parameters_rows += 1
            if options.get('delivery', False):
                parameters_rows += 1
        
        # Проверяем, поместится ли таблица параметров на текущей странице
        if not pdf.check_table_fit(parameters_rows + 3):  # +3 для заголовка и итоговой строки
            pdf.chapter_title("Параметры перголы:")  # Повторяем заголовок на новой странице
            
        # Создаем таблицу с основными параметрами перголы
        headers = ["Параметр", "Значение"]
        widths = [80, 80]  # Ширина колонок в мм
        
        pdf.table_header(headers, widths)
        
        pdf.table_row(["Модель перголы", pergola_type], widths, row_height=6)
        pdf.table_row(["Ширина", f"{width} м"], widths, row_height=6)
        pdf.table_row(["Вынос (длина)", f"{length} м"], widths, row_height=6)
        pdf.table_row(["Тип ламелей", lamella_type], widths, row_height=6)
        pdf.table_row(["Количество модулей", str(modules)], widths, row_height=6)
        
        # Если есть опции, добавляем их в таблицу
        if options:
            if 'lighting_type' in options and options['lighting_type'] != 'none':
                pdf.table_row(["Тип освещения", options['lighting_type']], widths, row_height=6)
            if options.get('installation', False):
                pdf.table_row(["Установка", "Включена"], widths, row_height=6)
            if options.get('delivery', False):
                pdf.table_row(["Доставка", "Включена"], widths, row_height=6)
                
        # Добавляем информацию о полной стоимости сразу под таблицей параметров
        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240)  # Светло-серый фон
        pdf.set_font('DejaVu', 'B', 13)  # Увеличиваем шрифт для лучшей видимости
        pdf.set_text_color(0, 0, 0)  # Черный текст
        
        # Форматируем стоимость в полном формате
        total_price_value = int(total_cost)
        if total_price_value >= 1000000:
            # Для миллионов форматируем как "1 234 567 рублей"
            total_price_str = f"{total_price_value:,d}".replace(',', ' ') + " рублей"
        else:
            # Для других значений так же
            total_price_str = f"{total_price_value:,d}".replace(',', ' ') + " рублей"
            
        pdf.cell(0, 12, f"Общая стоимость: {total_price_str}", 1, 1, "C", fill=True)
        pdf.ln(5)
        
        # Добавляем спецификацию перголы
        pdf.ln(10)
        pdf.chapter_title("Спецификация перголы:")
        
        # Получаем данные о спецификации
        specification = pergola_data.get('specification', [])
        
        if specification:
            # Подсчитываем количество строк в таблице спецификации
            spec_rows = len(specification) + 1  # +1 для заголовка
            
            # Убрали проверку поместится ли таблица, чтобы лучше использовать пространство
            # и избежать пустых мест на страницах
            
            headers = ["№", "Наименование", "Количество"]
            widths = [15, 120, 25]  # Ширина колонок в мм
            
            pdf.table_header(headers, widths)
            
            for i, item in enumerate(specification, 1):
                pdf.table_row([str(i), item['name'], str(item['quantity'])], widths, aligns=["C", "L", "C"], row_height=6)
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о спецификации отсутствуют", 0, 1)
        
        # Добавляем информацию о стоимости
        pdf.ln(10)
        pdf.chapter_title("Подробная стоимость:")
        
        # Получаем данные о стоимости
        cost_items = pergola_data.get('cost_items', [])
        
        if cost_items:
            # Подсчитываем количество строк в таблице стоимости
            cost_rows = len(cost_items) + 2  # +1 для заголовка, +1 для итоговой строки
            
            # Убрали проверку поместится ли таблица, чтобы лучше использовать пространство
            # и избежать пустых мест на страницах
            
            headers = ["№", "Наименование", "Стоимость (₽)"]
            widths = [10, 93, 57]  # Ширина колонок в мм: уменьшили первые две, значительно увеличили последнюю
            
            pdf.table_header(headers, widths)
            
            # Устанавливаем меньший шрифт для цен в таблице
            pdf.set_font('DejaVu', '', 9)  # Уменьшаем размер шрифта для всех записей таблицы
            
            for i, item in enumerate(cost_items, 1):
                # Форматируем цену с полным отображением
                price_value = int(item['price'])  # Убираем копейки для упрощения
                
                # Форматируем с разделением разрядов и добавляем символ рубля
                if price_value >= 1000000:
                    # Для миллионов: 1 000 000 ₽
                    price_str = f"{price_value:,d}".replace(',', ' ') + " ₽"
                elif price_value >= 1000:
                    # Для тысяч: 100 000 ₽
                    price_str = f"{price_value:,d}".replace(',', ' ') + " ₽"
                else:
                    # Для сотен: 100 ₽
                    price_str = f"{price_value} ₽"
                
                # Используем уменьшенную высоту строки (6 мм вместо 8 мм)
                pdf.table_row([str(i), item['name'], price_str], widths, aligns=["C", "L", "R"], row_height=6)
                
            # Добавляем итоговую строку
            pdf.set_fill_color(211, 211, 211)  # Светло-серый цвет
            pdf.set_font('DejaVu', 'B', 11)  # Увеличиваем шрифт для итоговой суммы
            pdf.set_text_color(0, 0, 0)  # Черный текст
            
            # Форматируем итоговую цену
            total_price_value = int(total_cost)
            if total_price_value >= 1000000:
                # Для миллионов форматируем как "1 234 567 ₽"
                total_price_str = f"{total_price_value:,d}".replace(',', ' ') + " ₽"
            else:
                # Для других значений так же
                total_price_str = f"{total_price_value:,d}".replace(',', ' ') + " ₽"
            
            pdf.cell(10, 10, "", 1, 0, "C", fill=True)
            pdf.cell(93, 10, "ИТОГО:", 1, 0, "R", fill=True)
            pdf.cell(57, 10, total_price_str, 1, 1, "R", fill=True)
            
            # Убрали дублирование итоговой суммы, чтобы не повторяться
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о стоимости отсутствуют", 0, 1)
        
        # Добавляем описание перголы - более эффективная обработка HTML
        pdf.add_page()
        pdf.chapter_title("Описание перголы:")
        
        # Получаем описание перголы
        pergola_description = pergola_data.get('description', '')
        pergola_type = pergola_data.get('pergola_type', 'биоклиматическая')
        
        # Выводим для отладки
        print(f"Длина HTML-описания: {len(pergola_description)} символов")
        print(f"Содержимое описания: {pergola_description[:100]}...")
        
        # Если описание отсутствует или пустое, добавляем базовое описание по типу перголы
        if not pergola_description or pergola_description == "<p>Описание для данного типа перголы отсутствует.</p>":
            print(f"Добавляем базовое описание для перголы типа {pergola_type}")
            
            # Используем разные базовые описания в зависимости от типа перголы
            if pergola_type == "B500NEW":
                description_title = "Серия B500NEW (с поворотными ламелями)"
                pergola_description = """
                <div>
                <h3>Серия B500NEW (с поворотными ламелями)</h3>
                <p>
                Биоклиматическая пергола с поворотными ламелями, вращающимися вокруг нижней оси. 
                Подходит для зон отдыха, террас, бассейнов.
                </p>
                <div>
                <strong>Ламели:</strong><br/>
                250x53 мм (NEW): Угол поворота 105°, шаг 250 мм, масса 4,684 кг/м.<br/>
                200x56 мм (NEW): Угол поворота 112°, шаг 200 мм, масса 4,375 кг/м.
                </div>
                <div>
                <strong>Преимущества:</strong><br/>
                • Высокая герметичность благодаря двойному уплотнению.<br/>
                • Интегрированная дренажная система с лотком 164x260 мм.<br/>
                • Быстрый монтаж (до 4 часов на модуль).<br/>
                • LED/RGB подсветка по периметру (опция).<br/>
                • Максимальный пролет до 8 м.
                </div>
                <div>
                <strong>Узлы:</strong><br/>
                • Несущая балка: Алюминиевая конструкция с двойным сливным лотком (322x260 мм).<br/>
                • Колонна: 164x164 мм, усиленная 7 анкерами для устойчивости.<br/>
                • Система вращения: Немецкий двигатель Bansbach easylift (IP65), синхронизация TANDEM для больших конструкций.
                </div>
                </div>
                """
            elif pergola_type == "B700NEW":
                description_title = "Серия B700NEW (со сдвижными ламелями)"
                pergola_description = """
                <div>
                <h3>Серия B700NEW (со сдвижными ламелями)</h3>
                <p>
                Пергола с ламелями, сдвигающимися в горизонтальной плоскости. Идеальна для больших пространств и экстремальных ветровых нагрузок.
                </p>
                <div>
                <strong>Ламели:</strong><br/>
                250x53 мм (NEW): Шаг 250 мм, масса 4,684 кг/м.<br/>
                200x56 мм (NEW): Шаг 200 мм, масса 4,375 кг/м.
                </div>
                <div>
                <strong>Преимущества:</strong><br/>
                • Устойчивость к сильным ветровым нагрузкам.<br/>
                • Не создает шума при закрытии/открытии.<br/>
                • Может комбинироваться с фиксированными панелями.<br/>
                • Компактное хранение ламелей в пачке.<br/>
                • Идеальна для больших площадей.
                </div>
                <div>
                <strong>Узлы:</strong><br/>
                • Несущая балка: Усиленная алюминиевая конструкция со сливным лотком.<br/>
                • Система привода: Немецкий привод Somfy с управлением через пульт или смартфон.
                </div>
                </div>
                """
            elif pergola_type == "B600":
                description_title = "Серия B600 (с PIR-панелями)"
                pergola_description = """
                <div>
                <h3>Серия B600 (с PIR-панелями)</h3>
                <p>
                Статичная пергола с сэндвич-панелями, предназначенная для всесезонного использования. Превосходная теплоизоляция.
                </p>
                <div>
                <strong>Панели:</strong><br/>
                Сэндвич-панели PIR: толщина 50 мм, двойной металлический лист с пенополиизоциануратным заполнением.
                </div>
                <div>
                <strong>Преимущества:</strong><br/>
                • Наилучшая теплоизоляция среди всех моделей.<br/>
                • Защита от солнца, дождя и снега.<br/>
                • Полностью водонепроницаемая конструкция.<br/>
                • Возможность установки освещения и обогрева.<br/>
                • Идеальна для всесезонных помещений.
                </div>
                <div>
                <strong>Использование:</strong><br/>
                • Зимние сады.<br/>
                • Всесезонные террасы.<br/>
                • Расширение жилых помещений.
                </div>
                </div>
                """
            else:
                description_title = f"Пергола {pergola_type}"
                pergola_description = f"""
                <div>
                <h3>Пергола {pergola_type}</h3>
                <p>
                Современная биоклиматическая пергола с автоматическим управлением. 
                Изготовлена из высококачественного алюминия с порошковым покрытием.
                </p>
                <div>
                <strong>Преимущества:</strong><br/>
                • Защита от осадков и солнца<br/>
                • Регулируемое положение ламелей<br/>
                • Встроенная система отвода воды<br/>
                • Долговечные материалы<br/>
                • Простота управления
                </div>
                <div>
                <strong>Технические характеристики:</strong><br/>
                • Алюминиевый профиль: экструдированный алюминий с порошковым покрытием (322х260 мм)<br/>
                • Размеры колонны: 164x164 мм, используется 7 различных типов алюминиевых профилей<br/>
                • Система автоматизации: приводной механизм высокого качества, работающий от электросети
                </div>
                </div>
                """
        
        # Печатаем весь HTML-текст для отладки
        print("ПОЛНОЕ ОПИСАНИЕ ПЕРГОЛЫ:")
        print(pergola_description)
        
        # HTML-описание нужно преобразовать в чистый текст более эффективным способом
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(pergola_description, 'html.parser')
            
            # Сначала обрабатываем заголовок и печатаем его для отладки
            pdf.set_font('DejaVu', 'B', 12)  # Больший размер шрифта для заголовка
            
            # Проверяем, есть ли заголовок h2 или h3 в описании
            title_tag = soup.find(['h2', 'h3'])
            if title_tag:
                title_text = title_tag.get_text().strip()
                print(f"Заголовок описания: {title_text}")
                pdf.multi_cell(0, 5, title_text)
                pdf.ln(3)
            else:
                # Если заголовка нет, используем тип перголы как заголовок
                if "B500" in pergola_type:
                    title_text = "Серия B500NEW (с поворотными ламелями)"
                elif "B700" in pergola_type:
                    title_text = "Серия B700NEW (со сдвижными ламелями)"
                elif "B600" in pergola_type:
                    title_text = "Серия B600 (с PIR-панелями)"
                else:
                    title_text = f"Пергола {pergola_type}"
                
                print(f"Используем тип перголы как заголовок: {title_text}")
                pdf.multi_cell(0, 5, title_text)
                pdf.ln(3)
            
            # Уменьшаем базовый размер шрифта для более компактного размещения
            pdf.set_font('DejaVu', '', 10)
            
            # Находим всё описание сразу - параграфы, div-блоки, списки и т.д.
            # Извлекаем все текстовые элементы в порядке их появления
            text_elements = []
            
            # 1. Ищем все параграфы
            paragraphs = soup.find_all('p')
            print(f"Найдено {len(paragraphs)} параграфов")
            for p in paragraphs:
                text = p.get_text().strip()
                if text:
                    text_elements.append({"type": "paragraph", "text": text})
            
            # 2. Ищем и обрабатываем div-блоки
            div_blocks = []
            # Сначала ищем блоки на верхнем уровне
            top_divs = soup.find_all('div', recursive=False)
            if top_divs:
                div_blocks.extend(top_divs)
            else:
                # Если на верхнем уровне нет, ищем внутри первого div
                main_div = soup.find('div')
                if main_div:
                    nested_divs = main_div.find_all('div', recursive=False)
                    div_blocks.extend(nested_divs)
            
            print(f"Найдено {len(div_blocks)} div-блоков")
            
            # Обрабатываем каждый div-блок
            for div in div_blocks:
                # Ищем заголовок (strong) внутри блока
                strong_tag = div.find('strong')
                if strong_tag:
                    header_text = strong_tag.get_text().strip()
                    text_elements.append({"type": "header", "text": header_text})
                    
                    # Если в блоке есть маркированный список (со знаком •)
                    div_text = div.get_text()
                    if '•' in div_text:
                        # Разделяем на отдельные маркированные пункты
                        bullet_items = div_text.split('•')
                        for item in bullet_items[1:]:  # Пропускаем первый элемент (заголовок)
                            item_text = item.strip()
                            if item_text and not header_text in item_text:
                                text_elements.append({"type": "bullet", "text": item_text})
                    else:
                        # Обычный текст, исключая заголовок
                        content_text = div_text.replace(header_text, '', 1).strip()
                        if content_text:
                            text_elements.append({"type": "paragraph", "text": content_text})
                else:
                    # Если нет заголовка, добавляем весь текст как параграф
                    text = div.get_text().strip()
                    if text:
                        text_elements.append({"type": "paragraph", "text": text})
            
            # Если мы не нашли никаких структурированных элементов, используем весь текст
            if not text_elements:
                print("Не найдено структурированных элементов, используем весь текст")
                clean_text = soup.get_text()
                clean_text = ' '.join([line.strip() for line in clean_text.split('\n')])
                text_elements.append({"type": "paragraph", "text": clean_text})
            
            # Добавляем все элементы в PDF
            print(f"Добавляем {len(text_elements)} элементов в PDF")
            for element in text_elements:
                element_type = element["type"]
                element_text = element["text"]
                
                if element_type == "header":
                    # Заголовок блока с жирным шрифтом
                    pdf.set_font('DejaVu', 'B', 10)
                    pdf.multi_cell(0, 5, element_text)
                    pdf.ln(2)
                    pdf.set_font('DejaVu', '', 10)
                elif element_type == "bullet":
                    # Маркированный список
                    pdf.multi_cell(0, 5, f"• {element_text}")
                    pdf.ln(1)
                else:  # paragraph
                    # Обычный параграф
                    pdf.multi_cell(0, 5, element_text)
                    pdf.ln(2)
                
        except Exception as e:
            print(f"Ошибка при обработке HTML-описания: {str(e)}")
            pdf.set_font('DejaVu', '', 10)
            
            # Если обработка HTML не удалась, используем простую разбивку текста
            try:
                # Удаляем HTML-теги и извлекаем только текст
                import re
                clean_text = re.sub('<.*?>', ' ', pergola_description)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                # Разбиваем текст на абзацы по длине
                max_chars = 100
                paragraphs = []
                
                words = clean_text.split()
                current_paragraph = []
                
                for word in words:
                    current_paragraph.append(word)
                    if len(' '.join(current_paragraph)) >= max_chars:
                        paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
                
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                
                # Добавляем текст в PDF
                for paragraph in paragraphs:
                    pdf.multi_cell(0, 5, paragraph)
                    pdf.ln(2)
                    
            except:
                # Если даже это не сработало, показываем сообщение об ошибке
                pdf.cell(0, 7, "Не удалось загрузить описание перголы", 0, 1)
        
        # Добавляем изображение перголы, если оно есть
        image_path = pergola_data.get('image_path')
        if image_path and os.path.exists(image_path):
            try:
                # Обрабатываем изображение перед добавлением
                original_img = Image.open(image_path)
                width, height = original_img.size
                
                # Определяем максимальную ширину для изображения (160 мм, учитывая поля)
                max_width_mm = 160
                
                # Вычисляем отношение сторон
                aspect_ratio = height / width
                
                # Рассчитываем размеры с сохранением пропорций
                img_width_mm = max_width_mm
                img_height_mm = img_width_mm * aspect_ratio
                
                # Отладочная информация
                print(f"Исходные размеры изображения: {width}x{height}")
                print(f"Отношение сторон: {aspect_ratio:.2f}")
                print(f"Размеры для PDF: {img_width_mm:.1f}x{img_height_mm:.1f} мм")
                
                # Проверяем, поместится ли изображение на текущей странице
                # (учитываем текущую позицию и высоту изображения + запас 20 мм)
                available_space = 297 - pdf.get_y() - 20  # 297 мм - высота страницы A4
                
                # Если изображение не поместится на текущей странице, создаем новую
                if img_height_mm + 15 > available_space:
                    pdf.add_page()
                
                # Добавляем заголовок изображения
                pdf.ln(5)
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(0, 10, "Иллюстрация перголы:", 0, 1, "C")
                pdf.ln(5)
                
                # Вставляем изображение с явным указанием ширины и высоты
                # для гарантии сохранения пропорций
                pdf.image(
                    image_path,
                    x=(210 - img_width_mm) / 2,  # центрируем
                    y=pdf.get_y(),  # текущая позиция Y
                    w=img_width_mm,  # ширина
                    h=img_height_mm  # высота, рассчитанная с сохранением пропорций
                )
                print(f"Добавляем изображение в PDF: {image_path}")
            except Exception as e:
                print(f"Ошибка при обработке изображения: {str(e)}")
        
        # Добавляем контактную информацию - проверяем, может ли она поместиться на текущей странице
        # Примерный размер для контактной информации (6 строк по 7 мм + заголовок и отступы)
        contact_info_height = 60
        
        # Проверяем, поместится ли контактная информация на текущей странице
        if 297 - pdf.get_y() < contact_info_height:
            pdf.add_page()
        else:
            pdf.ln(15)  # Добавляем отступ перед контактной информацией
            
        pdf.chapter_title("Контактная информация:")
        
        pdf.set_font('DejaVu', '', 10)  # Уменьшаем размер шрифта для экономии места
        pdf.multi_cell(0, 5, "Для получения дополнительной информации или оформления заказа, пожалуйста, свяжитесь с нами:")
        pdf.ln(3)
        
        contact_info = [
            "Телефон: +7 (495) 123-45-67",
            "Email: info@komfortnyj-dom.ru",
            "Веб-сайт: www.komfortnyj-dom.ru",
            "Адрес: г. Москва, ул. Примерная, д. 123"
        ]
        
        for info in contact_info:
            pdf.cell(0, 6, info, 0, 1)  # Уменьшаем высоту строк с 7 до 6 мм
        
        # Создаем директорию для сохранения PDF
        os.makedirs(os.path.dirname(pdf_filename), exist_ok=True)
        
        # Сохраняем PDF
        pdf.output(pdf_filename)
        print(f"PDF успешно создан: {pdf_filename}")
        
        return pdf_filename
        
    except Exception as e:
        print(f"Ошибка при создании PDF: {str(e)}")
        
        try:
            # Создаем упрощенный PDF без кириллицы в случае ошибки
            from fpdf import FPDF
            
            # Получаем данные из словаря
            p_type = pergola_data.get('pergola_type', 'пергола') if pergola_data else 'пергола'
            p_width = pergola_data.get('width', 0) if pergola_data else 0
            p_length = pergola_data.get('length', 0) if pergola_data else 0
            p_cost = pergola_data.get('total_cost', 0) if pergola_data else 0
            
            # Создаем упрощенный PDF
            simple_pdf = FPDF()
            simple_pdf.add_page()
            
            # Заголовок документа
            simple_pdf.set_font('Arial', 'B', 16)
            simple_pdf.cell(0, 10, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", 0, 1, 'C')
            simple_pdf.set_font('Arial', '', 12)
            simple_pdf.cell(0, 10, "на поставку и монтаж биоклиматической перголы", 0, 1, 'C')
            simple_pdf.ln(10)
            
            # Основная информация
            simple_pdf.set_font('Arial', 'B', 14)
            simple_pdf.cell(0, 10, "Параметры перголы:", 0, 1, 'L')
            
            # Таблица параметров
            simple_pdf.set_font('Arial', '', 12)
            simple_pdf.cell(70, 10, "Модель:", 0, 0)
            simple_pdf.cell(0, 10, p_type, 0, 1)
            
            simple_pdf.cell(70, 10, "Ширина:", 0, 0)
            simple_pdf.cell(0, 10, f"{p_width} м", 0, 1)
            
            simple_pdf.cell(70, 10, "Вынос (длина):", 0, 0)
            simple_pdf.cell(0, 10, f"{p_length} м", 0, 1)
            
            # Стоимость
            simple_pdf.ln(5)
            simple_pdf.set_fill_color(240, 240, 240)
            simple_pdf.set_font('Arial', 'B', 14)
            
            # Форматируем стоимость в полном формате
            price_value = int(p_cost)
            if price_value >= 1000000:
                # Для миллионов форматируем как "1 234 567 рублей"
                price_str = f"{price_value:,d}".replace(',', ' ') + " рублей"
            else:
                # Для других значений так же
                price_str = f"{price_value:,d}".replace(',', ' ') + " рублей"
                
            simple_pdf.cell(0, 10, f"Общая стоимость: {price_str}", 1, 1, 'C', fill=True)
            
            # Заметка о версии документа
            simple_pdf.ln(15)
            simple_pdf.set_font('Arial', 'I', 10)
            simple_pdf.cell(0, 10, "Данный документ является упрощенной версией коммерческого предложения.", 0, 1)
            simple_pdf.cell(0, 10, "Для получения полного предложения с детальным описанием, пожалуйста, свяжитесь с нами.", 0, 1)
            
            # Контактная информация
            simple_pdf.ln(10)
            simple_pdf.set_font('Arial', 'B', 12)
            simple_pdf.cell(0, 10, "Контактная информация:", 0, 1)
            
            simple_pdf.set_font('Arial', '', 10)
            simple_pdf.cell(0, 7, "Телефон: +7 (495) 123-45-67", 0, 1)
            simple_pdf.cell(0, 7, "Email: info@komfortnyj-dom.ru", 0, 1)
            simple_pdf.cell(0, 7, "Веб-сайт: www.komfortnyj-dom.ru", 0, 1)
            
            # Сохраняем упрощенный PDF в дефолтную директорию
            backup_filename = f"generated_pdf/KP_Pergola_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            os.makedirs(os.path.dirname(backup_filename), exist_ok=True)
            simple_pdf.output(backup_filename)
            print(f"Упрощенный PDF создан: {backup_filename}")
            
            return backup_filename
            
        except Exception as e2:
            print(f"Ошибка при создании упрощенного PDF: {str(e2)}")
            return None


def format_pergola_data_for_pdf(results, options, dimensions, pergola_description):
    """
    Форматирует данные расчета перголы для использования в генерации PDF
    
    Args:
        results (dict): Результаты расчета перголы
        options (dict): Выбранные опции
        dimensions (dict): Размеры перголы
        pergola_description (str): Описание перголы (HTML)
        
    Returns:
        dict: Отформатированные данные для генерации PDF
    """
    # Получаем константы из приложения
    EURO_RATE = 110  # Курс евро
    
    # Извлекаем тип перголы из опций
    pergola_type = options.get('pergola_type', '')
    
    pdf_data = {
        'pergola_type': pergola_type,
        'width': dimensions.get('width', 0),
        'length': dimensions.get('length', 0),
        'lamella_type': options.get('lamella_type', ''),
        'modules': dimensions.get('modules', 1),
        'options': options,
        'total_cost': results.get('total_price', 0) * EURO_RATE,  # Конвертируем в рубли
        'description': pergola_description,
    }
    
    # Форматируем спецификацию
    specification = []
    if 'specification' in results:
        for item in results['specification']:
            specification.append({
                'name': item.get('name', ''),
                'quantity': item.get('count', 0)
            })
    pdf_data['specification'] = specification
    
    # Форматируем стоимость
    cost_items = []
    if 'items' in results:
        for item in results['items']:
            cost_items.append({
                'name': item.get('name', ''),
                'price': item.get('price', 0) * EURO_RATE  # Конвертируем в рубли
            })
    pdf_data['cost_items'] = cost_items
    
    # Добавляем пути к изображениям перголы, использующиеся в UI
    # Проверяем наличие файлов из скриншотов в attached_assets
    if pergola_type == 'B500NEW':
        # Пробуем найти изображение B500 с вращением ламелей
        possible_paths = [
            "attached_assets/Снимок экрана 2025-04-09 в 22.44.59.png",
            "attached_assets/aluminum slats.png",
            "attached_assets/В500 со вращением ламелей.png",
            "attached_assets/b500_rotation.png",
            "attached_assets/Снимок экрана 2025-04-09 в 23.20.06.png"  # Добавлен новый скриншот
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    elif pergola_type == 'B700NEW':
        # Пробуем найти изображение B700 со сдвижением ламелей
        possible_paths = [
            "attached_assets/В700 со сдвижением ламелей.png",
            "attached_assets/b700_sliding.png",
            "attached_assets/Снимок экрана 2025-04-09 в 23.11.44.png"  # Добавлен новый скриншот
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    elif pergola_type == 'B600':
        # Пробуем найти изображение B600 с сэндвич панелями
        possible_paths = [
            "attached_assets/В600 с сэндвич панелями.png",
            "attached_assets/b600_sandwich.png",
            "attached_assets/Снимок экрана 2025-04-09 в 23.02.37.png"  # Добавлен новый скриншот
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pdf_data['image_path'] = path
                break
    
    return pdf_data