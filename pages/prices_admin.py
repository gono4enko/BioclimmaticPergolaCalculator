"""
Страница администрирования цен и контента для калькулятора пергол

Функциональность:
- Изменение курса евро
- Управление процентом наценки на доставку
- Управление процентом наценки на установку
- Настройка акций и скидок
- Загрузка новых прайс-листов
- Редактирование текстов описаний
- Настройка порядка отображения контента
"""
import streamlit as st
import pandas as pd
import os
import json
import sys
import datetime
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем модуль для авторизации администратора
try:
    from components.admin_auth import admin_required, check_admin_auth, admin_login_form
except ImportError:
    st.error("Не удалось импортировать модуль авторизации. Проверьте наличие файла components/admin_auth.py")
    st.stop()

# Импортируем модуль с настройками цен
try:
    from config import pricing_settings, promotions, pergola_descriptions
except ImportError:
    st.error("Не удалось импортировать модули конфигурации. Проверьте наличие файлов в директории config/")
    st.stop()

# Константы
PRICES_DIR = os.path.join("attached_assets")
ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"]

# Настройка страницы
st.set_page_config(
    page_title="Администрирование цен и контента",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Заголовок страницы
st.title("🔒 Администрирование цен и контента")

# Проверка авторизации
is_admin = check_admin_auth()

if not is_admin:
    admin_login_form(location="main")
else:
    # Верхний блок информации
    with st.expander("ℹ️ Информация о странице", expanded=False):
        st.markdown("""
        ### Управление ценами и контентом
        
        Эта страница позволяет управлять всеми параметрами ценообразования и контентом калькулятора пергол:
        
        1. **Базовые настройки цен**: Курс евро, наценки на доставку и установку
        2. **Управление акциями и скидками**: Создание, редактирование, активация/деактивация акций
        3. **Прайс-листы**: Загрузка и обновление прайс-листов для разных типов пергол
        4. **Тексты и описания**: Редактирование описаний пергол, ламелей и других компонентов
        5. **Порядок отображения контента**: Настройка последовательности и видимости блоков контента
        
        Все изменения сохраняются автоматически и вступают в силу немедленно.
        """)
    
    # Создаем вкладки для разных разделов
    tabs = st.tabs([
        "📊 Базовые настройки", 
        "🏷️ Акции и скидки", 
        "📋 Прайс-листы", 
        "📝 Тексты описаний",
        "🔄 Порядок контента"
    ])
    
    # Вкладка базовых настроек
    with tabs[0]:
        st.header("Базовые настройки цен")
        
        # Получаем текущие настройки
        current_settings = pricing_settings.get_settings()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Курс евро
            new_euro_rate = st.number_input(
                "Курс евро (руб.)",
                min_value=1.0,
                max_value=500.0,
                value=float(current_settings.get("euro_rate", 110.0)),
                step=0.5,
                format="%.2f",
                help="Установите текущий курс евро в рублях"
            )
            
            # Кнопка обновления курса
            if st.button("Обновить курс евро"):
                if pricing_settings.update_euro_rate(new_euro_rate):
                    st.success(f"✅ Курс евро обновлен до {new_euro_rate} руб.")
                else:
                    st.error("❌ Ошибка при обновлении курса евро")
        
        with col2:
            # Наценка на доставку
            new_delivery_markup = st.number_input(
                "Наценка за доставку (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_settings.get("delivery_markup_percent", 10.0)),
                step=1.0,
                format="%.1f",
                help="Установите процент наценки на доставку"
            )
            
            # Наценка на установку
            new_installation_markup = st.number_input(
                "Наценка за установку (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_settings.get("installation_markup_percent", 15.0)),
                step=1.0,
                format="%.1f",
                help="Установите процент наценки на установку"
            )
            
            # Кнопка обновления наценок
            if st.button("Обновить наценки"):
                delivery_updated = pricing_settings.update_delivery_markup(new_delivery_markup)
                installation_updated = pricing_settings.update_installation_markup(new_installation_markup)
                
                if delivery_updated and installation_updated:
                    st.success(f"✅ Наценки обновлены: доставка {new_delivery_markup}%, установка {new_installation_markup}%")
                else:
                    st.error("❌ Ошибка при обновлении наценок")

        # Блок с информацией о текущих настройках
        st.subheader("Информация о текущих настройках")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric(
                label="Текущий курс евро",
                value=f"{current_settings.get('euro_rate', 110.0):.2f} ₽"
            )
        
        with info_col2:
            st.metric(
                label="Наценка за доставку",
                value=f"{current_settings.get('delivery_markup_percent', 10.0):.1f}%"
            )
        
        with info_col3:
            st.metric(
                label="Наценка за установку",
                value=f"{current_settings.get('installation_markup_percent', 15.0):.1f}%"
            )
        
        # История изменений
        st.subheader("История изменений")
        
        # В будущем можно добавить логирование изменений в отдельный файл
        # и отображать историю здесь
        st.info("Журнал изменений находится в разработке")
    
    # Вкладка акций и скидок
    with tabs[1]:
        st.header("Управление акциями и скидками")
        
        # Подгружаем текущие акции
        current_promotions = promotions.get_all_promotions()
        
        # Создание новой акции
        with st.expander("➕ Создать новую акцию", expanded=False):
            st.subheader("Добавление новой акции")
            
            new_promo_col1, new_promo_col2 = st.columns(2)
            
            with new_promo_col1:
                new_promo_name = st.text_input(
                    "Название акции",
                    key="new_promo_name",
                    help="Введите название новой акции"
                )
                
                new_promo_code = st.text_input(
                    "Промокод (необязательно)",
                    key="new_promo_code",
                    help="Введите промокод для акции (можно оставить пустым)"
                )
                
                new_promo_discount = st.number_input(
                    "Размер скидки (%)",
                    min_value=1.0,
                    max_value=100.0,
                    value=5.0,
                    step=1.0,
                    format="%.1f",
                    key="new_promo_discount",
                    help="Укажите размер скидки в процентах"
                )
            
            with new_promo_col2:
                new_promo_start_date = st.date_input(
                    "Дата начала акции",
                    value=datetime.date.today(),
                    key="new_promo_start_date",
                    help="Выберите дату начала действия акции"
                )
                
                new_promo_end_date = st.date_input(
                    "Дата окончания акции",
                    value=datetime.date.today() + datetime.timedelta(days=30),
                    key="new_promo_end_date",
                    help="Выберите дату окончания действия акции"
                )
                
                new_promo_stackable = st.checkbox(
                    "Суммируется с другими акциями",
                    value=False,
                    key="new_promo_stackable",
                    help="Укажите, может ли акция суммироваться с другими акциями"
                )
                
                new_promo_active = st.checkbox(
                    "Акция активна",
                    value=True,
                    key="new_promo_active",
                    help="Активировать акцию сразу после создания"
                )
            
            new_promo_description = st.text_area(
                "Описание акции",
                key="new_promo_description",
                height=100,
                help="Введите подробное описание акции"
            )
            
            new_promo_conditions = st.text_area(
                "Условия применения",
                key="new_promo_conditions",
                height=100,
                help="Введите условия, при которых акция применяется"
            )
            
            # Кнопка создания акции
            if st.button("Создать акцию"):
                if not new_promo_name:
                    st.error("⚠️ Необходимо указать название акции")
                elif new_promo_end_date < new_promo_start_date:
                    st.error("⚠️ Дата окончания акции не может быть раньше даты начала")
                else:
                    # Создаем новую акцию
                    new_promotion = {
                        "name": new_promo_name,
                        "code": new_promo_code if new_promo_code else None,
                        "discount_percent": float(new_promo_discount),
                        "start_date": new_promo_start_date.strftime("%Y-%m-%d"),
                        "end_date": new_promo_end_date.strftime("%Y-%m-%d"),
                        "description": new_promo_description,
                        "conditions": new_promo_conditions,
                        "stackable": new_promo_stackable,
                        "active": new_promo_active
                    }
                    
                    # Добавляем акцию
                    success = promotions.add_promotion(new_promotion)
                    
                    if success:
                        st.success(f"✅ Акция '{new_promo_name}' успешно создана")
                        st.rerun()
                    else:
                        st.error("❌ Ошибка при создании акции")
        
        # Список существующих акций
        st.subheader("Список акций")
        
        if not current_promotions:
            st.warning("⚠️ Акции не найдены")
        else:
            # Фильтр по активности
            show_inactive = st.checkbox("Показать неактивные акции", value=False)
            
            # Подготовка данных для таблицы
            promo_data = []
            
            for promo_id, promo in current_promotions.items():
                # Пропускаем неактивные акции, если фильтр не включен
                if not promo.get("active", False) and not show_inactive:
                    continue
                    
                # Добавляем данные акции
                promo_data.append({
                    "ID": promo_id,
                    "Название": promo.get("name", ""),
                    "Скидка": f"{promo.get('discount_percent', 0)}%",
                    "Начало": promo.get("start_date", ""),
                    "Окончание": promo.get("end_date", ""),
                    "Суммируется": "Да" if promo.get("stackable", False) else "Нет",
                    "Активна": "Да" if promo.get("active", False) else "Нет"
                })
            
            # Создаем DataFrame для отображения
            promo_df = pd.DataFrame(promo_data)
            
            if not promo_data:
                st.warning("⚠️ Нет акций, соответствующих фильтру")
            else:
                # Отображаем таблицу акций
                st.dataframe(
                    promo_df,
                    use_container_width=True,
                    column_config={
                        "ID": st.column_config.TextColumn("ID"),
                        "Название": st.column_config.TextColumn("Название"),
                        "Скидка": st.column_config.TextColumn("Скидка"),
                        "Начало": st.column_config.DateColumn("Начало", format="DD.MM.YYYY"),
                        "Окончание": st.column_config.DateColumn("Окончание", format="DD.MM.YYYY"),
                        "Суммируется": st.column_config.TextColumn("Суммируется"),
                        "Активна": st.column_config.TextColumn("Активна")
                    }
                )
            
            # Редактирование выбранной акции
            selected_promo_id = st.selectbox(
                "Выберите акцию для редактирования",
                options=[promo_id for promo_id in current_promotions.keys()],
                format_func=lambda x: current_promotions[x].get("name", x) if x in current_promotions else x
            )
            
            if selected_promo_id and selected_promo_id in current_promotions:
                st.subheader(f"Редактирование акции: {current_promotions[selected_promo_id].get('name', '')}")
                
                selected_promo = current_promotions[selected_promo_id]
                
                edit_col1, edit_col2 = st.columns(2)
                
                with edit_col1:
                    edit_promo_name = st.text_input(
                        "Название акции",
                        value=selected_promo.get("name", ""),
                        key="edit_promo_name"
                    )
                    
                    edit_promo_code = st.text_input(
                        "Промокод (необязательно)",
                        value=selected_promo.get("code", ""),
                        key="edit_promo_code"
                    )
                    
                    edit_promo_discount = st.number_input(
                        "Размер скидки (%)",
                        min_value=1.0,
                        max_value=100.0,
                        value=float(selected_promo.get("discount_percent", 5.0)),
                        step=1.0,
                        format="%.1f",
                        key="edit_promo_discount"
                    )
                
                with edit_col2:
                    # Преобразуем строки с датами в объекты date
                    try:
                        start_date = datetime.datetime.strptime(
                            selected_promo.get("start_date", datetime.date.today().strftime("%Y-%m-%d")),
                            "%Y-%m-%d"
                        ).date()
                    except:
                        start_date = datetime.date.today()
                        
                    try:
                        end_date = datetime.datetime.strptime(
                            selected_promo.get("end_date", (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")),
                            "%Y-%m-%d"
                        ).date()
                    except:
                        end_date = datetime.date.today() + datetime.timedelta(days=30)
                    
                    edit_promo_start_date = st.date_input(
                        "Дата начала акции",
                        value=start_date,
                        key="edit_promo_start_date"
                    )
                    
                    edit_promo_end_date = st.date_input(
                        "Дата окончания акции",
                        value=end_date,
                        key="edit_promo_end_date"
                    )
                    
                    edit_promo_stackable = st.checkbox(
                        "Суммируется с другими акциями",
                        value=selected_promo.get("stackable", False),
                        key="edit_promo_stackable"
                    )
                    
                    edit_promo_active = st.checkbox(
                        "Акция активна",
                        value=selected_promo.get("active", True),
                        key="edit_promo_active"
                    )
                
                edit_promo_description = st.text_area(
                    "Описание акции",
                    value=selected_promo.get("description", ""),
                    key="edit_promo_description",
                    height=100
                )
                
                edit_promo_conditions = st.text_area(
                    "Условия применения",
                    value=selected_promo.get("conditions", ""),
                    key="edit_promo_conditions",
                    height=100
                )
                
                # Кнопки действий
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Сохранить изменения", key="save_promo_changes"):
                        if not edit_promo_name:
                            st.error("⚠️ Необходимо указать название акции")
                        elif edit_promo_end_date < edit_promo_start_date:
                            st.error("⚠️ Дата окончания акции не может быть раньше даты начала")
                        else:
                            # Обновляем акцию
                            updated_promotion = {
                                "name": edit_promo_name,
                                "code": edit_promo_code if edit_promo_code else None,
                                "discount_percent": float(edit_promo_discount),
                                "start_date": edit_promo_start_date.strftime("%Y-%m-%d"),
                                "end_date": edit_promo_end_date.strftime("%Y-%m-%d"),
                                "description": edit_promo_description,
                                "conditions": edit_promo_conditions,
                                "stackable": edit_promo_stackable,
                                "active": edit_promo_active
                            }
                            
                            # Обновляем акцию
                            success = promotions.update_promotion(selected_promo_id, updated_promotion)
                            
                            if success:
                                st.success(f"✅ Акция '{edit_promo_name}' успешно обновлена")
                                st.rerun()
                            else:
                                st.error("❌ Ошибка при обновлении акции")
                
                with col2:
                    # Кнопка активации/деактивации
                    new_status = not selected_promo.get("active", True)
                    action = "Активировать" if new_status else "Деактивировать"
                    
                    if st.button(action, key="toggle_promo_status"):
                        # Обновляем статус акции
                        updated_promo = selected_promo.copy()
                        updated_promo["active"] = new_status
                        
                        success = promotions.update_promotion(selected_promo_id, updated_promo)
                        
                        if success:
                            status_text = "активирована" if new_status else "деактивирована"
                            st.success(f"✅ Акция '{selected_promo.get('name', '')}' успешно {status_text}")
                            st.rerun()
                        else:
                            st.error(f"❌ Ошибка при изменении статуса акции")
                
                with col3:
                    # Кнопка удаления
                    if st.button("Удалить акцию", key="delete_promo"):
                        # Запрашиваем подтверждение
                        st.warning(f"⚠️ Вы уверены, что хотите удалить акцию '{selected_promo.get('name', '')}'?")
                        
                        confirm_col1, confirm_col2 = st.columns(2)
                        
                        with confirm_col1:
                            if st.button("Да, удалить", key="confirm_delete_promo"):
                                success = promotions.delete_promotion(selected_promo_id)
                                
                                if success:
                                    st.success(f"✅ Акция '{selected_promo.get('name', '')}' успешно удалена")
                                    st.rerun()
                                else:
                                    st.error("❌ Ошибка при удалении акции")
                        
                        with confirm_col2:
                            if st.button("Отмена", key="cancel_delete_promo"):
                                st.rerun()
    
    # Вкладка прайс-листов
    with tabs[2]:
        st.header("Управление прайс-листами")
        
        # Директория с прайс-листами
        if not os.path.exists(PRICES_DIR):
            os.makedirs(PRICES_DIR)
        
        # Функция для получения списка прайс-листов
        def get_price_lists():
            price_files = []
            for file in os.listdir(PRICES_DIR):
                if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    file_path = os.path.join(PRICES_DIR, file)
                    price_files.append({
                        "name": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    })
            return price_files
        
        # Получаем список прайс-листов
        price_lists = get_price_lists()
        
        # Загрузка нового прайс-листа
        with st.expander("⬆️ Загрузить новый прайс-лист", expanded=False):
            st.subheader("Загрузка нового прайс-листа")
            
            upload_col1, upload_col2 = st.columns(2)
            
            with upload_col1:
                # Выбор типа перголы
                pergola_type = st.selectbox(
                    "Тип перголы",
                    options=["B500NEW", "B700NEW", "B600"],
                    help="Выберите тип перголы для прайс-листа"
                )
                
                # Выбор размера ламелей
                lamella_size = st.selectbox(
                    "Размер ламелей",
                    options=["200", "250", "PIR"],
                    help="Выберите размер ламелей для прайс-листа"
                )
            
            with upload_col2:
                # Загрузка файла
                uploaded_file = st.file_uploader(
                    "Выберите файл прайс-листа",
                    type=["csv", "xlsx", "xls"],
                    help="Загрузите файл прайс-листа в формате CSV или Excel"
                )
                
                # Флаг замены существующего файла
                replace_existing = st.checkbox(
                    "Заменить существующий прайс-лист",
                    value=True,
                    help="При включении заменит существующий прайс-лист с таким же названием"
                )
            
            # Дополнительная информация о формате прайс-листа
            with st.expander("ℹ️ Формат прайс-листа", expanded=False):
                st.markdown("""
                **Требования к формату прайс-листа:**
                
                1. Первый столбец должен содержать значения выноса перголы (в метрах)
                2. Первая строка должна содержать значения ширины перголы (в метрах)
                3. Ячейки с ценами должны содержать числовые значения (в евро)
                4. CSV-файлы должны использовать разделитель ";"
                
                **Пример формата CSV:**
                ```
                ;3;3.5;4;4.5;5;5.5;6
                2;1000;1100;1200;1300;1400;1500;1600
                2.5;1100;1200;1300;1400;1500;1600;1700
                3;1200;1300;1400;1500;1600;1700;1800
                ```
                
                **Пример формата Excel:**
                Аналогичный формат, с шириной в первой строке и выносом в первом столбце.
                """)
            
            # Кнопка загрузки
            if st.button("Загрузить прайс-лист"):
                if uploaded_file is None:
                    st.error("⚠️ Выберите файл для загрузки")
                else:
                    # Формируем имя файла
                    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                    if file_extension not in ALLOWED_EXTENSIONS:
                        st.error(f"⚠️ Неподдерживаемый формат файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}")
                    else:
                        # Формируем имя файла для сохранения
                        new_filename = f"{pergola_type}_{lamella_size}{file_extension}"
                        new_file_path = os.path.join(PRICES_DIR, new_filename)
                        
                        # Проверяем, существует ли файл с таким именем
                        if os.path.exists(new_file_path) and not replace_existing:
                            st.error(f"⚠️ Файл с именем {new_filename} уже существует. Выберите опцию замены или используйте другое имя.")
                        else:
                            # Создаем резервную копию существующего файла, если он есть
                            if os.path.exists(new_file_path):
                                backup_dir = os.path.join(PRICES_DIR, "backups")
                                os.makedirs(backup_dir, exist_ok=True)
                                
                                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                backup_filename = f"{os.path.splitext(new_filename)[0]}_{timestamp}{file_extension}"
                                backup_path = os.path.join(backup_dir, backup_filename)
                                
                                try:
                                    shutil.copy2(new_file_path, backup_path)
                                    st.info(f"ℹ️ Создана резервная копия существующего прайс-листа: {backup_filename}")
                                except Exception as e:
                                    st.warning(f"⚠️ Не удалось создать резервную копию: {str(e)}")
                            
                            # Сохраняем загруженный файл
                            try:
                                with open(new_file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                st.success(f"✅ Прайс-лист успешно загружен: {new_filename}")
                                
                                # Обновляем список прайс-листов
                                price_lists = get_price_lists()
                            except Exception as e:
                                st.error(f"❌ Ошибка при сохранении файла: {str(e)}")
        
        # Список существующих прайс-листов
        st.subheader("Существующие прайс-листы")
        
        if not price_lists:
            st.warning("⚠️ Прайс-листы не найдены")
        else:
            # Создаем DataFrame с информацией о прайс-листах
            price_list_data = [{
                "Имя файла": pl["name"],
                "Размер": f"{pl['size'] / 1024:.1f} КБ",
                "Последнее изменение": pl["modified"].strftime("%d.%m.%Y %H:%M")
            } for pl in price_lists]
            
            price_list_df = pd.DataFrame(price_list_data)
            
            # Отображаем таблицу с прайс-листами
            st.dataframe(
                price_list_df,
                use_container_width=True,
                column_config={
                    "Имя файла": st.column_config.TextColumn("Имя файла"),
                    "Размер": st.column_config.TextColumn("Размер"),
                    "Последнее изменение": st.column_config.TextColumn("Последнее изменение")
                }
            )
            
            # Выбор файла для просмотра или удаления
            selected_price_list = st.selectbox(
                "Выберите прайс-лист для просмотра или удаления",
                options=[pl["name"] for pl in price_lists]
            )
            
            if selected_price_list:
                # Находим выбранный прайс-лист
                selected_pl = next((pl for pl in price_lists if pl["name"] == selected_price_list), None)
                
                if selected_pl:
                    preview_col, action_col = st.columns([3, 1])
                    
                    with preview_col:
                        st.subheader(f"Просмотр прайс-листа: {selected_price_list}")
                        
                        # Загружаем данные из файла
                        try:
                            if selected_price_list.endswith(".csv"):
                                df = pd.read_csv(selected_pl["path"], sep=";")
                            else:  # Excel файл
                                df = pd.read_excel(selected_pl["path"])
                            
                            # Отображаем данные
                            st.dataframe(df, use_container_width=True)
                        except Exception as e:
                            st.error(f"❌ Ошибка при загрузке файла: {str(e)}")
                    
                    with action_col:
                        st.subheader("Действия")
                        
                        # Кнопка для удаления файла
                        if st.button("Удалить прайс-лист"):
                            # Запрашиваем подтверждение
                            st.warning(f"⚠️ Вы уверены, что хотите удалить прайс-лист '{selected_price_list}'?")
                            
                            confirm_col1, confirm_col2 = st.columns(2)
                            
                            with confirm_col1:
                                if st.button("Да, удалить", key="confirm_delete_price_list"):
                                    try:
                                        # Создаем резервную копию файла перед удалением
                                        backup_dir = os.path.join(PRICES_DIR, "backups")
                                        os.makedirs(backup_dir, exist_ok=True)
                                        
                                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                        backup_filename = f"{os.path.splitext(selected_price_list)[0]}_{timestamp}{os.path.splitext(selected_price_list)[1]}"
                                        backup_path = os.path.join(backup_dir, backup_filename)
                                        
                                        shutil.copy2(selected_pl["path"], backup_path)
                                        
                                        # Удаляем файл
                                        os.remove(selected_pl["path"])
                                        
                                        st.success(f"✅ Прайс-лист '{selected_price_list}' успешно удален (резервная копия сохранена)")
                                        
                                        # Обновляем список прайс-листов
                                        price_lists = get_price_lists()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Ошибка при удалении файла: {str(e)}")
                            
                            with confirm_col2:
                                if st.button("Отмена", key="cancel_delete_price_list"):
                                    st.rerun()
                        
                        # Кнопка для скачивания файла
                        with open(selected_pl["path"], "rb") as file:
                            file_data = file.read()
                            st.download_button(
                                label="Скачать прайс-лист",
                                data=file_data,
                                file_name=selected_price_list,
                                mime="application/octet-stream"
                            )
    
    # Вкладка текстов описаний
    with tabs[3]:
        st.header("Управление текстами описаний")
        
        # Функция для получения доступных категорий описаний
        def get_description_categories():
            descriptions = pergola_descriptions.PERGOLA_DESCRIPTIONS
            categories = []
            
            for pergola_type, type_data in descriptions.items():
                if isinstance(type_data, dict):
                    categories.append({"id": pergola_type, "name": f"Пергола {pergola_type}"})
                    
                    # Проверяем наличие подкатегорий
                    for key, value in type_data.items():
                        if isinstance(value, dict) and "title" in value:
                            categories.append({
                                "id": f"{pergola_type}_{key}",
                                "name": f"{pergola_type} - {value.get('title', key)}",
                                "parent": pergola_type
                            })
            
            # Добавляем остальные категории из других ключей
            for key in ["LAMELLA_ENGINEERING", "DRAINAGE", "INSTALL_SYSTEM", "SOMFY", "BANSBACH"]:
                if key in descriptions and isinstance(descriptions[key], dict) and "title" in descriptions[key]:
                    categories.append({
                        "id": key,
                        "name": descriptions[key].get("title", key)
                    })
            
            return categories
        
        # Получаем категории описаний
        description_categories = get_description_categories()
        
        # Выбор категории для редактирования
        selected_category_id = st.selectbox(
            "Выберите категорию для редактирования",
            options=[category["id"] for category in description_categories],
            format_func=lambda x: next((category["name"] for category in description_categories if category["id"] == x), x)
        )
        
        if selected_category_id:
            # Находим выбранную категорию
            selected_category = next((category for category in description_categories if category["id"] == selected_category_id), None)
            
            if selected_category:
                st.subheader(f"Редактирование описания: {selected_category['name']}")
                
                # Получаем данные описания
                descriptions = pergola_descriptions.PERGOLA_DESCRIPTIONS
                
                # Определяем, является ли это подкатегорией
                if "_" in selected_category_id:
                    parts = selected_category_id.split("_", 1)
                    parent_id, child_id = parts
                    
                    if parent_id in descriptions and child_id in descriptions[parent_id]:
                        description_data = descriptions[parent_id][child_id]
                    else:
                        st.error(f"❌ Не удалось найти данные для категории {selected_category_id}")
                        description_data = {}
                else:
                    # Это основная категория
                    description_data = descriptions.get(selected_category_id, {})
                
                # Редактирование данных описания
                edited_title = st.text_input(
                    "Заголовок",
                    value=description_data.get("title", ""),
                    key=f"edit_title_{selected_category_id}"
                )
                
                edited_html = st.text_area(
                    "HTML-описание",
                    value=description_data.get("html", ""),
                    height=300,
                    key=f"edit_html_{selected_category_id}"
                )
                
                edited_image = st.text_input(
                    "Путь к изображению",
                    value=description_data.get("image", ""),
                    key=f"edit_image_{selected_category_id}"
                )
                
                # Превью изображения, если оно существует
                if edited_image and os.path.exists(edited_image):
                    st.image(edited_image, caption="Текущее изображение", use_column_width=True)
                elif edited_image:
                    st.warning(f"⚠️ Изображение не найдено по пути: {edited_image}")
                
                # Кнопка для сохранения изменений
                if st.button("Сохранить изменения"):
                    # Создаем обновленный словарь с данными описания
                    updated_description = {
                        "title": edited_title,
                        "html": edited_html,
                        "image": edited_image
                    }
                    
                    # Обновляем данные в модуле описаний
                    # Здесь нужно реализовать механизм сохранения изменений
                    st.info("ℹ️ Функция сохранения описаний находится в разработке")
                    
                    # В будущей реализации нужно будет сохранять изменения в файл
                    st.json(updated_description)
    
    # Вкладка порядка контента
    with tabs[4]:
        st.header("Настройка порядка отображения контента")
        
        # Получаем текущий порядок контента
        current_order = pricing_settings.get_content_order()
        
        # Названия блоков контента для удобства
        content_names = {
            "gallery": "Галерея проектов",
            "lamella_description": "Описание ламелей",
            "drive_description": "Описание привода",
            "drainage_description": "Система водоотвода",
            "installation_description": "Система установки"
        }
        
        # Преобразуем порядок в список для сортировки
        content_order = [{"id": key, "name": content_names.get(key, key), "order": value} 
                         for key, value in current_order.items()]
        
        # Сортируем по порядку
        content_order.sort(key=lambda x: x["order"])
        
        # Отображаем текущий порядок
        st.subheader("Текущий порядок отображения контента")
        
        content_df = pd.DataFrame([{
            "Порядок": item["order"],
            "Раздел контента": item["name"],
            "Идентификатор": item["id"]
        } for item in content_order])
        
        st.dataframe(
            content_df,
            use_container_width=True,
            column_config={
                "Порядок": st.column_config.NumberColumn("Порядок"),
                "Раздел контента": st.column_config.TextColumn("Раздел контента"),
                "Идентификатор": st.column_config.TextColumn("Идентификатор")
            }
        )
        
        # Редактирование порядка
        st.subheader("Изменение порядка отображения")
        
        st.markdown("""
        Установите порядок отображения разделов контента.
        Разделы с меньшим номером будут отображаться выше, с большим - ниже.
        """)
        
        # Создаем колонки для элементов управления
        col1, col2 = st.columns(2)
        
        # Словарь для хранения обновленного порядка
        new_order = {}
        
        # Создаем слайдеры для каждого элемента контента
        for item in content_order:
            with col1:
                new_position = st.slider(
                    f"{item['name']}",
                    min_value=1,
                    max_value=len(content_order),
                    value=item["order"],
                    key=f"order_{item['id']}"
                )
                new_order[item["id"]] = new_position
        
        # Проверка уникальности позиций
        if len(set(new_order.values())) != len(new_order):
            st.error("⚠️ Позиции должны быть уникальными. Два или более элемента имеют одинаковые номера позиций.")
        else:
            # Кнопка сохранения порядка
            if st.button("Сохранить порядок отображения"):
                # Сохраняем обновленный порядок
                if pricing_settings.update_content_order(new_order):
                    st.success("✅ Порядок отображения контента успешно обновлен")
                    st.rerun()
                else:
                    st.error("❌ Ошибка при обновлении порядка контента")
        
        # Дополнительная информация о применении порядка
        with st.expander("ℹ️ Информация о применении порядка контента", expanded=False):
            st.markdown("""
            **Как работает порядок контента:**
            
            1. Блоки контента отображаются на странице в порядке, указанном в настройках
            2. Блоки с меньшим номером отображаются выше других блоков
            3. Изменения порядка применяются немедленно после сохранения
            4. Если несколько элементов имеют одинаковый номер, порядок их отображения не определён
            
            **Примечание:** Некоторые блоки могут не отображаться в зависимости от выбранных параметров перголы
            или других настроек приложения.
            """)