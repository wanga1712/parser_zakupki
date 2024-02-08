# Импортируем модули для работы с файлами и xml
import os
import logging
import zipfile
import xml.etree.ElementTree as ET

from custom_logger import LoggerConfig
from config import ConfigSettings

# Определяем класс для удаления файлов
class FileRemover:

    # Конструктор класса принимает путь к папке и кортеж с ИНН

    def __init__(self, xml_zip_dr: (str), extract_dir_xml: (str),
                 pdf_zip_dir: (str), extract_dir_pdf: (str), set_inn: (tuple)) -> None:


        # Конфигурация логгера для ведения журнала событий
        self.logger = logging.getLogger(__name__)  # Получение логгера для текущего модуля
        LoggerConfig.configure_logger(self.logger)  # Настройка логгера согласно конфигурации

    # Метод для удаления zip-файла и xml-файла по условию
    def remove_files(self):
        # Получаем список файлов в папке
        files = os.listdir(self.folder)
        # Проходим по каждому файлу
        for file in files:
            # Получаем полный путь к файлу
            file_path = os.path.join(self.folder, file)
            # Проверяем, является ли файл zip-файлом
            if file.endswith(".zip"):
                # Пытаемся открыть zip-файл
                try:
                    with zipfile.ZipFile(file_path, "r") as zip_file:
                        # Получаем список файлов внутри zip-файла
                        zip_files = zip_file.namelist()
                        # Проходим по каждому файлу внутри zip-файла
                        for zip_file in zip_files:
                            # Проверяем, является ли файл xml-файлом
                            if zip_file.endswith(".xml"):
                                # Пытаемся открыть xml-файл
                                try:
                                    with zip_file.open(zip_file, "r") as xml_file:
                                        # Парсим xml-файл
                                        tree = ET.parse(xml_file)
                                        # Получаем корневой элемент
                                        root = tree.getroot()
                                        # Ищем элемент с тегом ИНН
                                        inn = root.find("ИНН")
                                        # Проверяем, есть ли такой элемент
                                        if inn is not None:
                                            # Проверяем, совпадает ли значение ИНН с кортежем
                                            if inn.text in self.inn_tuple:
                                                # Удаляем zip-файл и xml-файл
                                                os.remove(file_path)
                                                os.remove(os.path.join(self.folder, zip_file))
                                                # Выводим сообщение об успешном удалении
                                                print(f"Удален zip-файл {file_path} и xml-файл {zip_file}")
                                # Обрабатываем исключение при открытии xml-файла
                                except Exception as e:
                                    # Выводим сообщение об ошибке
                                    print(f"Не удалось открыть xml-файл {zip_file}: {e}")
                # Обрабатываем исключение при открытии zip-файла
                except Exception as e:
                    # Выводим сообщение об ошибке
                    print(f"Не удалось открыть zip-файл {file_path}: {e}")



______________
# Импортируем модули для работы с json и xml
import json
import xml.etree.ElementTree as ET

# Открываем файл json в режиме чтения
with open("inn.json", "r") as json_file:
    # Преобразуем содержимое файла в кортеж с ИНН
    inn_tuple = tuple(json.load(json_file))

# Открываем файл xml в режиме чтения
with open("data.xml", "r") as xml_file:
    # Парсим xml-данные
    tree = ET.parse(xml_file)
    # Получаем корневой элемент
    root = tree.getroot()
    # Ищем элемент с тегом ИНН
    inn = root.find("ИНН")
    # Проверяем, есть ли такой элемент
    if inn is not None:
        # Проверяем, совпадает ли значение ИНН с кортежем
        if inn.text in inn_tuple:
            # Удаляем файлы
            os.remove("data.xml")
            os.remove("data.zip")
            # Выводим сообщение об успешном удалении
            print("Удалены файлы data.xml и data.zip")

# Открываем файл json в режиме записи
with open("inn.json", "w") as json_file:
    # Сохраняем измененные данные в файле
    json.dump(list(inn_tuple), json_file)
