import os
import shutil
import xml.etree.ElementTree as ET
from config import ConfigSettings  # Предполагается, что ConfigSettings определен в модуле config
from loguru import logger

class ParsingXml():

    def __init__(self):
        """
        Инициализирует объект класса.
        """
        self.xml_unpacked_dir = ConfigSettings.get_config_value('xml_unpacked_local_directory')
        self.xml_positive_dir = ConfigSettings.get_config_value('xml_positive_file_directory')
        self.okpd_set = set(ConfigSettings.get_config_value('set_okpd'))

    def parse_and_move_files(self):
        """
        Парсит XML-файлы на предмет совпадения <OKPD2><code> с кодами из списка.
        Переносит или удаляет файлы в зависимости от результата.
        """
        for filename in os.listdir(self.xml_unpacked_dir):
            file_path = os.path.join(self.xml_unpacked_dir, filename)

            if filename.endswith('.xml'):
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    code_elements = root.findall('.//OKPD2/code')

                    if any(code.text in self.okpd_set for code in code_elements):
                        positive_file_path = os.path.join(self.xml_positive_dir, filename)
                        shutil.move(file_path, positive_file_path)
                        logger.info(f"Файл {filename} перенесен в {self.xml_positive_dir}")
                    else:
                        os.remove(file_path)
                        logger.info(f"Файл {filename} удален из {self.xml_unpacked_dir}")

                except ET.ParseError as e:
                    logger.error(f"Ошибка парсинга XML в файле {filename}: {e}")
                except Exception as e:
                    logger.error(f"Ошибка обработки файла {filename}: {e}")
