import logging


class ColoredConsoleHandler(logging.StreamHandler):
    COLOR_CODES = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',  # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m'  # Purple
    }

    def emit(self, record):
        try:
            level_color = self.COLOR_CODES.get(record.levelname, '\033[0m')  # По умолчанию сбрасывается цвет
            msg = f'{level_color}{record.msg}\033[0m'  # Применяем цвет к сообщению

            # Обновить сообщение записи
            record.msg = msg

            super().emit(record)
        except Exception:
            self.handleError(record)

    def format(self, record):
        msg = super().format(record)
        # Отформатируйте исключение соответствующим цветом
        return f"{self.COLOR_CODES[record.levelname]}{msg}\033[0m"


class LoggerConfig:
    @staticmethod
    def configure_logger(logger):
        logger.setLevel(logging.DEBUG)
        # Создаём обработчик и устанавливаем форматтер
        handler = ColoredConsoleHandler()
        formater = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formater)

        # Добавляем обработчик в логгер
        logger.addHandler(handler)
