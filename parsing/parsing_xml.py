import os
import shutil
import xml.etree.ElementTree as ET
from config import ConfigSettings  # Предполагается, что ConfigSettings определен в модуле config
from loguru import logger
from tqdm import tqdm

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
        files = [f for f in os.listdir(self.xml_unpacked_dir) if f.endswith('.xml')]
        for filename in tqdm(files, desc="Обработка файлов", unit="файл"):
            file_path = os.path.join(self.xml_unpacked_dir, filename)
            sig_file_path = os.path.splitext(file_path)[0] + '.sig'

            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                # Указываем пространство имен при поиске тега <OKPD2>
                ns = {'ns': 'http://zakupki.gov.ru/oos/types/1'}
                okpd2_elements = root.findall('.//ns:OKPD2', ns)

                # Попробуем найти все элементы с тегом <OKPD2> и их дочерние <code>
                code_elements = []
                for okpd2 in okpd2_elements:
                    # logger.debug(f"Элемент OKPD2 найден в файле {filename}: {ET.tostring(okpd2, encoding='unicode')}")
                    code_elements.extend(okpd2.findall('.//ns:code', ns))

                # Приведение кодов из XML и списка к строкам и удаление пробелов
                xml_codes = {code.text.strip() for code in code_elements if code.text}

                # Проверяем точное совпадение каждого кода
                if any(code in self.okpd_set for code in xml_codes):
                    positive_file_path = os.path.join(self.xml_positive_dir, filename)
                    shutil.move(file_path, positive_file_path)
                    if os.path.exists(sig_file_path):
                        os.remove(sig_file_path)
                    logger.info(f"Файл {filename} перенесен в {self.xml_positive_dir} и файл .sig удален")
                else:
                    os.remove(file_path)
                    if os.path.exists(sig_file_path):
                        os.remove(sig_file_path)
                    logger.info(f"Файл {filename} и соответствующий .sig файл удалены из {self.xml_unpacked_dir}")

            except ET.ParseError as e:
                logger.error(f"Ошибка парсинга XML в файле {filename}: {e}")
            except Exception as e:
                logger.error(f"Ошибка обработки файла {filename}: {e}")

# # Пример использования
# if __name__ == "__main__":
#     logger.add("file_processing.log", rotation="1 MB") # Записываем логи в файл
#     parser = ParsingXml()
#     parser.parse_and_move_files()
