""" Generates json files containing all bus data from db
"""

import json
from uuid import UUID

from tools.utils import save_to_json

from .connectdb import db_session
from .models import (
    Trip,
    BusTrip,
    Stop,
    TimeSchedule,
    Schedule,
    Service,
    RouteTo
)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


schedule = Schedule.get(db_session)
trips = {t.code: t.to_dict() for t in db_session.query(Trip).all()}
stops = {s.id.hex: s.to_dict() for s in db_session.query(Stop).all()}
routes_to = {rt.id.hex: rt.to_dict() for rt in db_session.query(RouteTo).all()}

# request all time schedules
query = db_session.query(TimeSchedule, BusTrip, Stop, Service)\
    .join(BusTrip,
          (BusTrip.route_to_id == TimeSchedule.route_to_id) &
          (BusTrip.stop_from_id == TimeSchedule.stop_id))\
    .join(Stop)\
    .join(Service)\
    .order_by(Stop.code, Service.days, TimeSchedule.time)
res = query.all()
times = {}
for r in res:
    stop = r.Stop.id.hex
    service = r.Service.days
    time = r.TimeSchedule.time
    bus_trip = r.BusTrip.id
    times.setdefault(stop, {})\
        .setdefault(service, {})\
        .setdefault(time, [])\
        .append(bus_trip)

export = {
    **schedule.to_dict(),
    "destinations": trips,
    "itinaries": routes_to,
    "stops": stops,
    "times": times,
}

save_to_json('./data/exports/data.json', export, encoder=UUIDEncoder)
save_to_json('./data/exports/data-readable.json',
             export, readable=True, encoder=UUIDEncoder)

export_graphql = {
    "schedule": schedule.to_dict(),
    "destinations": list(trips.values()),
    "itinaries": list(routes_to.values()),
    "stops": list(stops.values()),
    "times": times,
}

save_to_json('./data/exports/data-graphql.json',
             export_graphql, encoder=UUIDEncoder)
save_to_json('./data/exports/data-graphql-readable.json',
             export_graphql, readable=True, encoder=UUIDEncoder)
