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
    zip_archive_local_directory = r'E:\Программирование\Парсинг ЕИС\архив_проектов'
    unpacked_output_local_directory = r'E:\Программирование\Парсинг ЕИС\разархивированные_документы_торги'
    xml_zip_local_directory = r'E:\Программирование\Парсинг ЕИС\архив_xml'
    xml_unpacked_local_directory = r'E:\Программирование\Парсинг ЕИС\разархивированные_xml'
    xml_positive_file_directory = r'E:\Программирование\Парсинг ЕИС\позитивный файл xml'
    set_okpd = ["71", "71.1", "71.11.2", "71.11.21", "71.11.21.000", "71.11.22", "71.11.22.000", "71.11.23",
                "71.11.24", "71.12", "71.12.1", "71.12.12", "71.12.13", "71.12.14", "71.12.19", "41", "41.1", "41.10",
                "41.10.1", "41.10.10.000", "41.2", "41.20", "41.20.1", "41.20.10", "41.20.10.110", "41.20.10.120",
                "41.20.10.130", "41.20.10.140", "41.20.10.190", "41.20.2", "41.20.20", "41.20.3", "41.20.30",
                "41.20.4", "41.20.40", "42", "42.1", "42.11", "42.11.1", "42.11.10", "42.11.2", "42.11.20",
                "42.12", "42.12.1", "42.12.10", "42.12.2", "42.12.20", "42.13", "42.13.1", "42.13.10", "42.13.2",
                "42.13.20", "42.9", "42.91", "42.91.1", "42.91.10", "42.91.10.160", "42.91.10.130", "42.91.2",
                "42.91.20"
                ]
    set_stop_words = ['асфальтобетонных', 'асфальтобетонного', 'асфальтового покрытия', 'асфальтного',
                      'аварийно-восстановительных', 'аварийно-восстановительные', 'асфальтовых покрытий',
                      'автоматического пункта', 'автозимников', 'аттестации', 'автозимника', 'авторский надзор',
                      'авторского надзора', 'благоустройство', 'бордюрных съездов',
                      'берегоукрепительного', 'берегоукрепительных', 'береговых', 'береговые',
                      'восстановлению профиля', 'водоотведения', 'водоотведение', 'водоотводнойи',
                      'восстановление дорожной', 'видеонаблюдение', 'видеонаблюдению', 'видеонаблюдения', 'веществ',
                      'визуальных наблюдений', 'визуального контроля', 'выездных мероприятий',
                      'выбросови', 'в муниципальную собственность', 'вод', 'газовый', 'газовому', 'гравийных',
                      'гравийный', 'грунтовой', 'грунтовых дорог', 'гравийной', 'грейдированию', 'грейдирования',
                      'гравийного', 'грейдирование', 'гидротехнического', 'деревянного', 'деревянных',
                      'дозиметрического', 'дозиметров',
                      'дорожного полотна', 'дорожное полотно', 'деревянного тротуара', 'диагностике сети', 'дизель',
                      'дорожных знаков', 'дорожной разметки', 'дорожного покрытия', 'дорожными неровностями',
                      'дорожного движения', 'дублирующих знаков', 'движимого', 'дверей', 'дверьюи', 'единства',
                      'единство', 'зимняя скользкость', 'зимнему', 'зимнее', 'зимника', 'земельных', 'землеустройству',
                      'землеустроительных работ', 'землеустроительном', 'затопления', 'загрязняющих',
                      'замене ленолеума', 'замена ленолеума', 'зон охраны', 'камеральных',
                      'инженерных сетей', 'инеженерные сети', 'искусственных неровностей', 'испытания', 'измерение',
                      'изношенных слоев', 'инженерной защиты', 'инструментальной проверке',
                      'инструментальной диагностике', 'идентификации', 'инженерные сети',
                      'калибровке', 'калибровки', 'кабель', 'кабеля', 'корректировки проектной', 'канав', 'кадастр',
                      'кадастровых', 'кадастровом', 'канализации',
                      'карманов', 'крыльца', 'козырьков', 'козырька', 'ледовой', 'ледовая', 'лестничного марша',
                      'ледовых переправ', 'лестничных маршей', 'лестничный марш', 'лифта', 'лифт',
                      'лабораторному сопровождению', 'метрологическом',
                      'метрологии', 'метрологического', 'метрологических', 'метеорологического', 'метрологической',
                      'модульного здания', 'межевания',
                      'межевого плана', 'местоположения', 'модульного здания', 'метрологического', 'метрологии',
                      'микрорайона', 'микрофильмов', 'морозостойкости', 'модулизации', 'недвижимость', 'освещению',
                      'очистке', 'очистка', 'отсыпка', 'отсыпке', 'окон', 'обеспечению безопасности',
                      'обеспечение безопасности', 'организации нерегулируемого', 'обустройство подходов',
                      'остановочных', 'охранной сигнализации', 'проведению диагностики',
                      'покрытия проезжей', 'поверке', 'поверка', 'пожарного водоема', 'пожарного водоёма', 'пожарной',
                      'пожарных', 'проектов организации дорожного', 'приобретение квартиры', 'приобретение жилого',
                      'приобретение жилых', 'приобретение жилья', 'приобретение благоустроенного', 'полевых',
                      'приобретение благоустроенных', 'приобретение в муниципальную', 'приобретение 1',
                      'приобретение в',
                      'приобретение одного', 'профилировка', 'приемочной диагностики', 'права аренды',
                      'пешеходной лестницы', 'перед зданием', 'поставка электротехнических', 'поставка жилого',
                      'поставки', 'передвижных', 'подсыпка', 'пешеходных', 'переправы', 'переправа', 'пожарных',
                      'пожарного водоема', 'пожарного водоёма', 'противогололедной', 'противогололедная',
                      'противопожарного', 'проведению контроля', 'поверки', 'поверка', 'плотины', 'плотина',
                      'пожаротушению', 'паромных', 'паром', 'паспортизации', 'пожарных', 'пандусов',
                      'повышение энергетической', 'расчистке', 'расчистка', 'разметки', 'разметка', 'регулирование',
                      'регулирования', 'ремонт котла', 'разворотной площадки',
                      'ремонт бассейна', 'ремонт тротуаров', 'ремонт дороги', 'рыночной стоимости', 'спецтехнике',
                      'спецтехника', 'спецтехникой', 'съемке', 'съемка', 'снос', 'сносу', 'сетей отопления',
                      'светофорных объектов', 'санитарное содержание', 'спортивной площадки', 'сантехники',
                      'сантехника', 'санузла', 'санузел', 'снос', 'сносу', 'санитарно-защитной', 'скотомогильник',
                      'светофорного', 'системы анализа', 'системы отопления',
                      'систем отопления', 'снегоочистка', 'содержание ледовой', 'содержанию проездов',
                      'систем ветиляции', 'системы ветиляции', 'санитарной охраны', 'светофорных объектов',
                      'системы отопления', 'строительного контроля', 'строительному контролю',
                      'тревожной', 'технических планов', 'технических паспортов', 'тротуара', 'топографо-геодезической',
                      'технического надзора', 'трубы', 'труба', 'труб', 'устройство тротуаров', 'укрепеление переезда',
                      'укрепление',
                      'укрепление обочин', 'узла учета', 'цифровой базы', 'щебеночных', 'экспертизы оборудования',
                      'энергоэффективных мероприятий', 'электромонтажные', 'электромонтажных', 'электроснабжения',
                      'ямочный', 'ямочного', 'ямочному',
                      'ямочно', 'ямочно-ремонтных']

    start_date = '20240101'  # Дата в формате 'YYYYMMDD'

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
