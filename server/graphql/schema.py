from ariadne import (
    make_executable_schema,
    load_schema_from_path,
    snake_case_fallback_resolvers
)

from .types import types
from .scalars import datetime_scalar

type_defs = load_schema_from_path('./server/graphql/schema.graphql')

schema = make_executable_schema(
    type_defs,
    *types,
    datetime_scalar,
    snake_case_fallback_resolvers)
