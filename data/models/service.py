from .base import *


class Service(Base):
    __tablename__ = 'service'

    # id = Column(Integer, primary_key=True)
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    days = Column(String(20), nullable=False)
    mon = Column(Boolean, default=False)
    tue = Column(Boolean, default=False)
    wed = Column(Boolean, default=False)
    thu = Column(Boolean, default=False)
    fri = Column(Boolean, default=False)
    sat = Column(Boolean, default=False)
    sun = Column(Boolean, default=False)
    date = Column(Date)
    ext_id = Column(String(9), unique=True, index=True)

    @classmethod
    def get_service_for_date(cls, date):
        day = date.strftime('%a').lower()
        return db_session.query(cls).filter(getattr(cls, day)).one()

    def __repr__(self):
        return '<Service %r>' % self.days

    def to_dict(self):
        return {
            "id": self.id,
            "days": self.days,
        }
