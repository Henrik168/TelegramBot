import datetime
import logging.handlers
import os
import sys
import time
from threading import Thread
from datetime import datetime, timedelta
from CustomLogger.customformatter import FORMAT


def get_path(name: str, log_path: str) -> str:
    log_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), log_path))
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    timestamp = datetime.now().strftime("%Y%m%d")
    return os.path.join(log_path, f"{timestamp}_{name}.log")


class TimedFileHandler(Thread):
    def __init__(self, logger: logging.Logger, log_path: str):
        super(TimedFileHandler, self).__init__()
        self.daemon = True

        self.logger = logger
        self.log_path = log_path
        self.last_rollover: datetime = datetime.now()
        self.min_sleep: int = 1
        self.max_sleep: int = 60

        self.start()

    @property
    def next_rollover(self) -> datetime:
        next_day = self.last_rollover + timedelta(days=1)
        return datetime(next_day.year, next_day.month, next_day.day)

    def calc_sleep(self, current_time: datetime) -> int:
        return min(self.max_sleep, max(self.min_sleep, (self.next_rollover - current_time + timedelta(seconds=1)).seconds))

    def sleep(self) -> None:
        while datetime.now() < self.next_rollover:
            sleep_time = self.calc_sleep(datetime.now())
            self.logger.debug(f"Timed File Handler sleep for '{sleep_time}' seconds.")
            time.sleep(sleep_time)

    def do_rollover(self) -> None:
        file_path = get_path(self.logger.name, self.log_path)
        self.logger.debug(f"Change Logfile path to: '{file_path}'")
        fh = logging.FileHandler(file_path)
        fh.setFormatter(logging.Formatter(FORMAT, "%d.%m.%Y %H:%M:%S"))
        self.logger.addHandler(fh)
        self.logger.removeHandler(self.logger.handlers[-2])
        self.last_rollover: datetime = datetime.now()

    def run(self) -> None:
        while True:
            self.sleep()
            self.do_rollover()
