#!/usr/bin/env python3
"""
Скрипт для подготовки ресурсов для PDF-генератора.
Копирует необходимые файлы (логотип, шрифты) в соответствующие директории.
"""

import os
import shutil
import sys


def prepare_pdf_assets():
    """
    Подготавливает все необходимые ресурсы для PDF-генератора:
    - Создает директорию assets_for_pdf если её нет
    - Копирует логотип из assets/ в assets_for_pdf/
    - Проверяет наличие шрифтов
    """
    print("Подготовка ресурсов для PDF-генератора...")
    
    # Создаем директорию assets_for_pdf
    if not os.path.exists('assets_for_pdf'):
        os.makedirs('assets_for_pdf')
        print("Создана директория assets_for_pdf/")

    # Копируем логотип
    if os.path.exists('assets/logo.png') and (
            not os.path.exists('assets_for_pdf/logo.png') or 
            os.path.getmtime('assets/logo.png') > os.path.getmtime('assets_for_pdf/logo.png')):
        try:
            shutil.copy('assets/logo.png', 'assets_for_pdf/logo.png')
            print("Логотип успешно скопирован в assets_for_pdf/logo.png")
        except Exception as e:
            print(f"Ошибка при копировании логотипа: {e}")
    else:
        if os.path.exists('assets_for_pdf/logo.png'):
            print("Логотип уже существует в assets_for_pdf/")
        else:
            print("ВНИМАНИЕ: Исходный файл logo.png не найден в директории assets/")
    
    # Проверяем наличие директории fonts
    if not os.path.exists('fonts'):
        os.makedirs('fonts')
        print("Создана директория fonts/")
    
    # Проверяем шрифты
    fonts_path = 'fonts'
    required_fonts = ['DejaVuSans.ttf', 'DejaVuSans-Bold.ttf']
    
    for font in required_fonts:
        font_path = os.path.join(fonts_path, font)
        if not os.path.exists(font_path):
            # Пытаемся найти шрифт в системе
            usr_share_fonts = '/usr/share/fonts/truetype/dejavu'
            if os.path.exists(usr_share_fonts):
                src_path = os.path.join(usr_share_fonts, font)
                if os.path.exists(src_path):
                    try:
                        shutil.copy(src_path, font_path)
                        print(f"Шрифт {font} скопирован из системы")
                    except Exception as e:
                        print(f"Ошибка при копировании шрифта {font}: {e}")
                else:
                    print(f"ВНИМАНИЕ: Шрифт {font} не найден в системе")
            else:
                print(f"ВНИМАНИЕ: Шрифт {font} отсутствует")
        else:
            print(f"Шрифт {font} найден")
    
    print("Подготовка ресурсов для PDF-генератора завершена")
    
    # Возвращаем True если все ресурсы готовы
    return (os.path.exists('assets_for_pdf/logo.png') and 
            all(os.path.exists(os.path.join(fonts_path, font)) for font in required_fonts))


if __name__ == "__main__":
    # Если запускаем скрипт напрямую
    success = prepare_pdf_assets()
    sys.exit(0 if success else 1)