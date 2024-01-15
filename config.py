class ConfigSettings:
    '''
    Класс ConfigSettings содержит конфигурационные переменные для использования во всем приложении.

    Atributes:
        :atr page_address (str): путь до веб-страницы откуда нужно спарсить данные
        :atr zip_archive_directory (str): путь до папки содержащей ZIP архивы документов PDF
        :atr pdf_output_directory (str): путь до папки для распаковванных ZIP архивов документов PDF
        :atr xml_zip_local_directory (str): путь до папки содержащей ZIP архивы документов XML
        :atr xml_extracted_path (str): путь до папки для распакованных документов XML
        :atr tag_set (list): набор тегов для парсинга данных с сайта гос. закупки
        :atr inn_set (list): набор ИНН для первичного условия парсинга файлов XML
        :atr date (DATA): дата начиная с которой скачиваем архивы с FTP ЕИС

    Methods:
        get_config_value(key): Возвращает значение конфигурационной переменной по ключу.
    '''

    page_address = r'https://zakupki.gov.ru/'
    zip_archive_directory = r'C:\Users\wangr\OneDrive\Документы\тест'
    pdf_output_directory = r'C:\Users\wangr\OneDrive\Документы\тест2'
    xml_zip_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест'
    xml_extracted_path = r'C:\Users\wangr\OneDrive\Документы\тест2'
    tag_set = []
    set_inn = []
    date = '20240101'  # Дата в формате 'YYYYMMDD'

    # TODO -> путь до удаленного каталога ftp сервера гос. закупки?
    # ftp_remote_path = '/fcs_regions/Moskva/contracts/currMonth'

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
