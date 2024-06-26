class ConfigSettings:
    '''
    Класс ConfigSettings содержит конфигурационные переменные для использования во всем приложении.

    Atributes:
        :ftp_remote_path_44_fz (str): путь до ftp сервера ЕИС по 44-ФЗ, к папкам, которые содержат данные
         о торгах по регионам;
        :atr xml_zip_local_director (str): путь до папки, содержащей ZIP архивы документов XML;
        :atr xml_unpacked_local_directory (str): путь до папки для распакованных документов XML;
        :atr xml_zip_local_directory (str): путь до папки содержащей ZIP архивы документов XML
        :atr zip_archive_local_directory (str): путь до папки, содержащей ZIP архивы документов, скачанных с ЕИС;
        :atr unpacked_output_local_directory (str): нпуть до папки для распакованных ZIP архивов документов PDF;
        :atr inn_set (list): набор ИНН для первичного условия парсинга файлов XML;
        :atr set_okpd (list): набор данных по ОКПД для первичного условия парасинга файлов XML;
        :atr start_date: дата, начиная с которой скачиваем архивы с FTP ЕИС.

    Methods:
        get_config_value(key): Возвращает значение конфигурационной переменной по ключу.
    '''

    # Определение удаленного пути и даты для фильтрации файлов
    zip_archive_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\архив_проектов'
    unpacked_output_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\разархивированные_документы_торги'
    xml_zip_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\архив_xml_тест'
    xml_unpacked_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\разархивированные_xml'
    xml_positive_file_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\позитивный файл xml'
    set_okpd = ['42.1', '42.11', '42.11.1', '42.11.10', '42.11.10.120', '42.11.10.121', '42.11.20', '42.11.20.100',
                '42.11.20.200', '42.11.20.300', '42.11.20.900', '72', '42.13.10', '71.12.14', '71.12.14.000',
                '72.1', '71', '71.1', '71.11', '71.11.2', '71.11.21', '42.13.10', '42.13.2']
    start_date = '20240510'  # Дата в формате 'YYYYMMDD'

    @staticmethod
    def get_config_value(key):
        '''
        Возвращает значение конфигурационной переменной по ключу.
        Params:
            :param key (str): Имя конфигурационной переменной.
        return:
            Значение переменной, если она существует, иначе None.
        '''
        return getattr(ConfigSettings, key, None)