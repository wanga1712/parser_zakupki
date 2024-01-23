import logging

from custom_logger import LoggerConfig
from config import ConfigSettings
from open_file.extract_files import Extract

class ParsingXml(Extract):
    #наследуем из родительского класса Extract путь до распакованного файла XML
    def __init__(self, extract_dir_xml: (str)) -> None:
        super().__init__(extract_dir_xml)

        # Конфигурация логгера для ведения журнала событий
        self.logger = logging.getLogger(__name__)  # Получение логгера для текущего модуля
        LoggerConfig.configure_logger(self.logger)  # Настройка логгера согласно конфигурации

    def foo(self):
        print(self.extract_dir_xml)
        print()

parsing = ParsingXml(ConfigSettings.get_config_value('xml_output_local_directory'))
print(parsing)
parsing.foo()