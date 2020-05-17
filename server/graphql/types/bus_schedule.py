from ariadne import ObjectType

bus_schedule = ObjectType("BusSchedule")


@bus_schedule.field("busTrip")
def resolve_schedule_bus_trip(obj, _):
    return obj.BusTrip


@bus_schedule.field("scheduledAt")
def resolve_schedule_time(obj, _):
    return obj.TimeSchedule.date


@bus_schedule.field("service")
def resolve_schedule_service(obj, _):
    return obj.TimeSchedule.service
