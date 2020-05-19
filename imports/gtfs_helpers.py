""" Helpers for checking, reading, filtering data from gtfs files
"""

import csv

from tools.utils import (
    exchange_indexes_values,
    list_to_dict
)
from tools.datetime import ymd_to_dashed


def get_gtfs_descriptor(path_to_file: str) -> dict:
    """Return a gtfs file descriptor
    a dictionary where each column name indexes its position

    """
    with open(path_to_file, newline='') as fh:
        reader = csv.reader(fh, delimiter=',')
        headers = next(reader)
        return exchange_indexes_values(headers)


def make_gtfs_validator(required_columns: list) -> callable:
    """Return a validator function for a gtfs file

    """
    def validator(path_to_file) -> tuple:
        """Checks if a file has all the required columns
        Returns a tuple (boolean, message)

        """
        descriptor = get_gtfs_descriptor(path_to_file)
        missing = set(required_columns) - set(descriptor.keys())
        if len(missing) > 0:
            return (False, 'column(s) missing: ' + ', '.join(missing))
        return (True, 'OK')
    return validator


check_trips_file = make_gtfs_validator([
    'route_id',
    'direction_id',
    'service_id',
    'trip_id',
])

check_stop_times_file = make_gtfs_validator([
    'trip_id',
    'stop_id',
    'departure_time',
])

check_calendar_file = make_gtfs_validator([
    'service_id',
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
])

check_routes_file = make_gtfs_validator([
    'route_id',
    'route_short_name',
    'route_long_name',
])

check_stops_file = make_gtfs_validator([
    'stop_id',
    'stop_code',
    'stop_name',
])

check_directions_file = make_gtfs_validator([
    'route_name',
    'direction_id',
    'direction_name',
])

check_feed_info_file = make_gtfs_validator([
    'feed_version',
    'feed_start_date',
    'feed_end_date',
])


def filter_gtfs_file(path, filter) -> list:
    """Return all rows from a gtfs file which comply with a given filter

    """
    data = []
    with open(path, newline='') as fh:
        reader = csv.reader(fh, delimiter=',')
        next(reader)  # jump over row headers
        for row in reader:
            if filter(row):
                data.append(row)

    return data


def get_feed_info(path_to_file) -> dict:
    """Return a dictionary of feed info

    """
    descriptor = get_gtfs_descriptor(path_to_file)
    with open(path_to_file, newline='') as fh:
        reader = csv.reader(fh, delimiter=',')
        next(reader)  # jump over headers
        feed_info = next(reader)
    return list_to_dict(feed_info, descriptor)


def parse_feed_info(gtfs_feed_info):
    published_date = ymd_to_dashed(
        gtfs_feed_info['feed_version'].split('_')[1])
    return {
        'version': gtfs_feed_info['feed_version'],
        'published': published_date,
        'validity': {
            'begin': ymd_to_dashed(gtfs_feed_info["feed_start_date"]),
            'end': ymd_to_dashed(gtfs_feed_info["feed_end_date"])
        }
    }


def filter_trips(descriptor, route_ids, path):
    """Filter data from trips

    """
    return filter_gtfs_file(
        path, lambda row: row[descriptor['route_id']] in route_ids)


def filter_stop_times(descriptor, stop_ids, path):
    """Filter stop times

    """
    return filter_gtfs_file(
        path, lambda row: row[descriptor['stop_id']] in stop_ids)
