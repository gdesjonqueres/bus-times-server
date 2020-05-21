from sqlalchemy import create_engine

from .. import config

i_engine = create_engine(config.DB_URL, echo=config.VERBOSE)
