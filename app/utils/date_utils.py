from datetime import datetime, date, timedelta, timezone
import time


class D:
    def __init__(self, *args):
        self.utc_now = datetime.utcnow()
        self.timedelta = 0
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def datetime(cls, diff: int = 9) -> datetime:
        return cls().utc_now + timedelta(hours=diff) if diff > 0 else cls().utc_now + timedelta(hours=diff)

    @classmethod
    def date(cls, diff: int = 9) -> date:
        return cls.datetime(diff=diff).date()  # 2022-07-24

    @classmethod
    def date_num(cls, diff: int = 9) -> int:
        return int(cls.date(diff=diff).strftime('%Y%m%d'))  # 22020722

    @classmethod
    def timestamp_to_datetime(cls, n_timestamp):
        return datetime.strptime(
            datetime.fromtimestamp(n_timestamp, timezone(timedelta(hours=9))).strftime(cls().datetime_format), cls().datetime_format)

    @staticmethod
    def datetime_to_timestamp(data):
        return int(time.mktime(data.timetuple()))

    @staticmethod
    def validate_date(date_text, date_format):
        try:
            datetime.strptime(date_text, date_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def datetime_to_simple(data):
        return datetime.strftime(data, '%Y년 %m월 %d일 %H시 %M분')

    @staticmethod
    def convert_seconds_to_kor_time(t1):
        """초를 입력받아 읽기쉬운 한국 시간으로 변환"""
        days = t1.days
        _sec = t1.seconds
        (hours, minutes, seconds) = str(timedelta(seconds=_sec)).split(':')
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)

        result = []
        if days >= 1:
            result.append(str(days) + '일')
        if hours >= 1:
            result.append(str(hours) + '시간')
        if minutes >= 1:
            result.append(str(minutes) + '분')
        if seconds >= 1:
            result.append(str(seconds) + '초')
        return ' '.join(result)


