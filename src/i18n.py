"""
Management of internationalization.

Variables:
    all_strings: dictionary with all the strings appearing in the view
    mountain_ranges_labels: dictionary with all the names of mountain ranges
    regions_labels: dictionary with all the names of regions
    errors: list containing the errors detected in this module

Functions:
    load: load all the internationalization strings
    set_language: set the new active language
    get_languages_list: get the list of available languages
    get_current_language: get the current selected language (as an integer)
    get_current_language_string: get the current selected language (as a string)
    get_current_language_code: get the locale code of the current selected language
"""
import csv

from src import config
from src.config import ASSETS_PATH_DATA

_MOUNTAIN_RANGES_DATA_FILE = str(ASSETS_PATH_DATA / 'mountain_ranges.txt')
_REGIONS_DATA_FILE = str(ASSETS_PATH_DATA / 'regions.txt')
_STRINGS_DATA_FILE = str(ASSETS_PATH_DATA / 'strings.txt')


class _LanguageDict(dict):
    """
    Class which extends dict to return a value based on the current active language.
    Each value of the dictionary should be a list with as many values as the number of supported languages.
    """
    def __getitem__(self, key):
        """
        Get an item from the dictionary based on the key and on the current active language.
        A default string is returned if the key is not present or the language is not supported.

        :param key: key of the item to be retrieved
        :return: the value of the item corresponding to the key and the active language (or the default string)
        """
        try:
            return super().__getitem__(key)[_current_language]
        except IndexError:
            return '["' + str(key) + '"]'

    def __missing__(self, key):
        """Return a list of default strings if the key is not present.

        :param key: key of the item to be retrieved
        :return: a list of default strings
        """
        return ['["' + str(key) + '"]'] * (_current_language + 1)


all_strings = _LanguageDict()
mountain_ranges_labels = _LanguageDict()
regions_labels = _LanguageDict()
errors = []

_current_language = 0
_languages = []
_language_codes = []


def load():
    """
    Load all internationalization-dependent strings (view strings, mountain ranges, regions)
    and set the current active language based on the preferences.
    """
    try:
        old_language = get_current_language_string()
    except IndexError:
        old_language = None

    _languages.clear()
    _language_codes.clear()

    config_languages = config.LANGUAGES
    if config_languages is None:
        errors.append({'type': 'Configuration Error',
                       'message': 'LANGUAGES definition missing from configuration file'})
    else:
        _languages.extend([list(lang.keys())[0] for lang in config_languages])
        _language_codes.extend([list(lang.values())[0] for lang in config_languages])

    if old_language is not None and old_language in _languages:
        set_language(_languages.index(old_language))
    else:
        language = config.LANGUAGE
        if language is not None:
            try:
                language_index = _languages.index(language)
            except ValueError as e:
                language_index = 0
                errors.append({'type': type(e), 'message': str(e)})
            set_language(language_index)

    all_strings.clear()
    mountain_ranges_labels.clear()
    regions_labels.clear()
    all_strings.update(_load_strings_file(_STRINGS_DATA_FILE))
    mountain_ranges_labels.update(_load_strings_file(_MOUNTAIN_RANGES_DATA_FILE))
    regions_labels.update(_load_strings_file(_REGIONS_DATA_FILE))


def set_language(language_index):
    """Set the active language.

    :param language_index: the index of the language to be set as active
    """
    global _current_language
    if language_index in range(len(_languages)):
        _current_language = language_index
    else:
        errors.append({'type': IndexError, 'message': f"Language index {language_index} not valid"})


def get_languages_list():
    """Get the list of available languages.

    :return: list of available languages
    """
    return _languages.copy()


def get_current_language():
    """Get the current selected language (as an integer).

    :return: current selected language (as an integer)
    """
    return _current_language


def get_current_language_string():
    """Get the current selected language (as a string).

    :return: current selected language (as a string)
    """
    return _languages[_current_language]


def get_current_language_code():
    """Get the locale code of the current selected language.

    :return: locale code of the current selected language
    """
    return _language_codes[_current_language]


def _load_strings_file(strings_data_file):
    """
    Load a dictionary of internationalization-dependent strings from a CSV (tab-separated) file.
    Each row of the file must have the following structure:
    key <tab> string_in_language_0 <tab> string_in_language_1...

    :param strings_data_file: file to be loaded
    :return: a dictionary of lists of strings
    """
    strings_dict = {}
    try:
        with open(strings_data_file, encoding='UTF-8-SIG') as tsv:
            for line in csv.reader(tsv, dialect='excel-tab'):
                try:
                    key = line[0]
                    strings_dict[key] = line[1:]
                    if len(line) < len(_languages) + 1:
                        errors.append({'type': 'IndexError',
                                       'message': f'Not enough strings for key "{key}"'})
                except ValueError as e:
                    errors.append({'type': type(e), 'message': str(e)})
    except FileNotFoundError as e:
        errors.append({'type': type(e), 'message': str(e)})
    return strings_dict
