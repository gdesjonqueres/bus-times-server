""" Creates the db structure
"""

from ..connectdb import engine
from ..models import Base


def run():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    run()
