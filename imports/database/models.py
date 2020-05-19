from sqlalchemy import MetaData
from sqlalchemy.sql import select, and_

from .connectdb import i_engine

i_meta = MetaData()
i_meta.reflect(bind=i_engine)

i_routes = i_meta.tables['routes']
i_directions = i_meta.tables['route_directions']
i_stops = i_meta.tables['stops']
i_times = i_meta.tables['stop_times']
i_trips = i_meta.tables['trips']
i_feed = i_meta.tables['feed_info']
i_service = i_meta.tables['calendar']


def get_route(code: str):
    with i_engine.connect() as conn:
        s = select([i_routes]).where(i_routes.c.route_short_name == code)
        res = conn.execute(s)
        row = res.fetchone()
        if row is None:
            raise ValueError(f'ImportDB: No route {code} was found')
        return row


def get_route_direction(code: str, direction_name: str):
    with i_engine.connect() as conn:
        # numeric route codes are left padded with 0
        select_code = code.rjust(3, '0') if code.isnumeric() else code
        s = select([i_directions])\
            .where(and_(
                i_directions.c.route_name == select_code,
                i_directions.c.direction_name == direction_name))
        res = conn.execute(s)
        row = res.fetchone()
        if row is None:
            raise ValueError(
                f'ImportDB: No direction {direction_name} was found for route {code}')
        return row


def get_stop(code: str):
    with i_engine.connect() as conn:
        s = select([i_stops]).where(i_stops.c.stop_code == code)
        res = conn.execute(s)
        row = res.fetchone()
        if row is None:
            raise ValueError(f'ImportDB: No stop {code} was found')
        return row


def get_feed():
    with i_engine.connect() as conn:
        s = select([i_feed])
        res = conn.execute(s)
        row = res.fetchone()
        if row is None:
            raise ValueError('ImportDB: No feed found')
        return row


def get_service(service_id):
    with i_engine.connect() as conn:
        s = select([i_service]).where(i_service.c.service_id == service_id)
        res = conn.execute(s)
        row = res.fetchone()
        if row is None:
            raise ValueError(f'ImportDB: No service {service_id} was found')
        return row


def get_timetable(route_code, direction_id, stop_code):
    with i_engine.connect() as conn:
        s = select([
            i_trips.c.service_id,
            i_times.c.departure_time
        ]).select_from(
            i_times
            .join(i_stops, i_stops.c.stop_id == i_times.c.stop_id)
            .join(i_trips, i_trips.c.trip_id == i_times.c.trip_id)
            .join(i_routes, i_routes.c.route_id == i_trips.c.route_id)
        ).where(
            and_(
                i_stops.c.stop_code == stop_code,
                i_trips.c.direction_id == direction_id,
                i_routes.c.route_short_name == route_code
            )
        ).order_by(
            i_trips.c.service_id,
            i_times.c.departure_time,)
        res = conn.execute(s)
        rows = res.fetchall()
        if not rows:
            raise ValueError(f'ImportDB: No timetable found for route {route_code}'
                             f' direction {direction_id} at stop {stop_code}')
        return rows
