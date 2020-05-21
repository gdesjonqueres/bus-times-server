import argparse

parser = argparse.ArgumentParser()
parser.add_argument('archive', nargs='?', default='')
parser.add_argument('--no-verbose', action='store_true')
args, _ = parser.parse_known_args()

VERBOSE = not args.no_verbose
ARCHIVE = args.archive
DB_PATH = 'imports/database/import.db'
DB_URL = f'sqlite:///{DB_PATH}'
TRANSLINK_GTFS_DL_PAGE = 'https://developer.translink.ca/ServicesGtfs/GtfsData'
IMPORTS_ROOT_DIR = './imports/'
PATHS = {
    'download-dir': f'{IMPORTS_ROOT_DIR}download/',
    'archives-dir': f'{IMPORTS_ROOT_DIR}download/archives/',
    'current-dir': f'{IMPORTS_ROOT_DIR}download/current/',
    'importdb-dir': f'{IMPORTS_ROOT_DIR}database/',
    'tmp-dir': f'{IMPORTS_ROOT_DIR}tmp/',
}
