import logging
from CustomLogger.customformatter import CustomFormatter, FORMAT
from CustomLogger.customhandlers import TimedFileHandler, get_path


def getLogger(name: str = "CustomLogger",
              level: int = 20,
              log_path: str = "./log/") -> logging.Logger:
    # create logger
    logger = logging.getLogger(name)

    # create console handler and set Formatter
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())

    # create directory if not exists
    file_path = get_path(name, log_path)

    # create file handler and set Formatter
    fh = logging.FileHandler(file_path)
    fh.setFormatter(logging.Formatter(FORMAT, "%d.%m.%Y %H:%M:%S"))

    # add Handler
    logger.addHandler(ch)
    logger.addHandler(fh)

    # setting logging level
    logger.setLevel(level)
    fh.setLevel(level)
    ch.setLevel(level)

    # Thread to change Logfile Name at Midnight
    TimedFileHandler(logger, log_path, name)

    logger.info(f"Logger started. Write Logfile to: {file_path}")
    return logger
