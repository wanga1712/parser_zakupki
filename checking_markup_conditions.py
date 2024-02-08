import os
import logging
import zipfile
from bs4 import BeautifulSoup

from config import local_directory
from config import extracted_path
from config import expected_inn
from custom_logger import LoggerConfig

class FileProcessor:
    def __init__(self, zip_path=None):
        # Конструктор класса, принимает логгер для записи сообщений
        # Конфигурация логгера для ведения журнала событий
        # self.zip_path = local_directory
        self.zip_path = zip_path
        self.extracted_path = extracted_path
        self.expected_inn = expected_inn
        self.expected_inn = expected_inn  # Инициализация expected_inn здесь
        self.extracted_path = extracted_path
        self.logger = logging.getLogger(__name__)  # Получение логгера для текущего модуля
        LoggerConfig.configure_logger(self.logger)  # Настройка логгера согласно конфигурации


    # В вашем методе process_file
    def process_file(self, *args):
        # zip_path - путь к ZIP-архиву, который нужно распаковать
        # extracted_path - директория, куда будет распакован содержимое архива
        # expected_inn - ожидаемое значение INN для проверки в XML файле
        # Открытие и распаковка ZIP-архива в указанную директорию
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.extracted_path)

        # Поиск XML файла в распакованной директории
        xml_file = next((f for f in os.listdir(self.extracted_path) if f.endswith('.xml')), None)
        if xml_file:
            # Если XML файл найден, формируем полный путь к файлу
            xml_path = os.path.join(self.extracted_path, xml_file)
            # Переменная для хранения результата проверки условия
            condition_met = False

            # Открытие XML файла и его чтение с использованием BeautifulSoup для парсинга
            with open(xml_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'xml')
                # Вызов функции condition_check для проверки соответствия содержимого XML файла ожидаемому значению INN
                condition_met = self.condition_check(soup, self.expected_inn)

            # Файл xml_path теперь закрыт, так как мы вышли из блока with
            if condition_met:
                # Если условие выполнено, удаляем ZIP-архив
                os.remove(self.zip_path)
                self.logger.info(f'Archive deleted: {self.zip_path}')
            else:
                # Если условие не выполнено, удаляем распакованный XML файл и ZIP-архив
                os.remove(xml_path)
                os.remove(self.zip_path)
                self.logger.info(f'\nXML file deleted: {xml_path}\nArchive deleted: {self.zip_path}')
        else:
            # Если XML файл не найден, записываем ошибку в лог
            self.logger.error(f'No XML file found in the archive: {self.zip_path}')

    def condition_check(self, soup):
        # Находим тег <inn> в документе XML
        inn_tag = soup.find('inn')
        # Проверяем, существует ли тег и равно ли его содержимое (как строка) ожидаемому значению (также как строка)
        return inn_tag is not None and inn_tag.text == str(self.expected_inn)


# Определение локальной директории для сохранения скачанных файлов
# zip_path = local_directory

# Создание экземпляра класса и вызов метода process_file
my_instance = FileProcessor()
my_instance.process_file()

# Определение локальной директории для сохранения скачанных файлов
# local_directory = r'C:\Users\wangr\OneDrive\Документы\тест'


# def condition_check(soup, expected_inns):
#     # Находим тег <inn> в документе XML
#     inn_tag = soup.find('inn')
#     # Проверяем, существует ли тег и содержится ли его содержимое в списке ожидаемых значений INN
#     return inn_tag is not None and inn_tag.text in map(str, expected_inns)
