import os
import re
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

    def find_text(self, element, path, namespaces=None):
        """
        Извлекает текст из элемента XML по заданному пути. Если пространства имен уже удалены,
        параметр `namespaces` можно игнорировать.
        """
        found_element = element.find(path)
        return found_element.text if found_element is not None else None

    def remove_namespaces(self, xml_string):
        """
        Полностью удаляет все пространства имен из XML-строки.
        Убирает как префиксы, так и их определения.
        """
        # Удаление всех атрибутов xmlns:... и xmlns="..."
        no_namespaces = re.sub(r'\sxmlns(:\w+)?="[^"]+"', '', xml_string)
        # Удаление всех префиксов вида <ns3:tag> и </ns3:tag>
        no_namespaces = re.sub(r'<(/?\w+):', r'<\1', no_namespaces)
        return no_namespaces

    def parse_and_store_data(self):
        """
        Парсит XML-файлы из директории и извлекает необходимые данные для вставки в базу данных.
        Пространства имен удаляются перед обработкой.
        """
        # Получаем список всех файлов с расширением .xml в директории
        files = [f for f in os.listdir(self.xml_unpacked_dir) if f.endswith('.xml')]

        # Проходим по каждому XML-файлу
        for filename in tqdm(files, desc="Обработка файлов", unit="файл"):
            file_path = os.path.join(self.xml_unpacked_dir, filename)  # Полный путь к XML-файлу
            sig_file_path = os.path.splitext(file_path)[0] + '.sig'  # Путь к .sig файлу (если существует)

            try:
                # Читаем XML-файл
                with open(file_path, 'r', encoding='utf-8') as file:
                    xml_data = file.read()

                # Удаляем пространства имен из XML
                cleaned_xml_data = self.remove_namespaces(xml_data)

                # Парсим очищенный XML
                root = ET.fromstring(cleaned_xml_data)

                # Ищем код OKPD2 в XML
                okpd2_code = self.find_text(
                    root,
                    './/contractConditionsInfo/IKZInfo/OKPD2Info/OKPD2/OKPDCode'
                )

                # Если код OKPD2 найден в наборе допустимых кодов
                if okpd2_code in self.okpd_set:
                    logger.debug(f"OKPD2 Code {okpd2_code} найден в файле {filename}")

                    # Получаем последний file_id для архива
                    file_id = self.db_manager.get_last_file_id()
                    archive_name = filename
                    self.db_manager.insert_archive_file_xml_name(file_id, archive_name)

                    # Извлекаем дополнительные данные из XML
                    purchase_number = self.find_text(root, './/commonInfo/purchaseNumber')
                    purchase_url = self.find_text(root, './/commonInfo/href')
                    etp_name = self.find_text(root, './/commonInfo/ETP/name')
                    start_date = self.find_text(root, './/notificationInfo/procedureInfo/collectingInfo/startDT')
                    end_date = self.find_text(root, './/notificationInfo/procedureInfo/collectingInfo/endDT')
                    okpd2_name = self.find_text(root, './/contractConditionsInfo/IKZInfo/OKPD2Info/OKPD2/OKPDName')
                    purchase_object_info = self.find_text(root, './/commonInfo/purchaseObjectInfo')
                    customer_short_name = self.find_text(root,
                                                         './/purchaseResponsibleInfo/responsibleOrgInfo/shortName')
                    customer_fact_address = self.find_text(root,
                                                           './/purchaseResponsibleInfo/responsibleOrgInfo/factAddress')
                    contractor_inn = self.find_text(root,
                                                    './/purchaseResponsibleInfo/responsibleOrgInfo/INN')
                    contractor_kpp = self.find_text(root,
                                                    './/purchaseResponsibleInfo/responsibleOrgInfo/KPP')

                    # Извлекаем ссылки на документы
                    documentation_links = [attachment.text for attachment in root.findall('.//url')]

                    # Получаем ID последнего архива
                    archive_id = self.db_manager.get_last_archive_id()

                    # Вставляем данные в таблицу contract_data
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

                    # Удаляем XML и .sig файлы после успешной вставки данных
                    os.remove(file_path)
                    if os.path.exists(sig_file_path):
                        os.remove(sig_file_path)

                else:
                    # Если OKPD2 код не подходит, удаляем файлы
                    os.remove(file_path)
                    if os.path.exists(sig_file_path):
                        os.remove(sig_file_path)

            except ET.ParseError as e:
                # Логируем ошибку при парсинге XML файла
                logger.error(f"Ошибка при парсинге файла {filename}: {e}")

            except Exception as e:
                # Логируем общие ошибки при обработке файла и продолжаем выполнение
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
