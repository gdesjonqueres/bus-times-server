from ariadne import QueryType

from api.static_api import StaticApi

api = StaticApi()

query = QueryType()


@query.field("stops")
def resolve_stops(*_):
    return api.get_stops()


@query.field("services")
def resolve_services(*_):
    return api.get_services()


@query.field("routes")
def resolve_routes(*_):
    return api.get_routes()


@query.field("trips")
def resolve_trips(*_):
    return api.get_trips()


@query.field("trip")
def resolve_trip(*_, id=None, code=None):
    if id is not None:
        return api.get_trip_by_id(id)
    if code is not None:
        return api.get_trip_by_code(code)


@query.field("timetableInfos")
def resolve_timetable_infos(*_):
    return api.get_schedule()
