from datetime import datetime
from ariadne import ScalarType

def serialize_datetime(value):
    return value.isoformat()


def parse_datetime_value(value):
    if value:
        return datetime.fromisoformat(value)


datetime_scalar = ScalarType(
    'DateTime',
    serializer=serialize_datetime,
    value_parser=parse_datetime_value)
