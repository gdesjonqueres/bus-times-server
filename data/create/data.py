""" Fills app.db with routes, stops, trips, services
as defined in user_data.yaml and filtered from import.db
"""

from pathlib import Path
from ruamel.yaml import YAML

from ..connectdb import db_session
from .helpers import (
    create_route,
    create_route_to,
    create_stop,
    create_trip,
    create_bus_trip,
    create_service
)

path_to_user_data = 'data/user_data.yaml'


def run():
    yaml = YAML(typ='safe')

    routes = {}
    routes_to = {}
    stops = {}
    trips = []
    services = []

    def add_route_to(route_to_code):
        (route_code, direction_name) = route_to_code.split('-')
        direction_name = direction_name.replace('_', ' ')
        if (route_code in routes):
            route = routes[route_code]
        else:
            route = create_route(route_code)
            routes[route_code] = route
        routes_to[route_to_code] = create_route_to(route, direction_name)

    def add_stop(desc, code):
        stops[desc] = create_stop(code, desc.replace('_', ' '))

    def add_trip(code, trip):
        (trip_from, trip_to) = tuple(s.strip()
                                     for s in trip['name'].split('>'))
        trip_info = {
            'code': code,
            'name': trip['name'],
            'trip_from': trip_from,
            'trip_to': trip_to
        }
        trips.append(
            create_trip(trip_info, [
                create_bus_trip(
                    routes_to[bt['route']],
                    stops[bt['stop']],
                    bt.get('minutes')
                ) for bt in trip['buses']
            ]))

    def add_service(days, ext_id):
        services.append(create_service(days, ext_id))

    def generate_data():
        data = yaml.load(Path(path_to_user_data))

        for route_to in data['routes']:
            add_route_to(route_to)

        for code, id in data['stops'].items():
            add_stop(code, id)

        for code, id in data['services'].items():
            add_service(code, id)

        for code, trip in data['trips'].items():
            add_trip(code, trip)

    try:
        generate_data()

        for service in services:
            db_session.add(service)

        for trip in trips:
            db_session.add(trip)

        db_session.commit()
    except:
        db_session.rollback()
        raise
