""" Mappers for mapping import data to app data
"""

from tools.datetime import Timezone

from imports.database.models import (
    i_routes,
    i_directions,
    i_stops,
    i_feed
)


def map_route(route: dict) -> dict:
    return {
        'name': route[i_routes.c.route_short_name],
        'description': route[i_routes.c.route_long_name],
        'ext_id': route[i_routes.c.route_id],
    }


def map_route_direction(direction: dict) -> dict:
    return {
        'direction': direction[i_directions.c.direction_id],
        'route_to': direction[i_directions.c.direction_name],
    }


def map_stop(stop: dict) -> dict:
    return {
        'code': stop[i_stops.c.stop_code],
        'name': stop[i_stops.c.stop_name],
        'ext_id': stop[i_stops.c.stop_id],
    }


def map_feed(feed: dict, timezone: Timezone) -> dict:
    return {
        'version': feed[i_feed.c.feed_version],
        'published': timezone.parse(feed[i_feed.c.feed_version].split('_')[1], '%Y%m%d'),
        'begin': timezone.parse(feed[i_feed.c.feed_start_date], '%Y%m%d'),
        'end': timezone.parse(feed[i_feed.c.feed_end_date], '%Y%m%d'),
        'timezone': timezone.timezone.zone,
    }


def map_service(service: dict) -> dict:
    return {
        'mon': int(service.monday) == 1,
        'tue': int(service.tuesday) == 1,
        'wed': int(service.wednesday) == 1,
        'thu': int(service.thursday) == 1,
        'fri': int(service.friday) == 1,
        'sat': int(service.saturday) == 1,
        'sun': int(service.sunday) == 1
    }
