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

from tools.utils import prompt_yes_no_loop as prompt

from data.connectdb import db_session
from data.models import Schedule

from .. import gtfs_helpers as gtfs
from ..config import PATHS, VERBOSE
from . import helpers as dl


def run():
    #
    # -----------------------------------------------------------
    # Set up coloring
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
    printb(f'* Current Feed Version: {current_version}', 'highlight')
    printb('... Checking Latest Translink Feed ...', 'info')

    try:
        latest_data = dl.get_latest_archive_info()
    except ConnectionError as err:
        raise SystemExit(
            b(f'... Unable to contact Translink server ({err}), exiting.', 'danger'))

    #
    # -----------------------------------------------------------
    # Check if latest feed has already been archived
    # -----------------------------------------------------------
    #
    do_download = True
    archived_file = dl.get_local_archive(latest_data)
    if archived_file:
        printb(f'... Latest Translink feed of {latest_data["published_name"]} '
               f'is already archived (as {latest_data["archive_name"]})', 'info')

        print('\n')

        choice = prompt(b('Do you still want to download it?', 'prompt'), 'no')
        if choice == 'no':
            print('\n')

            choice = prompt(
                b('Do you want to proceed with importing current archive?', 'prompt'), 'no')
            if choice == 'no':
                exit(0)

            # Using current archive as import
            try:
                subprocess.run(
                    ['cp', archived_file, PATHS['tmp-dir']], check=True)
            except subprocess.CalledProcessError as err:
                raise SystemExit(
                    b(f'... Unable to copy current local archive ({err.output}), exiting.', 'danger'))
            do_download = False

            print('\n')

            printb('* Using archived feed.', 'highlight')
    else:
        print('\n')

        printb('* New feed found.', 'highlight')

    #
    # -----------------------------------------------------------
    # Download latest feed
    # -----------------------------------------------------------
    #
    if do_download:
        printb(
            f'... Downloading from {latest_data["download_url"]} ...', 'info')
        try:
            dl.download_archive(latest_data, PATHS['tmp-dir'])
        except ConnectionError as err:
            raise SystemExit(
                b(f'... Unable to download from Translink server ({err}), exiting.', 'danger'))
        printb('... Done.', 'success')

        print('\n')

    #
    # -----------------------------------------------------------
    # Unzip and check dowloaded feed
    # -----------------------------------------------------------
    #
    printb('... Unzipping ...', 'info')
    try:
        subprocess.run(['unzip', latest_data['archive_name']],
                       cwd=PATHS['tmp-dir'], check=True)
    except subprocess.CalledProcessError as err:
        raise SystemExit(
            b(f'... Unable to unzip downloaded archive ({err.output}), exiting.', 'danger'))
    printb('... Done.', 'success')

    print('\n')

    printb('* Checking downloaded archive ...', 'highlight')
    (is_valid, error) = dl.check_archive(PATHS['tmp-dir'])
    if not is_valid:
        raise SystemExit(
            b(f'... Archive is not valid ({error}), exiting.', 'danger'))
    printb('... Done.', 'success')

    latest_feed_info = gtfs.parse_feed_info(
        gtfs.get_feed_info(PATHS['tmp-dir'] + 'feed_info.txt'))

    print('\n')

    printb('* Latest Feed', 'highlight')
    printb(f'... Version: {latest_feed_info["version"]}', 'info')
    printb(f'... Published: {latest_feed_info["published"]}', 'info')
    printb(f'... Schedule: {latest_feed_info["validity"]["begin"]} - '
           f'{latest_feed_info["validity"]["end"]}', 'info')

    print('\n')

    #
    # -----------------------------------------------------------
    # Move latest feed to current folder and archive it
    # -----------------------------------------------------------
    #
    path_to_archive = f'{PATHS["tmp-dir"]}{latest_data["archive_name"]}'
    choice = prompt(
        b('Do you want to use these data for import?', 'prompt'), 'yes')
    if choice == 'yes':
        try:
            dl.set_archive_current(path_to_archive)
            dl.store_archive(path_to_archive)
        except Exception as err:
            raise SystemExit(
                b(f'... Problem using archive ({err}), exiting.', 'danger'))
        printb('... Done.', 'success')

    print('\n')

    #
    # -----------------------------------------------------------
    # Import new gtfs data into app database
    # -----------------------------------------------------------
    #
    choice = prompt(
        b(f'Do you want to import current data into app?{Style.RESET_ALL}', 'prompt'), 'yes')
    if choice == 'yes':
        modifier = '' if VERBOSE else ' --no-verbose'
        try:
            subprocess.run(f'./import_gtfs{modifier}',
                           shell=True, cwd='./', check=True)
        except subprocess.CalledProcessError as err:
            raise SystemExit(
                b(f'... Problem importing archive ({err.output}), exiting.', 'danger'))
        # reinit()
        printb('... Done.', 'success')

    print('\n')

    #
    # -----------------------------------------------------------
    # Clean up
    # -----------------------------------------------------------
    #
    choice = prompt(b('Clean up temporary import files?', 'prompt'), 'yes')
    if choice == 'yes':
        dl.cleanup_tmp_files()
        printb('... Done.', 'success')

    print('\n')

    printb('All good, exiting.', 'success')

    print('\n')

    deinit()


if __name__ == '__main__':
    run()
