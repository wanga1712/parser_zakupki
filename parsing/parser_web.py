import requests
from bs4 import BeautifulSoup
import os

from config import ConfigSettings


def automatic_downloading_file_from_web_page(
        page_address: object, tag_set, zip_archive_directory) -> None:
    """
    Функция для автоматического скачивания ZIP архива документов с сайта ЕИС по ссылке.

    :param page_address: получает адрес страницы, с которой необходимо скачать архив
    :param tag_set: получает набор tag html страницы, в которой находится информация
    :param zip_archive_directory: скачивает в указанную директорию документы с сайта
    :rtype: None
    """
    # Отправляем GET-запрос на URL
    response = requests.get(page_address)
    # Создаем объект BeatifulSouop для парсинга HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    # Проходимся по каждому тегу из нашего спсика тегов
    for tag_name in tag_set:
        # Находим все теги данного типа
        for tag in soup.find_all(tag_name):
            # Если тег содержит текст, извлекаем
            if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span']:
                print(tag.get_text())
            # Если тег содержит ссылку на файл, скачиваем файл
            elif tag.name == 'a' and tag['href'].startswith('http'):
                file_url = tag['href']
                file_name = os.path.basename(file_url)
                # Полный путь к файлу, включая имя директории
                full_file_path = os.path.join(zip_archive_directory, file_name)
                # Отправляем GET-запрос на URL файла
                with requests.get(file_url, stream=True) as file_response:
                    # Открываем файл для записи в бинарном режиме
                    with open(file_name, 'wb') as file:
                        # Записываем содержимое файла по частям
                        for chunk in file_response.iter_content(chunk_size=8192):
                            file.write(chunk)
                        print(f'Файл {file_name} скачан')
    print(page_address, tag_set, zip_archive_directory)


# Вызов функции с передачей параметров из ConfigSettings
automatic_downloading_file_from_web_page(
    ConfigSettings.page_address, ConfigSettings.tag_set, ConfigSettings.zip_archive_directory)
