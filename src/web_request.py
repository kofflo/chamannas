"""
Management of web requests of data and pages.

Variables:
    errors: list containing the errors occurred during web requests

Functions:
    configure: configure the necessary data for the web requests
    perform_web_request_for_hut: perform the web request retrieving the data about free beds for a hut
    open_hut_page: open the web page of a hut in the browser
    open_book_page: open the booking page of a hut in the browser
    search_for_updates: search for application updates
"""
import webbrowser
import requests
import json
import datetime
import time
from html.parser import HTMLParser
import pathlib
import hashlib
from threading import Thread

from src import config

errors = []

_REQUEST_DELAY = 1.0  # seconds: determines the minimum delay between two web requests
_WEB_DATE_FORMAT = '%d.%m.%Y'
_DAY_DELTA = datetime.timedelta(days=1.0)
_HUT_PAGE = 'calendar?hut_id={0}&lang={1}'
_BOOK_PAGE = 'wizard?hut_id={0}&selectedDate={1}&lang={2}'
_TIMEOUT = 5.0
_DEFAULT_MAX_NIGHTS = 14
_DEFAULT_ROOM_BASIC_TYPES = {'default_type': 'shared'}

_configured = False
_max_nights = 0
_last_request = None
_base_url = ""
_updates_url = ""
_room_basic_types = {}
_update_cancelled = False


class _HutHTMLParser(HTMLParser):
    """
    Class used to parse the HTML hut page and extract the information about the available beds.
    Subclass of the Python standard HTMLParser class.

    Methods:
        handle_starttag: handle an HTML tag, identifying the key information about the hut
        handle_data: handle the content of an HTML element, identifying the key information about the hut
    """
    def __init__(self):
        """Initialize the instance."""
        super().__init__()
        self.name = ''  # Hut name
        self.rooms = {}  # Available beds for room type
        self._is_hut_name = False
        self._room_no = None
        self._is_room_label = False

    def handle_starttag(self, tag, attrs):
        """Handle an HTML tag, identifying the key information about the hut.

        :param tag: the HTML tag
        :param attrs: the HTML tag attributes
        """
        if tag == 'h4' and not self.name:
            # Hut name is contained in a 'h4' tag
            self._is_hut_name = True
        elif tag == 'div':
            # Room information is contained in a 'div' tag with 'id' attribute starting with to 'room0-'
            for attr in attrs:
                if attr[0] == 'id' and attr[1][0:6] == 'room0-':
                    self._room_no = int(attr[1][6:])
                    break
        elif self._room_no is not None and tag == 'label':
            # Room label is contained in a 'label' tag with 'class' attribute equal to 'item-label'
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'item-label':
                    self._is_room_label = True
                    break

    def handle_data(self, data):
        """Handle the content of an HTML element, identifying the key information about the hut.

        :param data: the element content
        """
        if self._is_hut_name and data:
            # The content is the hut name
            self.name = data
            self._is_hut_name = False
        elif self._room_no is not None and self._is_room_label:
            # The content is the room label
            self.rooms[self._room_no] = data
            self._room_no = None
            self._is_room_label = False


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


def perform_web_request_for_hut(index, hut, start_date):
    """
    Perform the web request retrieving the data about free beds for a single hut.

    Data are retrieved from an HTML page and from a JSON file; each request covers an interval of 14 days.

    :param index: id number of the hut
    :param hut: dictionary of information about the hut
    :param start_date: start date of the request time interval
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
        result = {'warning': None, 'error': None, 'requested_dates': set(), 'places': {}}
        try:
            # Retrieve the web page for the hut
            lang_code = 'de_' + hut['lang_code']
            web_page = session.get(_base_url + f'calendar?hut_id={index}&lang={lang_code}', timeout=_TIMEOUT,
                                   verify=True)
            if web_page.status_code != requests.codes.ok:
                errors.append({'type': f"Requests error on {web_page.url}",
                               'message': f"Status code: {web_page.status_code}"})

            # Retrieve the booking data in JSON format for the hut
            json_data = session.get(_base_url + 'selectDate?date=' + start_date.strftime(_WEB_DATE_FORMAT),
                                    timeout=_TIMEOUT, verify=True)
            if json_data.status_code != requests.codes.ok:
                errors.append({'type': f"Requests error on {json_data.url}",
                               'message': f"Status code: {json_data.status_code}"})

            _last_request = time.time()
            result['request_time'] = datetime.datetime.now()

            # Analyze the web page and the JSON data to find the required information
            parser = _HutHTMLParser()
            parser.feed(web_page.text)
            if not parser.rooms:
                raise ValueError('No rooms found')
            if parser.name != hut['name']:
                result['warning'] = 'Unexpected name: ' + parser.name
            dict_data = json.loads(json_data.text)
            for j in range(_max_nights):
                book_date = start_date + j * _DAY_DELTA
                result['requested_dates'].add(book_date)
                result['places'][book_date] = {}
                for room in dict_data[str(j)]:
                    if room['closed']:
                        result['places'][book_date]['closed'] = 0
                        break
                    else:
                        room_type = parser.rooms[room['bedCategoryId']].strip()
                        if room_type in _room_basic_types:
                            room_type = _room_basic_types[room_type]
                        else:
                            result['warning'] = 'Unexpected room type: ' + room_type
                            room_type = _room_basic_types['default_type']
                        if room_type not in result['places'][book_date]:
                            result['places'][book_date][room_type] = room['freeRoom']
                        else:
                            result['places'][book_date][room_type] += room['freeRoom']

        except Exception as e:
            result['error'] = f'Error occurred: {e}'
            result['request_time'] = datetime.datetime.now()
            for j in range(_max_nights):
                book_date = start_date + j * _DAY_DELTA
                result['requested_dates'].add(book_date)

    return result


def open_hut_page(index, lang_code):
    """Open the web page of a hut in the browser.

    :param index: id no of the hut
    :param lang_code: locale code to be used in the browser
    """
    if not _configured:
        configure()

    try:
        webbrowser.open(_base_url + _HUT_PAGE.format(index, lang_code), new=2)
    except Exception as e:
        errors.append({'type': type(e), 'message': str(e)})


def open_book_page(index, date, lang_code):
    """Open the booking page of a hut in the browser.

    :param index: id no of the hut
    :param date: required booking date
    :param lang_code: locale code to be used in the browser
    """
    if not _configured:
        configure()

    date_string = date.strftime(_WEB_DATE_FORMAT)
    try:
        webbrowser.open(_base_url + _BOOK_PAGE.format(index, date_string, lang_code), new=2)
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
