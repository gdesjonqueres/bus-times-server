""" Fills db with time schedules for already imported user bus trips
"""

from sqlalchemy.sql import select, and_

from tools.datetime import format_time, minutes_since_midnight, Timezone

from imports.database.connectdb import i_engine
from imports.database.models import (
    i_times,
    i_trips
)

from ..config import SCHEDULE_TIMEZONE
from ..connectdb import db_session
from ..models import (
    RouteTo,
    Service,
    TimeSchedule,
    Stop
)

from .helpers import create_schedule


def run():

    def generate_data():
        services = dict((s.ext_id, s) for s in db_session.query(Service).all())
        routes_to = dict((f'{rt.route.ext_id}-{rt.direction}', rt)
                         for rt in db_session.query(RouteTo).all())
        stops = dict((s.ext_id, s) for s in db_session.query(Stop).all())

        schedule = create_schedule(Timezone(SCHEDULE_TIMEZONE))

        with i_engine.connect() as conn:
            s = select([
                i_trips.c.route_id,
                i_trips.c.direction_id,
                i_times.c.stop_id,
                i_trips.c.service_id,
                i_times.c.departure_time, ]
            ).select_from(
                i_times.join(i_trips, i_trips.c.trip_id == i_times.c.trip_id)
            ).where(
                and_(
                    i_trips.c.service_id.in_(services.keys()),
                    (i_trips.c.route_id + '-' +
                     i_trips.c.direction_id).in_(routes_to.keys()),
                    i_times.c.stop_id.in_(stops.keys())
                )
            ).order_by(
                i_trips.c.route_id,
                i_trips.c.direction_id,
                i_times.c.stop_id,
                i_trips.c.service_id,
                i_times.c.departure_time,)
            res = conn.execute(s).fetchall()
            for row in res:
                time = format_time(row['departure_time'], ':')
                db_session.add(TimeSchedule(
                    schedule=schedule,
                    stop=stops[row['stop_id']],
                    service=services[row['service_id']],
                    route_to=routes_to[f"{row['route_id']}-{row['direction_id']}"],
                    time=time,
                    minutes=minutes_since_midnight(time)
                ))

    try:
        generate_data()
        db_session.commit()
    except BaseException:
        db_session.rollback()
        raise
