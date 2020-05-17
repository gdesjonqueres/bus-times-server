from .base import *
from .time_schedule import TimeSchedule


class BusTrip(Base):
    __tablename__ = 'bus_trip'

    # id = Column(Integer, primary_key=True)
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # trip_id = Column(Integer, ForeignKey('trip.id'), nullable=False)
    trip_id = Column(GUID(), ForeignKey('trip.id'), nullable=False)
    trip = relationship('Trip', back_populates='bus_trips')

    # route_to_id = Column(Integer, ForeignKey('route_to.id'), nullable=False)
    route_to_id = Column(GUID(), ForeignKey('route_to.id'), nullable=False)
    route_to = relationship("RouteTo")

    # stop_from_id = Column(Integer, ForeignKey('stop.id'), nullable=False)
    stop_from_id = Column(GUID(), ForeignKey('stop.id'), nullable=False)
    stop_from = relationship('Stop', back_populates='bus_trips')

    # stop_to_id = Column(Integer, ForeignKey('stop.id'))
    # stop_to = relationship('Stop')

    minutes = Column(SmallInteger)

    def get_timetable(self):
        query = db_session.query(TimeSchedule)\
            .join(BusTrip,
                  (BusTrip.route_to_id == TimeSchedule.route_to_id) &
                  (BusTrip.stop_from_id == TimeSchedule.stop_id))\
            .filter(BusTrip.id == self.id)\
            .order_by(TimeSchedule.service_id, TimeSchedule.minutes)

        return query.all()

    def __repr__(self):
        return f'<BusTrip route={self.route_to.route.name} stop={self.stop_from.code}>'

    def to_dict(self):
        return {
            "id": self.id,
            "stop_id": self.stop_from_id,
            "itinary_id": self.route_to_id,
            "minutes": self.minutes,
            "__comment": f"{self.route_to.route.name} @ {self.stop_from.description}"
        }
