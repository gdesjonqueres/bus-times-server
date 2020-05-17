from datetime import timedelta

from tools.datetime import minutes_since_midnight_int

from .base import *
from .time_schedule import TimeSchedule
from .bus_trip import BusTrip
from .service import Service
from .schedule import Schedule


class Trip(Base):
    __tablename__ = 'trip'

    # id = Column(Integer, primary_key=True)
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    code = Column(String(10), nullable=False)
    name = Column(String(80), nullable=False)

    trip_from = Column(String(80), nullable=False)
    trip_to = Column(String(80), nullable=False)

    description = Column(String(150))

    def get_scheduled_buses(self, from_date=None, time_frame=None):
        schedule = Schedule.get()
        if from_date is None:
            from_date = schedule.tz.now()
        else:
            from_date = schedule.tz.localize(from_date)

        if time_frame is None:
            time_frame = 45

        if time_frame < 15:
            raise ValueError("Minimum time frame is 15 minutes")
        if time_frame > 120:
            raise ValueError("Maximum time frame is 120 minutes")
        if not schedule.is_valid_for(from_date):
            raise ValueError("Schedule is not valid for given date")

        hours = from_date.hour
        minutes = from_date.minute
        from_date_schedule = from_date

        # between midnight and before 2am we fall in yesterday time schedule
        # 0am is then the 24th hour of the time schedule, 1am is 25th
        if hours < 2:
            hours = hours + 24
            from_date_schedule = from_date_schedule - timedelta(days=1)

        from_minutes = minutes_since_midnight_int(hours, minutes)

        service = Service.get_service_for_date(from_date_schedule)

        TimeSchedule.seed_date(from_date)

        query = db_session.query(TimeSchedule, BusTrip)\
            .filter(TimeSchedule.service_id == service.id)\
            .filter(BusTrip.trip_id == self.id)\
            .filter((BusTrip.route_to_id == TimeSchedule.route_to_id) &
                    (BusTrip.stop_from_id == TimeSchedule.stop_id))\
            .filter(between(TimeSchedule.minutes, from_minutes, from_minutes + time_frame))\
            .order_by(TimeSchedule.minutes)
        results = query.all()

        TimeSchedule.seed_date(None)

        return results

    def __repr__(self):
        return f'<Trip {self.code} {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "from": self.trip_from,
            "to": self.trip_to,
            "description": self.description,
            "itinaries": [bt.to_dict() for bt in self.bus_trips]
        }


Trip.bus_trips = relationship(
    'BusTrip', order_by=BusTrip.id, back_populates='trip')
