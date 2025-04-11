"""
Страница администрирования кэша.
Позволяет просматривать статистику кэша, очищать устаревшие записи
и предварительно кэшировать стандартные размеры пергол.
"""

import os
import streamlit as st
import pandas as pd
import time
import sys

# Добавляем родительскую директорию в путь, чтобы импортировать модули
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем модули нашего приложения
import cache_manager
from app import perform_calculation

st.set_page_config(
    page_title="Управление кэшем - Калькулятор пергол",
    page_icon="🔄",
    layout="wide"
)

# Стили
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1 {
        color: #0066cc;
        font-weight: 600;
    }
    .stats-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .cache-table {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def display_cache_stats():
    """Отображает статистику кэша"""
    stats = cache_manager.get_cache_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Всего записей", stats["total_entries"])
    
    with col2:
        st.metric("Действительных записей", stats["valid_entries"])
    
    with col3:
        st.metric("Размер кэша", f"{stats['cache_size_mb']} МБ")
    
    st.markdown("---")
    
    st.markdown("### Дополнительная информация")
    st.markdown(f"""
    - **Директория кэша:** `{stats["cache_dir"]}`
    - **Срок действия кэша:** {stats["expiry_days"]} дней
    - **Устаревших записей:** {stats["expired_entries"]}
    """)


def display_cache_entries():
    """Отображает содержимое кэша в виде таблицы"""
    cache_dir = cache_manager.CACHE_DIR
    if not os.path.exists(cache_dir):
        st.warning("Директория кэша не существует")
        return
    
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    
    if not cache_files:
        st.info("Кэш пуст")
        return
    
    cache_data = []
    for filename in cache_files:
        cache_path = os.path.join(cache_dir, filename)
        is_valid = cache_manager.is_cache_valid(cache_path)
        
        try:
            file_time = os.path.getmtime(cache_path)
            file_size = os.path.getsize(cache_path) / 1024  # KB
            
            import json
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            pergola_type = data.get("options", {}).get("pergola_type", "Неизвестно")
            width = data.get("dimensions", {}).get("width", 0)
            length = data.get("dimensions", {}).get("length", 0)
            
            cache_data.append({
                "Ключ": filename.replace(".json", ""),
                "Тип перголы": pergola_type,
                "Размеры": f"{width}x{length}м",
                "Дата создания": time.strftime("%Y-%m-%d %H:%M", time.localtime(file_time)),
                "Размер (KB)": round(file_size, 2),
                "Действителен": "Да" if is_valid else "Нет"
            })
        except Exception as e:
            st.error(f"Ошибка при чтении файла кэша {filename}: {str(e)}")
    
    # Создаем DataFrame и отображаем его
    if cache_data:
        df = pd.DataFrame(cache_data)
        st.dataframe(df, use_container_width=True, height=400)


def main():
    st.title("Управление кэшем калькулятора пергол")
    
    st.markdown("""
    Эта страница позволяет управлять кэшем расчетов калькулятора пергол. 
    Кэширование позволяет значительно ускорить работу приложения за счет
    сохранения результатов предыдущих расчетов.
    """)
    
    tab1, tab2, tab3 = st.tabs(["Статистика", "Содержимое кэша", "Управление"])
    
    with tab1:
        st.header("Статистика кэша")
        display_cache_stats()
    
    with tab2:
        st.header("Содержимое кэша")
        display_cache_entries()
    
    with tab3:
        st.header("Управление кэшем")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Очистка кэша")
            
            if st.button("Очистить устаревший кэш", type="secondary"):
                with st.spinner("Очистка устаревших записей кэша..."):
                    cache_manager.clean_expired_cache()
                st.success("Устаревшие записи кэша успешно удалены")
                st.rerun()
            
            if st.button("Очистить весь кэш", type="primary", help="Будут удалены все записи кэша"):
                if st.session_state.get("confirm_clear_all", False):
                    with st.spinner("Очистка всех записей кэша..."):
                        import shutil
                        if os.path.exists(cache_manager.CACHE_DIR):
                            shutil.rmtree(cache_manager.CACHE_DIR)
                        os.makedirs(cache_manager.CACHE_DIR, exist_ok=True)
                    st.success("Весь кэш успешно очищен")
                    st.session_state.confirm_clear_all = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear_all = True
                    st.warning("Вы уверены, что хотите удалить все записи кэша? Нажмите кнопку еще раз для подтверждения.")
        
        with col2:
            st.subheader("Предварительное кэширование")
            
            if st.button("Кэшировать стандартные размеры", type="primary", 
                         help="Рассчитает и сохранит в кэш типовые размеры пергол"):
                with st.spinner("Идёт предварительный расчёт и кэширование стандартных размеров..."):
                    cache_manager.prepare_standard_sizes_cache(perform_calculation)
                st.success("Стандартные размеры успешно кэшированы")
                st.rerun()


if __name__ == "__main__":
    main()