import logging

class ColoredConsoleHandler(logging.StreamHandler):
    COLOR_CODES = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m'  # Purple
    }

    def emit(self, record):
        try:
            # Get the color corresponding to the log level
            level_color = self.COLOR_CODES.get(record.levelname, '\033[0m')  # Default to reset color
            msg = f"{level_color}{record.msg}\033[0m"  # Apply color to the message

            # Update the record message
            record.msg = msg

            super().emit(record)
        except Exception:
            self.handleError(record)

    def formatException(self, ei):
        # Format the exception with the appropriate color
        return f"{self.COLOR_CODES['ERROR']}{super().formatException(ei)}\033[0m"

class LoggerConfig:
    @staticmethod
    def configure_logger(logger):
        logger.setLevel(logging.DEBUG)

        # Create a handler and set the formatter
        handler = ColoredConsoleHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)
