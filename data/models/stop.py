from .base import *
from .bus_trip import BusTrip


class Stop(Base):
    __tablename__ = 'stop'

    # id = Column(Integer, primary_key=True)
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    code = Column(String(10), nullable=False)
    name = Column(String(80))
    description = Column(String(150))
    ext_id = Column(String(9), unique=True, index=True)

    def __repr__(self):
        return '<Stop %r desc=%r>' % (self.code, self.description)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "itinaries": [bt.id for bt in self.bus_trips],
            "__comment": self.description,
        }


Stop.bus_trips = relationship(
    'BusTrip', order_by=BusTrip.id, back_populates='stop_from')
