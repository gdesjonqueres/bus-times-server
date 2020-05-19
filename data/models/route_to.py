import uuid
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from tools.sqlalchemy_guid import GUID

from .base import Base


class RouteTo(Base):
    __tablename__ = 'route_to'

    # id = Column(Integer, primary_key=True)
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    route_id = Column(Integer, ForeignKey('route.id'), nullable=False)
    route = relationship("Route")

    direction = Column(String(3), nullable=False)

    route_from = Column(String(80), nullable=True)
    route_to = Column(String(80), nullable=False)

    def __repr__(self):
        return f'<RouteTo {self.route.name} from={self.route_from} '
        f'to={self.route_to}>'

    def to_dict(self):
        return {
            "id": self.id,
            "route": self.route.to_dict(),
            "direction_id": self.direction,
            "__comment": f"{self.route.name} to {self.route_to}"
        }
