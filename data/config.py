import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--no-verbose', action='store_true')
args, _ = parser.parse_known_args()

# exported config
DB_PATH = 'data/app.db'
DB_URL = f'sqlite:///{DB_PATH}'
SCHEDULE_TIMEZONE = 'America/Vancouver'
USER_TIMEZONE = 'America/Vancouver'
VERBOSE = not args.no_verbose
