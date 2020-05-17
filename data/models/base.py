import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    SmallInteger,
    Date,
    DateTime,
    ForeignKey,
    between
)
from sqlalchemy.orm import relationship, reconstructor

from tools.sqlalchemy_guid import GUID

from ..connectdb import db_session

Base = declarative_base()
