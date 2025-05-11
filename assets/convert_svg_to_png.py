#!/usr/bin/env python3
"""
Скрипт для конвертации SVG в PNG с помощью CairoSVG.
Используется для создания логотипа компании в формате PNG для PDF-документов.
"""

import os
import cairosvg

def convert_svg_to_png(svg_path, png_path, width=None, height=None):
    """
    Конвертирует SVG-файл в PNG.
    
    Args:
        svg_path (str): Путь к SVG-файлу
        png_path (str): Путь для сохранения PNG-файла
        width (int, optional): Ширина выходного изображения
        height (int, optional): Высота выходного изображения
    """
    # Создаем директорию для выходного файла, если она не существует
    output_dir = os.path.dirname(png_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Конвертируем SVG в PNG
    print(f"Конвертация {svg_path} в {png_path}")
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width, output_height=height)
    print(f"Конвертация завершена. Файл сохранен: {png_path}")

if __name__ == "__main__":
    # Конвертируем логотип
    svg_path = "assets/logo.svg"
    png_path = "assets/logo.png"
    convert_svg_to_png(svg_path, png_path, width=400, height=120)
    
    # Создаем версию с белым фоном для использования в PDF
    svg_path = "assets/logo.svg"
    png_path = "assets/logo_white_bg.png"
    
    # Создаем SVG с белым фоном
    with open(svg_path, 'r') as f:
        svg_content = f.read()
    
    # Заменяем прозрачный фон на белый для версии с белым фоном
    svg_with_bg = svg_content.replace('fill="none"', 'fill="#FFFFFF"')
    
    # Сохраняем во временный файл
    temp_svg_path = "assets/temp_logo_with_bg.svg"
    with open(temp_svg_path, 'w') as f:
        f.write(svg_with_bg)
    
    # Конвертируем в PNG
    convert_svg_to_png(temp_svg_path, png_path, width=400, height=120)
    
    # Удаляем временный файл
    if os.path.exists(temp_svg_path):
        os.remove(temp_svg_path)