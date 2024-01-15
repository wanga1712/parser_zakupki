# Функция для извлечения файлов PDF из архива ZIP
def extracting_pdf_file_archive(archive_directory: object, output_directory: object) -> None:
    """
    :param archive_directory: принимает путь до файла с архивом документов PDF
    :param output_directory: извлекает по указанному пути документы PDF из архива
    :rtype: None
    """
    pass


# Функция для парсинга и извлечения данных из файла PDF, сверяет на словосочетание в тексте
# документа и возвращает строку с найденным текстом и название документа
def extract_search_phrase_pdf(output_directory: object, search_word: str) -> object:
    """
    :param output_directory: принимает путь до файла из функции def extracting_pdf_file_archive
    :param search_word: принимает в качестве аргумента слово, по которому будет производиться поиск
    :rtype: возвращает найденную строку в документе целиком, если она содержит в себе указанное слово,
     и наименование файла в котором найдено слово
    """
    pass


# Функция для автоматического скачивания ZIP архива документов с сайта ЕИС по ссылке
def automatic_downloading_file_from_web_page(
        page_address: object, tag_html, archive_directory) -> None:
    """
    :param page_address: получает адрес страницы, с которой необходимо скачать архив
    :param tag_html: получает tag html страницы, в которой находится ссылка на скачивание документа
    :param archive_directory: скачивает в указанную директорию документы с сайта
    :rtype: None
    """
    pass