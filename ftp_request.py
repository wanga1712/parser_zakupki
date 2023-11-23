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
            self.logger.info(f'Извлечение дирректорий из каталога {remote_path}')
            path = self.ftp.nlst(remote_path)
            self.logger.info('Дирректории каталога успешно извлечены')
            return path
        except Exception as e:
            self.logger.error(f'Ошибка получения директории {e} в функции def retrieve_directory')

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
directory_path = ftp_client.get_directory_paths('/fcs_nsi')

print('Полученные директории с ftp закупки.гов:')
for path in directory_path:
    print(path)

ftp_client.disconnect()



