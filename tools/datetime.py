from datetime import datetime
import pytz


class Timezone:
    """Helper class to provide localized datetime in a specific timezone

    """

    def __init__(self, timezone: str):
        """Constructor
        timezone is a standard timezone code

        """
        self.timezone = pytz.timezone(timezone)

    def is_aware(self, dt: datetime) -> bool:
        """Return True if dt is aware (a timezone is set on the object)

        """
        return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

    def now(self, no_seconds=True) -> datetime:
        """Return now in current timezone

        """
        dt = datetime.now(tz=pytz.utc)
        if no_seconds:
            dt = dt.replace(second=0, microsecond=0)
        return dt.astimezone(self.timezone)

    def localize(self, dt: datetime) -> datetime:
        """Localize dt in current timezone

        """
        if self.is_aware(dt):
            return dt.astimezone(self.timezone)
        return self.timezone.localize(dt)

    def parse(self, text: str, pattern: str, replace_date=False) -> datetime:
        """Return the corresponding datetime in current timezone

        """
        dt = datetime.strptime(text, pattern)
        if replace_date:
            now = self.now()
            dt = dt.replace(year=now.year, month=now.month, day=now.day)
        return self.localize(dt)

    def parse_time(self, text: str, pattern: str):
        """Return the corresponding datetime in current timezone
        with today's date

        """
        return self.parse(text, pattern, True)


class DateTime:
    pass


def get_hours_minutes(time_str: str, separator: str = ':') -> (int, int):
    """Return the tuple (int hours, int minutes)
    from a string representing time

    """
    (hours, minutes) = time_str.split(separator)[:2]
    return int(hours), int(minutes)


def format_time(time_str: str, separator: str = ':') -> str:
    """Return a properly formated time string
    making sure that numeric values are on two digits
    and left padded with '0' if less than 10

    """
    (hours, minutes) = get_hours_minutes(time_str, separator)
    if hours < 10:
        hours = '0' + str(hours)
    if minutes < 10:
        minutes = '0' + str(minutes)
    return f'{hours}{separator}{minutes}'


def minutes_since_midnight(time_str: str, separator: str = ':') -> int:
    """Return the total number of minutes since midnight for a given time

    """
    (hours, minutes) = get_hours_minutes(time_str, separator)
    return minutes_since_midnight_int(hours, minutes)


def minutes_since_midnight_int(hours: int, minutes: int) -> int:
    """Return the total number of minutes since midnight for a given time

    """
    return hours * 60 + minutes


def ymd_to_dashed(ymd: str) -> str:
    """Return a 'yyyy-mm-dd' string representation of a date
    in a 'yyyymmdd' form

    """
    return '-'.join([ymd[0:4], ymd[4:6], ymd[6:]])
