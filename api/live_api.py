from datetime import datetime, timedelta

from tools.async_requests import AsyncHTTPRequests
from tools.utils import save_to_json
from tools.datetime import Timezone

from data.connectdb import db_session
from data.models import (
    Trip,
    BusTrip,
    TimeSchedule,
    Service
)

from .config import TRANSLINK_API_KEY
from .translink_api import TranslinkApi


class LiveApi:
    """Get live schedules for user bus trips

    """

    class __ResultContainer:
        """Bus time container

        """

        def __init__(self, bus_trip: BusTrip, timeschedule: TimeSchedule):
            self.BusTrip = bus_trip
            self.TimeSchedule = timeschedule

        @classmethod
        def factory(cls, bus_trip: BusTrip, scheduled_date: datetime):
            service = Service.get_service_for_date(scheduled_date)
            schedule = TimeSchedule(route_to=bus_trip.route_to,
                                    stop=bus_trip.stop_from, service=service,
                                    time=scheduled_date.strftime('%H:%M'))
            schedule.date = scheduled_date
            return cls(bus_trip, schedule)

        def __repr__(self):
            return (f'<BusSchedule route={self.BusTrip.route_to.route.name}'
                    f' stop={self.BusTrip.stop_from.code}'
                    f' date={self.TimeSchedule.date.isoformat()}>')

    def __init__(self):
        self._tl_api = TranslinkApi(
            TRANSLINK_API_KEY, return_request_only=True)
        self.timezone = Timezone(self._tl_api.timezone)
        self._async = AsyncHTTPRequests()

    def _parse_tl_expected_time(self, tl_datetime, timezone: Timezone):
        # if date is included in schedule time
        if len(tl_datetime) > 7:
            return timezone.parse(tl_datetime, '%I:%M%p %Y-%m-%d')
        else:
            now = timezone.now()
            dt = timezone.parse_time(tl_datetime, '%I:%M%p')
            # if scheduled hour is before current hour,
            # it means this is after midnight schedule, so date is tomorrow
            if dt.hour < now.hour:
                dt = dt + timedelta(days=1)
            return dt

    def _get_requests_for_trip(self, trip: Trip, time_frame):
        requests = {}
        for bus_trip in trip.bus_trips:
            requests[bus_trip.id] = self._tl_api.get_estimates(
                bus_trip.stop_from.code, bus_trip.route_to.route.name, time_frame)
        return requests

    def get_bus_trip_by_id(self, bus_trip_id):
        return db_session.query(BusTrip).filter_by(id=bus_trip_id).one()

    async def get_coming_buses(self, trip: Trip, time_frame=40):
        requests = self._get_requests_for_trip(trip, time_frame)
        results = await self._async.fetch(requests)

        save_to_json('./api/tmp/live_results.json',
                     [r[1] for r in results], readable=True)

        times = []
        for (bus_trip_id, estimates) in results:
            bus_trip = self.get_bus_trip_by_id(bus_trip_id)
            for estimate in estimates:
                for schedule in estimate['Schedules']:
                    if schedule['CancelledTrip'] or schedule['CancelledStop']:
                        continue

                    scheduled_date = self._parse_tl_expected_time(
                        schedule['ExpectedLeaveTime'], self.timezone)
                    times.append(
                        LiveApi.__ResultContainer.factory(
                            bus_trip, scheduled_date)
                    )

        return sorted(times, key=lambda e: e.TimeSchedule.date.isoformat())
