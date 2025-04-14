#!/usr/bin/env python3
import os
import glob

# Функция для создания изображений с английскими именами
def create_image_copies():
    # Сначала найдем все файлы изображений
    image_files = glob.glob("attached_assets/*.png") 
    
    # Вывод списка всех найденных файлов
    print("Найдены следующие изображения:")
    for img in image_files:
        print(f"- {img}")
    
    # Создадим файлы с английскими именами
    with open("attached_assets/b500_rotation.png", "wb") as f_out:
        for img in image_files:
            if "b500" in img.lower() or "в500" in img.lower() or "500" in img:
                print(f"Обработка файла {img} для B500")
                try:
                    with open(img, "rb") as f_in:
                        f_out.write(f_in.read())
                    print(f"Успешно создан файл b500_rotation.png из {img}")
                    break
                except Exception as e:
                    print(f"Ошибка при обработке {img}: {e}")
    
    with open("attached_assets/b700_sliding.png", "wb") as f_out:
        for img in image_files:
            if "b700" in img.lower() or "в700" in img.lower() or "700" in img:
                print(f"Обработка файла {img} для B700")
                try:
                    with open(img, "rb") as f_in:
                        f_out.write(f_in.read())
                    print(f"Успешно создан файл b700_sliding.png из {img}")
                    break
                except Exception as e:
                    print(f"Ошибка при обработке {img}: {e}")

if __name__ == "__main__":
    create_image_copies()