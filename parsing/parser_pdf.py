def extracting_pdf_file_archive(archive_directory: object, output_directory: object) -> None:
    """
    Функция для извлечения файлов PDF из архива ZIP.

    :param archive_directory: принимает путь до файла с архивом документов PDF
    :param output_directory: извлекает по указанному пути документы PDF из архива
    :rtype: None
    """
    pass


def extract_search_phrase_pdf(output_directory: object, search_word: str) -> object:
    """
    Функция для парсинга и извлечения данных из файла PDF, сверяет на словосочетание в тексте
    документа и возвращает строку с найденным текстом и название документа.

    :param output_directory: принимает путь до файла из функции def extracting_pdf_file_archive
    :param search_word: принимает в качестве аргумента слово, по которому будет производиться поиск
    :rtype: возвращает найденную строку в документе целиком, если она содержит в себе указанное слово,
     и наименование файла в котором найдено слово.
    """
    pass
