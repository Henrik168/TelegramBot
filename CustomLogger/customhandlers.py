import datetime
import logging.handlers
import os
import sys
from time import sleep
from threading import Thread
from datetime import datetime, timedelta
from CustomLogger.customformatter import FORMAT


def get_path(name: str, log_path: str) -> str:
    log_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), log_path))
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    timestamp = datetime.now().strftime("%Y%m%d")
    return os.path.join(log_path, f"{timestamp}_{name}.log")


def calc_sleep(current_time: datetime) -> int:
    next_day = current_time.date() + timedelta(days=1)
    midnight = datetime(next_day.year, next_day.month, next_day.day)
    return max(1, (midnight - datetime.now() + timedelta(seconds=1)).seconds)


class TimedFileHandler(Thread):
    def __init__(self, logger: logging.Logger, log_path: str, name: str):
        super(TimedFileHandler, self).__init__()
        self.daemon = True

        self.logger = logger
        self.log_path = log_path
        self.name = name
        self.sleep_time = calc_sleep(datetime.now())

        self.start()

    def run(self) -> None:
        while True:
            self.logger.info(f"Timed File Handler rollover in '{self.sleep_time}' seconds.")
            sleep(self.sleep_time)
            file_path = get_path(self.name, self.log_path)
            fh = logging.FileHandler(file_path)
            fh.setFormatter(logging.Formatter(FORMAT, "%d.%m.%Y %H:%M:%S"))
            self.logger.addHandler(fh)
            self.logger.removeHandler(self.logger.handlers[-2])
            self.logger.info(f"Change Logfile path to: '{file_path}'")
            self.sleep_time = calc_sleep(datetime.now())
