from loguru import logger
import os
import psycopg2
from dotenv import load_dotenv

from config import ConfigSettings


class DatabaseManager:
    """
    Класс для управления подключением и взаимодействием с базой данных.

    Атрибуты:
        connection (psycopg2.extensions.connection): Объект соединения с базой данных.
        cursor (psycopg2.extensions.cursor): Курсор для выполнения SQL-запросов к базе данных.
        db_host (str): Хост базы данных.
        db_name (str): Название базы данных.
        db_user (str): Имя пользователя базы данных.
        db_password (str): Пароль пользователя базы данных.
        db_port (str): Порт подключения к базе данных.
        zip_directory (str): Директория для хранения ZIP-архивов.
    """

    def __init__(self):
        """
        Инициализация объекта DatabaseManager.

        Загружает настройки подключения из файла .env, устанавливает соединение с базой данных и инициализирует курсор.

        Исключения:
            Exception: В случае ошибки подключения к базе данных.
        """
        # Загружаем переменные окружения из файла .env
        load_dotenv(dotenv_path=r'C:\Users\wangr\PycharmProjects\pythonProject9\config\db_credintials.env')

        # Получаем данные для подключения к базе данных
        self.db_host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_DATABASE")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_port = os.getenv("DB_PORT")

        # Директория для хранения ZIP-архивов
        self.zip_directory = ConfigSettings.get_config_value('zip_archive_local_directory')

        try:
            # Устанавливаем соединение с базой данных
            self.connection = psycopg2.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )

            # Инициализируем курсор для выполнения операций с базой данных
            self.cursor = self.connection.cursor()
            logger.debug('Подключился к базе данных.')
        except Exception as e:
            # Логируем и выбрасываем исключение в случае ошибки подключения
            logger.exception(f'Ошибка подключения к базе данных: {e}')

    def check_file_exists(self, filename):
        """
        Проверяет, существует ли указанный файл в базе данных.

        Аргументы:
            filename (str): Имя файла, которое необходимо проверить.

        Возвращает:
            bool: True, если файл найден в базе данных, иначе False.

        Исключения:
            psycopg2.Error: Возникает при ошибке выполнения SQL-запроса.
        """
        try:
            # Формируем запрос для проверки наличия файла в таблице базы данных
            query = "SELECT COUNT(*) FROM downloaded_files_ftp_44_fz WHERE filename = %s"
            self.cursor.execute(query, (filename,))  # Выполняем запрос с параметром filename
            count = self.cursor.fetchone()[0]  # Получаем результат запроса

            # Если результат больше нуля, значит файл найден
            return count > 0
        except psycopg2.Error as e:
            # Логируем ошибку в случае возникновения исключения
            logger.error(f"Ошибка при проверке файла в базе данных: {e}")
            return False

    def insert_file(self, filename):
        """
        Добавляет запись о файле в базу данных.

        Аргументы:
            filename (str): Имя файла, которое необходимо добавить в базу данных.

        Возвращает:
            None

        Исключения:
            psycopg2.Error: Возникает, если произошла ошибка при выполнении SQL-запроса.
        """
        try:
            # Формируем SQL-запрос для добавления записи о файле в таблицу базы данных
            query = "INSERT INTO downloaded_files_ftp_44_fz (filename) VALUES (%s)"
            self.cursor.execute(query, (filename,))  # Выполняем запрос с параметром filename
            self.connection.commit()  # Фиксируем изменения в базе данных
            logger.debug("Функция: insert_file - Запись о файле успешно добавлена в базу данных.")
        except psycopg2.Error as e:
            # Логируем ошибку и передаем исключение дальше
            logger.error(f"Ошибка при вставке файла в базу данных: {e}")
            raise e

    # испытуемые методы ниже, для парсинга файла xml

    def insert_file_downloaded(self, filename):
        """
        Вставляет запись о загруженном файле в таблицу архива и возвращает ID вставленной записи, если она еще не существует.

        Аргументы:
            filename (str): Имя загруженного файла для добавления в таблицу.

        Возвращает:
            int или None: Возвращает идентификатор вставленного файла (file_id),
            если операция прошла успешно, или None в случае ошибки.

        Исключения:
            Exception: Если произошла ошибка при выполнении запроса или при вставке данных.
        """
        try:
            # Проверяем, существует ли уже запись с таким filename
            check_query = "SELECT file_id FROM archives_of_folders_with_eis_44_Federal_Law WHERE filename = %s"
            self.cursor.execute(check_query, (filename,))
            existing_file = self.cursor.fetchone()

            if existing_file:
                # Если файл уже существует, записываем информацию в лог и пропускаем вставку
                logger.debug(f"Запись с filename '{filename}' уже существует в таблице.")
                return None  # Можно вернуть ID найденной записи, если нужно

            # Если запись не найдена, выполняем вставку
            insert_query = """
                INSERT INTO archives_of_folders_with_eis_44_Federal_Law (filename)
                VALUES (%s)
                RETURNING file_id;
            """
            self.cursor.execute(insert_query, (filename,))
            self.connection.commit()
            file_id = self.cursor.fetchone()[0]
            logger.debug(f'Данные успешно вставлены в таблицу archives_of_folders_with_eis_44_Federal_Law: {filename}')
            return file_id

        except Exception as e:
            # Откатываем транзакцию и логируем ошибку
            self.connection.rollback()
            logger.exception(f'Ошибка при вставке данных в таблицу archives_of_folders_with_eis_44_Federal_Law: {e}')
            return None

    def insert_contract_data(self, archive_id, **kwargs):
        """
        Вставляет данные в таблицу contract_data, если запись с данным purchase_number еще не существует.

        Аргументы:
            archive_id (int): Идентификатор архива из таблицы archives_file_xml_name_eis.
            **kwargs: Именованные аргументы, соответствующие полям таблицы contract_data.

        Исключения:
            Exception: Если произошла ошибка при выполнении запроса или при вставке данных.
        """
        try:
            # Добавляем archive_id к переданным аргументам
            kwargs['archive_id'] = archive_id
            purchase_number = kwargs.get("purchase_number")

            # Проверка существования записи по purchase_number
            check_query = "SELECT 1 FROM contract_data WHERE purchase_number = %s"
            self.cursor.execute(check_query, (purchase_number,))
            existing_record = self.cursor.fetchone()

            if existing_record:
                # Если запись уже существует, логируем это и пропускаем вставку
                logger.debug(f"Запись с purchase_number '{purchase_number}' уже существует. Вставка пропущена.")
                return None

            # Формируем список полей и значений для вставки
            fields = kwargs.keys()
            values = kwargs.values()

            # Формируем строку запроса для вставки данных
            insert_query = f"INSERT INTO contract_data ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})"
            self.cursor.execute(insert_query, list(values))
            self.connection.commit()  # Фиксируем изменения в базе данных
            logger.debug(f"Данные успешно вставлены в таблицу contract_data: {purchase_number}")

        except Exception as e:
            # Откатываем транзакцию в случае ошибки и логируем исключение
            self.connection.rollback()
            logger.exception(f"Ошибка при вставке данных в таблицу contract_data: {e}")

    def insert_archive_file_xml_name(self, file_id, archive_name):
        """
        Вставляет данные о файле в таблицу archives_file_xml_name_eis, если они еще не существуют.

        Аргументы:
            file_id (int): Идентификатор файла, который будет связан с архивом.
            archive_name (str): Имя архива, которое будет сохранено в таблице.

        Возвращает:
            int: Новый идентификатор записи в таблице (возвращаемый после вставки).
            None: В случае, если запись уже существует или произошла ошибка вставки данных.

        Исключения:
            Exception: Если произошла ошибка при выполнении запроса или вставке данных.
        """
        try:
            # Проверяем, существует ли уже запись с данным archive_name
            check_query = "SELECT id FROM archives_file_xml_name_eis WHERE archive_name = %s"
            self.cursor.execute(check_query, (archive_name,))
            existing_record = self.cursor.fetchone()

            if existing_record:
                # Если запись уже существует, логируем это и пропускаем вставку
                logger.debug(f"Запись с archive_name '{archive_name}' уже существует.")
                return None  # Можно вернуть существующий id, если это необходимо

            # Если записи нет, выполняем вставку
            insert_query = """
                INSERT INTO archives_file_xml_name_eis (file_id, archive_name)
                VALUES (%s, %s)
                RETURNING id;
            """
            self.cursor.execute(insert_query, (file_id, archive_name))
            self.connection.commit()  # Фиксируем изменения в базе данных
            new_id = self.cursor.fetchone()[0]  # Получаем id вставленной записи
            logger.debug(f'Данные успешно вставлены в таблицу archives_file_xml_name_eis: {archive_name}')
            return new_id

        except Exception as e:
            # Откатываем транзакцию и логируем ошибку
            self.connection.rollback()
            logger.exception(f'Ошибка при вставке данных в таблицу archives_file_xml_name_eis: {e}')
            return None

    def get_last_file_id(self):
        """
        Получает последний file_id из таблицы archives_of_folders_with_eis_44_Federal_Law.

        Возвращает:
            int: Последний file_id в таблице, если он существует.
            None: Если данных нет или произошла ошибка при выполнении запроса.

        Исключения:
            Exception: В случае ошибки выполнения запроса или обработки данных.
        """
        try:
            # Запрос для получения последнего file_id
            query = """
                SELECT file_id
                FROM archives_of_folders_with_eis_44_Federal_Law
                ORDER BY file_id DESC
                LIMIT 1;
            """
            # Выполнение запроса
            self.cursor.execute(query)
            result = self.cursor.fetchone()

            # Проверка на наличие данных
            if result:
                last_file_id = result[0]  # Получаем последний file_id
            else:
                last_file_id = None  # Если данных нет, возвращаем None

            return last_file_id
        except Exception as e:
            # Логирование ошибки
            logger.exception(f'Ошибка при получении последнего file_id: {e}')
            return None

    def get_last_archive_id(self):
        """
        Получает последний archive_id из таблицы archives_file_xml_name_eis.

        Возвращает:
            int: Последний archive_id в таблице, если он существует.
            None: Если данных нет или произошла ошибка при выполнении запроса.

        Исключения:
            Exception: В случае ошибки выполнения запроса или обработки данных.
        """
        try:
            # Запрос для получения последнего archive_id
            query = """
                SELECT archive_id
                FROM archives_file_xml_name_eis
                ORDER BY archive_id DESC
                LIMIT 1;
            """
            # Выполнение запроса
            self.cursor.execute(query)
            result = self.cursor.fetchone()

            # Проверка на наличие данных
            if result:
                last_archive_id = result[0]  # Получаем последний archive_id
            else:
                last_archive_id = None  # Если данных нет, возвращаем None

            return last_archive_id
        except Exception as e:
            # Логирование ошибки
            logger.exception(f'Ошибка при получении последнего archive_id: {e}')
            return None

    def get_contract_data(self, data_id):
        """
        Получение данных contract_id и documentation_links из таблицы contract_data по заданному data_id.

        Args:
            data_id (int): Идентификатор данных для поиска в таблице contract_data.

        Returns:
            dict: Словарь с полями "data_id" и "documentation_links", если данные найдены.
            None: Если данные не найдены или произошла ошибка при выполнении запроса.

        Исключения:
            Exception: В случае ошибки при выполнении запроса или обработки данных.
        """
        try:
            # Запрос для получения contract_id и documentation_links по data_id
            query = """
                SELECT contract_id, documentation_links
                FROM contract_data
                WHERE contract_id = %s;
            """
            # Выполнение запроса с параметром data_id
            self.cursor.execute(query, (data_id,))
            result = self.cursor.fetchone()

            # Проверка наличия данных и возвращение результата
            if result:
                return {"data_id": result[0], "documentation_links": result[1]}
            else:
                return None
        except Exception as e:
            # Логирование ошибки
            print(f"Ошибка при получении данных из таблицы contract_data: {e}")
            return None

    def fetch_contract_data(self):
        """
        Получает все данные контрактов (data_id и documentation_links) из таблицы contract_data.

        Returns:
            list: Список кортежей с полями "data_id" и "documentation_links" для каждого контракта.
            Пустой список: Если произошла ошибка при выполнении запроса.

        Исключения:
            Exception: В случае ошибки при выполнении запроса или обработки данных.
        """
        try:
            # Запрос для получения всех данных contract_id и documentation_links
            query = """
                SELECT data_id, documentation_links
                FROM contract_data;
            """
            # Выполнение запроса и получение всех результатов
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            return results
        except Exception as e:
            # Логирование ошибки
            logger.error(f"Ошибка при получении данных из таблицы contract_data: {e}")
            return []

    def close(self):
        """
        Закрывает соединение с базой данных и курсор.

        Эта функция завершает работу с базой данных, закрывая соединение и курсор.

        Исключения:
            Exception: Если при закрытии соединения или курсора происходит ошибка.
        """
        try:
            # Закрытие курсора, если он существует
            if self.cursor:
                self.cursor.close()
                logger.debug('Курсор закрыт.')

            # Закрытие соединения, если оно существует
            if self.connection:
                self.connection.close()
                logger.debug('Соединение с базой данных закрыто.')
        except Exception as e:
            # Логирование ошибки при закрытии
            logger.error(f"Ошибка при закрытии соединения с базой данных: {e}")


# Пример использования
if __name__ == "__main__":
    db_manager = DatabaseManager()
    download_links = db_manager.download_and_process_documents()
    db_manager.close()
