from ariadne import (
    ObjectType,
    convert_kwargs_to_snake_case
)

from api.static_api import StaticApi
from api.live_api import LiveApi

static_api = StaticApi()
live_api = LiveApi()

trip = ObjectType("Trip")

trip.set_alias('from', 'trip_from')
trip.set_alias('to', 'trip_to')


@trip.field("scheduledBuses")
@convert_kwargs_to_snake_case
def resolve_scheduled_buses(obj, _, *, from_date=None, time_frame=None):
    try:
        return {'results': static_api.get_coming_buses(obj, from_date, time_frame)}
    except ValueError as err:
        return {'error': str(err)}


@trip.field("liveBuses")
@convert_kwargs_to_snake_case
def resolve_live_buses(obj, _, *, time_frame=None):
    try:
        return {'results': live_api.get_coming_buses(obj, time_frame)}
    except ValueError as err:
        return {'error': str(err)}
