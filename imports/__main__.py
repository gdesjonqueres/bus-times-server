""" Main import script

Will import translink archive from current directory into the import db

If archive argument is passed to script will import the specified archive
and make it the current archive
"""

import subprocess

from . import config
from .download.helpers import set_archive_current


def run():
    if config.ARCHIVE:
        set_archive_current(config.ARCHIVE)
    try:
        subprocess.run('./fill_importdb',
                       cwd=config.paths['importdb-dir'], check=True)
    except subprocess.CalledProcessError as err:
        raise Exception('Unable to execute import db fill script')


if __name__ == '__main__':
    run()
