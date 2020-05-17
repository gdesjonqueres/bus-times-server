from api.live_api import LiveApi
from data.connectdb import db_session
from data.models import Trip

trip = db_session.query(Trip).filter_by(code='dst01').one()

api = LiveApi()
