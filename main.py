from ftp_requests.ftp_request_44_fz import FTPDownloader

# Создаем экземпляр класса FTPDownloader
ftp_downloader = FTPDownloader()

# Вызываем метод скачивания файлов из ЕИС ФТП гос.закупок
ftp_downloader.download_files()
