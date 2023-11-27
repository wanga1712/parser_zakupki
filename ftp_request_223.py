import logging
import os
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

        # Configuration of logger
        self.logger = logging.getLogger(__name__)
        LoggerConfig.configure_logger(self.logger)

    def connect(self):
        try:
            self.logger.info(f'Connecting to FTP host: {self.host}')
            self.ftp.connect(self.host, self.port)
            self.ftp.set_pasv(True)
            self.ftp.login(self.username, self.password)
            self.logger.info('Connection to FTP established')
        except Exception as e:
            self.logger.error(f'Error connecting to FTP host: {self.host}. {e}')

    def get_files_after_date(self, remote_path, date):
        file_paths = []

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
                file_path = os.path.join(current_directory, filename).replace('\\', '/')

                if item.startswith('-') and self.is_valid_date(filename, date):
                    # File found and matches the date condition, add it to the file_paths
                    file_paths.append(file_path)
                elif item.startswith('d') and not item.endswith('xml.zip'):
                    # Directory found, recursively retrieve subdirectories
                    try:
                        self.ftp.cwd(file_path)
                        subdirectories = self.get_files_after_date(file_path, date)
                        file_paths.extend(subdirectories)
                    except Exception as e:
                        self.logger.error(f'Failed to change directory: {file_path}. {e}')

        except Exception as e:
            self.logger.error(f'Failed to get directory: {e}')

        return file_paths

    def is_valid_date(self, filename, date):
        # Extract the date from the filename
        match = re.search(r'\d{8}', filename)
        if match:
            file_date = match.group()
            return file_date > date
        else:
            return False

    def download_files(self, file_paths, local_directory):
        try:
            os.makedirs(local_directory, exist_ok=True)
            for file_path in file_paths:
                local_file = os.path.join(local_directory, os.path.basename(file_path))
                self.logger.info(f'Downloading file: {file_path}')
                self.ftp.retrbinary(f'RETR {file_path}', open(local_file, 'wb').write)
                self.logger.info(f'Downloaded file: {file_path}')
        except Exception as e:
            self.logger.error(f'Failed to download files: {e}')

    def disconnect(self):
        try:
            self.logger.info('Disconnecting')
            self.ftp.quit()
            self.logger.info('Disconnected')
        except Exception as e:
            self.logger.error(f'Error disconnecting: {e}')


# Testing the function
ftp_client = FTPClient('ftp.zakupki.gov.ru', 'fz223free', 'fz223free')
ftp_client.connect()
remote_path = '/out/published/Moskva'
date = '20230101'
file_paths = ftp_client.get_files_after_date(remote_path, date)
local_directory = r'C:\Users\wangr\OneDrive\Документы\тест'

ftp_client.download_files(file_paths, local_directory)
ftp_client.disconnect()