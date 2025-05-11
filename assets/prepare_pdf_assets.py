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

    # Копируем логотип - ищем в разных директориях и с разными именами
    logo_paths = [
        'assets/logo.png',
        'assets/logo.jpg',
        'assets/pergola_logo.png',
        'assets/pergola_logo.jpg',
        'assets_for_pdf/logo.png',
        'assets/pergola_b500.jpg',  # используем как запасной вариант
        'assets/pergola_b700.jpg',  # используем как запасной вариант
        'attached_assets/logo.png',
        'attached_assets/logo.jpg'
    ]
    
    # Флаг, показывающий, что логотип нашли и скопировали
    logo_found = False
    
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                if not logo_path.startswith('assets_for_pdf/'):  # Если нашли не в директории назначения
                    shutil.copy(logo_path, 'assets_for_pdf/logo.png')
                    print(f"Логотип успешно скопирован из {logo_path} в assets_for_pdf/logo.png")
                else:
                    print("Логотип уже существует в директории assets_for_pdf/")
                logo_found = True
                break  # Прекращаем поиск, если нашли логотип
            except Exception as e:
                print(f"Ошибка при копировании логотипа из {logo_path}: {e}")
    
    # Если логотип не найден ни в одном из указанных мест, создаем заглушку
    if not logo_found and not os.path.exists('assets_for_pdf/logo.png'):
        print("ВНИМАНИЕ: Логотип не найден ни в одной из директорий. Копируем любое доступное изображение.")
        # Ищем любое изображение в директории assets или attached_assets
        image_found = False
        for dir_path in ['assets', 'attached_assets']:
            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)
                    if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        try:
                            shutil.copy(file_path, 'assets_for_pdf/logo.png')
                            print(f"Копирование альтернативного изображения из {file_path} в assets_for_pdf/logo.png")
                            image_found = True
                            break
                        except Exception as e:
                            print(f"Ошибка при копировании альтернативного изображения: {e}")
                if image_found:
                    break
        
        if not image_found:
            print("ВНИМАНИЕ: Не удалось найти ни одного изображения для логотипа!")
    
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