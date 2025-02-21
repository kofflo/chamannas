"""
Management of web requests of data and pages.

Variables:
    errors: list containing the errors occurred during web requests

Functions:
    configure: configure the necessary data for the web requests
    perform_web_request_for_hut: perform the web request retrieving the data about free beds for a hut
    open_hut_page: open the web page of a hut in the browser
    search_for_updates: search for application updates
"""
import webbrowser
import requests
import json
import datetime
import time
import pathlib
import hashlib
from threading import Thread

from src import config

errors = []

_REQUEST_DELAY = 1.0  # seconds: determines the minimum delay between two web requests
_WEB_DATE_FORMAT = '%d.%m.%Y'
_DAY_DELTA = datetime.timedelta(days=1.0)
_HUT_PAGE = '/reservation/book-hut/{0}/wizard'
_TIMEOUT = 5.0
_DEFAULT_MAX_NIGHTS = 14
_DEFAULT_ROOM_BASIC_TYPES = {'default_type': 'shared'}
_HUT_STATUS_TYPES = ['SERVICED', 'UNSERVICED', 'CLOSED']
_HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 "
        "Safari/537.36",
}

_configured = False
_max_nights = 0
_last_request = None
_base_url = ""
_updates_url = ""
_room_basic_types = {}
_update_cancelled = False


def configure():
    """Configure the necessary data for the web requests (URLs, maximum number of nights, room types)."""
    global _base_url, _updates_url, _max_nights, _room_basic_types, _configured

    _base_url = config.get('BASE_URL', True)
    _updates_url = config.get('UPDATES_URL', True)
    _max_nights = config.MAX_NIGHTS
    if _max_nights is None:
        _max_nights = _DEFAULT_MAX_NIGHTS
    _room_basic_types = config.ROOM_BASIC_TYPES
    if _room_basic_types is None:
        _room_basic_types = _DEFAULT_ROOM_BASIC_TYPES
    _configured = True


def perform_web_request_for_hut(index, hut):
    """
    Perform the web request retrieving the data about free beds for a single hut.

    Data are retrieved from an HTML page and from a JSON file; each request covers an interval of 14 days.

    :param index: id number of the hut
    :param hut: dictionary of information about the hut
    :return: dictionary containing the retrieved information about free beds
    """
    global _last_request

    if not _configured:
        configure()

    # Limit the rate of web requests by delaying the execution of the function if required
    if _last_request is not None:
        time_from_last_request = time.time() - _last_request
        if time_from_last_request < _REQUEST_DELAY:
            time.sleep(_REQUEST_DELAY - time_from_last_request)

    with requests.Session() as session:
        result = {'warning': None, 'error': None,
                  'hut_status': {}, 'places': {}, 'request_time': datetime.datetime.now()}
        try:
            _last_request = time.time()

            # Retrieve the hut information
            url_hut_info = _base_url + f"api/v1/reservation/hutInfo/{index}"
            hut_info = session.get(url_hut_info, headers=_HEADERS, timeout=_TIMEOUT, verify=True)
            if hut_info.status_code != requests.codes.ok:
                errors.append({'type': f"Requests error on {hut_info.url}",
                              'message': f"Status code: {hut_info.status_code}"})
                raise Exception(f"Hut information error on hut {index}")

            # Retrieve the availability information
            url_availability = _base_url + f"api/v1/reservation/getHutAvailability?hutId={index}"
            availability = session.get(url_availability, headers=_HEADERS, timeout=_TIMEOUT, verify=True)
            if availability.status_code != requests.codes.ok:
                errors.append({'type': f"Requests error on {availability.url}",
                              'message': f"Status code: {availability.status_code}"})
                raise Exception(f"Hut availability error on hut {index}")

            hut_info_json = json.loads(hut_info.text)
            hut_availability_json = json.loads(availability.text)

            # Analyze the JSON data to find the required information
            hut_id, hut_name, category_id_list, room_label_list = _parse_hut_info_json(hut_info_json)
            if hut_id != index:
                result['warning'] = 'Unexpected index: ' + hut_id
            if hut_name != hut['name']:
                result['warning'] = 'Unexpected name: ' + hut_name

            hut_status, availabilities = _parse_hut_availability_json(hut_availability_json,
                                                                      category_id_list, room_label_list)

            for book_date in hut_status:
                result['hut_status'][book_date] = hut_status[book_date]
                result['places'][book_date] = {}
                if hut_status[book_date] == "CLOSED":
                    result['places'][book_date]['closed'] = 0
                    continue
                for room_label in availabilities[book_date]:
                    if room_label in _room_basic_types:
                        room_type = _room_basic_types[room_label]
                    else:
                        result['warning'] = 'Unexpected room type: ' + room_label
                        room_type = _room_basic_types['default_type']
                    if room_type not in result['places'][book_date]:
                        result['places'][book_date][room_type] = availabilities[book_date][room_label]
                    else:
                        result['places'][book_date][room_type] += availabilities[book_date][room_label]

        except Exception as e:
            result['error'] = f'Error occurred: {e}'

    return result


