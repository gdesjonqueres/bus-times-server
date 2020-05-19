from ariadne import ObjectType

route = ObjectType("Route")


@route.field("code")
def resolve_route_code(obj, _):
    return obj.route.name


@route.field("name")
def resolve_route_name(obj, _):
    return obj.route.description


route.set_alias('from', 'route_from')
route.set_alias('to', 'route_to')
