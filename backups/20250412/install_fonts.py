import urllib.request
import os

# Создаем директорию для шрифтов, если её нет
fonts_dir = 'fonts'
os.makedirs(fonts_dir, exist_ok=True)

# Список шрифтов для загрузки
fonts = [
    'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf',
    'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf'
]

# Загружаем каждый шрифт
for font_url in fonts:
    font_name = os.path.basename(font_url)
    font_path = os.path.join(fonts_dir, font_name)
    
    # Загружаем только если файл ещё не существует
    if not os.path.exists(font_path):
        print(f"Загрузка шрифта {font_name}...")
        try:
            urllib.request.urlretrieve(font_url, font_path)
            print(f"Шрифт {font_name} успешно загружен")
        except Exception as e:
            print(f"Ошибка при загрузке шрифта {font_name}: {str(e)}")
    else:
        print(f"Шрифт {font_name} уже существует")