class ConfigSettings:
    '''
    Класс ConfigSettings содержит конфигурационные переменные для использования во всем приложении.

    Atributes:
        :atr page_address (str): путь до веб-страницы откуда нужно спарсить данные
        :atr zip_archive_local_directory (str): путь до папки содержащей ZIP архивы документов скачанные с ЕИС
        :atr unpacked_output_local_directory (str): путь до папки для распаковванных ZIP архивов документов PDF
        :atr xml_zip_local_directory (str): путь до папки содержащей ZIP архивы документов XML
        :atr xml_unpacked_local_directory (str): путь до папки для распакованных документов XML
        :atr tag_set (list): набор тегов для парсинга данных с сайта гос. закупки
        :atr inn_set (list): набор ИНН для первичного условия парсинга файлов XML
        :atr date (DATA): дата начиная с которой скачиваем архивы с FTP ЕИС

    Methods:
        get_config_value(key): Возвращает значение конфигурационной переменной по ключу.
    '''

    page_address = r'https://zakupki.gov.ru/epz/order/notice/ok504/view/documents.html?regNumber=0364100001819000010'
    zip_archive_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\архив_проектов'
    unpacked_output_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\разархивированные_документы_торги'
    xml_zip_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\архив_xml_тест'
    xml_unpacked_local_directory = r'C:\Users\wangr\OneDrive\Документы\тест парсера закупок\разархивированные_xml'
    tag_set = ['a href']
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