def _parse_hut_info_json(hut_info_json):
    hut_id = hut_info_json["hutId"]
    hut_name = hut_info_json["hutName"]
    hut_bed_categories = hut_info_json["hutBedCategories"]
    hut_languages = hut_info_json["hutLanguages"]
    for i_lang in range(len(hut_languages)):
        if hut_languages[i_lang].startswith("DE"):
            preferred_hut_language = hut_languages[i_lang]
            break
    else:
        if "IT" in hut_languages:
            preferred_hut_language = "IT"
        elif "FR" in hut_languages:
            preferred_hut_language = "FR"
        else:
            raise Exception("No valid hut language")
    category_id_list = []
    room_label_list = []
    for i_bed in range(len(hut_bed_categories)):
        category_id_list.append(hut_bed_categories[i_bed]["categoryID"])
        hut_bed_category_language_data = hut_bed_categories[i_bed]["hutBedCategoryLanguageData"]
        for i_lang in range(len(hut_bed_category_language_data)):
            language = hut_bed_category_language_data[i_lang]["language"]
            if language == preferred_hut_language:
                room_label_list.append(hut_bed_category_language_data[i_lang]["label"])
                break
        else:
            raise Exception("No valid hut language")
    return hut_id, hut_name, category_id_list, room_label_list


def _parse_hut_availability_json(hut_availability_json, category_id_list, room_label_list):
    hut_status = {}
    availabilities = {}
    for i_day in range(len(hut_availability_json)):
        availabilities_day = {}
        date_formatted = hut_availability_json[i_day]["dateFormatted"]
        date = datetime.datetime.strptime(date_formatted, '%d.%m.%Y').date()
        if hut_availability_json[i_day]["hutStatus"] not in _HUT_STATUS_TYPES:
            raise Exception("Invalid hut status")
        hut_status[date] = hut_availability_json[i_day]["hutStatus"]
        free_beds_per_category = hut_availability_json[i_day]["freeBedsPerCategory"]
        for room_label, category_id in zip(room_label_list, category_id_list):
            availabilities_day[room_label] = free_beds_per_category.get(str(category_id), 0)
        availabilities[date] = availabilities_day
    return hut_status, availabilities


def open_hut_page(index):
    """Open the web page of a hut in the browser.

    :param index: id no of the hut
    """
    if not _configured:
        configure()

    try:
        webbrowser.open(_base_url + _HUT_PAGE.format(index), new=2)
    except Exception as e:
        errors.append({'type': type(e), 'message': str(e)})


def search_for_updates(temp_folder, initial, observer, final_observer):
    """Search for application updates.

    :param temp_folder: temporary folder where to download the update files
    :param initial: function to be executed at the beginning of the search process
    :param observer: function to be executed during the search process (signature: (string))
    :param final_observer: function to be executed at the end of the search process (signature: (dict, boolean))
    """
    global _update_cancelled
    _update_cancelled = False
    if initial is not None:
        initial(_cancel_update, 'all updates')

    thread = Thread(target=_perform_update_request,
                    args=(temp_folder, observer, final_observer))
    thread.start()


