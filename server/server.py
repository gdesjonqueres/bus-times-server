"""Setup Ariadne ASGI server
"""

from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .graphql.schema import schema

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'],
               allow_methods=['*'], allow_headers=['*'])
]

app = Starlette(debug=True, middleware=middleware)
app.mount("/", GraphQL(schema, debug=True))
