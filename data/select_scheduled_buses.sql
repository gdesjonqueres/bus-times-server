SELECT * FROM schedule
  JOIN stop on stop_id = stop.id
  JOIN bus_trip on schedule.route_to_id = bus_trip.route_to_id
  JOIN service on service_id = service.id
  WHERE service.mon AND schedule.minutes BETWEEN 950 AND 980 AND bus_trip.trip_id = 1
  ORDER BY schedule.minutes
LIMIT 10;

Schedule.query\
   .join(Stop)\
   .join(Service)\
   .join(BusTrip, (BusTrip.route_to_id == Schedule.route_to_id) & (BusTrip.stop_from_id == Schedule.stop_id))\
   .options(contains_eager('bus_trips'))
   .filter(Service.mon)\
   .filter(BusTrip.trip_id == 1)\
   .filter(between(Schedule.minutes, 950, 980))\
   .order_by(Schedule.minutes)

db.session.query(Schedule, BusTrip)\
    .join(Stop, Stop.id == Schedule.stop_id)\
    .join(Service)\
    .filter(Service.mon)\
    .filter(BusTrip.trip_id == 1)\
    .filter((BusTrip.route_to_id == Schedule.route_to_id) & (BusTrip.stop_from_id == Schedule.stop_id))\
    .filter(between(Schedule.minutes, 950, 980))\
    .order_by(Schedule.minutes)

SELECT schedule.id, schedule.route_to_id, schedule.stop_id,
  schedule.service_id, schedule.time, schedule.minutes,
  bus_trip.id, bus_trip.trip_id, bus_trip.route_to_id,
  bus_trip.stop_from_id, bus_trip.minutes
FROM bus_trip, schedule
  JOIN stop ON stop.id = schedule.stop_id
  JOIN service ON service.id = schedule.service_id
WHERE service.mon
  AND bus_trip.trip_id = 1
  AND bus_trip.route_to_id = schedule.route_to_id
  AND bus_trip.stop_from_id = schedule.stop_id
  AND schedule.minutes BETWEEN 950 AND 980
ORDER BY schedule.minutes

query getBusesForTrip($code: String!, $fromDate: DateTime, $withInfo: Boolean = false) {
  timetableInfos @include (if: $withInfo) {
    version
    published
    begin
    end
  }
  trip(code:$code) {
    id
    code
    name
    scheduledBuses(fromDate: $fromDate) {
      error
      results {
        busTrip {
          id
          route {
            code
            to
          }
          stop {
            code
            name
          }
          minutes
        }
        scheduledAt
        service {
          days
        }
      }
    }
  }
}
{
  "code": "dst01",
  "fromDate": "2019-12-19 20:10"
}

SELECT * FROM stop_times st
  JOIN trips t ON t.trip_id = st.trip_id
  JOIN routes r ON r.route_id = t.route_id
  JOIN stops s ON s.stop_id = st.stop_id
WHERE t.service_id IN ('1', '2', '3')
  AND r.route_short_name IN ('239');

SELECT r.route_short_name, t.direction_id, d.direction_name, st.departure_time, s.stop_code, s.stop_name FROM stop_times st
  JOIN trips t ON t.trip_id = st.trip_id
  JOIN routes r ON r.route_id = t.route_id
  JOIN stops s ON s.stop_id = st.stop_id
  JOIN route_directions d ON (d.direction_id = t.direction_id AND route_name = r.route_short_name)
WHERE t.service_id IN ('1', '2', '3')
  AND r.route_short_name IN ('230')
ORDER BY t.service_id, t.direction_id, t.trip_id, st.departure_time;

SELECT r.route_short_name, t.direction_id, d.direction_name, st.departure_time, s.stop_code, s.stop_name FROM stop_times st
  JOIN trips t ON t.trip_id = st.trip_id
  JOIN routes r ON r.route_id = t.route_id
  JOIN stops s ON s.stop_id = st.stop_id
  JOIN route_directions d ON (d.direction_id = t.direction_id AND route_name = r.route_short_name)
WHERE t.service_id IN ('1', '2', '3')
  AND s.stop_name = 'LONSDALE QUAY BAY 4 NEW'
ORDER BY r.route_id, t.service_id, t.direction_id, t.trip_id, st.departure_time;

SELECT t.route_id, t.direction_id, st.stop_id, t.service_id, st.departure_time
FROM stop_times st
  JOIN trips t ON t.trip_id = st.trip_id
  JOIN routes r ON r.route_id = t.route_id
WHERE t.service_id IN ('1', '2', '3')
  AND r.route_short_name IN ('232', '239')
ORDER BY t.route_id, t.direction_id, st.stop_id, t.service_id, st.departure_time;


query getSchedAndLive($code: String!, $timeFrame: Int = 120) {
  trip(code: $code) {
    name
    liveBuses(timeFrame: $timeFrame) {
      results {
        ...scheduleFields
      }
    }
    scheduledBuses(timeFrame: $timeFrame) {
      results {
        ...scheduleFields
      }
    }
  }
}

fragment scheduleFields on BusSchedule {
  busTrip {
    route {
      code
    }
    stop {
      code
    }
  }
  scheduledAt
}

{
  "code": "dst01"
}
