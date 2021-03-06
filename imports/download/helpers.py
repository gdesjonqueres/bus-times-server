from subprocess import run as runp  # , CalledProcessError
import requests
from bs4 import BeautifulSoup
from pathlib import Path

from tools.utils import (
    run_validators,
    download_file,
    extract_filename_from_path
)

from .. import gtfs_helpers as gtfs

from ..config import (
    PATHS,
    TRANSLINK_GTFS_DL_PAGE,
    IMPORTS_ROOT_DIR
)


archive_validators = {
    'feed_info.txt': gtfs.check_feed_info_file,
    'trips.txt': gtfs.check_trips_file,
    'stop_times.txt': gtfs.check_stop_times_file,
    'calendar.txt': gtfs.check_calendar_file,
    'direction_names_exceptions.txt': gtfs.check_directions_file,
    'routes.txt': gtfs.check_routes_file,
    'stops.txt': gtfs.check_stops_file,
}


def cleanup_tmp_files():
    runp('rm -rf ./tmp/*', shell=True, cwd=IMPORTS_ROOT_DIR)


def get_latest_archive_info():
    http = requests.get(TRANSLINK_GTFS_DL_PAGE)
    html = BeautifulSoup(http.text, 'html.parser')
    dl_opt = html.select('#ddGTFS option')[0]
    dl_url = dl_opt['value']
    published_date = dl_url.split('/')[-2]

    return {
        'download_url': dl_url,
        'published_date': published_date,
        'published_name': dl_opt.text,
        'archive_name': published_date + '.zip'
    }


def get_local_archive(gtfsdata_info):
    path_to_file = f'{PATHS["archives-dir"]}/{gtfsdata_info["archive_name"]}'
    archived = Path(path_to_file)
    if archived.is_file():
        return path_to_file
    return None


def curry_file_validator(validator, file_name):
    def curried():
        try:
            (is_valid, error) = validator(file_name)
            if not is_valid:
                return (False, f'file {file_name} is invalid, {error}')
        except FileNotFoundError as err:
            return (False, str(err))
        return (True, None)
    return curried


def make_archive_validators(path_to_dir):
    return [
        curry_file_validator(validator, f'{path_to_dir}{file_name}')
        for (file_name, validator) in archive_validators.items()]


def check_archive(path_to_dir):
    return run_validators(make_archive_validators(path_to_dir))


def download_archive(gtfsdata_info, directory):
    path_to_file = f"{directory}/{gtfsdata_info['archive_name']}"
    download_file(gtfsdata_info['download_url'], path_to_file)
    return path_to_file


def store_archive(path_to_archive):
    try:
        runp(['cp', path_to_archive, PATHS["archives-dir"]], check=True)
    except Exception as err:
        raise Exception(f'Unable to copy to archive dir: {err}')


def set_archive_current(path_to_archive):
    filename = extract_filename_from_path(path_to_archive)
    try:
        runp(f'rm -rf {PATHS["current-dir"]}/*', shell=True, check=True)
        runp(['cp', path_to_archive, PATHS["current-dir"]], check=True)
        runp(['unzip', '-q', filename], cwd=PATHS["current-dir"], check=True)
        runp(f'rm {filename}', shell=True,
             cwd=PATHS["current-dir"], check=True)
        runp(f"echo '{filename}' > current",
             cwd=PATHS["current-dir"], check=True, shell=True)
    except Exception as err:
        raise Exception(f'Unable to copy archive to current dir: {err}')
