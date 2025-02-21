"""
Management of configuration, preferences and log files.

Constants:
    ASSETS_PATH_DATA: path of the data folder (containing configuration, huts data, preferences etc.)
    ASSETS_PATH_TILES: path of the tiles folder (containing the map tiles)
    ASSETS_PATH_ICONS: path of the icons folder (containing the icons for the map display)
    ASSETS_PATH_FONTS: path of the fonts folder (containing the font definitions)

Variables:
    errors: list containing the errors detected in this module

Functions:
    __getattr__: retrieve a configuration or preferences parameter using dot notation
    load: load the configuration and preferences files
    get: retrieve a configuration or preferences parameter
    save_preferences: save the preferences in the preferences files
    save_results: save the retrieved results in the results files
    save_log: save a log file
"""
import sys
import os
import pathlib
import yaml
import json
import datetime

_ASSETS_PATH = pathlib.Path(os.getcwd()) / 'assets'

ASSETS_PATH_DATA = _ASSETS_PATH / 'data'
ASSETS_PATH_TILES = _ASSETS_PATH / 'tiles'
ASSETS_PATH_ICONS = _ASSETS_PATH / 'icons'
ASSETS_PATH_FONTS = _ASSETS_PATH / 'fonts'

_CONFIG_FILE = ASSETS_PATH_DATA / 'config.yaml'
_PREFERENCES_FILE = ASSETS_PATH_DATA / 'preferences.yaml'
_RESULTS_FILE = ASSETS_PATH_DATA / 'results.json'

_LOG_PATH = pathlib.Path(os.getcwd()) / 'log'
_LOG_FILE = str(_LOG_PATH / 'chamannas_{0}_{1}.log')

_LOG_DATE_FORMAT = '%Y%m%d%H%M%S'
_JSON_DATE_FORMAT = '%Y-%m-%d'
_JSON_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

RESULTS_DICTIONARY_STRING = 'RESULTS_DICTIONARY'
LANGUAGE_STRING = 'LANGUAGE'
REFERENCE_LOCATION_STRING = 'REFERENCE_LOCATION'
SELECTED_STRING = 'SELECTED'
GUI_STRING = 'GUI'
VIEW_STRING = 'VIEW'

_config = {}
_args = None
errors = []


def __getattr__(key):
    """Retrieve a configuration or preferences parameter using dot notation.

    :param key: key of the parameter to be retrieved
    :return: the parameter or None if the key is missing
    """
    return get(key)


def load(args=None):
    """Load the configuration, preferences and cached results files.
    
    param args: command line arguments to be added to the configuration data
    """
    # Retrieve the command line arguments saved during the first execution of the function
    # (necessary in case of configuration reload after an update)
    global _args
    if _args is not None:
        args = _args

    _config.clear()

    # Load the configuration file
    try:
        with open(_CONFIG_FILE, encoding='UTF-8-SIG') as yaml_config_data_file:
            _config.update(yaml.safe_load(yaml_config_data_file))
    except FileNotFoundError:
        print(f"Fatal error: configuration file '{_CONFIG_FILE}' does not exist")
        sys.exit(1)
    except (IOError, yaml.YAMLError) as e:
        print(f"Fatal error '{type(e).__name__}' reading configuration file '{_CONFIG_FILE}'")
        print(e)
        sys.exit(1)

    # Load the preferences file
    try:
        with open(_PREFERENCES_FILE, encoding='UTF-8-SIG') as yaml_config_preferences_file:
            _config.update(yaml.safe_load(yaml_config_preferences_file))
    except FileNotFoundError:
        errors.append({'type': 'Configuration Error',
                       'message': f"Preferences file '{_PREFERENCES_FILE}' does not exist"})
    except (IOError, yaml.YAMLError, TypeError) as e:
        errors.append({'type': type(e), 'message': str(e)})

    # Load the cached results file
    try:
        with open(_RESULTS_FILE, encoding='UTF-8-SIG') as json_config_results_file:
            results_dict_from_json = json.load(json_config_results_file)
            results_dict = _convert_results_dict_from_json(results_dict_from_json)
            _config.update(results_dict)
    except FileNotFoundError:
        errors.append({'type': 'Configuration Error',
                       'message': f"Results file '{_RESULTS_FILE}' does not exist"})
    except (IOError, json.JSONDecodeError, TypeError) as e:
        errors.append({'type': type(e), 'message': str(e)})

    # Add the command line parameters to the configuration data if any is available
    # Save the command line parameters in the global _args variable to have them available in case of update
    if args is not None:
        _args = args
        for arg, value in (vars(args)).items():
            if value is not None:
                _config[arg.upper()] = value[0]


