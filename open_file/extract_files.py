  # импортируем модуль logging
import os
import shutil  # предоставляет ряд высокоуровневых операций с файлами
# и коллекциями файлов. Он используется для копирования, перемещения и удаления файлов, а также для работы с директориями
import zipfile
import py7zr  # модуль для определения кодировки для распаковки файлов в 7z
import rarfile

from loguru import logger
from config import ConfigSettings


class Extract():
    '''
    Класс Extract предназначен для распаковки zip, rar - файлов, содержащих xml-и
    pdf - документов, из одной папки в другую, класс получает значения для атрибутов из модуля
    config.
        Параметры:
            :param xml_zip_local_directory (str): путь до папки содержащей ZIP архивы документов XML
            :param xml_unpacked_local_directory (str): путь до папки для распакованных документов XML
            :param zip_archive_local_directory (str): путь до папки содержащей ZIP архивы документов скачанные с ЕИС
            :param unpacked_output_local_directory (str): путь до папки для распаковванных ZIP архивов документов PDF
        Методы:
            init((self): конструктор класса, принимает аргументы из модуля config, класса ConfigSettings.
    '''

    def __init__(self):
        '''
        Конструктор класса Extract. Получает из модуля config, класса ConfigSettings локальный путь
        до папок с архивными и распакованными документами XML, Word, PDF, Excel.
        '''
        # присваиваем аргументы конструктора атрибутам класса
        self.settings = ConfigSettings()


    def extract_xml(self):
        '''
        Метод для распаковки zip-файлов с xml-документами из папки xml_zip_dr в папку extract_dir_xml.
            Использует модуль zipfile для работы с архивами.
            В случае успеха записывает в логгер информацию о распакованных файлах,
            в случае ошибки записывает в логгер сообщение об ошибке.
            Также выводит на экран значение атрибута xml_zip_dr.
        :return:
        '''
        logger.debug('Функция запущена')
        xml_zip_dir = self.settings.xml_zip_local_directory
        xml_unpacked_dir = self.settings.xml_unpacked_directory
        try:
            for filename in os.listdir(xml_zip_dir):
                if filename.endswith('.zip'):
                    zip_path = os.path.join(xml_zip_dir, filename)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(xml_unpacked_dir)
            logger.info(f"Файлы успешно распакованы в директорию: {xml_unpacked_dir}")

        except Exception as e:
            logger.error(f"Ошибка распаковки ZIP файлов: {e}")
            #TODO--> этот метод должен будет запускаться первым, для извлечения данных из файла XML

    def extract_documents(self):
        '''
        Функция распаковывает находящиеся в локальной папке zip_archive_local_directory
        файлы из архивов .ZIP, .RAR и .7Z.
        Распакованные файлы пеермещает в папку extract_dir_pdf
         в эту же папку переносит документы находящиеся вне архива, в форматах
         '.pdf', '.docx', '.xlsx', '.doc'
        :return: None
        '''
        logger.debug('Функция запущена')
        zip_archive_local_dir = self.settings.zip_archive_local_directory
        unpack_output_local_dir = self.settings.unpacked_output_local_directory
        try:
            # Создаем список возможных расширений документов
            extensions = ['.pdf', '.docx', '.xlsx', '.doc']
            # Перебираем все файлы в исходной папке
            for filename in os.listdir(zip_archive_local_dir):
                # Получаем полный путь к файлу
                file_path = os.path.join(zip_archive_local_dir, filename)

                # Проверяем, является ли файл архивом zip
                try:
                    if filename.endswith('.zip'):
                        # Открываем архив на чтение
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            # Извлекаем все файлы из архива в целевую папку
                            zip_ref.extractall(unpack_output_local_dir)
                        logger.info(
                            f"Документы формата zip найдены и перемещены в директорию: {unpack_output_local_dir}")
                    else:
                        # Добавляем сообщение self.debug, если не было исключений
                        self.logger.debug(f'Документы формата .zip не найдены в директории: {zip_archive_local_dir}')
                except Exception as e:
                    logger.error(f"Произошла ошибка при распаковке файлов .zip: {e}")

                # Проверяем, является ли файл архивом rar
                try:
                    if filename.endswith('.rar'):
                        # Открываем архив на чтение
                        with rarfile.RarFile(file_path, 'r') as rar_ref:
                            # Извлекаем все файлы из архива в целевую папку
                            rar_ref.extractall(unpack_output_local_dir)
                        logger.info(
                            f"Документы формата rar найдены и перемещены в директорию: {unpack_output_local_dir}")
                    else:
                        # Добавляем сообщение self.debug, если не было исключений
                        logger.debug(f'Документы формата .zip не найдены в директории: {zip_archive_local_dir}')

                except Exception as e:
                    logger.error(f"Произошла ошибка при распаковке файлов .zip: {e}")

                # Проверяем, является ли файл архивом 7z
                try:
                    if filename.endswith(".7z"):
                        with py7zr.SevenZipFile(file_path, mode='r') as z:
                            # Извлекаем только файлы, которые заканчиваются на .pdf
                            z.extract(path=unpack_output_local_dir)
                        logger.info(
                            f"Документы формата 7z найдены и перемещены в директорию: {unpack_output_local_dir}")
                    else:
                        # Добавляем сообщение self.debug, если не было исключений
                        logger.debug(f'Документы формата .7z не найдены в директории: {zip_archive_local_dir}')

                except Exception as e:
                    logger.error(f"документы не найдены или произошла ошибка: {e}")

                # Проверяем, является ли файл документом
                try:
                    if any(filename.endswith(ext) for ext in extensions):
                        # Перемещаем файл в целевую папку
                        shutil.move(file_path, unpack_output_local_dir)
                        logger.info(
                            f"Документы не архивного формата найдены и перемещены в директорию: {unpack_output_local_dir}")
                    else:
                        # Добавляем сообщение self.debug, если не было исключений
                        logger.debug(f'Не архивные документы не найдены в директории: {zip_archive_local_dir}')

                except Exception as e:
                    logger.debug(f"документы не найдены или произошла ошибка: {e}")

        except Exception as e:
            # Выводим сообщение об ошибке
            logger.error(f"Ошибка при работе с документами: {e}")


# Функция запуска методов класса из модуля
def extract():
    extractor = Extract()
    extractor.extract_xml()
    extractor.extract_documents()

# extractor = Extract(ConfigSettings.get_config_value('xml_zip_local_directory'),
#                     ConfigSettings.get_config_value('xml_output_local_directory'),
#                     ConfigSettings.get_config_value('pdf_zip_archive_local_directory'),
#                     ConfigSettings.get_config_value(
#                         'pdf_output_local_directory'))  # создаем экземпляр класса Extract с аргументами из класса ConfigSettings
#
# extractor.extract_xml()  # вызываем функцию extract_xml у экземпляра
