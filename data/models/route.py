from sqlalchemy import Column, Integer, String

from .base import Base


class Route(Base):
    __tablename__ = 'route'

    id = Column(Integer, primary_key=True)

    name = Column(String(80), nullable=False)
    description = Column(String(150))
    ext_id = Column(String(9), unique=True, index=True)

    def __repr__(self):
        return '<Route %r>' % self.name

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.name,
            "name": self.description
        }
