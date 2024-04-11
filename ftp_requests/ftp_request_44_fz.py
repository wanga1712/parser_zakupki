from loguru import logger
from ftplib import FTP


from config_requests_ftp_44_fz import FTPClientSettings


def connect():
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
    ftp = FTP()
    try:
        host = FTPClientSettings.get_config_value_ftp_settings('host')
        port = FTPClientSettings.get_config_value_ftp_settings('port')
        username = FTPClientSettings.get_config_value_ftp_settings('username')
        password = FTPClientSettings.get_config_value_ftp_settings('password')

        logger.debug(f'Попытка соединения с хостингом гос.закупки по ftp {host}')

        ftp.connect(host, port)
        ftp.set_pasv(True)
        ftp.login(username, password)

        logger.info('Соединение с ftp установлено успешно')
        return ftp
    except Exception as e:
        logger.error(f'Произошла ошибка при подключении к ftp {host}: {e}')
        return None


ftp_connection = connect()

#     def get_directory_paths(self, remote_path):
#         try:
#             # Получение списка путей в удаленном каталоге
#             paths = self.ftp.nlst(remote_path)
#
#             # Фильтрация путей по определенным регионам (Москва и Московская область)
#             filtered_paths = [path for path in paths if
#                               path.startswith('/fcs_regions/Moskva') or path.startswith('/fcs_regions/Moskovskaja_obl')]
#             # Возврат отфильтрованных путей
#             return filtered_paths
#         except Exception as e:
#             # Запись информации об ошибке при получении директорий в журнал
#             self.logger.error(f'Ошибка получения директории {e} в функции def retrieve_directory')
#
#     def get_subdirectories(self, remote_path, filter_criteria):
#         try:
#             # Получение субдиректорий для заданного удаленного пути с учетом критериев фильтрации
#             subdirectories = []
#
#             # Получение путей директорий в удаленном каталоге
#             subdirectories_paths = self.get_directory_paths(remote_path)
#
#             # Фильтрация субдиректорий, соответствующих критериям фильтрации
#             matching_subbdirectories = [subdir for subdir in subdirectories_paths if
#                                         any(criteria in subdir for criteria in filter_criteria)]
#             # Добавление отфильтрованных субдиректорий в список
#             subdirectories.extend(matching_subbdirectories)
#
#             # Рекурсивный обход субдиректорий для поиска дополнительных субдиректорий
#             for subdir in matching_subbdirectories:
#                 subdirectories_paths = f'{remote_path}/{subdir}'
#                 subdirectories.extend(self.get_subdirectories(subdirectories_paths, filter_criteria))
#
#             # Возврат списка всех найденных субдиректорий
#             return subdirectories
#         except Exception as e:
#             # Запись информации об ошибке при получении субдиректорий в журнал
#             self.logger.error(f'Ошибка получения субдирректорий для {remote_path} в функции get_subdirectories')
#             # Возврат пустого списка в случае ошибки
#             return []
#
#     def disconnect(self):
#         try:
#             # Запись информации о начале процесса отключения от FTP сервера в журнал
#             self.logger.info('Disconnect')
#             # Завершение сеанса связи с FTP сервером
#             self.ftp.quit()
#             # Запись информации об успешном завершении сеанса связи в журнал
#             self.logger.info('Disconnected completed')
#         except Exception as e:
#             # Запись информации об ошибке при завершении сеанса связи в журнал
#             self.logger.error(f'Ошибка в завершении сеанса связи: {e} в функции def disconnect')
#
#     def download_and_open_file(self, remote_directory, local_directory):
#         try:
#             # Запись информации о начале скачивания файлов из удаленной директории в журнал
#             self.logger.info(f'Скачиваем файлы из дирректории {remote_directory}')
#             # Переход в удаленную директорию на FTP сервере
#             self.ftp.cwd(remote_directory)
#             # Получение списка файлов в удаленной директории
#             files = self.ftp.nlst()
#             # Фильтрация и выбор файлов для скачивания
#             zip_files = [file for file in files]
#             # Перебор файлов и их скачивание в локальную директорию
#             for file in zip_files:
#                 # Открытие файла для записи в бинарном режиме
#                 with open(os.path.join(local_directory, file), 'wb') as local_file:
#                     # Скачивание файла с FTP сервера и запись его в локальный файл
#                     self.ftp.retrbinary(f'RETR {file}', local_file.write)
#
#             # Запись информации о завершении скачивания файлов в журнал
#             self.logger.debug(f'Скачивание файлов директорию {local_directory} завершено')
#
#         except Exception as e:
#             # Запись информации об ошибке при скачивании файлов в журнал
#             self.logger.error(f'Произошла ошибка скачивания файлов: {e}')
#
#
# # Создание экземпляра клиента FTP с указанными учетными данными
# ftp_client = FTPClient('ftp.zakupki.gov.ru', 'free', 'free')
# # Установка соединения с FTP сервером
# ftp_client.connect()
#
# # Определение порта для соединения (не используется в данном контексте)
# port = 21
#
# # Получение путей директорий в корневом каталоге '/fcs_regions'
# directory_path = ftp_client.get_directory_paths('/fcs_regions')
#
# # Определение критериев фильтрации для поиска субдиректорий
# filter_criteria = ['acts', 'contracts', 'notifications', 'protocols', 'currMonth', 'prevMonth']
#
# # Запуск процесса скачивания файлов из указанной удаленной директории в локальную директорию
# remote_directory = '/fcs_regions/Moskva/contracts/currMonth'
# local_directory = r'C:\Users\ofman9\Documents\test'
# ftp_client.download_and_open_file(remote_directory, local_directory)
#
# # Раскомментирование следующего блока кода позволит вывести в консоль полученные директории
# # и субдиректории, соответствующие критериям фильтрации
# # print('Полученные директории с ftp закупки.гов:')
# # for dir_path in directory_path:
# #     print(dir_path)
# #     subdirectories = ftp_client.get_subdirectories(dir_path, filter_criteria)
# #     for sub_dir_path in subdirectories:
# #         print(f'\t{sub_dir_path}')
#
# # Отключение от FTP сервера и завершение сеанса связи
# ftp_client.disconnect()
