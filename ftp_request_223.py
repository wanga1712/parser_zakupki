import logging
import os.path
import re
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
            self.logger.error(f'Произошла ошибка при подключении к ftp {self.host} {e} в функции def connect')

    import os

    def get_directory_paths(self, remote_path):
        paths = []

        try:
            self.ftp.cwd(remote_path)
            current_directory = self.ftp.pwd()

            self.logger.info(f'Current directory: {current_directory}')

            data = []

            def callback(line):
                line = line.strip()
                if line:
                    data.append(line)

            self.ftp.retrlines('LIST', callback)

            self.logger.info(f'Directory listing: {data}')

            for item in data:
                line_parts = item.split(maxsplit=8)
                filename = line_parts[-1]
                path = os.path.join(current_directory, filename).replace('\\', '/')

                if item.startswith('-'):
                    # File found, add it to the paths
                    paths.append(path)
                elif item.startswith('d') and not item.endswith('xml.zip'):
                    # Directory found, recursively retrieve subdirectories
                    try:
                        self.ftp.cwd(path)
                        subdirectories = self.get_directory_paths(path)
                        paths.extend(subdirectories)
                    except Exception as e:
                        self.logger.error(f'Failed to change directory: {path}. {e}')

        except Exception as e:
            self.logger.error(f'Failed to get directory: {e} in function get_directory_paths')

        return paths

    def disconnect(self):
        try:
            self.logger.info('Disconnect')
            self.ftp.quit()
            self.logger.info('Disconnected completed')
        except Exception as e:
            self.logger.error(f'Ошибка в завершении сеанса связи: {e} в функции def disconnect')


# Проверка работы функции
ftp_client = FTPClient('ftp.zakupki.gov.ru', 'fz223free', 'fz223free')
ftp_client.connect()
port = 21
remote_path = ftp_client.get_directory_paths('/out')
# Запуск скачивания файла из директории
remote_directory = '/out'
local_directory = r'C:\Users\wangr\OneDrive\Документы\тест'


print('Полученные директории с ftp закупки.гов:')
for dir_path in remote_path:
    print(dir_path)

ftp_client.disconnect()