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

        Этот метод переходит в указанную директорию на FTP сервере, получает список файлов
        и скачивает их на локальную машину. В процессе выполнения логируется информация о текущем каталоге
        и процессе скачивания.

        Аргументы:
            directory (str): Путь к директории на FTP сервере, из которой необходимо скачать файлы.

        Возврат:
            List[str]: Список путей к скачанным файлам.

        Исключения:
            Exception: В случае возникновения ошибки при переходе в директорию или скачивании файлов.
        """
        file_paths = []  # Список для хранения путей к скачанным файлам

        try:
            self.ftp.cwd(directory)  # Переход в указанную директорию
            current_directory = self.ftp.pwd()  # Получаем текущий рабочий каталог
            logger.info(f'Начинаю работу с директорией: {current_directory}')  # Логируем текущий каталог

            data = []  # Список для хранения данных о файлах

            def callback(line):
                line = line.strip()
                if line:
                    data.append(line)  # Добавление информации о файле в список

            self.ftp.retrlines('LIST', callback)  # Получение списка файлов с сервера

            logger.info(f'Создаю список файлов')  # Логирование списка файлов

            # Получаем общее количество файлов для tqdm
            total_files = len(data)

            # with tqdm(total=total_files, desc='Downloading files') as pbar:
            for item in data:
                line_parts = item.split(maxsplit=8)  # Разделение строки на части
                filename = line_parts[-1]  # Получение имени файла
                file_path = os.path.join(current_directory, filename).replace('\\',
                                                                                '/')  # Формирование полного пути к файлу

                if item.startswith('-') and self.is_valid_date(filename, self.date) and filename.endswith(
                        'xml.zip'):
                        # Если элемент является файлом, соответствует условию даты и имеет нужное расширение, скачиваем его
                    try:
                        file_paths.append(file_path)
                        self.download_single_file(filename, file_path)  # Скачиваем файл
                        # pbar.update(1)  # Увеличиваем значение progress bar
                    except Exception as e:
                        logger.error(
                            f'Ошибка при скачивании файла {filename}: {e}')  # Логирование ошибки при скачивании файла

                elif item.startswith('d'):
                    # Если элемент является директорией, рекурсивно скачиваем файлы из этой директории
                    subdirectory = os.path.join(current_directory, filename).replace('\\', '/')
                    try:
                        subdirectories = self.download_files_from_directory(
                            subdirectory)  # Рекурсивный вызов для поддиректории
                        file_paths.extend(subdirectories)  # Добавление путей субдиректорий в список
                        # pbar.update(len(subdirectories))  # Увеличиваем значение прогресс бара
                    except Exception as e:
                        logger.error(
                            f'Ошибка при работе с поддиректорией {subdirectory}: {e}')  # Логирование ошибок при работе с поддиректориями

        except Exception as e:
            logger.error(
            f'Ошибка во время загрузки файлов из директории {directory}: {e}')  # Логирование ошибки при загрузке файлов

        return file_paths  # Возврат списка путей к файлам

    def download_files(self):
        """
        Скачивает файлы с FTP сервера из нескольких директорий.

        Этот метод подключается к FTP серверу, загружает список директорий из JSON файла,
        затем для каждой директории скачивает файлы. После завершения работы соединение с FTP сервером закрывается.

        Возврат:
            List[str]: Список путей ко всем скачанным файлам.

        Исключения:
            Exception: В случае возникновения ошибки при подключении, загрузке файлов или других этапах.
        """
        try:
            self.connect()  # Подключение к FTP серверу

            # Получение списка директорий из JSON файла
            directory_list = self.load_paths_from_json()

            all_file_paths = []  # Список для хранения путей ко всем скачанным файлам

            # Проход по всем директориям и скачивание файлов из каждой
            for directory in directory_list:
                file_paths = self.download_files_from_directory(directory)  # Скачивание файлов из текущей директории
                all_file_paths.extend(file_paths)  # Добавление путей файлов в общий список

            return all_file_paths  # Возврат списка всех скачанных файлов

        finally:
            self.close_connection()  # Закрываем соединение с FTP сервером

    @staticmethod
    def is_valid_date(filename, date):
        """
        Проверяет, является ли дата в имени файла более поздней, чем заданная дата.

        Этот метод извлекает дату из имени файла и сравнивает её с переданной датой.

        Аргументы:
            filename (str): Имя файла, из которого необходимо извлечь дату.
            date (str): Заданная дата, с которой будет сравниваться дата из имени файла.

        Возврат:
            bool: Возвращает True, если дата в имени файла позже заданной даты, иначе False.

        Исключения:
            Нет.
        """
        # Извлечение даты из имени файла
        match = re.search(r'\d{8}', filename)  # Поиск последовательности из 8 цифр в имени файла
        if match:
            file_date = match.group()  # Получение найденной даты
            return file_date > date  # Сравнение даты файла с заданной датой
        else:
            return False  # Возврат False, если дата в имени файла не найдена

    def download_single_file(self, filename, file_path):
        """
        Скачивает файл с FTP-сервера, если он еще не был скачан ранее, и выполняет серию операций
        с файлом: разархивирование, парсинг данных и удаление локальной копии файла.

        Параметры:
        filename (str): Имя файла для скачивания.
        file_path (str): Путь к файлу на FTP-сервере.

        Операции:
        1. Проверка наличия файла в базе данных (если файл уже скачан ранее, скачивание пропускается).
        2. Скачивание файла с FTP-сервера на локальный диск.
        3. Добавление записи о скачанном файле в базу данных.
        4. Разархивирование файла (если это XML).
        5. Парсинг и сохранение данных из файла XML.
        6. Удаление локальной копии скачанного файла.
        """
        # Проверка, существует ли уже файл в базе данных
        if not self.db_manager.check_file_exists(filename):
            # Скачивание файла с FTP-сервера, если его нет в базе данных
            local_file_path = os.path.join(self.local_directory, filename)
            with open(local_file_path, 'wb') as local_file:
                # Отправка команды RETR для скачивания файла с FTP-сервера
                self.ftp.retrbinary(f'RETR {file_path}', local_file.write)

            # Вставка записи о скачанном файле в базу данных
            self.db_manager.insert_file_downloaded(filename)

            # Разархивирование XML файла (если файл поддерживает разархивирование)
            self.extractor.extract_xml()

            # Парсинг XML файла и сохранение данных в базе данных
            self.parsing_xml.parse_and_store_data()

            # Удаление локальной копии скачанного файла после выполнения всех операций
            self.delete_downloaded_file(local_file_path)

        else:
            # Если файл уже скачан, пропускаем скачивание и логируем это
            logger.info(f"Файл {filename} уже скачан ранее. Пропускаем скачивание.")

    def delete_downloaded_file(self, file_path):
        """
        Удаляет локальный файл по указанному пути после завершения операций с ним.

        Параметры:
        file_path (str): Путь к файлу, который нужно удалить.

        Возвращает:
        None. Выполняет операцию удаления файла и логирует результат.
        """
        try:
            # Попытка удалить файл по указанному пути
            os.remove(file_path)
            # Логируем успешное удаление файла
            logger.info(f"Файл {file_path} удален после завершения операций")
        except Exception as e:
            # Логируем ошибку, если файл не удается удалить
            logger.error(f"Ошибка при удалении файла {file_path}: {e}")

    def load_paths_from_json(self):
        """
        Загружает данные о путях из JSON-файла и возвращает их в виде списка.

        Ожидается, что JSON-файл содержит структуру данных, где пути хранятся в виде значений.
        В случае ошибки при открытии или чтении файла, функция логирует ошибку.

        Возвращает:
        list: Список значений путей, загруженных из JSON-файла.

        Исключения:
        В случае ошибки открытия или чтения файла, функция записывает ошибку в лог.
        """
        try:
            # Логируем попытку открытия JSON-файла
            logger.info('Открываю файл Json')

            # Открытие файла и загрузка данных
            with open(self.json_file_path, 'r') as json_file:
                paths_data = json.load(json_file)

            # Возвращаем список значений (путей) из данных
            return list(paths_data.values())

        except Exception as e:
            # Логируем ошибку в случае исключения
            logger.error(f'Ошибка открытия файла: {e}')

# ftp_downloader = FTPDownloader()
# ftp_downloader.download_files()
