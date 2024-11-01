from loguru import logger
import os
import psycopg2
from dotenv import load_dotenv

from config import ConfigSettings


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

        self.zip_directory = ConfigSettings.get_config_value('zip_archive_local_directory')


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

    # испытуемые методы ниже, для парсинга файла xml

    def insert_file_downloaded(self, filename):
        try:
            query = """
                INSERT INTO archives_of_folders_with_eis_44_Federal_Law (filename)
                VALUES (%s)
                RETURNING file_id;
            """
            self.cursor.execute(query, (filename,))
            self.connection.commit()
            file_id = self.cursor.fetchone()[0]
            logger.debug(f'Данные успешно вставлены в таблицу archives_of_folders_with_eis_44_Federal_Law: {filename}')
            return file_id
        except Exception as e:
            self.connection.rollback()
            logger.exception(f'Ошибка при вставке данных в таблицу archives_of_folders_with_eis_44_Federal_Law: {e}')
            return None

    def insert_contract_data(self, archive_id, **kwargs):
        """
        Вставка данных в таблицу contract_data. Поля передаются в виде именованных аргументов.

        Args:
            archive_id (int): Идентификатор архива из таблицы archives_file_xml_name_eis.
            **kwargs: Именованные аргументы, соответствующие полям таблицы contract_data.
        """
        try:
            # Добавляем archive_id к переданным аргументам
            kwargs['archive_id'] = archive_id

            # Формирование списка полей и значений для вставки
            fields = kwargs.keys()
            values = kwargs.values()

            # Формирование строки запроса
            query = f"INSERT INTO contract_data ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})"

            # Выполнение запроса
            self.cursor.execute(query, list(values))
            self.connection.commit()
            logger.debug(
                f'Данные успешно вставлены в таблицу contract_data: {kwargs.get("purchase_number", "не указан")}')
        except Exception as e:
            self.connection.rollback()
            logger.exception(f'Ошибка при вставке данных в таблицу contract_data: {e}')

    def insert_archive_file_xml_name(self, file_id, archive_name):
        try:
            query = """
                INSERT INTO archives_file_xml_name_eis (file_id, archive_name)
                VALUES (%s, %s)
                RETURNING id;
            """
            self.cursor.execute(query, (file_id, archive_name))
            self.connection.commit()
            new_id = self.cursor.fetchone()[0]
            logger.debug(f'Данные успешно вставлены в таблицу archives_file_xml_name_eis: {archive_name}')
            return new_id
        except Exception as e:
            self.connection.rollback()
            logger.exception(f'Ошибка при вставке данных в таблицу archives_file_xml_name_eis: {e}')
            return None

    def get_last_file_id(self):
        try:
            query = """
                SELECT file_id
                FROM archives_of_folders_with_eis_44_Federal_Law
                ORDER BY file_id DESC
                LIMIT 1;
            """
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result:
                last_file_id = result[0]
            else:
                last_file_id =\
                    None
            return last_file_id
        except Exception as e:
            logger.exception(f'Ошибка при получении последнего file_id: {e}')
            return None

    def get_last_archive_id(self):
        try:
            query = """
                SELECT archive_id
                FROM archives_file_xml_name_eis
                ORDER BY archive_id DESC
                LIMIT 1;
            """
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result:
                last_archive_id = result[0]
            else:
                last_archive_id = None
            return last_archive_id
        except Exception as e:
            logger.exception(f'Ошибка при получении последнего archive_id: {e}')
            return None

    def get_contract_data(self, data_id):
        """
        Получение data_id и documentation_links из таблицы contract_data по data_id.

        Args:
            data_id (int): Идентификатор данных.

        Returns:
            dict: Словарь с полями data_id и documentation_links.
        """
        try:
            query = """
                SELECT contract_id, documentation_links
                FROM contract_data
                WHERE contract_id = %s;
            """
            self.cursor.execute(query, (data_id,))
            result = self.cursor.fetchone()
            if result:
                return {"data_id": result[0], "documentation_links": result[1]}
            else:
                return None
        except Exception as e:
            print(f"Ошибка при получении данных из таблицы contract_data: {e}")
            return None

    # def get_all_contract_data(self):
    #     """
    #     Получение всех data_id и documentation_links из таблицы contract_data.
    #
    #     Returns:
    #         list: Список словарей с полями data_id и documentation_links.
    #     """
    #     try:
    #         query = """
    #             SELECT data_id, documentation_links
    #             FROM contract_data;
    #         """
    #         self.cursor.execute(query)
    #         results = self.cursor.fetchall()
    #         all_data = [{"data_id": row[0], "documentation_links": row[1]} for row in results]
    #         return all_data
    #     except Exception as e:
    #         print(f"Ошибка при получении данных из таблицы contract_data: {e}")
    #         return []

    def fetch_contract_data(self):
        """
        Получает данные контрактов из базы данных.
        """
        try:
            query = """
                SELECT data_id, documentation_links
                FROM contract_data;
            """
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"Ошибка при получении данных из таблицы contract_data: {e}")
            return []

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.debug('Соединение с базой данных закрыто.')


# Пример использования
if __name__ == "__main__":
    db_manager = DatabaseManager()
    download_links = db_manager.download_and_process_documents()
    db_manager.close()
