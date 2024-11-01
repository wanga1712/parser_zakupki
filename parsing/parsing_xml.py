import os
import shutil
import xml.etree.ElementTree as ET
from loguru import logger
from tqdm import tqdm

from config import ConfigSettings  # Предполагается, что ConfigSettings определен в модуле config
from database.database_connection import DatabaseManager


class ParsingXml():

    def __init__(self):
        """
        Инициализирует объект класса.
        """
        self.xml_unpacked_dir = ConfigSettings.get_config_value('xml_unpacked_local_directory')
        self.xml_positive_dir = ConfigSettings.get_config_value('xml_positive_file_directory')
        self.db_manager = DatabaseManager()
        self.archive_id = None
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

    def find_text(self, element, path, namespaces):
        found_element = element.find(path, namespaces)
        return found_element.text if found_element is not None else None

    def parse_and_store_data(self):
        """
        Парсит XML-файлы и выводит необходимые данные в консоль.
        """
        files = [f for f in os.listdir(self.xml_unpacked_dir) if f.endswith('.xml')]
        for filename in tqdm(files, desc="Обработка файлов", unit="файл"):
            file_path = os.path.join(self.xml_unpacked_dir, filename)
            sig_file_path = os.path.splitext(file_path)[0] + '.sig'

            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                # Указываем пространства имен
                namespaces = {
                    'ns2': 'http://zakupki.gov.ru/oos/base/1',
                    'ns3': 'http://zakupki.gov.ru/oos/export/1',
                    'ns4': 'http://zakupki.gov.ru/oos/common/1',
                    'ns5': 'http://zakupki.gov.ru/oos/EPtypes/1',
                    'ns6': 'http://zakupki.gov.ru/oos/TPtypes/1',
                    'ns7': 'http://zakupki.gov.ru/oos/KOTypes/1',
                    'ns8': 'http://zakupki.gov.ru/oos/CPtypes/1',
                    'ns9': 'http://zakupki.gov.ru/oos/pprf615types/1',
                    'ns10': 'http://zakupki.gov.ru/oos/SMTypes/1',
                    'ns11': 'http://zakupki.gov.ru/oos/URTypes/1',
                    'ns12': 'http://zakupki.gov.ru/oos/EATypes/1',
                    'ns13': 'http://zakupki.gov.ru/oos/printform/1',
                    'ns14': 'http://zakupki.gov.ru/oos/control99/1'
                }

                # Ищем okpd2_code
                okpd2_code = self.find_text(root,
                                            './/ns5:contractConditionsInfo/ns5:IKZInfo/ns5:OKPD2Info/ns4:OKPD2/ns2:OKPDCode',
                                            namespaces)

                if okpd2_code in self.okpd_set:
                    # Здесь вы можете выполнить дополнительные действия
                    logger.debug(f"OKPD2 Code {okpd2_code} найден в файле {filename}")
                    file_id = self.db_manager.get_last_file_id()  # Получаем последний file_id
                    archive_name = filename
                    self.db_manager.insert_archive_file_xml_name(file_id, archive_name)


                    # Извлечение остальных данных
                    purchase_number = self.find_text(root, './/ns5:commonInfo/ns5:purchaseNumber', namespaces)
                    purchase_url = self.find_text(root, './/ns5:commonInfo/ns5:href', namespaces)
                    etp_name = self.find_text(root, './/ns5:commonInfo/ns5:ETP/ns2:name', namespaces)
                    start_date = self.find_text(root,
                                                './/ns5:notificationInfo/ns5:procedureInfo/ns5:collectingInfo/ns5:startDT',
                                                namespaces)
                    end_date = self.find_text(root,
                                              './/ns5:notificationInfo/ns5:procedureInfo/ns5:collectingInfo/ns5:endDT',
                                              namespaces)
                    okpd2_name = self.find_text(root,
                                                './/ns5:contractConditionsInfo/ns5:IKZInfo/ns5:OKPD2Info/ns4:OKPD2/ns2:OKPDName',
                                                namespaces)
                    purchase_object_info = self.find_text(root, './/ns5:commonInfo/ns5:purchaseObjectInfo', namespaces)
                    customer_short_name = self.find_text(root,
                                                         './/ns5:purchaseResponsibleInfo/ns5:responsibleOrgInfo/ns5:shortName',
                                                         namespaces)
                    customer_fact_address = self.find_text(root,
                                                           './/ns5:purchaseResponsibleInfo/ns5:responsibleOrgInfo/ns5:factAddress',
                                                           namespaces)
                    contractor_inn = self.find_text(root,
                                                    './/ns5:purchaseResponsibleInfo/ns5:responsibleOrgInfo/ns5:INN',
                                                    namespaces)
                    contractor_kpp = self.find_text(root,
                                                    './/ns5:purchaseResponsibleInfo/ns5:responsibleOrgInfo/ns5:KPP',
                                                    namespaces)

                    # Извлечение всех ссылок на документацию
                    documentation_links = [attachment.text for attachment in root.findall('.//ns4:url', namespaces)]

                    archive_id = self.db_manager.get_last_archive_id()  # Получаем последний file_id

                    # Вызов функции для вставки данных в БД
                    self.db_manager.insert_contract_data(
                        archive_id=archive_id,
                        purchase_number=purchase_number,
                        purchase_url=purchase_url,
                        etp_name=etp_name,
                        start_date=start_date,
                        end_date=end_date,
                        okpd2_code=okpd2_code,
                        okpd2_name=okpd2_name,
                        purchase_object_info=purchase_object_info,
                        customer_short_name=customer_short_name,
                        customer_inn=contractor_inn,
                        customer_kpp=contractor_kpp,
                        customer_fact_address=customer_fact_address,
                        documentation_links=documentation_links
                    )

                    # Удаление файлов после вставки данных в БД
                    os.remove(file_path)
                    if os.path.exists(sig_file_path):
                        os.remove(sig_file_path)

                else:
                    os.remove(file_path)
                    if os.path.exists(sig_file_path):
                        os.remove(sig_file_path)

            except ET.ParseError as e:
                logger.error(f"Ошибка при парсинге файла {filename}: {e}")

            except Exception as e:
                logger.error(f"Ошибка при обработке файла {filename}: {e}")
                continue


if __name__ == "__main__":
    parser = ParsingXml()
    parser.parse_and_store_data()

# # Пример использования
# if __name__ == "__main__":
#     logger.add("file_processing.log", rotation="1 MB") # Записываем логи в файл
#     parser = ParsingXml()
#     parser.parse_and_move_files()
