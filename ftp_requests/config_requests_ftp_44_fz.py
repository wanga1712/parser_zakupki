import os


class FTPClientSettings:
    """
        Класс для хранения настроек подключения к FTP серверу.

        Этот класс предоставляет базовые настройки для установления соединения с FTP сервером,
        включая адрес сервера, имя пользователя, пароль и порт. Эти настройки используются
        клиентом FTP для аутентификации и подключения к серверу.

        Attributes:
            ftp_remote_path_44_fz (str): удаленный путь в котором содержаться файлы с разметкой XML;
            host (str): Адрес сервера FTP;
            username (str): Имя пользователя для аутентификации;
            password (str): Пароль пользователя для аутентификации;
            port (int): Порт сервера FTP, по умолчанию 21.
        """

    # ftp_remote_path_44_fz = '/fcs_regions/Moskva/contracts/currMonth'
    host = 'ftp.zakupki.gov.ru'  # Адрес сервера FTP
    username = 'free'  # Имя пользователя для аутентификации
    password = 'free'  # Пароль пользователя для аутентификации
    port = 21  # Порт сервера FTP, по умолчанию 21

    @staticmethod
    def get_config_value_ftp_settings(key):
        '''
        Возвращает значение конфигурационной переменной по ключу, используется для настроек функции соединения
        с сервером.
        Params:
            :param key (str): Имя конфигурационной переменной.
        return:
            Значение переменной, если она существует, иначе None.
        '''
        return getattr(FTPClientSettings, key, None)

    @staticmethod
    def get_json_file_path():
        """
            Получает путь к JSON-файлу.

            Returns:
                str: Путь к JSON-файлу.
            """
        # Получение пути к JSON-файлу
        current_directory = os.path.dirname(__file__)  # Получение текущей директории модуля
        json_file_name = 'directories.json'  # Имя вашего JSON-файла
        return os.path.join(current_directory, json_file_name)
