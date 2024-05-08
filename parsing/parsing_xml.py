from loguru import logger
from config import ConfigSettings
from open_file.extract_files import Extract

class ParsingXml(Extract):
    #наследуем из родительского класса Extract путь до распакованного файла XML
    def __init__(self, extract_dir_xml: (str)) -> None:
        super().__init__(extract_dir_xml)

    def foo(self):
        print(self.extract_dir_xml)
        print()

parsing = ParsingXml(ConfigSettings.get_config_value('xml_output_local_directory'))
print(parsing)
parsing.foo()