def get(key, mandatory=False):
    """Retrieve a configuration or preferences parameter.

    :param key: key of the parameter to be retrieved
    :param mandatory: flag to mark a parameter as mandatory (if the key is missing, program will exit)
    :return: the parameter or None if the key is missing
    """
    try:
        return _config[key]
    except KeyError as e:
        if not mandatory:
            return None
        else:
            print(f"Fatal error '{type(e).__name__}' reading configuration file: '{key}' key is missing")
            sys.exit(1)


def save_preferences(preferences_dict):
    """Save the preferences in the preferences file.

    :param preferences_dict: dictionary containing the preferences
    """
    try:
        with open(_PREFERENCES_FILE, 'w', encoding='UTF-8') as yaml_config_save_file:
            yaml_config_save_file.write(yaml.dump(preferences_dict))
    except (IOError, json.JSONDecodeError) as e:
        errors.append({'type': type(e), 'message': str(e)})


def save_results(results_dict):
    """Save the retrieved results in the results file.

    :param results_dict: dictionary containing the results
    """
    try:
        results_dict_for_json = _convert_results_dict_to_json(results_dict)
        with open(_RESULTS_FILE, 'w', encoding='UTF-8') as json_config_save_file:
            json_config_save_file.write(json.dumps(results_dict_for_json, default=str))
    except (IOError, yaml.YAMLError) as e:
        errors.append({'type': type(e), 'message': str(e)})


def save_log(info_type, developer_info):
    """Save a log file.

    :param info_type: type of information to be saved ('warning' or 'error')
    :param developer_info: list containing the information to be saved in the log
    """
    _LOG_PATH.mkdir(exist_ok=True)
    filename = _LOG_FILE.format(info_type[0], datetime.datetime.now().strftime(_LOG_DATE_FORMAT))
    try:
        with open(filename, mode='w', encoding='UTF-8') as logfile:
            for item in developer_info:
                log_name = item['name']
                log_type = item['type']
                log_message = item['message']
                logfile.write(f'{log_name}\t{log_type}\t{log_message}\n')
    except IOError as e:
        errors.append({'type': type(e), 'message': str(e)})


def _convert_results_dict_to_json(results_dict):
    results_dict = results_dict[RESULTS_DICTIONARY_STRING]
    to_json = {}
    for index in results_dict:
        to_json[index] = {}
        to_json[index]['error'] = results_dict[index]['error']
        to_json[index]['warning'] = results_dict[index]['warning']
        to_json[index]['request_time'] = results_dict[index]['request_time'].strftime(_JSON_DATETIME_FORMAT)
        to_json[index]['hut_status'] = {}
        for date in results_dict[index]['hut_status']:
            date_string = date.strftime(_JSON_DATE_FORMAT)
            to_json[index]['hut_status'][date_string] = results_dict[index]['hut_status'][date]
        to_json[index]['places'] = {}
        for date in results_dict[index]['places']:
            date_string = date.strftime(_JSON_DATE_FORMAT)
            to_json[index]['places'][date_string] = results_dict[index]['places'][date]
    return {RESULTS_DICTIONARY_STRING: to_json}


def _convert_results_dict_from_json(from_json):
    """

    :param from_json:
    :return:
    """
    results_dict = {}
    from_json = from_json[RESULTS_DICTIONARY_STRING]
    for index in from_json:
        int_index = int(index)
        results_dict[int_index] = {}
        results_dict[int_index]['error'] = from_json[index]['error']
        results_dict[int_index]['warning'] = from_json[index]['warning']
        results_dict[int_index]['request_time'] = datetime.datetime.strptime(
            from_json[index]['request_time'], _JSON_DATETIME_FORMAT)
        results_dict[int_index]['hut_status'] = {}
        for date_string in from_json[index]['hut_status']:
            date = datetime.datetime.strptime(date_string, _JSON_DATE_FORMAT).date()
            results_dict[int_index]['hut_status'][date] = from_json[index]['hut_status'][date_string]
        results_dict[int_index]['places'] = {}
        for date_string in from_json[index]['places']:
            date = datetime.datetime.strptime(date_string, _JSON_DATE_FORMAT).date()
            results_dict[int_index]['places'][date] = from_json[index]['places'][date_string]
    return {RESULTS_DICTIONARY_STRING: results_dict}
