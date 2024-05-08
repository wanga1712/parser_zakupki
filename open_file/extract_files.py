from loguru import logger
import os
import shutil  # предоставляет ряд высокоуровневых операций с файлами
# и коллекциями файлов. Он используется для копирования, перемещения и удаления файлов, а также для работы с директориями
import zipfile
import py7zr  # модуль для определения кодировки для распаковки файлов в 7z
import rarfile

from config import ConfigSettings

# Установка пути к WinRAR в переменную среды PATH
winrar_path = r"C:\Program Files\WinRAR"
os.environ["PATH"] += os.pathsep + winrar_path


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
        """
        Инициализирует объект класса.
        """
        self.unpacked_directory = ConfigSettings.get_config_value('unpacked_output_local_directory')
        self.zip_directory = ConfigSettings.get_config_value('zip_archive_local_directory')
        self.extensions = ['.pdf', '.docx', '.xlsx', '.doc']

        self.xml_zip_dir = ConfigSettings.get_config_value('xml_zip_local_directory')
        self.xml_unpacked_dir = ConfigSettings.get_config_value('xml_unpacked_local_directory')

    def extract_xml(self):
        '''
        Метод для распаковки zip-файлов с xml-документами из папки xml_zip_dr в папку extract_dir_xml.
            Использует модуль zipfile для работы с архивами.
            В случае успеха записывает в логгер информацию о распакованных файлах,
            в случае ошибки записывает в логгер сообщение об ошибке.
            Также выводит на экран значение атрибута xml_zip_dr.
        :return:
        '''
        logger.debug('Функция запущена extract_xml')
        try:
            for filename in os.listdir(self.xml_zip_dir):
                if filename.endswith('.zip'):
                    zip_path = os.path.join(self.xml_zip_dir, filename)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(self.xml_unpacked_dir)
            logger.info(f"Файлы успешно распакованы в директорию: {self.xml_unpacked_dir}")

        except Exception as e:
            logger.error(f"Ошибка распаковки ZIP файлов: {e}")
            # TODO--> этот метод должен будет запускаться первым, для извлечения данных из файла XML

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
        for root, dirs, files in os.walk(self.zip_directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                target_path = os.path.join(self.unpacked_directory, os.path.relpath(root, self.zip_directory))

                # Убедимся, что целевая директория существует
                os.makedirs(target_path, exist_ok=True)

                try:
                    if filename.endswith('.zip'):
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            for zip_info in zip_ref.infolist():
                                # Попытка декодировать имена файлов с использованием cp866
                                zip_info.filename = zip_info.filename.encode('cp437').decode('cp866')
                                zip_ref.extract(zip_info, target_path)
                        logger.info(f"Zip-файл {filename} извлечен в {target_path}")
                    elif filename.endswith('.rar'):
                        try:
                            with rarfile.RarFile(file_path, 'r') as rar_ref:
                                rar_ref.extractall(target_path)
                            logger.info(f"Rar-файл {filename} извлечен в {target_path}")
                        except rarfile.NeedFirstVolume:
                            logger.error(f"Необходимо начинать извлечение архива из первого тома (текущий: {filename})")
                            break  # Прекратить выполнение извлечения из текущего архива и продолжить обработку остальных файлов
                        except Exception as e:
                            logger.error(f"Ошибка при обработке файла {filename}: {e}")
                    elif filename.endswith('.7z'):
                        with py7zr.SevenZipFile(file_path, mode='r') as z:
                            z.extract(path=target_path)
                        logger.info(f"7z-файл {filename} извлечен в {target_path}")
                    elif any(filename.endswith(ext) for ext in self.extensions):
                        shutil.move(file_path, os.path.join(target_path, filename))
                        logger.info(f"Документ {filename} перемещен в {target_path}")
                    else:
                        logger.debug(f"Файл {filename} не соответствует известным форматам и был проигнорирован.")
                except Exception as e:
                    logger.error(f"Ошибка при обработке файла {filename}: {e}")


# Функция запуска методов класса из модуля
# extractor = Extract()
# extractor.extract_xml()
# extractor.extract_documents()

# extractor = Extract(ConfigSettings.get_config_value('xml_zip_local_directory'),
#                     ConfigSettings.get_config_value('xml_output_local_directory'),
#                     ConfigSettings.get_config_value('pdf_zip_archive_local_directory'),
#                     ConfigSettings.get_config_value(
#                         'pdf_output_local_directory'))  # создаем экземпляр класса Extract с аргументами из класса ConfigSettings
#
# extractor.extract_xml()  # вызываем функцию extract_xml у экземпляра
