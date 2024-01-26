import logging  # импортируем модуль logging
import os
import zipfile
import shutil  # Импорт модуля shutil
import py7zr  # модуль для определения кодировки для распаковки файлов в 7z

from custom_logger import LoggerConfig
from config import ConfigSettings


class Extract():
    '''
    Класс Extract предназначен для распаковки zip-файлов, содержащих xml-и
    pdf - документов, из одной папки в другую, класс получает значения для атрибутов из модуля
    config.
        Параметры:
            :param xml_zip_dr: путь к папке с архивами zip, содержащими xml-документы
            :param extract_dir_xml: путь к папке, куда извлекаются xml - документы
            :param pdf_zip_dir: путь к папке с архивами zip, содкржащими pdf - докумменты
            :param extract_dir_pdf: путь к папке, куда распаковываются pdf - документы
            :param logger (logging.Logger): объект логгера для ведения журнала событий
        Методы:
            init((self, xml_zip_dr, extract_dir_xml, pdf_zip_dir, extract_dir_pdf): конструктор
                класса, принимает четыре аргумента и присваивает их атрибутам класса, а также настривает
                логгер.
            extract_xml(self): метод для распаковки zip-файлов с xml-документами из папки xml_zip_dr
                в папку extract_dir_xml испольузя модуль zipfile. В случае успеха выдает сообщение
                о успешной распаковки файлов в директорию, иначе выдает ошибку через логгер.
    '''

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
        # Конфигурация логгера для ведения журнала событий
        self.logger = logging.getLogger(__name__)  # Получение логгера для текущего модуля
        LoggerConfig.configure_logger(self.logger)  # Настройка логгера согласно конфигурации

    def extract_xml(self):
        '''
        Метод для распаковки zip-файлов с xml-документами из папки xml_zip_dr в папку extract_dir_xml.
            Использует модуль zipfile для работы с архивами.
            В случае успеха записывает в логгер информацию о распакованных файлах,
            в случае ошибки записывает в логгер сообщение об ошибке.
            Также выводит на экран значение атрибута xml_zip_dr.
        :return:
        '''
        print('функция запущена')
        try:
            for filename in os.listdir(self.xml_zip_dr):
                if filename.endswith('.zip'):
                    zip_path = os.path.join(self.xml_zip_dr, filename)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(self.extract_dir_xml)
            self.logger.info(f"Файлы успешно распакованы в директорию: {self.extract_dir_xml}")

        except Exception as e:
            self.logger.error(f"Ошибка распаковки ZIP файлов: {e}")

    def extract_documents(self):
        '''
        Функция распаковывает находящиеся в локальной папке pdf_zip_dir
        файлы из архивов .ZIP и 7Z.
        Распакованные файлы пеермещает в папку extract_dir_pdf
         в эту же папку переносит документы находящиеся вне архива, в форматах
         '.pdf', '.docx', '.xlsx', '.doc'
        :return: None
        '''
        try:
            # Создаем список возможных расширений документов
            extensions = ['.pdf', '.docx', '.xlsx', '.doc']
            # Перебираем все файлы в исходной папке
            for filename in os.listdir(self.pdf_zip_dir):
                # Получаем полный путь к файлу
                file_path = os.path.join(self.pdf_zip_dir, filename)
                # Проверяем, является ли файл архивом
                try:
                    if filename.endswith('.zip'):
                        # Открываем архив на чтение
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            # Извлекаем все файлы из архива в целевую папку
                            zip_ref.extractall(self.extract_dir_pdf)
                        self.logger.info(
                            f"Документы формата zip найдены и перемещены в директорию: {self.extract_dir_pdf}")
                    else:
                        # Добавляем сообщение self.debug, если не было исключений
                        self.logger.debug(f'Документы формата .zip не найдены в директории: {self.pdf_zip_dir}')

                except Exception as e:
                    self.logger.error(f"Произошла ошибка при распаковке файлов .zip: {e}")
                try:
                    if filename.endswith(".7z"):
                        with py7zr.SevenZipFile(file_path, mode='r') as z:
                            # Извлекаем только файлы, которые заканчиваются на .pdf
                            z.extract(path=self.extract_dir_pdf)
                        self.logger.info(
                            f"Документы формата 7z найдены и перемещены в директорию: {self.extract_dir_pdf}")
                    else:
                        # Добавляем сообщение self.debug, если не было исключений
                        self.logger.debug(f'Документы формата .7z не найдены в директории: {self.pdf_zip_dir}')

                except Exception as e:
                    self.logger.error(f"документы не найдены или произошла ошибка: {e}")
                try:
                    # Проверяем, является ли файл документом
                    if any(filename.endswith(ext) for ext in extensions):
                        # Перемещаем файл в целевую папку
                        shutil.move(file_path, self.extract_dir_pdf)
                        self.logger.info(
                            f"Документы не архивного формата найдены и перемещены в директорию: {self.extract_dir_pdf}")
                    else:
                        # Добавляем сообщение self.debug, если не было исключений
                        self.logger.debug(f'Не архивные документы не найдены в директории: {self.pdf_zip_dir}')

                except Exception as e:
                    self.logger.debug(f"документы не найдены или произошла ошибка: {e}")

        except Exception as e:
            # Выводим сообщение об ошибке
            self.logger.error(f"Ошибка при работе с документами: {e}")


# Функция запуска методов класса из модуля
def extract():
    extractor = Extract(ConfigSettings.get_config_value('xml_zip_local_directory'),
                        ConfigSettings.get_config_value('xml_output_local_directory'),
                        ConfigSettings.get_config_value('pdf_zip_archive_local_directory'),
                        ConfigSettings.get_config_value(
                            'pdf_output_local_directory'))
    extractor.extract_xml()
    extractor.extract_documents()

# extractor = Extract(ConfigSettings.get_config_value('xml_zip_local_directory'),
#                     ConfigSettings.get_config_value('xml_output_local_directory'),
#                     ConfigSettings.get_config_value('pdf_zip_archive_local_directory'),
#                     ConfigSettings.get_config_value(
#                         'pdf_output_local_directory'))  # создаем экземпляр класса Extract с аргументами из класса ConfigSettings
#
# extractor.extract_xml()  # вызываем функцию extract_xml у экземпляра
