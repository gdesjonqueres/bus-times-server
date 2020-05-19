from data.connectdb import db_session
from data.models import (
    Trip,
    Schedule,
    Service,
    RouteTo,
    Stop
)


class StaticApi:
    """Interface to app data

    """

    def get_stops(self):
        return db_session.query(Stop).all()

    def get_services(self):
        return db_session.query(Service).all()

    def get_routes(self):
        return db_session.query(RouteTo).all()

    def get_trips(self):
        return db_session.query(Trip).all()

    def get_schedule(self):
        return Schedule.get(db_session)

    def get_trip_by_id(self, id):
        return db_session.query(Trip).filter_by(id=id).one()

    def get_trip_by_code(self, code):
        return db_session.query(Trip).filter_by(code=code).one()

    def get_coming_buses(self, trip: Trip, from_date=None, time_frame=None):
        return trip.get_scheduled_buses(from_date, time_frame)
