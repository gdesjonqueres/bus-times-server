import argparse

parser = argparse.ArgumentParser()
parser.add_argument('archive', nargs='?', default='')
parser.add_argument('--no-verbose', action='store_true')
args = parser.parse_args()

VERBOSE = not args.no_verbose
ARCHIVE = args.archive

TRANSLINK_GTFS_DL_PAGE = 'https://developer.translink.ca/ServicesGtfs/GtfsData'

IMPORTS_ROOT_DIR = './imports/'

paths = {
    'download-dir': f'{IMPORTS_ROOT_DIR}download/',
    'archives-dir': f'{IMPORTS_ROOT_DIR}download/archives/',
    'current-dir': f'{IMPORTS_ROOT_DIR}download/current/',
    'importdb-dir': f'{IMPORTS_ROOT_DIR}database/',
    'tmp-dir': f'{IMPORTS_ROOT_DIR}tmp/',
}
