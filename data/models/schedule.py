from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import reconstructor

from tools.datetime import Timezone

from .base import Base
# from .base import *


class Schedule(Base):
    __tablename__ = 'schedule'

    # class attribute, Schedule is used as a singleton
    _instance = None

    id = Column(Integer, primary_key=True)

    version = Column(String)
    published = Column(DateTime)
    begin = Column(DateTime)
    end = Column(DateTime)
    timezone = Column(String)
    generated = Column(DateTime, default=datetime.utcnow)

    # def __init__(self):
    #     self._tz = None

    @reconstructor
    def __init_on_load__(self):
        self._tz = None
        self.published = self.tz.localize(self.published)
        self.begin = self.tz.localize(self.begin)
        self.end = self.tz.localize(self.end)
        self.generated = Timezone('utc').localize(self.generated)

    @classmethod
    def get(cls, session):
        if not cls._instance:
            cls._instance = session.query(cls).filter_by(id=1).one()
        return cls._instance

    def is_valid_for(self, date: datetime) -> bool:
        return self.begin <= date <= self.end

    @property
    def tz(self) -> Timezone:
        if not self._tz:
            self._tz = Timezone(self.timezone)
        return self._tz

    def __repr__(self):
        return (f'<Schedule version={self.version} '
                f'from={self.begin.isoformat()} to={self.end.isoformat()}>')

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.generated.isoformat(),
            "timezone": self.timezone,
            "feed_info": {
                "version": self.version,
                "published": self.published.isoformat(),
                "validity": {
                    "begin": self.begin.isoformat(),
                    "end": self.end.isoformat()
                }
            }
        }
