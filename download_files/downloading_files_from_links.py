from loguru import logger
from tqdm import tqdm
import requests
import re
import os

from config import ConfigSettings
from database.database_connection import DatabaseManager


class DownloadFilesLinks():
    '''
    Класс DownloadFilesLinks предназначен для скачивания файлов, полученных по ссылкам из базы данных.

    Атрибуты:
        :param xml_zip_local_directory (str): Путь до папки, содержащей ZIP-архивы документов XML.
        :param xml_unpacked_local_directory (str): Путь до папки для распакованных документов XML.
        :param zip_archive_local_directory (str): Путь до папки, содержащей ZIP-архивы документов, скачанные с ЕИС.
        :param unpacked_output_local_directory (str): Путь до папки для распакованных ZIP-архивов документов PDF.

    Методы:
        __init__(self): Конструктор класса, инициализирует объект класса, используя значения конфигурации.
    '''

    def __init__(self):
        """
        Инициализирует объект класса DownloadFilesLinks.

        В этом методе происходит:
        - Чтение настроек из конфигурационного файла для указания путей к папкам.
        - Инициализация менеджера базы данных для работы с данными.
        """
        # Инициализация директории для ZIP-архивов с документами
        self.zip_directory = ConfigSettings.get_config_value('zip_archive_local_directory')

        # Инициализация менеджера базы данных для взаимодействия с БД
        self.db_manager = DatabaseManager()

    def decode_filename(self, filename):
        """
        Декодирует имя файла из заголовка Content-Disposition, если оно закодировано.

        Этот метод используется для декодирования имени файла, которое может быть закодировано
        в формате URL (например, с символами, представленными как %XX). Также учитывает кодировку
        `latin1`, чтобы преобразовать строку в байты, а затем декодировать её в UTF-8.

        Параметты:
            filename (str): Имя файла, которое может быть закодировано в формате URL.

        Возвращает:
            str: Декодированное имя файла, если декодирование успешно. Если произошла ошибка, возвращается исходное имя файла.
        """
        try:
            # Удаляем проценты и преобразуем последовательности символов %XX в символы
            decoded_filename = re.sub(r'%[0-9A-Fa-f]{2}', lambda match: chr(int(match.group(0)[1:], 16)), filename)

            # Преобразуем строку в байты, затем декодируем как UTF-8
            utf8_encoded = bytes(decoded_filename, 'latin1').decode('utf-8')
            return utf8_encoded
        except Exception as e:
            # Логируем ошибку, если декодирование не удалось
            logger.error(f"Ошибка при декодировании имени файла: {e}")

            # Если произошла ошибка, возвращаем исходное имя файла без изменений
            return filename

    def download_and_process_documents(self):
        """
        Получает ссылки, скачивает документы и обрабатывает их.

        Этот метод извлекает ссылки на документы из базы данных, проверяет доступность URL,
        скачивает файлы, сохраняет их на диск, и обрабатывает ошибки, если они возникают.

        Параметры:
            Нет.

        Возвращает:
            Нет. Этот метод выполняет действия, такие как скачивание и обработка файлов.
        """
        try:
            # Извлечение данных из базы данных
            results = self.db_manager.fetch_contract_data()
            logger.debug(f"Fetched {len(results)} records from the database.")

            # Устанавливаем заголовки для HTTP-запросов
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            # Создаем директорию для хранения ZIP файлов, если она не существует
            if not os.path.exists(self.zip_directory):
                os.makedirs(self.zip_directory)
                logger.debug(f"Created directory {self.zip_directory}")

            # Прогресс-бар для отслеживания обработки контрактов
            with tqdm(total=len(results), desc="Обработка контрактов", unit="контракт") as pbar:
                # Обработка каждого контракта из базы данных
                for data_id, documentation_links in results:
                    logger.debug(f"Processing data_id: {data_id}")
                    logger.debug(f"Documentation links: {documentation_links}")

                    # Преобразование строкового представления ссылок в список
                    if isinstance(documentation_links, str):
                        documentation_links = [link.strip() for link in documentation_links.strip('[]').split(',')]
                        logger.debug(f"Parsed documentation_links: {documentation_links}")

                    # Скачивание файлов по каждой ссылке
                    for link in documentation_links:
                        if 'file' in link:
                            try:
                                # Проверка доступности URL
                                logger.debug(f"Checking link: {link}")
                                head_response = requests.head(link, headers=headers)
                                head_response.raise_for_status()

                                # Скачивание файла по ссылке
                                response = requests.get(link, headers=headers, stream=True)
                                response.raise_for_status()

                                # Определение имени файла из заголовков или URL
                                content_disposition = response.headers.get('content-disposition')
                                if content_disposition:
                                    filename = re.findall("filename\*?=['\"]?([^;'\"]+)", content_disposition)
                                    if filename:
                                        filename = filename[0].split("''")[-1]
                                        filename = self.decode_filename(filename)
                                    else:
                                        filename = os.path.basename(link.split('?')[0])
                                else:
                                    filename = os.path.basename(link.split('?')[0])

                                # Путь для сохранения файла
                                file_path = os.path.join(self.zip_directory, filename)
                                logger.debug(f"Saving file to: {file_path}")

                                # Запись содержимого файла на диск
                                with open(file_path, 'wb') as file:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        file.write(chunk)

                                logger.debug(f"Файл {filename} успешно скачан.")

                            except Exception as e:
                                # Обработка ошибок при скачивании
                                logger.error(f"Ошибка при скачивании файла по ссылке {link}: {e}")

                    # Обновление прогресс-бара
                    pbar.update(1)

            # Закрытие подключения к базе данных
            self.db_manager.close()

        except Exception as e:
            # Обработка ошибок при обработке документов
            logger.error(f"Ошибка при обработке документов: {e}")

# # Пример использования
# if __name__ == "__main__":
#     download_manager = DownloadFilesLinks()
#     download_links = download_manager.download_and_process_documents()
