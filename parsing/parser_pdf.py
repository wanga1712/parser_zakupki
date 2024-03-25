# Импортируем модуль os для работы с файлами и папками
import os

from docx import Document
from loguru import logger
from config import ConfigSettings


# Определяем класс FileChecker
class FileChecker:
    """
    Класс для проверки типов файлов в папке и запуска разных функций в зависимости от типа.
    """

    # Определяем конструктор класса
    def __init__(self, xml_zip_dr: (str) = None, extract_dir_xml: (str) = None,
                 pdf_zip_dir: (str) = None, extract_dir_pdf: (str) = None) -> None:
        '''
        Конструктор класса Extract. Значения для аргументов заданы как необязательные,
        для применения аргументов в дочерних классах по одному
            Аргументы
                :param xml_zip_dr (str): путь к папке с архивами zip, содержащими xml-документы
                :param extract_dir_xml (str): путь к папке, куда извлекать xml-документы
                :param pdf_zip_dir (str): путь к папке с архивами zip, содержащими pdf-документы
                :param extract_dir_pdf (str): путь к папке, куда извлекать pdf-документы
        '''
        # присваиваем аргументы конструктора атрибутам класса
        self.xml_zip_dr = xml_zip_dr
        self.extract_dir_xml = extract_dir_xml
        self.pdf_zip_dir = pdf_zip_dir
        self.extract_dir_pdf = extract_dir_pdf



    # Определяем метод check_file_type
    def check_file_type(self, file_path):
        """
        Метод для проверки типа файла по его расширению и запуска соответствующей функции для поиска ключевых слов по документу.
        :param file_path: путь к файлу, который нужно проверить
        :return: результат работы соответствующей функции или None, если тип файла не поддерживается
        """
        # Получаем расширение файла из его пути
        file_extension = os.path.splitext(file_path)[1]
        # Проверяем, какое расширение имеет файл
        if file_extension == ".docx":
            # Если файл является документом Word, то запускаем функцию для поиска слов заранее определенных слов для поиска в Word-файле
            # Пока такой функции нет, пусть она будет с pass
            pass
        elif file_extension == ".xlsx":
            # Если файл является документом Excel, то запускаем функцию для работы с Excel-файлами
            # Пока такой функции нет, пусть она будет с pass
            pass
        elif file_extension == ".pdf":
            # Если файл является документом PDF, то запускаем функцию для работы с PDF-файлами
            # Эта функция уже определена выше, мы можем использовать ее
            return self.extract_search_phrase_pdf(file_path)
        else:
            # Если файл имеет другое расширение, то возвращаем None, так как тип файла не поддерживается
            return None

    # Определяем метод extract_search_phrase_pdf
    def extract_search_phrase_pdf(self, file_path):
        """
        Метод для парсинга и извлечения данных из файла PDF, сверяет на словосочетание в тексте
        документа и возвращает строку с найденным текстом и название документа.

        :param file_path: принимает путь до файла PDF
        :return: возвращает найденную строку в документе целиком, если она содержит в себе указанное слово,
         и наименование файла в котором найдено слово.
        """
        # Здесь вы можете использовать код, который я показал вам ранее, для работы с PDF-файлами
        # Я не буду повторять его здесь, чтобы сэкономить место
        pass

    def extract_search_phrase_word(self, file_path, search_terms):
        """
        Метод для парсинга и извлечения данных из файла Word, сверяет на словосочетание в тексте
        документа и возвращает строку с найденным текстом и название документа.

        :param file_path: принимает путь до файла Word
        :return: возвращает найденную строку в документе целиком, если она содержит в себе указанное слово,
         и наименование файла в котором найдено слово.
        """
        try:
            doc = Document(file_path)
            found_terms = {}
            for paragraph in doc.paragraphs:
                for term in paragraph.text:
                    if term in paragraph.text:
                        if term not in found_terms:
                            found_terms[term].append(paragraph.text)

            for term, sentences in found_terms.items():
                for sentence in sentences:
                    logger.info(f'Найдено "{term}" в файле {file_path}: {sentence}')

            if not found_terms:
                logger.info(f'Слова или словосочетания из списка не найдены в файле {file_path}')

        except Exception as e:
            logger.error(f'Ошибка при поиске в файле {file_path}: {e}')




search_terms ={'свето', 'светильник', 'светодиод', 'композит', 'периль', 'лоток', 'подвесной', 'стеклопластик'}

def FileChecker():
    extractor = FileChecker(ConfigSettings.get_config_value('xml_zip_local_directory'),
                        ConfigSettings.get_config_value('xml_output_local_directory'),
                        ConfigSettings.get_config_value('pdf_zip_archive_local_directory'),
                        ConfigSettings.get_config_value(
                            'pdf_output_local_directory'))
    extractor.extract_xml()
    extractor.extract_documents()