def _cancel_update(obj):
    """Cancel the application update request by setting the dedicated flag.

    :param obj: GUI object generating the cancel request
    """
    global _update_cancelled
    _update_cancelled = True


def _perform_update_request(temp_folder, observer, final_observer):
    """
    Perform the web requests for application updates.

    This method executes in a secondary thread.

    :param temp_folder: temporary folder where to download the update files
    :param observer: function to be executed during the search process (signature: (string))
    :param final_observer: function to be executed at the end of the search process (signature: (dict, boolean))
    """
    with requests.Session() as session:
        all_updates = {}

        if observer is not None:
            observer('data_files')

        update_data_files = config.UPDATE_DATA_FILES
        if update_data_files is not None:
            all_updates['data_files'] = _perform_data_update_request(session, temp_folder, update_data_files)

        if observer is not None:
            observer('tiles')

        update_tiles = config.UPDATE_TILES
        if update_tiles is not None:
            all_updates['tiles'] = _perform_tiles_update_request(session, temp_folder, update_tiles)

    if observer is not None:
        observer(None)

    if final_observer is not None:
        final_observer(all_updates, _update_cancelled)


def _perform_data_update_request(session, temp_folder, update_data_files):
    """
    Perform the web requests for data files updates.

    This method executes in a secondary thread.

    :param session: a request Session object to be used to retrieve data
    :param temp_folder: temporary folder where to download the update files
    :param update_data_files: dictionary describing the data files for which updates should be searched
    :return: dictionary containing the information about the downloaded update files
    """
    if not _configured:
        configure()

    available_updates = {}
    for folder, files_dict in update_data_files.items():
        for filename, description in files_dict.items():
            if _update_cancelled:
                break
            try:
                with open(str(config.ASSETS_PATH_DATA / filename), 'rb') as old_file:
                    old_content = old_file.read()
                    old_md5 = hashlib.md5(old_content).digest()
                updated_file = session.get(_updates_url + folder + filename, timeout=_TIMEOUT)
                if updated_file.status_code == requests.codes.ok:
                    content = updated_file.content
                    update_md5 = hashlib.md5(content).digest()
                    if update_md5 != old_md5:
                        update_path = pathlib.Path(temp_folder) / filename
                        available_updates[filename] = (update_path, description)
                        with open(pathlib.Path(temp_folder) / filename, 'wb') as f:
                            f.write(content)
                else:
                    errors.append({'type': f"Requests error on {updated_file.url}",
                                   'message': f"Status code: {updated_file.status_code}"})
            except Exception as e:
                errors.append({'type': type(e), 'message': str(e)})

    return available_updates


def _perform_tiles_update_request(session, temp_folder, update_tiles):
    """
    Perform the web requests for tiles updates.

    This method executes in a secondary thread.

    :param session: a request Session object to be used to retrieve data
    :param temp_folder: temporary folder where to download the update files
    :param update_tiles: dictionary describing the tiles files for which updates should be searched
    :return: dictionary containing the information about the downloaded update files
    """
    if not _configured:
        configure()

    available_updates = {}
    for folder, files_dict in update_tiles.items():
        for filename, description in files_dict.items():
            if _update_cancelled:
                break
            try:
                updated_file = session.get(_updates_url + folder + filename, timeout=_TIMEOUT)
                if updated_file.status_code == requests.codes.ok:
                    content = updated_file.content
                    update_path = pathlib.Path(temp_folder) / filename
                    available_updates[filename] = (update_path, description)
                    with open(pathlib.Path(temp_folder) / filename, 'wb') as f:
                        f.write(content)
                else:
                    errors.append({'type': f"Requests error on {updated_file.url}",
                                   'message': f"Status code: {updated_file.status_code}"})
            except Exception as e:
                errors.append({'type': type(e), 'message': str(e)})

    return available_updates
