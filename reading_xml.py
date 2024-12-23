import logging
import zipfile
import os
import xml.etree.ElementTree as ET
from loguru import logger


class XMLZipFileHandler:
    def __init__(self, extraction_path):
        self.extraction_path = extraction_path


    def extract_xml_files(self, output_directory):
        try:
            for root, dirs, files in os.walk(self.extraction_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith('.zip'):
                        logger.debug(f'Извлечение файлов из архива {file_path}')
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(output_directory)
                        logger.debug('Извлечение завершено успешно')

        except Exception as e:
            logger.error(f'Ошибка при извлечении файлов из архива: {e}')


    def process_xml_files(self, input_directory):
        try:
            for root_1, dirs, files in os.walk(input_directory):
                for file in files:
                    file_path = os.path.join(root_1, file)
                    if file_path.endswith('.xml'):
                        logger.debug(f'Чтение файла XML: {file_path}')
                        try:
                            tree = ET.parse(file_path)
                            root = tree.getroot()
                            for elem in root.iter():
                                logger.debug(f'Tag: {elem.tag}, Text: {elem.text}')

                        except Exception as e:
                            logger.error(f'Произошла ошибка чтения файла xml: {e}')

        except Exception as e:
            logger.error(f'Ошибка чтения файлов полная {e}')



extraction_path = r'C:\Users\wangr\OneDrive\Документы\тест'
output_directory = r'C:\Users\wangr\OneDrive\Документы\тест2'

processor = XMLZipFileHandler(extraction_path)
processor.extract_xml_files(output_directory)
processor.process_xml_files(output_directory)
