from datetime import datetime, timedelta

from sqlalchemy import Column, ForeignKey, SmallInteger, Integer, String
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.orm.session import Session

from tools.sqlalchemy_guid import GUID
from tools.datetime import get_hours_minutes

from .base import Base
from .schedule import Schedule


class TimeSchedule(Base):
    __tablename__ = 'time_schedule'

    # class attribute
    date_seed = None

    id = Column(Integer, primary_key=True)

    schedule_id = Column(Integer, ForeignKey('schedule.id'), nullable=False)
    schedule = relationship("Schedule")

    # route_to_id = Column(Integer, ForeignKey('route_to.id'), nullable=False)
    route_to_id = Column(GUID(), ForeignKey('route_to.id'), nullable=False)
    route_to = relationship("RouteTo")

    # stop_id = Column(Integer, ForeignKey('stop.id'), nullable=False)
    stop_id = Column(GUID(), ForeignKey('stop.id'), nullable=False)
    stop = relationship('Stop')

    # service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    service_id = Column(GUID(), ForeignKey('service.id'), nullable=False)
    service = relationship('Service')

    time = Column(String(5), nullable=False)
    minutes = Column(SmallInteger, nullable=False)

    @classmethod
    def seed_date(cls, date_seed: datetime):
        cls.date_seed = date_seed

    @reconstructor
    def __init_on_load__(self):
        # set object date using seed date from class and object time
        date_seed = self.date_seed if self.date_seed else Schedule.get(
            Session.object_session(self)).tz.now()

        (hours, minutes) = get_hours_minutes(self.time)
        # if scheduled time is hour 24 then time is 0am, hour 25 is 1am
        if hours // 24:
            hours = hours % 24
            # if date_seed is before midnight, then schedule is for tomorrow
            if date_seed.hour >= 2:
                date_seed = date_seed + timedelta(days=1)

        self.date = date_seed.replace(hour=hours, minute=minutes)

    def __repr__(self):
        return (f'<TimeSchedule route={self.route_to.route.name} '
                f'stop={self.stop.code} service={self.service.days} '
                f'time={self.time}>')

    def to_dict(self):
        return {
            "time": self.time,
            "minutes": self.minutes,
        }
