import logging
import zipfile
import os
import xml.etree.ElementTree as ET
import json
from custom_logger import LoggerConfig


class XMLZipFileHandler:
    def __init__(self, extraction_path):
        self.extraction_path = extraction_path

        # Configuration of logger
        self.logger = logging.getLogger(__name__)
        LoggerConfig.configure_logger(self.logger)

    def extract_xml_files(self, output_directory):
        try:
            for root, dirs, files in os.walk(self.extraction_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith('.zip'):
                        self.logger.debug(f'Extracting files from the archive: {file_path}')
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(output_directory)
                        self.logger.debug('Extraction completed successfully')

        except Exception as e:
            self.logger.error(f'Error occurred while extracting files from the archive: {e}')

    def process_xml_files(self, input_directory, output_file):
        try:
            xml_data = []

            for root_1, dirs, files in os.walk(input_directory):
                for file in files:
                    file_path = os.path.join(root_1, file)
                    if file_path.endswith('.xml'):
                        self.logger.debug(f'Reading XML file: {file_path}')
                        try:
                            tree = ET.parse(file_path)
                            root = tree.getroot()
                            for elem in root.iter():
                                xml_data.append({elem.tag: elem.text})

                        except Exception as e:
                            self.logger.error(f'Error occurred while reading XML file: {e}')

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(xml_data, f, ensure_ascii=False, indent=4)
            self.logger.debug(f'XML data saved to JSON file: {output_file}')

        except Exception as e:
            self.logger.error(f'Error occurred while processing XML files: {e}')


extraction_path = r'C:\Users\wangr\OneDrive\Документы\тест'
output_directory = r'C:\Users\wangr\OneDrive\Документы\тест2'
output_file = r'C:\Users\wangr\OneDrive\Документы\output.json'

processor = XMLZipFileHandler(extraction_path)
processor.extract_xml_files(output_directory)
processor.process_xml_files(output_directory, output_file)