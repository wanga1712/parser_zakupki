from loguru import logger
import os
import psycopg2
from dotenv import load_dotenv


class DatabaseManager:
    """
    Класс для управления базой данных.

    Attributes:
        connection (psycopg2.extensions.connection): Соединение с базой данных.
        cursor (psycopg2.extensions.cursor): Курсор для выполнения операций с базой данных.
    """

    def __init__(self):
        """
        Инициализация объекта DatabaseManager.

        Подключается к базе данных и инициализирует курсор.

        Raises:
            Exception: В случае ошибки подключения к базе данных.
        """
        load_dotenv(dotenv_path=r'C:\Users\wangr\PycharmProjects\pythonProject9\config\db_credintials.env')

        # Use the provided database_name or default from DefaultConfig
        self.db_host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_DATABASE")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_port = os.getenv("DB_PORT")

        try:
            # Установление соединения
            self.connection = psycopg2.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )

            self.cursor = self.connection.cursor()
            logger.debug('Подключился к базе данных.')
        except Exception as e:
            logger.exception(f'Ошибка подключения к базе данных: {e}')

    def check_file_exists(self, filename):
        """
        Проверяет наличие файла в базе данных.

        Args:
            filename (str): Имя файла для проверки.

        Returns:
            bool: True, если файл найден, False в противном случае.
        """
        try:
            query = "SELECT COUNT(*) FROM downloaded_files_ftp_44_fz WHERE filename = %s"
            self.cursor.execute(query, (filename,))
            count = self.cursor.fetchone()[0]
            return count > 0
        except psycopg2.Error as e:
            logger.error(f"Ошибка при проверке файла в базе данных: {e}")
            return False

    def insert_file(self, filename):
        """
        Добавляет запись о файле в базу данных.

        Args:
            filename (str): Имя файла для вставки.

        Raises:
            psycopg2.Error: Если произошла ошибка при выполнении запроса.
        """
        try:
            query = "INSERT INTO downloaded_files_ftp_44_fz (filename) VALUES (%s)"
            self.cursor.execute(query, (filename,))
            self.connection.commit()
            logger.debug("Запись о файле успешно добавлена в базу данных.")
        except psycopg2.Error as e:
            logger.error(f"Ошибка при вставке файла в базу данных: {e}")
            raise e
