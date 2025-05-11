"""
Модуль для парсинга PDF-файлов с коммерческими предложениями.
Позволяет извлекать данные из PDF-файлов, чтобы использовать их в приложении.
"""

import re
import logging
import os
from typing import Dict, Any, List, Optional, Tuple

from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4

# Настройка логирования
logger = logging.getLogger(__name__)


class PdfParser:
    """Класс для парсинга PDF-файлов с коммерческими предложениями."""
    
    def __init__(self, pdf_path: str):
        """
        Инициализирует парсер с путем к PDF-файлу.
        
        Args:
            pdf_path (str): Путь к PDF-файлу
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF-файл не найден: {pdf_path}")
        
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        self.text = ""
        self._extract_text()
    
    def _extract_text(self) -> None:
        """Извлекает текст из всех страниц PDF-файла."""
        try:
            for page in self.reader.pages:
                self.text += page.extract_text() + "\n"
            logger.debug(f"Текст успешно извлечен из PDF: {self.pdf_path}")
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста: {e}")
            raise
    
    def extract_header_info(self) -> Dict[str, Any]:
        """
        Извлекает основную информацию из заголовка коммерческого предложения.
        
        Returns:
            Dict[str, Any]: Словарь с параметрами перголы
        """
        header_info = {}
        
        # Извлечение модели
        model_match = re.search(r"Модель:\s*(\w+)", self.text)
        if model_match:
            header_info["model"] = model_match.group(1)
        
        # Извлечение ширины
        width_match = re.search(r"Ширина:\s*([\d.]+)\s*м", self.text)
        if width_match:
            header_info["width"] = float(width_match.group(1))
        
        # Извлечение длины (выноса)
        length_match = re.search(r"Длина\s*\(вынос\):\s*([\d.]+)\s*м", self.text)
        if length_match:
            header_info["length"] = float(length_match.group(1))
        
        # Извлечение количества модулей
        modules_match = re.search(r"Количество модулей:\s*(\d+)", self.text)
        if modules_match:
            header_info["modules"] = int(modules_match.group(1))
        
        # Извлечение информации о ламелях
        lamella_match = re.search(r"Ламели\s+(\d+)\s+мм", self.text)
        if lamella_match:
            header_info["lamella_size"] = int(lamella_match.group(1))
        
        # Поиск количества ламелей
        lamella_count_match = re.search(r"Количество ламелей\s*-\s*(\d+)\s*шт", self.text)
        if lamella_count_match:
            header_info["lamella_count"] = int(lamella_count_match.group(1))
        
        logger.info(f"Извлечена информация из заголовка: {header_info}")
        return header_info
    
    def extract_price_info(self) -> Dict[str, float]:
        """
        Извлекает информацию о ценах из коммерческого предложения.
        
        Returns:
            Dict[str, float]: Словарь с ценами
        """
        price_info = {}
        
        # Извлечение общей стоимости
        total_match = re.search(r"ИТОГО:\s*([\d\s.,]+)[\s₽]", self.text)
        if total_match:
            price_str = total_match.group(1).replace(" ", "").replace(",", ".")
            price_info["total"] = float(price_str)
        
        # Извлечение скидки
        discount_match = re.search(r"СКИДКА:\s*([\d\s.,]+)[\s₽]", self.text)
        if discount_match:
            discount_str = discount_match.group(1).replace(" ", "").replace(",", ".")
            price_info["discount"] = float(discount_str)
        
        # Извлечение итоговой стоимости со скидкой
        final_match = re.search(r"ИТОГО СО СКИДКОЙ:\s*([\d\s.,]+)[\s₽]", self.text)
        if final_match:
            final_str = final_match.group(1).replace(" ", "").replace(",", ".")
            price_info["final"] = float(final_str)
        
        # Извлечение цен на опции
        drive_match = re.search(r"Привод\s+.*?(\d[\d\s.,]+)[\s₽]", self.text)
        if drive_match:
            drive_str = drive_match.group(1).replace(" ", "").replace(",", ".")
            price_info["drive"] = float(drive_str)
        
        remote_match = re.search(r"Пульт ДУ\s+.*?(\d[\d\s.,]+)[\s₽]", self.text)
        if remote_match:
            remote_str = remote_match.group(1).replace(" ", "").replace(",", ".")
            price_info["remote"] = float(remote_str)
        
        delivery_match = re.search(r"Доставка\s+.*?(\d[\d\s.,]+)[\s₽]", self.text)
        if delivery_match:
            delivery_str = delivery_match.group(1).replace(" ", "").replace(",", ".")
            price_info["delivery"] = float(delivery_str)
        
        installation_match = re.search(r"Установка\s+.*?(\d[\d\s.,]+)[\s₽]", self.text)
        if installation_match:
            installation_str = installation_match.group(1).replace(" ", "").replace(",", ".")
            price_info["installation"] = float(installation_str)
        
        logger.info(f"Извлечена информация о ценах: {price_info}")
        return price_info
    
    def extract_specification(self) -> List[Dict[str, Any]]:
        """
        Извлекает спецификацию из коммерческого предложения.
        
        Returns:
            List[Dict[str, Any]]: Список словарей с параметрами элементов спецификации
        """
        spec_items = []
        
        # Ищем секцию спецификации
        spec_section_match = re.search(r"Спецификация перголы:.*?Примечания:", self.text, re.DOTALL)
        if not spec_section_match:
            logger.warning("Секция спецификации не найдена")
            return spec_items
        
        spec_section = spec_section_match.group(0)
        
        # Разбиваем на строки и обрабатываем каждую строку
        for line in spec_section.split('\n'):
            # Ищем строки, содержащие название и количество
            item_match = re.search(r"([^\d]+)(\d+\s*(?:шт|модуль)?\.?)", line)
            if item_match:
                name = item_match.group(1).strip()
                quantity_str = item_match.group(2).strip()
                
                # Извлекаем числовое значение из строки количества
                quantity_match = re.search(r"(\d+)", quantity_str)
                quantity = int(quantity_match.group(1)) if quantity_match else 1
                
                if name and not name.startswith("Количество"):
                    spec_items.append({
                        "name": name,
                        "quantity": quantity,
                        "unit": "шт." if "шт" in quantity_str else "модуль" if "модуль" in quantity_str else ""
                    })
        
        logger.info(f"Извлечена спецификация: {spec_items}")
        return spec_items
    
    def extract_all_data(self) -> Dict[str, Any]:
        """
        Извлекает все данные из коммерческого предложения.
        
        Returns:
            Dict[str, Any]: Полная информация из PDF
        """
        data = {
            "header": self.extract_header_info(),
            "prices": self.extract_price_info(),
            "specification": self.extract_specification()
        }
        
        # Извлечение даты
        date_match = re.search(r"сформировано:\s*(\d{2}\.\d{2}\.\d{4})", self.text)
        if date_match:
            data["date"] = date_match.group(1)
        
        # Дополнительные примечания
        notes_match = re.search(r"Примечания:(.*?)(?:Компания|$)", self.text, re.DOTALL)
        if notes_match:
            notes_text = notes_match.group(1).strip()
            notes = [note.strip() for note in notes_text.split("\n") if note.strip()]
            data["notes"] = notes
        
        return data


def parse_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Обертка для парсинга PDF-файла.
    
    Args:
        pdf_path (str): Путь к PDF-файлу
    
    Returns:
        Dict[str, Any]: Извлеченные данные из PDF
    """
    try:
        parser = PdfParser(pdf_path)
        return parser.extract_all_data()
    except Exception as e:
        logger.error(f"Ошибка при парсинге PDF: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Пример использования
    import json
    
    logging.basicConfig(level=logging.INFO)
    pdf_path = "path/to/your.pdf"
    
    if os.path.exists(pdf_path):
        result = parse_pdf(pdf_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Файл не найден: {pdf_path}")