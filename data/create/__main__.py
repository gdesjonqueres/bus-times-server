""" Main script to create app db and fill all data
"""

from .db import run as create_db
from .data import run as create_data
from .schedule import run as create_schedule


def run():
    create_db()
    create_data()
    create_schedule()


if __name__ == '__main__':
    run()
