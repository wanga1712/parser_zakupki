import logging
import os.path
from ftplib import FTP
from custom_logger import LoggerConfig


class FTPClient:
    def __init__(self, host, username, password, port=21):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ftp = FTP()

        # Конфигурация логгера
        self.logger = logging.getLogger(__name__)
        LoggerConfig.configure_logger(self.logger)

    def connect(self):
        try:
            self.logger.info(f'Соединение с хостингом гос.закупки по ftp {self.host}')
            self.ftp.connect(self.host, self.port)
            self.ftp.set_pasv(True)
            self.ftp.login(self.username, self.password)
            self.logger.info('Соединение с ftp установлено')
        except Exception as e:
            self.logger.error(f'Произошла ошибка при подключении к ftp {self.host} в функции def connect')

    def get_directory_paths(self, remote_path):
        try:
            # self.logger.info(f'Извлечение дирректорий из каталога {remote_path}')
            paths = self.ftp.nlst(remote_path)

            # Фльтрация по регионам
            filtered_paths = [path for path in paths if
                              path.startswith('/fcs_regions/Moskva') or path.startswith('/fcs_regions/Moskovskaja_obl')]
            # self.logger.info('Дирректории каталога успешно извлечены')
            return filtered_paths
        except Exception as e:
            self.logger.error(f'Ошибка получения директории {e} в функции def retrieve_directory')

    def get_subdirectories(self, remote_path, filter_criteria):
        try:
            # self.logger.info(f'Получение субдирректорий для {remote_path}')
            subdirectories = []

            subdirectories_paths = self.get_directory_paths(remote_path)

            matching_subbdirectories = [subdir for subdir in subdirectories_paths if
                                       any(criteria in subdir for criteria in filter_criteria)]
            subdirectories.extend(matching_subbdirectories)

            for subdir in matching_subbdirectories:
                subdirectories_paths = f'{remote_path}/{subdir}'
                subdirectories.extend(self.get_subdirectories(subdirectories_paths, filter_criteria))

            paths = self.get_directory_paths(remote_path)

            subdirectories = []

            for path in paths:
                subdirectories_paths = self.get_directory_paths(path)
                matching_subbdirectories = [subdir for subdir in subdirectories_paths if
                                            any(criteria in subdir for criteria in filter_criteria)]
                subdirectories.extend(matching_subbdirectories)

            # self.logger.info('Субдирректории получены успешно!')
            return subdirectories
        except Exception as e:
            self.logger.error(f'Ошибка получения субдирректорий для {remote_path} в функции get_subdirectories')
            return []

    def disconnect(self):
        try:
            self.logger.info('Disconnect')
            self.ftp.quit()
            self.logger.info('Disconnected completed')
        except Exception as e:
            self.logger.error(f'Ошибка в завершении сеанса связи: {e} в функции def disconnect')

    def download_and_open_file(self, remote_directory, local_directory):
        try:
            self.logger.info(f'Скачиваем файлы из дирректории {remote_directory}')
            self.ftp.cwd(remote_directory)
            files = self.ftp.nlst()
            zip_files = [file for file in files]
            for file in zip_files:
                with open(os.path.join(local_directory, file), 'wb') as local_file:
                    self.ftp.retrbinary(f'RETR {file}', local_file.write)

            self.logger.debug(f'Скачивание файлов директорию {local_directory} завершено')

        except Exception as e:
            self.logger.error(f'Произошла ошибка скачивания файлов: {e}')



# Проверка работы функции
ftp_client = FTPClient('ftp.zakupki.gov.ru', 'free', 'free')
ftp_client.connect()
port = 21
directory_path = ftp_client.get_directory_paths('/fcs_regions')
filter_criteria = ['acts', 'contracts', 'notifications', 'protocols', 'currMonth', 'prevMonth']
# Запуск скачивания файла из директории
remote_directory = '/fcs_regions/Moskva/contracts/currMonth'
local_directory = r'C:\Users\ofman9\Documents\test'
ftp_client.download_and_open_file(remote_directory, local_directory)

#
# print('Полученные директории с ftp закупки.гов:')
# for dir_path in directory_path:
#     print(dir_path)
#     subdirectories = ftp_client.get_subdirectories(dir_path, filter_criteria)
#     for sub_dir_path in subdirectories:
#         print(f'\t{sub_dir_path}')

ftp_client.disconnect()
