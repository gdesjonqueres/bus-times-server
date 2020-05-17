from ariadne import ObjectType

bus_trip = ObjectType("BusTrip")


@bus_trip.field("route")
def resolve_bus_trip_route(obj, _):
    return obj.route_to


@bus_trip.field("stop")
def resolve_bus_trip_stop(obj, _):
    return obj.stop_from


@bus_trip.field("timetable")
def resolve_bus_trip_timetable(obj, _):
    return obj.get_timetable()
