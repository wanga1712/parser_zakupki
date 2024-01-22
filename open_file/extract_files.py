import logging  # импортируем модуль logging
import os
import zipfile
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

    def __init__(self, xml_zip_dr: (str), extract_dir_xml: (str),
                 pdf_zip_dir: (str), extract_dir_pdf: (str)) -> None:
        '''
        Конструктор класса Extract.
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
        try:
            for filename in os.listdir(self.xml_zip_dr):
                if filename.endswith('.zip'):
                    zip_path = os.path.join(self.xml_zip_dr, filename)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(self.extract_dir_xml)
            self.logger.info(f"Файлы успешно распакованы в директорию: {self.extract_dir_xml}")

        except Exception as e:
            self.logger.error(f"Ошибка распаковки ZIP файлов: {e}")


extractor = Extract(ConfigSettings.get_config_value('xml_zip_local_directory'),
                    ConfigSettings.get_config_value('xml_output_local_directory'),
                    ConfigSettings.get_config_value('pdf_zip_archive_local_directory'),
                    ConfigSettings.get_config_value(
                        'pdf_output_local_directory'))  # создаем экземпляр класса Extract с аргументами из класса ConfigSettings

extractor.extract_xml()  # вызываем функцию extract_xml у экземпляра
