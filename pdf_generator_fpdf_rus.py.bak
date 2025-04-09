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
            
            # Определяем начальный размер шрифта в зависимости от типа данных
            if i == len(data) - 1 and ("₽" in cell_text or "руб" in cell_text):
                # Для ячеек с ценами сразу используем меньший размер
                font_size = 8
                
                # Если это цена свыше миллиона или имеет много символов, начинаем с еще меньшего размера
                if len(cell_text.strip()) > 10:  # Для длинных цен
                    font_size = 7
                if len(cell_text.strip()) > 14:  # Для очень длинных цен
                    font_size = 6
            elif i == 0 and len(cell_text) < 3:
                # Для номеров строк используем стандартный размер
                font_size = 10
            elif "Итого" in cell_text or "ИТОГО" in cell_text:
                # Для итоговой строки используем чуть больший шрифт
                font_size = 9
            else:
                # Для основного текста
                font_size = 9
            
            # Цикл уменьшения шрифта, пока текст не поместится
            # Разрешаем уменьшать шрифт до 5 для длинных цен
            min_font_size = 5 if ("₽" in cell_text or "руб" in cell_text) else 7
            
            while font_size >= min_font_size:
                # FPDF принимает только целые числа для размера шрифта
                self.set_font("DejaVu", "", int(font_size))
                text_width = self.get_string_width(cell_text)
                
                # Используем разные отступы в зависимости от типа ячейки
                padding = 2 if i == len(data) - 1 else 3  # Для цен меньший отступ
                
                # Если текст помещается в ячейку с учетом отступа, выходим из цикла
                if text_width <= widths[i] - padding:
                    break
                
                # Уменьшаем размер шрифта
                font_size -= 1  # Уменьшаем размер шрифта на 1 пункт
            
            # Выводим ячейку с адаптированным размером шрифта
            self.cell(widths[i], row_height, cell_text, 1, 0, aligns[i])
        
        self.ln()
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
            widths = [10, 83, 67]  # Ширина колонок в мм: еще больше увеличиваем последнюю колонку для цен
            
            pdf.table_header(headers, widths)
            
            # Устанавливаем еще меньший шрифт для цен в таблице, чтобы гарантированно поместились полные суммы
            pdf.set_font('DejaVu', '', 8)  # Дополнительно уменьшаем размер шрифта для всех записей таблицы
            
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
                # Меняем выравнивание с R (правого) на L (левое) для соответствия таблице спецификации
                pdf.table_row([str(i), item['name'], price_str], widths, aligns=["C", "L", "L"], row_height=6)
                
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
            pdf.cell(83, 10, "ИТОГО:", 1, 0, "R", fill=True)
            pdf.cell(67, 10, total_price_str, 1, 1, "L", fill=True)
            
            # Убрали дублирование итоговой суммы, чтобы не повторяться
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о стоимости отсутствуют", 0, 1)
        
        # Добавляем описание перголы и дополнительные разделы
        pdf.add_page()
        pdf.chapter_title("Описание перголы:")
        
        # Собираем все типы описаний
        descriptions = []
        
        # Основное описание перголы
        pergola_description = pergola_data.get('description', '')
        pergola_type = pergola_data.get('pergola_type', 'биоклиматическая')
        if pergola_description:
            descriptions.append(pergola_description)
            
        # Дополнительные описания
        modular_description = pergola_data.get('modular_description', '')
        if modular_description:
            descriptions.append(modular_description)
            
        drainage_description = pergola_data.get('drainage_description', '')
        if drainage_description:
            descriptions.append(drainage_description)
        
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
        
        # Обрабатываем все блоки описаний последовательно
        for section_index, html_description in enumerate(descriptions):
            # Добавляем разрыв страницы между разными описаниями (кроме первого)
            if section_index > 0:
                pdf.add_page()
                # Если у нас более одного раздела, добавляем заголовки для дополнительных
                if section_index == 1:
                    pdf.chapter_title("Модульная система пергол:")
                elif section_index == 2:
                    pdf.chapter_title("Система водоотведения:")
            
            # HTML-описание нужно преобразовать в чистый текст более эффективным способом
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_description, 'html.parser')
                
                # Сначала обрабатываем заголовок и печатаем его для отладки
                pdf.set_font('DejaVu', 'B', 12)  # Больший размер шрифта для заголовка
                
                # Проверяем, есть ли заголовок h2 или h3 в описании
                title_tag = soup.find(['h2', 'h3'])
                if title_tag:
                    title_text = title_tag.get_text().strip()
                    print(f"Заголовок описания: {title_text}")
                    pdf.multi_cell(0, 5, title_text)
                    pdf.ln(3)
                elif section_index == 0:  # Только для первого раздела используем тип перголы
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
                
                # 3. Ищем все списки
                list_elements = soup.find_all(['ul', 'ol'])
                for list_elem in list_elements:
                    # Определяем тип списка (нумерованный или маркированный)
                    is_ordered = list_elem.name == 'ol'
                    
                    # Получаем все элементы списка
                    list_items = list_elem.find_all('li')
                    for i, li in enumerate(list_items):
                        item_text = li.get_text().strip()
                        if is_ordered:
                            text_elements.append({"type": "ordered", "number": i+1, "text": item_text})
                        else:
                            text_elements.append({"type": "bullet", "text": item_text})
                
                # 4. Обрабатываем каждый div-блок
                for div in div_blocks:
                    # Ищем заголовок (strong, b) внутри блока
                    header_tag = div.find(['strong', 'b', 'h4', 'h5', 'h6'])
                    if header_tag:
                        header_text = header_tag.get_text().strip()
                        # Проверяем, что это действительно заголовок, а не просто выделенный текст
                        if len(header_text) < 100:  # Заголовки обычно короткие
                            text_elements.append({"type": "header", "text": header_text})
                    
                    # Проверяем, есть ли в div маркированный список
                    list_markers = ['•', '◦', '▪', '▫', '–', '-']
                    div_text = div.get_text()
                    
                    has_markers = any(marker in div_text for marker in list_markers)
                    
                    if has_markers:
                        # Если есть маркированный список, разделяем по маркерам
                        for marker in list_markers:
                            if marker in div_text:
                                # Разделяем на отдельные маркированные пункты
                                bullet_items = div_text.split(marker)
                                for i, item in enumerate(bullet_items):
                                    if i == 0 and header_tag:  # Пропускаем первый элемент, если есть заголовок
                                        continue
                                    
                                    item_text = item.strip()
                                    if item_text:
                                        # Проверяем, не содержит ли этот элемент заголовок
                                        if header_tag and header_text in item_text:
                                            # Если содержит, удаляем заголовок из текста
                                            item_text = item_text.replace(header_text, '', 1).strip()
                                        
                                        if item_text:  # Добавляем только если есть текст
                                            text_elements.append({"type": "bullet", "text": item_text})
                                break  # Используем только первый найденный маркер
                    elif header_tag:
                        # Если есть заголовок, но нет маркированного списка, обрабатываем обычный текст
                        content_text = div_text.replace(header_text, '', 1).strip()
                        if content_text:
                            text_elements.append({"type": "paragraph", "text": content_text})
                    else:
                        # Если нет ни заголовка, ни маркированного списка, 
                        # добавляем весь текст div как параграф
                        text = div.get_text().strip()
                        if text:
                            text_elements.append({"type": "paragraph", "text": text})
                
                # Если мы не нашли никаких структурированных элементов, используем весь текст
                if not text_elements:
                    print("Не найдено структурированных элементов, используем весь текст")
                    clean_text = soup.get_text()
                    # Удаляем лишние пробелы и переносы строк
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
                    elif element_type == "ordered":
                        # Нумерованный список
                        number = element.get("number", 1)
                        pdf.multi_cell(0, 5, f"{number}. {element_text}")
                        pdf.ln(1)
                    else:  # paragraph
                        # Обычный параграф
                        pdf.multi_cell(0, 5, element_text)
                        pdf.ln(2)
                
            except Exception as e:
                print(f"Ошибка при обработке HTML-описания (раздел {section_index}): {str(e)}")
                pdf.set_font('DejaVu', '', 10)
                
                # Если обработка HTML не удалась, используем простую разбивку текста
                try:
                    # Удаляем HTML-теги и извлекаем только текст
                    import re
                    clean_text = re.sub('<.*?>', ' ', html_description)
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
                        
                except Exception as ex:
                    print(f"Ошибка при обработке текста: {str(ex)}")
                    # Если даже это не сработало, показываем сообщение об ошибке
                    pdf.cell(0, 7, f"Не удалось загрузить описание перголы (раздел {section_index})", 0, 1)
        
        # Добавляем изображения перголы (может быть несколько)
        image_paths = pergola_data.get('image_paths', [])
        if not image_paths and 'image_path' in pergola_data:
            # Для обратной совместимости
            image_path = pergola_data.get('image_path')
            if image_path and os.path.exists(image_path):
                image_paths = [image_path]
        
        # Получаем подпись для изображений
        image_caption = pergola_data.get('image_caption', "Иллюстрация перголы")
        
        # Добавляем все изображения
        if image_paths:
            # Добавляем заголовок для раздела с изображениями (один раз)
            pdf.add_page()
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, "Иллюстрации:", 0, 1, "C")
            pdf.ln(5)
            
            # Добавляем все изображения по очереди
            for i, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    try:
                        # Обрабатываем изображение перед добавлением
                        original_img = Image.open(img_path)
                        width, height = original_img.size
                        
                        # Определяем максимальную ширину для изображения (160 мм, учитывая поля)
                        max_width_mm = 160
                        
                        # Вычисляем отношение сторон
                        aspect_ratio = height / width
                        
                        # Рассчитываем размеры с сохранением пропорций
                        img_width_mm = max_width_mm
                        img_height_mm = img_width_mm * aspect_ratio
                        
                        # Отладочная информация
                        print(f"Изображение {i+1}: {img_path}")
                        print(f"Исходные размеры изображения: {width}x{height}")
                        print(f"Отношение сторон: {aspect_ratio:.2f}")
                        print(f"Размеры для PDF: {img_width_mm:.1f}x{img_height_mm:.1f} мм")
                        
                        # Проверяем, поместится ли изображение на текущей странице
                        # (учитываем текущую позицию и высоту изображения + запас 20 мм)
                        available_space = 297 - pdf.get_y() - 20  # 297 мм - высота страницы A4
                        
                        # Если изображение не поместится на текущей странице, создаем новую
                        if img_height_mm + 20 > available_space:
                            pdf.add_page()
                        
                        # Добавляем изображение с подписью
                        if i > 0:
                            pdf.ln(15)  # Отступ между изображениями
                            
                        # Формируем подпись с номером изображения, если их несколько
                        if len(image_paths) > 1:
                            caption = f"{image_caption} ({i+1}/{len(image_paths)})"
                        else:
                            caption = image_caption
                            
                        pdf.set_font('DejaVu', 'B', 11)
                        pdf.cell(0, 8, caption, 0, 1, "C")
                        pdf.ln(5)
                        
                        # Вставляем изображение с явным указанием ширины и высоты
                        # для гарантии сохранения пропорций
                        pdf.image(
                            img_path,
                            x=(210 - img_width_mm) / 2,  # центрируем
                            y=pdf.get_y(),  # текущая позиция Y
                            w=img_width_mm,  # ширина
                            h=img_height_mm  # высота, рассчитанная с сохранением пропорций
                        )
                        print(f"Добавлено изображение в PDF: {img_path}")
                    except Exception as e:
                        print(f"Ошибка при обработке изображения {img_path}: {str(e)}")
                else:
                    print(f"Изображение не найдено: {img_path}")
        
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
            if file.startswith("proc_"):
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
        pdf.cell(0, 5, f"Москва, {current_date}", 0, 1, "L")
        
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
        
        # Создаем таблицу с основными параметрами перголы
        headers = ["Параметр", "Значение"]
        widths = [80, 80]  # Ширина колонок в мм
        
        pdf.table_header(headers, widths)
        
        pdf.table_row(["Модель перголы", pergola_type], widths)
        pdf.table_row(["Ширина", f"{width} м"], widths)
        pdf.table_row(["Вынос (длина)", f"{length} м"], widths)
        pdf.table_row(["Тип ламелей", lamella_type], widths)
        pdf.table_row(["Количество модулей", str(modules)], widths)
        
        # Если есть опции, добавляем их в таблицу
        options = pergola_data.get('options', {})
        if options:
            if 'lighting_type' in options and options['lighting_type'] != 'none':
                pdf.table_row(["Тип освещения", options['lighting_type']], widths)
            if options.get('installation', False):
                pdf.table_row(["Монтаж", "Включен"], widths)
            if options.get('delivery', False):
                pdf.table_row(["Доставка", "Включена"], widths)
        
        # Добавляем спецификацию перголы
        pdf.ln(10)
        pdf.chapter_title("Спецификация перголы:")
        
        # Получаем данные о спецификации
        specification = pergola_data.get('specification', [])
        
        if specification:
            headers = ["№", "Наименование", "Кол-во"]
            widths = [10, 145, 15]  # Ширина колонок в мм
            
            pdf.table_header(headers, widths)
            
            for i, item in enumerate(specification, 1):
                pdf.table_row([str(i), item['name'], str(item['quantity'])], widths, aligns=["C", "L", "C"])
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о спецификации отсутствуют", 0, 1)
        
        # Добавляем информацию о стоимости
        pdf.ln(10)
        pdf.chapter_title("Информация о стоимости:")
        
        # Получаем данные о стоимости
        cost_items = pergola_data.get('cost_items', [])
        total_cost = pergola_data.get('total_cost', 0)
        
        if cost_items:
            headers = ["№", "Наименование", "Стоимость"]
            widths = [10, 83, 67]  # Изменены ширины колонок для лучшего размещения длинных цен
            
            pdf.table_header(headers, widths)
            
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
                # Меняем выравнивание с R (правого) на L (левое) для соответствия таблице спецификации
                pdf.table_row([str(i), item['name'], price_str], widths, aligns=["C", "L", "L"], row_height=6)
                
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
            pdf.cell(83, 10, "ИТОГО:", 1, 0, "R", fill=True)
            pdf.cell(67, 10, total_price_str, 1, 1, "L", fill=True)
            
            # Убрали дублирование итоговой суммы, чтобы не повторяться
        else:
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 7, "Данные о стоимости отсутствуют", 0, 1)
        
        # Добавляем описание перголы и дополнительные разделы
        pdf.add_page()
        pdf.chapter_title("Описание перголы:")
        
        # Собираем все типы описаний
        descriptions = []
        
        # Основное описание перголы
        pergola_description = pergola_data.get('description', '')
        pergola_type = pergola_data.get('pergola_type', 'биоклиматическая')
        if pergola_description:
            descriptions.append(pergola_description)
            
        # Дополнительные описания
        modular_description = pergola_data.get('modular_description', '')
        if modular_description:
            descriptions.append(modular_description)
            
        drainage_description = pergola_data.get('drainage_description', '')
        if drainage_description:
            descriptions.append(drainage_description)
        
        if len(descriptions) == 0:
            # Если описания отсутствуют, добавляем стандартное описание
            descriptions.append(f"""
            <div>
                <p>Пергола {pergola_type} — современная биоклиматическая пергола с автоматическим управлением. 
                Изготовлена из высококачественного алюминия с порошковой покраской.</p>
                
                <p><strong>Преимущества:</strong><br/>
                • Защита от осадков и солнца<br/>
                • Регулируемое положение ламелей<br/>
                • Встроенная система водоотведения<br/>
                • Долговечные материалы<br/>
                • Простота использования</p>
            </div>
            """)
        
        # Проходим по всем описаниям и преобразуем HTML в текст
        section_index = 0
        for description_html in descriptions:
            section_index += 1
            
            # Пропускаем пустые описания
            if not description_html or description_html == "<p>Описание для данного типа перголы отсутствует.</p>":
                continue
                
            # Добавляем разделительную линию между разными описаниями, если это не первое описание
            if section_index > 1:
                pdf.ln(5)
            
            try:
                # Преобразуем HTML в текст с помощью BeautifulSoup
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(description_html, 'html.parser')
                
                # Обрабатываем заголовки - делаем их крупнее и жирным шрифтом
                for heading in soup.find_all(['h1', 'h2', 'h3']):
                    heading_text = heading.get_text().strip()
                    
                    # Устанавливаем размер шрифта в зависимости от уровня заголовка
                    font_size = 14 if heading.name == 'h1' else 12 if heading.name == 'h2' else 11
                    pdf.set_font('DejaVu', 'B', font_size)
                    
                    # Добавляем отступ перед заголовком
                    pdf.ln(2) if section_index > 1 and heading == soup.find(['h1', 'h2', 'h3']) else pdf.ln(5)
                    
                    # Выводим заголовок 
                    pdf.cell(0, 8, heading_text, 0, 1, 'C' if heading.name == 'h1' else 'L')
                    pdf.ln(2)
                    
                    # Удаляем заголовок из супа, чтобы не дублировать его
                    heading.extract()
                
                # Обрабатываем абзацы текста
                for paragraph in soup.find_all('p'):
                    paragraph_text = paragraph.get_text().strip()
                    if paragraph_text:
                        pdf.set_font('DejaVu', '', 10)
                        
                        # Разбиваем длинные абзацы на части, чтобы избежать проблем с Unicode
                        # в многострочном тексте и обеспечить корректное отображение
                        chunk_size = const_chunk_size = 180  # Начальный размер чанка (символов)
                        
                        # Если абзац короткий, выводим его целиком
                        if len(paragraph_text) <= chunk_size:
                            pdf.multi_cell(0, 5, paragraph_text)
                            pdf.ln(2)  # Небольшой отступ между абзацами
                        else:
                            # Разбиваем на части и выводим по одной
                            paragraph_parts = []
                            current_pos = 0
                            
                            while current_pos < len(paragraph_text):
                                # Адаптивный размер чанка
                                if current_pos + chunk_size >= len(paragraph_text):
                                    # Последний кусок текста - берем до конца
                                    paragraph_parts.append(paragraph_text[current_pos:])
                                    break
                                else:
                                    # Ищем последний пробел перед chunk_size, чтобы не разрывать слова
                                    end_pos = current_pos + chunk_size
                                    while end_pos > current_pos and paragraph_text[end_pos] != ' ':
                                        end_pos -= 1
                                    
                                    # Если пробела нет, используем chunk_size как есть
                                    if end_pos == current_pos:
                                        end_pos = current_pos + chunk_size
                                    
                                    paragraph_parts.append(paragraph_text[current_pos:end_pos])
                                    current_pos = end_pos + 1
                            
                            # Выводим разбитый на части абзац
                            for part in paragraph_parts:
                                if part.strip():  # Пропускаем пустые строки
                                    pdf.multi_cell(0, 5, part.strip())
                            
                            pdf.ln(2)  # Отступ после абзаца
                
                # Обрабатываем списки
                for ul in soup.find_all('ul'):
                    pdf.ln(2)
                    
                    for li in ul.find_all('li'):
                        li_text = li.get_text().strip()
                        if li_text:
                            pdf.set_font('DejaVu', '', 10)
                            # Добавляем маркер списка
                            pdf.multi_cell(0, 5, f"• {li_text}")
                    
                    pdf.ln(2)
                
                # Обрабатываем жирный текст для совместимости с HTML
                pdf.set_font('DejaVu', '', 10)
                for bold in soup.find_all(['strong', 'b']):
                    if bold.parent.name not in ['h1', 'h2', 'h3', 'p', 'li']:
                        bold_text = bold.get_text().strip()
                        if bold_text:
                            pdf.set_font('DejaVu', 'B', 10)
                            pdf.multi_cell(0, 5, bold_text)
                            pdf.set_font('DejaVu', '', 10)
                
                # Добавляем отступ после раздела
                pdf.ln(2)
                
            except Exception as e:
                print(f"Ошибка при обработке HTML-описания (раздел {section_index}): {str(e)}")
                pdf.set_font('DejaVu', '', 10)
                pdf.multi_cell(0, 5, "Ошибка при обработке описания перголы.")
                
        # Добавляем все необходимые изображения
        image_paths = pergola_data.get('images', [])
        image_caption = pergola_data.get('image_caption', 'Изображение перголы')
        
        if image_paths and isinstance(image_paths, list) and len(image_paths) > 0:
            pdf.add_page()
            pdf.chapter_title("Изображения:")
            
            for i, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    try:
                        # Обрабатываем изображение перед добавлением для сохранения пропорций
                        original_img = Image.open(img_path)
                        width, height = original_img.size
                        
                        # Определяем максимальную ширину для изображения (160 мм, учитывая поля)
                        max_width_mm = 160
                        
                        # Вычисляем отношение сторон
                        aspect_ratio = height / width
                        
                        # Рассчитываем размеры с сохранением пропорций
                        img_width_mm = max_width_mm
                        img_height_mm = img_width_mm * aspect_ratio
                        
                        # Отладочная информация
                        print(f"Изображение {i+1}: {img_path}")
                        print(f"Исходные размеры изображения: {width}x{height}")
                        print(f"Отношение сторон: {aspect_ratio:.2f}")
                        print(f"Размеры для PDF: {img_width_mm:.1f}x{img_height_mm:.1f} мм")
                        
                        # Проверяем, поместится ли изображение на текущей странице
                        # (учитываем текущую позицию и высоту изображения + запас 20 мм)
                        available_space = 297 - pdf.get_y() - 20  # 297 мм - высота страницы A4
                        
                        # Если изображение не поместится на текущей странице, создаем новую
                        if img_height_mm + 20 > available_space:
                            pdf.add_page()
                        
                        # Добавляем изображение с подписью
                        if i > 0:
                            pdf.ln(15)  # Отступ между изображениями
                            
                        # Формируем подпись с номером изображения, если их несколько
                        if len(image_paths) > 1:
                            caption = f"{image_caption} ({i+1}/{len(image_paths)})"
                        else:
                            caption = image_caption
                            
                        pdf.set_font('DejaVu', 'B', 11)
                        pdf.cell(0, 8, caption, 0, 1, "C")
                        pdf.ln(5)
                        
                        # Вставляем изображение с явным указанием ширины и высоты
                        # для гарантии сохранения пропорций
                        pdf.image(
                            img_path,
                            x=(210 - img_width_mm) / 2,  # центрируем
                            y=pdf.get_y(),  # текущая позиция Y
                            w=img_width_mm,  # ширина
                            h=img_height_mm  # высота, рассчитанная с сохранением пропорций
                        )
                        print(f"Добавлено изображение в PDF: {img_path}")
                    except Exception as e:
                        print(f"Ошибка при обработке изображения {img_path}: {str(e)}")
                else:
                    print(f"Изображение не найдено: {img_path}")
        
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
            
            # Создаем простой PDF без кириллицы
            simple_pdf = FPDF()
            simple_pdf.add_page()
            simple_pdf.set_font('Arial', 'B', 14)
            simple_pdf.cell(0, 10, "Pergola Calculator", 0, 1, 'C')
            simple_pdf.set_font('Arial', '', 12)
            simple_pdf.cell(0, 10, f"Model: {p_type}", 0, 1)
            simple_pdf.cell(0, 10, f"Dimensions: {p_width}x{p_length} m", 0, 1)
            simple_pdf.cell(0, 10, f"Total cost: {p_cost:,.2f} RUB", 0, 1)
            
            # Добавляем примечание о проблеме с кириллицей
            simple_pdf.ln(10)
            simple_pdf.set_font('Arial', 'I', 10)
            simple_pdf.cell(0, 10, "Oshibka pri sozdanii PDF s podderzhkoj kirillicy.", 0, 1)
            simple_pdf.cell(0, 10, "Pozhalujsta, obraschaites k menedzheru dlya poluchenija pravilnoj versii.", 0, 1)
            
            # Добавляем контактную информацию без кириллицы
            simple_pdf.ln(10)
            simple_pdf.set_font('Arial', 'B', 12)
            simple_pdf.cell(0, 10, "Contact Info:", 0, 1)
            simple_pdf.set_font('Arial', '', 10)
            simple_pdf.cell(0, 7, "Telefon: +7 (495) 123-45-67", 0, 1)
            simple_pdf.cell(0, 7, "Email: info@komfortnyj-dom.ru", 0, 1)
            simple_pdf.cell(0, 7, "Veb-sajt: www.komfortnyj-dom.ru", 0, 1)
            
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
    
    # Импортируем функции для работы с описаниями и изображениями пергол
    try:
        from config.pergola_descriptions import (
            get_pergola_description, 
            get_pergola_images, 
            get_modular_system_description,
            get_drainage_system_description,
            get_pergola_image_caption
        )
        
        # Получаем полное HTML-описание перголы
        # Если описание не было передано, запрашиваем его
        if not pergola_description or pergola_description == "<p>Описание для данного типа перголы отсутствует.</p>":
            full_description = get_pergola_description(pergola_type)
            if full_description:
                pdf_data['description'] = full_description
            
            # Добавляем модульную систему и другие общие описания
            modular_description = get_modular_system_description()
            drainage_description = get_drainage_system_description()
            
            if modular_description:
                pdf_data['modular_description'] = modular_description
            
            if drainage_description:
                pdf_data['drainage_description'] = drainage_description
        
        # Получаем список изображений для данного типа перголы
        image_paths = []
        pergola_images = get_pergola_images(pergola_type)
        
        # Проверяем наличие всех изображений
        for img_path in pergola_images:
            if os.path.exists(img_path):
                image_paths.append(img_path)
        
        # Если нашли хотя бы одно изображение, добавляем его
        if image_paths:
            pdf_data['image_paths'] = image_paths
            pdf_data['image_caption'] = get_pergola_image_caption(pergola_type)
        else:
            # Запасной вариант: используем скриншоты как раньше
            if pergola_type == 'B500NEW':
                # Пробуем найти изображение B500 с вращением ламелей
                possible_paths = [
                    "attached_assets/Снимок экрана 2025-04-09 в 22.44.59.png",
                    "attached_assets/aluminum slats.png",
                    "attached_assets/В500 со вращением ламелей.png",
                    "attached_assets/b500_rotation.png",
                    "attached_assets/Снимок экрана 2025-04-09 в 23.20.06.png"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        image_paths.append(path)
            elif pergola_type == 'B700NEW':
                # Пробуем найти изображение B700 со сдвижением ламелей
                possible_paths = [
                    "attached_assets/В700 со сдвижением ламелей.png",
                    "attached_assets/b700_sliding.png",
                    "attached_assets/Снимок экрана 2025-04-09 в 23.11.44.png"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        image_paths.append(path)
            elif pergola_type == 'B600':
                # Пробуем найти изображение B600 с сэндвич панелями
                possible_paths = [
                    "attached_assets/В600 с сэндвич панелями.png",
                    "attached_assets/b600_sandwich.png",
                    "attached_assets/Снимок экрана 2025-04-09 в 23.02.37.png"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        image_paths.append(path)
                
            if image_paths:
                pdf_data['image_paths'] = image_paths
                if len(image_paths) == 1:
                    pdf_data['image_path'] = image_paths[0]  # Для обратной совместимости
    
    except ImportError as e:
        print(f"Ошибка при импорте модулей для работы с описаниями: {str(e)}")
        # Запасной вариант со старым кодом
        if pergola_type == 'B500NEW':
            possible_paths = ["attached_assets/b500_rotation.png"]
            for path in possible_paths:
                if os.path.exists(path):
                    pdf_data['image_path'] = path
                    break
        elif pergola_type == 'B700NEW':
            possible_paths = ["attached_assets/b700_sliding.png"]
            for path in possible_paths:
                if os.path.exists(path):
                    pdf_data['image_path'] = path
                    break
        elif pergola_type == 'B600':
            possible_paths = ["attached_assets/b600_sandwich.png"]
            for path in possible_paths:
                if os.path.exists(path):
                    pdf_data['image_path'] = path
                    break
    
    return pdf_data