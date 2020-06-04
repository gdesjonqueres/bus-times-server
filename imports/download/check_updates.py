#!/usr/bin/env python3

import sys
from subprocess import run as runp, CalledProcessError

from requests.exceptions import ConnectionError

from colorama import (
    init,
    deinit,
    # reinit,
    Fore,
    Back,
    Style
)

from tools.utils import prompt_yes_no_loop

from data.connectdb import db_session
from data.models import Schedule

from .. import gtfs_helpers as gtfs
from ..config import PATHS, VERBOSE
from . import helpers as dl


colors = {
    'info': Fore.BLUE,
    'highlight': Fore.CYAN + Style.BRIGHT,
    'danger': Back.RED + Fore.WHITE,
    'success': Back.GREEN + Fore.WHITE,
    'prompt': Fore.YELLOW
}


def b(text, color):
    return f'{Style.RESET_ALL}{colors[color]}{text}'


def printb(text, color):
    print(b(text, color))


def n(text):
    return text + '\n'


def nb(text):
    return '\n' + text


def print_info(text):
    printb(text, 'info')


def print_title(text):
    printb(text, 'highlight')


def print_success(text):
    printb(text, 'success')


def format_error(text):
    return b(text, 'danger')


def exit_with_error(error):
    sys.exit(format_error(error) + f'{Style.RESET_ALL}')


def prompt(text, default):
    return prompt_yes_no_loop(b(text, 'prompt'), default, '')


class UpdateError(BaseException):
    pass


def run():
    try:
        # setup colorama
        init(autoreset=True)

        dl.cleanup_tmp_files()

        current_version = Schedule.get(db_session).version
        print_title(f'* Current Feed Version: {current_version}')

        print_info('... Checking Latest Translink Feed ...')
        latest_data = _get_current_feeds()

        local_archive = dl.get_local_archive(latest_data)
        if local_archive:
            print_info(f'... Latest feed of "{latest_data["published_name"]}" '
                       f'already archived (as {latest_data["archive_name"]})')
            do_download = _ask_if_download()
        else:
            print_title(nb('* New feed found.'))
            do_download = True

        if do_download:
            print_info(f'... Downloading {latest_data["download_url"]} ...')
            _download_feed(latest_data)
        else:
            print_title(nb('* Using local archive.'))
            _use_archive(local_archive)

        print_info('... Unzipping ...')
        _unzip_archive(latest_data)

        print_title('* Checking archive ...')
        _check_archive()

        print_title('* Feed Details')
        latest_feed_info = _get_archive_feed_info()
        _print_archive_info(latest_feed_info)

        if prompt('Do you want to use this feed as current?', 'yes'):
            _set_feed_current(latest_data)

        if prompt('Proceed and run imports?', 'yes'):
            _do_imports()
    except BaseException as err:
        exit_with_error(err)
    else:
        print_success(nb('All good.'))
    finally:
        _cleanup()


def _cleanup():
    if prompt(nb('Clean up temporary import files?'), 'yes'):
        dl.cleanup_tmp_files()
        print_success('... Done.')
    deinit()


def _get_current_feeds():
    try:
        latest_data = dl.get_latest_archive_info()
    except ConnectionError as err:
        raise UpdateError(f'... Unable to connect to server ({err})')
    return latest_data


def _ask_if_download():
    if not prompt(nb('Re-download archive?'), 'no'):
        if not prompt(nb('Proceed and use local archive?'), 'no'):
            sys.exit()
        return False
    return True


def _use_archive(archived_file):
    try:
        runp(['cp', archived_file, PATHS['tmp-dir']], check=True)
    except CalledProcessError as err:
        raise UpdateError(
            f'... Unable to use local archive ({err})')


def _download_feed(latest_data):
    try:
        dl.download_archive(latest_data, PATHS['tmp-dir'])
    except ConnectionError as err:
        raise UpdateError(f'... Unable to download from Translink ({err})')
    print_success(n('... Done.'))


def _unzip_archive(latest_data):
    try:
        runp(['unzip', latest_data['archive_name']],
             cwd=PATHS['tmp-dir'], check=True)
    except Exception as err:
        raise UpdateError(f'... Unable to unzip archive ({err})')
    print_success(n('... Done.'))


def _check_archive():
    (is_valid, error) = dl.check_archive(PATHS['tmp-dir'])
    if not is_valid:
        raise UpdateError(f'... Archive is not valid ({error})')
    print_success(n('... Done.'))


def _get_archive_feed_info():
    feed_infos = gtfs.get_feed_info(PATHS['tmp-dir'] + 'feed_info.txt')
    return gtfs.parse_feed_info(feed_infos)


def _print_archive_info(latest_feed_info):
    print_info(f'... Version: {latest_feed_info["version"]}')
    print_info(f'... Published: {latest_feed_info["published"]}')
    print_info(n(f'... Schedule: {latest_feed_info["validity"]["begin"]} -'
                 f' {latest_feed_info["validity"]["end"]}'))


def _set_feed_current(latest_data):
    """Move latest feed to current folder and archive it

    """
    path_to_archive = f'{PATHS["tmp-dir"]}{latest_data["archive_name"]}'
    try:
        dl.set_archive_current(path_to_archive)
        dl.store_archive(path_to_archive)
    except Exception as err:
        raise UpdateError(f'... Problem using archive ({err})')
    print_success(n('... Done.'))


def _do_imports():
    """Import new gtfs data into app database

    """
    modifier = '' if VERBOSE else ' --no-verbose'
    try:
        runp(f'./import_gtfs{modifier}', shell=True, cwd='./', check=True)
    except CalledProcessError as err:
        raise UpdateError(f'... Problem importing archive ({err})')
    print_success(n('... Done.'))


if __name__ == '__main__':
    run()
