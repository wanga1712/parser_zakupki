import logging
import os
import re
from ftplib import FTP

from config import local_directory
from checking_markup_conditions import FileProcessor
from custom_logger import LoggerConfig


class FTPClient:
    def __init__(self, host, username, password, port=21):
        # Инициализация клиента FTP с заданными параметрами подключения.
        self.host = host  # Адрес сервера FTP
        self.username = username  # Имя пользователя для аутентификации
        self.password = password  # Пароль пользователя для аутентификации
        self.port = port  # Порт сервера FTP, по умолчанию 21
        self.ftp = FTP()  # Создание экземпляра клиента FTP
        FileProcessor.process_file()
        self.local_directory = local_directory


        # Конфигурация логгера для ведения журнала событий
        self.logger = logging.getLogger(__name__)  # Получение логгера для текущего модуля
        LoggerConfig.configure_logger(self.logger)  # Настройка логгера согласно конфигурации

    def connect(self):
        try:
            # Запись информации о попытке соединения с FTP сервером в журнал
            self.logger.info(f'Соединение с хостингом гос.закупки по ftp {self.host}')
            # Установка соединения с FTP сервером с использованием указанного хоста и порта
            self.ftp.connect(self.host, self.port)
            # Включение пассивного режима передачи данных
            self.ftp.set_pasv(True)
            # Аутентификация на FTP сервере с использованием имени пользователя и пароля
            self.ftp.login(self.username, self.password)
            # Запись информации об успешном соединении с FTP сервером в журнал
            self.logger.info('Соединение с ftp установлено')
        except Exception as e:
            # Запись информации об ошибке при соединении с FTP сервером в журнал
            self.logger.error(f'Произошла ошибка при подключении к ftp {self.host} в функции def connect')

    def get_files_after_date(self, remote_path, date):
        file_paths = []  # Список для хранения путей к файлам, соответствующим условиям

        try:
            self.ftp.cwd(remote_path)  # Переход в указанный удаленный каталог
            current_directory = self.ftp.pwd()  # Получение текущего рабочего каталога

            self.logger.info(f'Current directory: {current_directory}')  # Логирование текущего каталога

            data = []  # Список для хранения данных о файлах

            def callback(line):
                line = line.strip()
                if line:
                    data.append(line)  # Добавление информации о файле в список

            self.ftp.retrlines('LIST', callback)  # Получение списка файлов с сервера

            self.logger.info(f'Directory listing: {data}')  # Логирование списка файлов

            for item in data:
                line_parts = item.split(maxsplit=8)  # Разделение строки на части
                filename = line_parts[-1]  # Получение имени файла
                file_path = os.path.join(current_directory, filename).replace('\\',
                                                                              '/')  # Формирование полного пути к файлу

                if item.startswith('-') and self.is_valid_date(filename, date):
                    # Если элемент является файлом и соответствует условию даты, добавляем его в список
                    file_paths.append(file_path)
                elif item.startswith('d') and not item.endswith('xml.zip'):
                    # Если элемент является директорией, рекурсивно получаем субдиректории
                    try:
                        self.ftp.cwd(file_path)  # Переход в субдиректорию
                        subdirectories = self.get_files_after_date(file_path, date)  # Рекурсивный вызов функции
                        file_paths.extend(subdirectories)  # Добавление путей субдиректорий в список
                    except Exception as e:
                        self.logger.error(f'Failed to change directory: {file_path}. {e}')  # Логирование ошибки

        except Exception as e:
            self.logger.error(f'Failed to get directory: {e}')  # Логирование ошибки при получении каталога

        return file_paths  # Возврат списка путей к файлам

    def is_valid_date(self, filename, date):
        # Извлечение даты из имени файла
        match = re.search(r'\d{8}', filename)  # Поиск последовательности из 8 цифр в имени файла
        if match:
            file_date = match.group()  # Получение найденной даты
            return file_date > date  # Сравнение даты файла с заданной датой
        else:
            return False  # Возврат False, если дата в имени файла не найдена

    def download_files(self, file_paths):
        try:
            os.makedirs(self.local_directory, exist_ok=True)
            for file_path in file_paths:
                # Получение названия файла
                file_name = os.path.basename(file_path)
                # Формирование полного пути к локальному файлу
                local_zip_path = os.path.join(self.local_directory, file_name)
                self.logger.info(f'Downloading file: {file_path}')
                # Скачивание файла и запись его в локальный путь
                with open(local_zip_path, 'wb') as local_file:
                    self.ftp.retrbinary(f'RETR {file_path}', local_file.write)
                self.logger.info(f'Downloaded file: {local_zip_path}')
                # Передаем путь к ZIP-архиву и путь к распакованной директории в метод process_file
                self.file_processor_instance.zip_path = local_zip_path
                # Теперь вызываем метод process_file
                self.file_processor_instance.process_file(self.local_zip_path)

                # Продолжение работы с файлами
        except Exception as e:
            self.logger.error(f'Failed to download files: {e}')

    def disconnect(self):
        try:
            # Логирование начала процесса отключения от FTP сервера
            self.logger.info('Disconnecting')
            # Вызов метода quit() для завершения сеанса связи с FTP сервером
            self.ftp.quit()
            # Логирование успешного завершения процесса отключения
            self.logger.info('Disconnected')
        except Exception as e:
            # Логирование ошибки, возникшей в процессе отключения
            self.logger.error(f'Error disconnecting: {e}')


# Создание экземпляра клиента FTP с указанными учетными данными
ftp_client = FTPClient('ftp.zakupki.gov.ru', 'free', 'free')
# Установка соединения с FTP сервером
ftp_client.connect()

# Определение удаленного пути и даты для фильтрации файлов
remote_path = '/fcs_regions/Moskva/contracts/currMonth'
date = '20240101'  # Дата в формате 'YYYYMMDD'

# Получение списка путей к файлам, измененным после указанной даты
file_paths = ftp_client.get_files_after_date(remote_path, date)

# Скачивание файлов из списка путей в локальную директорию
ftp_client.download_files(file_paths)

# Отключение от FTP сервера и завершение сеанса связи
ftp_client.disconnect()
