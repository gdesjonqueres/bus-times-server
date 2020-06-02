#!/usr/bin/env python3

import subprocess

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


def run():
    #
    # -----------------------------------------------------------
    # Set up coloring and formating
    # -----------------------------------------------------------
    #
    init(autoreset=True)
    colors = {
        'info': Fore.BLUE,
        'highlight': Fore.CYAN + Style.BRIGHT,
        'danger': Back.RED + Fore.WHITE,
        'success': Back.GREEN + Fore.WHITE,
        'prompt': Fore.YELLOW
    }

    def b(text, color):
        return f'{colors[color]}{text}'

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

    def prompt(text, default):
        return prompt_yes_no_loop(b(text, 'prompt'), default, '')

    def format_error_message(text):
        return b(text, 'danger')

    class ExitError(SystemExit):
        def __init__(self, error_message):
            super().__init__(format_error_message(
                error_message + '. Exiting...'))

    #
    # -----------------------------------------------------------
    # Clean up
    # -----------------------------------------------------------
    #
    dl.cleanup_tmp_files()

    #
    # -----------------------------------------------------------
    # Get info about current feed and latest translink feed
    # -----------------------------------------------------------
    #
    current_version = Schedule.get(db_session).version
    print_title(f'* Current Feed Version: {current_version}')
    print_info('... Checking Latest Translink Feed ...')

    try:
        latest_data = dl.get_latest_archive_info()
    except ConnectionError as err:
        raise ExitError(f'... Unable to contact Translink server ({err})')

    #
    # -----------------------------------------------------------
    # Check if latest feed has already been archived
    # -----------------------------------------------------------
    #
    do_download = True
    archived_file = dl.get_local_archive(latest_data)
    if archived_file:
        print_info(f'... Latest feed of "{latest_data["published_name"]}"'
                   f' is already archived (as {latest_data["archive_name"]})')

        choice = prompt(nb('Re-download archive?'), 'no')
        if choice == 'no':
            choice = prompt(nb('Proceed and import current archive?'), 'no')
            if choice == 'no':
                exit(0)

            # Using current archive as import
            try:
                subprocess.run(
                    ['cp', archived_file, PATHS['tmp-dir']], check=True)
            except subprocess.CalledProcessError as err:
                raise ExitError(
                    f'... Unable to copy current local archive ({err.output})')
            do_download = False
            print_title(nb('* Using archived feed.'))
    else:
        print_title(nb('* New feed found.'))

    #
    # -----------------------------------------------------------
    # Download latest feed
    # -----------------------------------------------------------
    #
    if do_download:
        print_info(f'... Downloading from {latest_data["download_url"]} ...')
        try:
            dl.download_archive(latest_data, PATHS['tmp-dir'])
        except ConnectionError as err:
            raise ExitError(
                f'... Unable to download from Translink server ({err})')
        print_success(n('... Done.'))

    #
    # -----------------------------------------------------------
    # Unzip and check dowloaded feed
    # -----------------------------------------------------------
    #
    print_info('... Unzipping ...')
    try:
        subprocess.run(['unzip', latest_data['archive_name']],
                       cwd=PATHS['tmp-dir'], check=True)
    except subprocess.CalledProcessError as err:
        raise ExitError(
            f'... Unable to unzip downloaded archive ({err.output})')
    print_success(n('... Done.'))

    print_title('* Checking downloaded archive ...')
    (is_valid, error) = dl.check_archive(PATHS['tmp-dir'])
    if not is_valid:
        raise ExitError(f'... Archive is not valid ({error})')
    print_success(n('... Done.'))

    latest_feed_info = gtfs.parse_feed_info(
        gtfs.get_feed_info(PATHS['tmp-dir'] + 'feed_info.txt'))

    print_title('* Latest Feed')
    print_info(f'... Version: {latest_feed_info["version"]}')
    print_info(f'... Published: {latest_feed_info["published"]}')
    print_info(n(f'... Schedule: {latest_feed_info["validity"]["begin"]} - '
                 f'{latest_feed_info["validity"]["end"]}'))

    #
    # -----------------------------------------------------------
    # Move latest feed to current folder and archive it
    # -----------------------------------------------------------
    #
    path_to_archive = f'{PATHS["tmp-dir"]}{latest_data["archive_name"]}'
    choice = prompt('Do you want to use these data for import?', 'yes')
    if choice == 'yes':
        try:
            dl.set_archive_current(path_to_archive)
            dl.store_archive(path_to_archive)
        except Exception as err:
            raise ExitError(f'... Problem using archive ({err})')
        print_success(n('... Done.'))

    #
    # -----------------------------------------------------------
    # Import new gtfs data into app database
    # -----------------------------------------------------------
    #
    # choice = prompt(f'Import current data into app?{Style.RESET_ALL}', 'yes')
    choice = prompt('Import current data into app?', 'yes')
    if choice == 'yes':
        modifier = '' if VERBOSE else ' --no-verbose'
        try:
            subprocess.run(f'./import_gtfs{modifier}',
                           shell=True, cwd='./', check=True)
        except subprocess.CalledProcessError as err:
            raise ExitError(f'... Problem importing archive ({err.output})')
        # reinit()
        print_success(n('... Done.'))

    #
    # -----------------------------------------------------------
    # Clean up
    # -----------------------------------------------------------
    #
    choice = prompt('Clean up temporary import files?', 'yes')
    if choice == 'yes':
        dl.cleanup_tmp_files()
        print_success(n('... Done.'))

    print_success(n('All good, exiting.'))

    deinit()


if __name__ == '__main__':
    run()
