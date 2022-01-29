import logging

FORMAT = "%(asctime)s.%(msecs)03d - %(name)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s"


class CustomFormatter(logging.Formatter):
    """ColoredFormatter to change colors depending on severity level"""

    CSI = "\x1b"
    GREEN = CSI + "[32m"
    GREY = CSI + "[97m"
    YELLOW = CSI + "[33m"
    RED = CSI + "[31m"
    MAGENTA = CSI + "[95m"
    RESET = CSI + "[0m"

    FORMATS = {
        logging.DEBUG: GREEN + FORMAT + RESET,
        logging.INFO: GREY + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: MAGENTA + FORMAT + RESET,
        logging.NOTSET: MAGENTA + FORMAT + RESET
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, "%d.%m.%Y %H:%M:%S")
        return formatter.format(record)
