from sqlalchemy import create_engine

from .. import config

i_engine = create_engine(
    'sqlite:///imports/database/import.db', echo=config.VERBOSE)
