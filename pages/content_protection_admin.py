"""
Административная страница для управления системой защиты контента.
Позволяет просматривать защищенные файлы, создавать резервные копии
и управлять флагами разрешения изменений.
"""

import streamlit as st
import os
import sys
import time
from datetime import datetime

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import content_protection
except ImportError:
    st.error("Модуль content_protection.py не найден. Убедитесь, что он существует в корневой директории проекта.")
    st.stop()


def main():
    st.title("Управление защитой контента")
    
    st.markdown("""
    ### Система предотвращения случайных изменений
    
    Эта система защищает ключевые файлы контента и конфигурации от непреднамеренных
    изменений во время разработки. Когда защита активна, система отслеживает MD5-хеши
    файлов и предупреждает при обнаружении изменений.
    """)
    
    # Показываем текущий статус
    st.subheader("Текущий статус")
    
    allow_changes = getattr(content_protection, 'ALLOW_CHANGES', False)
    status_color = "green" if not allow_changes else "orange"
    status_text = "АКТИВНА" if not allow_changes else "ПРИОСТАНОВЛЕНА"
    
    st.markdown(f"""
    <div style="background-color: {status_color}; padding: 10px; border-radius: 5px; color: white; text-align: center; font-weight: bold;">
        Защита контента: {status_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Выводим информацию о защищенных файлах
    content_protection.display_protected_files_info()
    
    # Управление статусом защиты
    st.subheader("Управление статусом защиты")
    
    cols = st.columns(2)
    
    with cols[0]:
        if st.button("Включить защиту", disabled=not allow_changes):
            content_protection.set_allow_changes(False)
            st.success("Защита контента активирована")
            time.sleep(1)
            st.rerun()
    
    with cols[1]:
        if st.button("Отключить защиту", disabled=allow_changes):
            st.warning("⚠️ Защита будет отключена. Не забудьте включить ее обратно после внесения изменений!")
            content_protection.set_allow_changes(True)
            time.sleep(1)
            st.rerun()
    
    # Проверка целостности контента
    st.subheader("Проверка целостности контента")
    
    if st.button("Запустить проверку"):
        with st.spinner("Проверка целостности контента..."):
            # Временно включаем проверку даже если флаг разрешения установлен
            original_allow = content_protection.ALLOW_CHANGES
            content_protection.ALLOW_CHANGES = False
            
            if content_protection.verify_content_protection():
                st.success("✅ Все файлы соответствуют сохраненным хешам.")
            else:
                st.error("⚠️ Обнаружены измененные файлы. Рекомендуется создать резервную копию или обновить хеши.")
            
            # Восстанавливаем оригинальное значение
            content_protection.ALLOW_CHANGES = original_allow
    
    # Управление резервными копиями
    st.subheader("Резервные копии")
    
    backup_dir = "backups"
    if os.path.exists(backup_dir):
        backups = [d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d)) and "content_protection" in d]
        backups.sort(reverse=True)
        
        if backups:
            st.write("Существующие резервные копии:")
            for backup in backups:
                st.write(f"- {backup}")
        else:
            st.info("Резервных копий пока нет.")
    else:
        st.info("Директория для резервных копий не существует.")
    
    if st.button("Создать новую резервную копию"):
        with st.spinner("Создание резервной копии..."):
            backup_path = content_protection.create_backup_before_changes()
            st.success(f"✅ Резервная копия создана: {backup_path}")
    
    # Расширенные настройки
    with st.expander("Расширенные настройки"):
        st.warning("⚠️ Используйте эти функции с осторожностью!")
        
        # Обновление хешей с осознанием последствий
        st.subheader("Обновление хешей")
        st.info("Эта функция обновит сохраненные хеши в соответствии с текущим состоянием файлов.")
        
        confirm = st.checkbox("Я понимаю, что обновление хешей подтвердит текущее состояние файлов как эталонное")
        
        if confirm and st.button("Обновить хеши"):
            with st.spinner("Обновление хешей..."):
                content_protection.update_protected_hashes()
                st.success("✅ Хеши обновлены для текущего состояния файлов.")
                time.sleep(1)
                st.rerun()


if __name__ == "__main__":
    main()