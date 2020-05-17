"""Helpers functions to factory models
"""

from tools.datetime import Timezone

from imports.database.models import (
    get_route,
    get_route_direction,
    get_feed,
    get_stop,
    get_timetable,
    get_service
)

from ..models import (
    Trip,
    Service,
    BusTrip,
    Route,
    RouteTo,
    Stop,
    Schedule
)

from .mappers import (
    map_route_direction,
    map_feed,
    map_route,
    map_stop,
    map_service
)


def _import_route(code: str) -> dict:
    return map_route(get_route(code))


def _import_route_direction(code: str, direction_name: str) -> dict:
    return map_route_direction(get_route_direction(code, direction_name))


def _import_stop(code: str) -> dict:
    return map_stop(get_stop(code))


def _import_schedule(timezone: Timezone) -> dict:
    return map_feed(get_feed(), timezone)


def _import_service(service_id: str) -> dict:
    return map_service(get_service(service_id))


def create_route(code: str) -> Route:
    return Route(**_import_route(code))


def create_route_to(route: str, direction_name: str) -> RouteTo:
    return RouteTo(route=route, **_import_route_direction(route.name, direction_name))


def create_stop(code: str, description: str) -> Stop:
    return Stop(**_import_stop(code), description=description)


def create_service(name: str, ext_id: str) -> Service:
    return Service(days=name, **_import_service(ext_id), ext_id=ext_id)


def create_bus_trip(route_to: RouteTo, stop_from: Stop, minutes: int = None) -> BusTrip:
    # make sure a timetable exists for this bus trip
    try:
        get_timetable(route_to.route.name, route_to.direction, stop_from.code)
    except ValueError:
        raise
    return BusTrip(route_to=route_to, stop_from=stop_from, minutes=minutes)


def create_trip(info: dict, bus_trips: list) -> Trip:
    return Trip(**info, bus_trips=bus_trips)


def create_schedule(timezone: Timezone) -> Schedule:
    return Schedule(**_import_schedule(timezone))
