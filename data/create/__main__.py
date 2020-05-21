""" Main script to create app db and fill all data
"""
from pathlib import Path

from .. import config

from .db import run as create_db
from .data import run as create_data
from .schedule import run as create_schedule


def run():
    def backup_db():
        if config.VERBOSE:
            print('Backing up DB...')
        db = Path(config.DB_PATH)
        try:
            db.rename(f'{config.DB_PATH}.bck')
        except FileNotFoundError:
            pass

    def restore_backup():
        db_bck = Path(f'{config.DB_PATH}.bck')
        if db_bck.is_file():
            if config.VERBOSE:
                print('Cleaning up corrupted DB and Restoring backup...')
            db = Path(config.DB_PATH)
            db.unlink()
            db_bck.rename(config.DB_PATH)

    def erase_backup():
        if config.VERBOSE:
            print('Cleaning up DB backup...')
        try:
            Path(f'{config.DB_PATH}.bck').unlink()
        except FileNotFoundError:
            pass

    backup_db()

    try:
        create_db()
        create_data()
        create_schedule()
    except BaseException:
        restore_backup()
        raise
    else:
        erase_backup()


if __name__ == '__main__':
    run()
