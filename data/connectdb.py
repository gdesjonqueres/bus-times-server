""" Configures db connection
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import config

engine = create_engine('sqlite:///data/app.db', echo=config.VERBOSE)
Session = sessionmaker(bind=engine)
db_session = Session()
