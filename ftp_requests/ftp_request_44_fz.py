from loguru import logger
import os
import re
from ftplib import FTP
from tqdm import tqdm
import json


from ftp_requests.config_requests_ftp_44_fz import FTPClientSettings
from config import ConfigSettings
from database.database_connection import DatabaseManager
from open_file.extract_files import Extract
from parsing.parsing_xml import ParsingXml

extreactor = Extract()

class FTPDownloader:
    """
    Класс для подключения и скачивания файлов с FTP сервера.

    Атрибуты:
        host (str): Адрес FTP сервера.
        port (int): Порт FTP сервера.
        username (str): Имя пользователя для аутентификации на FTP сервере.
        password (str): Пароль пользователя для аутентификации на FTP сервере.
        ftp: Объект FTP соединения.
        json_file_path (str): Путь к JSON-файлу, содержащему информацию о директориях для скачивания файлов.
        local_directory (str): Локальная директория, куда будут сохраняться скачанные файлы.
        date (str): Начальная дата для фильтрации файлов по дате.
    """

    def __init__(self):
        """
        Инициализирует объект класса FTPDownloader. Получает настройки подключения к FTP серверу и другие конфигурации.

        Инициализирует все атрибуты для подключения к FTP серверу, включая хост, порт, имя пользователя и пароль.
        Также инициализирует пути для сохранения скачанных файлов, путь к JSON файлу с директориями,
        а также конфигурацию для фильтрации файлов по дате.
        """
        self.host = FTPClientSettings.get_config_value_ftp_settings('host')  # Получаем хост FTP сервера из настроек
        self.port = FTPClientSettings.get_config_value_ftp_settings('port')  # Получаем порт FTP сервера из настроек
        self.username = FTPClientSettings.get_config_value_ftp_settings('username')  # Получаем имя пользователя для FTP
        self.password = FTPClientSettings.get_config_value_ftp_settings('password')  # Получаем пароль для FTP
        self.ftp = None  # Инициализируем объект FTP (пока пустой)
        self.json_file_path = FTPClientSettings.get_json_file_path()  # Получаем путь к JSON-файлу с директориями
        self.local_directory = ConfigSettings.get_config_value('xml_zip_local_directory')  # Путь для сохранения локально
        self.date = ConfigSettings.get_config_value('start_date')  # Получаем начальную дату для фильтрации
        self.db_manager = DatabaseManager()  # Менеджер базы данных для обработки информации о файлах

        self.extractor = Extract()  # Инициализируем объект для извлечения данных
        self.parsing_xml = ParsingXml()  # Инициализируем объект для парсинга XML данных

    def connect(self):
        """
        Устанавливает соединение с FTP сервером по указанным настройкам.

        Этот метод создает объект FTP-соединения и пытается подключиться к серверу с использованием хоста, порта, имени пользователя
        и пароля, предоставленных в атрибутах объекта. Включает настройку пассивного режима и авторизацию.
        В случае успеха сохраняет объект FTP-соединения в атрибуте `self.ftp`. В случае ошибки логирует ошибку и устанавливает
        значение `self.ftp` в `None`.

        Исключения:
            Exception: Ловит и логирует исключения, возникающие при подключении к серверу.
        """
        try:
            logger.debug(
                f'Пытаюсь подключиться к хостингу гос.закупок по ftp {self.host}')  # Логирование попытки подключения

            # Создание объекта FTP и попытка подключиться
            self.ftp = FTP()  # Создание объекта FTP для соединения
            self.ftp.connect(self.host, self.port)  # Подключение к серверу по хосту и порту
            self.ftp.set_pasv(True)  # Включение пассивного режима FTP (чаще используется в корпоративных настройках)
            self.ftp.login(self.username, self.password)  # Логин с использованием имени пользователя и пароля

            logger.info('Установил соединение с ftp')  # Логирование успешного соединения
        except Exception as e:
            # Логирование ошибки в случае неудачного подключения
            logger.error(f'Произошла ошибка при подключении к ftp {self.host}: {e}')
            self.ftp = None  # Устанавливаем значение self.ftp в None, если подключение не удалось

    def close_connection(self):
        """
        Закрывает активное FTP-соединение, если оно существует.

        Этот метод проверяет наличие активного FTP-соединения и, если оно существует,
        завершает его с помощью метода `quit()`. В случае успешного завершения соединения
        логируется сообщение об этом. Если соединение не установлено, выводится предупреждение.

        Исключения:
            Exception: Ловит и логирует исключения, возникающие при попытке закрыть соединение.
        """
        if self.ftp:
            self.ftp.quit()  # Завершаем соединение с FTP сервером
            logger.info('Закрыл соединение с ftp')  # Логируем успешное закрытие соединения
        else:
            logger.warning(
                'Нет активного соединения для закрытия')  # Логируем предупреждение, если соединение не установлено

    def download_files_from_directory(self, directory):
        """
            Скачивает файлы из указанной директории на FTP сервере.
                Args:
                    directory (str): Путь к директории на FTP сервере.
                Returns:
                    List[str]: Список путей к скачанным файлам.
                Raises:
                Exception: В случае возникновения ошибки при загрузке файлов.
                    """
        file_paths = []

        try:
            self.ftp.cwd(directory)  # Переход в указанную директорию

            current_directory = self.ftp.pwd()  # Получение текущего рабочего каталога
            logger.info(f'Начинаю работу с директорией: {current_directory}')  # Логирование текущего каталога

            data = []  # Список для хранения данных о файлах

            def callback(line):
                line = line.strip()
                if line:
                    data.append(line)  # Добавление информации о файле в список

            self.ftp.retrlines('LIST', callback)  # Получение списка файлов с сервера

            logger.info(f'Создаю список файлов')  # Логирование списка файлов

            # Получаем общее количество файлов для tqdm
            total_files = len(data)

            with tqdm(total=total_files, desc='Downloading files') as pbar:
                for item in data:
                    line_parts = item.split(maxsplit=8)  # Разделение строки на части
                    filename = line_parts[-1]  # Получение имени файла
                    file_path = os.path.join(current_directory, filename).replace('\\',
                                                                                  '/')  # Формирование полного пути к файлу

                    if item.startswith('-') and self.is_valid_date(filename, self.date) and filename.endswith(
                            'xml.zip'):
                        # Если элемент является файлом, соответствует условию даты и имеет нужное расширение, скачиваем его
                        file_paths.append(file_path)
                        self.download_single_file(filename, file_path)  # Скачиваем файл
                        pbar.update(1)  # Увеличиваем значение progress bar

                    elif item.startswith('d'):
                        # Если элемент является директорией, рекурсивно скачиваем файлы из этой директории
                        subdirectory = os.path.join(current_directory, filename)
                        subdirectory = subdirectory.replace('\\', '/')
                        subdirectories = self.download_files_from_directory(subdirectory)
                        file_paths.extend(subdirectories)  # Добавление путей субдиректорий в список
                        pbar.update(
                            len(subdirectories))  # Увеличиваем значение progress bar на количество субдиректорий

        except Exception as e:
            logger.error(f'Ошибка во время загрузки файлов: {e}')  # Логирование ошибки при загрузке файлов

        return file_paths  # Возврат списка путей к файлам

    def download_files(self):
        try:
            self.connect()  # Подключение к FTP серверу
            directory_list = self.load_paths_from_json()  # Получение списка директорий из JSON файла

            all_file_paths = []
            for directory in directory_list:
                file_paths = self.download_files_from_directory(directory)  # Скачивание файлов из каждой директории
                all_file_paths.extend(file_paths)

            return all_file_paths  # Возврат списка всех скачанных файлов

        finally:
            self.close_connection()  # Закрываем соединение с FTP сервером

    @staticmethod
    def is_valid_date(filename, date):
        # Извлечение даты из имени файла
        match = re.search(r'\d{8}', filename)  # Поиск последовательности из 8 цифр в имени файла
        if match:
            file_date = match.group()  # Получение найденной даты
            return file_date > date  # Сравнение даты файла с заданной датой
        else:
            return False  # Возврат False, если дата в имени файла не найдена

    def download_single_file(self, filename, file_path):
        if not self.db_manager.check_file_exists(filename):
            # Скачивание файла
            local_file_path = os.path.join(self.local_directory, filename)
            with open(local_file_path, 'wb') as local_file:
                self.ftp.retrbinary(f'RETR {file_path}', local_file.write)

            # Вставка записи о файле в базу данных
            self.db_manager.insert_file_downloaded(filename)
            # Запуск функции разархивирования xml
            self.extractor.extract_xml()
            # Запуск функции парсинга файла xml по заданным условиям
            self.parsing_xml.parse_and_store_data()
            # Удаление папки после завершения всех операций
            self.delete_downloaded_file(local_file_path)

        else:
            logger.info(f"Файл {filename} уже скачан ранее. Пропускаем скачивание.")


    def delete_downloaded_file(self, file_path):
        try:
            os.remove(file_path)
            logger.info(f"Файл {file_path} удален после завершения операций")
        except Exception as e:
            logger.error(f"Ошибка при удалении файла {file_path}: {e}")

    def load_paths_from_json(self):
        try:
            logger.info('Открываю файл Json')
            with open(self.json_file_path, 'r') as json_file:
                paths_data = json.load(json_file)
            return list(paths_data.values())
        except Exception as e:
            logger.error(f'Ошибка открытия файла: {e}')


# ftp_downloader = FTPDownloader()
# ftp_downloader.download_files()
