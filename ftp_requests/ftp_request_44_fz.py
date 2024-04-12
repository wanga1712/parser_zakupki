from loguru import logger
from ftplib import FTP
import os
import re
from tqdm import tqdm

from config_requests_ftp_44_fz import FTPClientSettings
from config import ConfigSettings


class FTPDownloader:
    def __init__(self):
        self.host = FTPClientSettings.get_config_value_ftp_settings('host')
        self.port = FTPClientSettings.get_config_value_ftp_settings('port')
        self.username = FTPClientSettings.get_config_value_ftp_settings('username')
        self.password = FTPClientSettings.get_config_value_ftp_settings('password')
        self.ftp = None
        self.directory_ftp_44_fz = FTPClientSettings.get_config_value_ftp_settings('ftp_remote_path_44_fz')
        self.local_directory = ConfigSettings.get_config_value('xml_zip_local_directory')
        self.date = ConfigSettings.get_config_value('start_date')

    def connect(self):

        """
        Устанавливает соединение с FTP сервером, используя настройки из класса FTPClientSettings.

        Пытается установить соединение с FTP сервером, используя предоставленные настройки (адрес сервера,
        порт, имя пользователя и пароль). В случае успешного соединения возвращает экземпляр соединения.
        В случае неудачи логирует ошибку и возвращает None.

        Returns:
            ftp: Возвращает экземпляр соединения с FTP сервером в случае успеха. В противном случае возвращает None.

        Raises:
            Exception: В случае неудачи логирует возникшее исключение.
        """

        try:
            logger.debug(f'Пытаюсь подключиться к хостингу гос.закупок по ftp {self.host}')

            self.ftp = FTP()
            self.ftp.connect(self.host, self.port)
            self.ftp.set_pasv(True)
            self.ftp.login(self.username, self.password)

            logger.info('Установил соединение с ftp')
        except Exception as e:
            logger.error(f'Произошла ошибка при подключении к ftp {self.host}: {e}')
            self.ftp = None

    def close_connection(self):
        if self.ftp:
            self.ftp.quit()
            logger.info('Закрыл соединение с ftp')
        else:
            logger.warning('Нет активного соединения для закрытия')

    def download_files(self):
        file_paths = []

        try:
            self.connect()  # Подключение к FTP серверу

            self.ftp.cwd(self.directory_ftp_44_fz)  # Переход в указанную директорию

            current_directory = self.ftp.pwd()  # Получение текущего рабочего каталога
            logger.info(f'Начинаю работу с директорией: {current_directory}')  # Логирование текущего каталога

            data = []  # Список для хранения данных о файлах

            def callback(line):
                line = line.strip()
                if line:
                    data.append(line)  # Добавление информации о файле в список

            self.ftp.retrlines('LIST', callback)  # Получение списка файлов с сервера

            logger.info(f'Создаю список файлов: {data}')  # Логирование списка файлов

            # Получаем общее количество файлов для tqdm
            total_files = len(data)

            with tqdm(total=total_files, desc='Downloading files') as pbar:
                for item in data:
                    line_parts = item.split(maxsplit=8)  # Разделение строки на части
                    filename = line_parts[-1]  # Получение имени файла
                    file_path = os.path.join(current_directory, filename).replace('\\',
                                                                                  '/')  # Формирование полного пути к файлу

                    if item.startswith('-') and self.is_valid_date(filename, self.date) and filename.endswith('xml.zip'):
                        # Если элемент является файлом, соответствует условию даты и имеет нужное расширение, скачиваем его
                        file_paths.append(file_path)
                        self.download_single_file(filename, file_path)  # Скачиваем файл
                        pbar.update(1)  # Увеличиваем значение progress bar

                    elif item.startswith('d'):
                        # Если элемент является директорией, рекурсивно скачиваем файлы из этой директории
                        subdirectory = os.path.join(current_directory, filename)
                        subdirectory = subdirectory.replace('\\', '/')
                        subdirectories = self.download_files(subdirectory)
                        file_paths.extend(subdirectories)  # Добавление путей субдиректорий в список
                        pbar.update(len(subdirectories))  # Увеличиваем значение progress bar на количество субдиректорий

        except Exception as e:
            logger.error(f'Ошибка во время загрузки файлов: {e}')  # Логирование ошибки при загрузке файлов

        finally:
            self.close_connection()  # Закрываем соединение с FTP сервером

        return file_paths  # Возврат списка путей к файлам

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
        local_file_path = os.path.join(self.local_directory, filename)
        with open(local_file_path, 'wb') as local_file:
            self.ftp.retrbinary(f'RETR {file_path}', local_file.write)

ftp_downloader = FTPDownloader()
ftp_downloader.download_files()
