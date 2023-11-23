import logging
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
            self.ftp.login(self.username, self.password)
            self.logger.info('Соединение с ftp установлено')
        except Exception as e:
            self.logger.error(f'Произошла ошибка при подключении к ftp {self.host} в функции def connect')

    def get_directory_paths(self, remote_path):
        try:
            # self.logger.info(f'Извлечение дирректорий из каталога {remote_path}')
            paths = self.ftp.nlst(remote_path)

            # Фльтрация по регионам
            filtered_paths = [path for path in paths if path.startswith('/fcs_regions/Moskva') or path.startswith('/fcs_regions/Moskovskaja_obl')]
            # self.logger.info('Дирректории каталога успешно извлечены')
            return filtered_paths
        except Exception as e:
            self.logger.error(f'Ошибка получения директории {e} в функции def retrieve_directory')

    def get_subdirectories(self, remote_path):
        try:
            # self.logger.info(f'Получение субдирректорий для {remote_path}')
            paths = self.get_directory_paths(remote_path)

            subdirectories = []
            for path in paths:
                # if self.ftp.nlst(path) == path:
                subdirectories.append(path)

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


# Проверка работы функции
ftp_client = FTPClient('ftp.zakupki.gov.ru', 'free', 'free')
ftp_client.connect()
directory_path = ftp_client.get_directory_paths('/fcs_regions')

print('Полученные директории с ftp закупки.гов:')
for dir_path in directory_path:
    print(dir_path)
    subdirectories = ftp_client.get_subdirectories(dir_path)
    for sub_dir_path in subdirectories:
        print(f'\t{sub_dir_path}')

ftp_client.disconnect()
