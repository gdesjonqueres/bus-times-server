"""Diverse helper functions
"""

from typing import List, Union


def extract_filename_from_path(path_to_file: str) -> str:
    (_, _, filename) = path_to_file.rpartition('/')
    return filename


def concat_to_filename(path_to_file: str, str: str) -> str:
    """Concat str to the file name portion of path_to_file
    leaving extension and path untouched

    """
    (path, path_separator, filename) = path_to_file.rpartition('/')
    if filename.rfind('.') >= 0:
        (filename_minus_extension, filename_extension_separator,
         extension) = filename.rpartition('.')
        new_path_to_file = path + path_separator + filename_minus_extension + \
            str + filename_extension_separator + extension
    else:
        new_path_to_file = path + path_separator + filename + str
    return new_path_to_file


def list_to_dict(values: list, keys: list) -> dict:
    """Return a dictionary from keys and values lists

    """
    return dict(zip(keys, values))


def has_all_elements(my_list: list, elements: list) -> bool:
    """Return True if all items from elements are contained in my list

    """
    return all(element in my_list for element in elements)


def exchange_indexes_values(my_list: list) -> dict:
    return dict((v, k) for k, v in enumerate(my_list))


def sort_by_keys(my_dict: dict) -> dict:
    return dict((k, my_dict[k]) for k in sorted(my_dict.keys()))


def save_to_csv(file_name: str, descriptor: list, data: list):
    """Save csv data to disk

    descriptor is a list of column names
    data is a list of rows

    """
    import csv
    with open(file_name, 'w') as fh:
        writer = csv.writer(fh)
        writer.writerow(descriptor)
        writer.writerows(data)


def save_to_json(file_name: str, data: dict, readable=False,
                 sorted=False, encoder=None):
    """Save data to json on disk

    """
    import json
    params = {}
    if readable:
        params['indent'] = 4
    if sorted:
        params['sort_keys'] = True
    if encoder:
        params['cls'] = encoder
    with open(file_name, 'w') as fp:
        json.dump(data, fp, **params)


def check_files(validators: List[callable]) -> (bool, ):
    for validator in validators:
        if not validator[0](validator[1]):
            return (False, validator[1])
    return (True, 'Ok')


def prompt_loop(message: str, choices: list, prompt='$ ') -> Union[bool, str]:
    """Perform a loop displaying a prompt and waiting for a user input
    Return the user input when it matches the choices otherwise keep looping

    """
    while True:
        choice = input(f'{prompt}{message}: ')
        if choice in choices:
            return choice
    return False


def prompt_yes_no_loop(message, default=False, prompt='$ ') -> str:
    """Perform a loop displaying a prompt and waiting for a Yes/No user input
    Return either the string 'yes' or 'no'

    """
    choices = ['Y', 'y', 'n', 'N']
    choice_str = '[y/n]'
    if default in ['yes', 'no']:
        choices.append('')
        if default == 'yes':
            choice_str = '[Y/n]'
        elif default == 'no':
            choice_str = '[N/y]'
    choice = prompt_loop(f'{message} {choice_str}', choices, prompt)
    if choice == '':
        return default
    if choice in ['Y', 'y']:
        return 'yes'
    return 'no'


def download_file(url: str, filename: str):
    """Download the file at url and save it to disk

    """
    import requests
    resp = requests.get(url)
    with open(filename, 'wb') as fh:
        fh.write(resp.content)


def run_validators(validators: List[callable]) -> (bool, str):
    """Run a list of validators
    Return a tuple (True if valid or False, 'Ok' or error message)

    """
    for validator in validators:
        (is_valid, error_msg) = validator()
        if not is_valid:
            return (False, error_msg)
    return (True, 'OK')
