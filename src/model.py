"""
Application Model: manages all the information about the huts and the available beds.

Constants:
    ROOM_TYPES: list of the different types of rooms

Classes:
    HutStatus: enumeration defining the possible status of a hut
    HutsModel: model class which stores and manages all the information about the huts and the available beds
"""
import sys
import datetime
import csv
import distutils.util
from threading import Thread
from enum import Enum, auto

from src import i18n
from src.spherical_earth import distance
from src import config
from src.config import ASSETS_PATH_DATA
from src import web_request


ROOM_TYPES = ['single', 'double', 'shared', 'dormitory']

_HUTS_DATA_FILE = str(ASSETS_PATH_DATA / 'huts.txt')
_DAY_DELTA = datetime.timedelta(days=1.0)
_SKIP_CODE = 'SKIP'
_DEFAULT_REFERENCE_LOCATION = (48.1, - 11.6)
_DEFAULT_RESULTS_CACHE_EXPIRATION = 7


class HutStatus(Enum):
    """Enumeration defining the possible status of a hut."""
    NO_REQUEST = auto()
    NO_RESPONSE = auto()
    CLOSED = auto()
    NOT_AVAILABLE = auto()
    AVAILABLE = auto()


class HutsModel:
    """Model class which stores and manages all the information about the huts and the available beds.

    Attributes:
        errors: list containing the errors triggered by the class

    Properties:
        request_dates: list of currently requested dates
        hut_errors: dictionary of errors detected during hut data retrieval
        hut_warnings: dictionary of warnings detected during hut data retrieval

    Methods:
        reload_huts_data: reload the huts dictionary after an update
        get_lang_code: get the native language code of the hut
        get_hut_info: get the whole data about a hut for the current request dates
        get_results_dictionary: get the dictionary containing the retrieved results about free places
        set_reference_location: set the reference location to the specified coordinates
        set_reference_location_from_hut: set the reference location to the location of a hut
        update_results_for_displayed: retrieve the result about free places for all the displayed huts
        update_results_for_selected: retrieve the result about free places for all the selected huts
        update_results_for_indexes: retrieve the result about free places for a group of huts
        update_dates: update the request dates
        select_all: add all the huts in the list of selected ones
        clear_selected: remove all the hust from the list of selected ones
        filter_displayed_by: filter the list of displayed huts using the provided key and parameters
        filter_selected_by: filter the list of selected huts using the provided key and parameters
        sort_displayed_by: sort the list of displayed huts using the provided key
        sort_displayed: sort the list of displayed huts using the active key
        sort_selected_by: sort the list of selected huts using the provided key
        sort_selected: sort the list of selected huts using the active key
        add_to_selected: add a hut to the list of selected ones
        remove_from_selected: remove a hut from the list of selected ones
        get_all_huts: get dummy lists of displayed and selected containing all huts
        get_displayed_selected_huts: get the lists of displayed and selected huts
        check_in_window: check if a hut is located inside a geographical window.
        get_selected: get copies of the lists of currently selected huts
        get_reference_location: get the current reference location
        get_all_data: get all the data relative to huts
        get_all_data_after_retrieve: get all the data which are affected by a data retrieval from web
        enable_retrieved: enable or disable the retrieval of data from the web
        is_retrieved_enabled: get the current status of the retrieve enabled flag
    """

    def __init__(self):
        """Initialize the model."""
        self.errors = []

        self._retrieve_enabled = True
        self._results_cancelled = False
        self._sort_displayed_key = None
        self._sort_displayed_ascending = True
        self._sort_selected_key = None
        self._sort_selected_ascending = True
        self._request_date = datetime.datetime.now().date() + _DAY_DELTA
        self._number_days = 1
        self._reference_location = None
        self._huts_dictionary = {}
        self._results_dictionary = {}
        self._displayed = []
        self._all_selected = []
        self._selected = []
        self._filter_displayed_keys = {}
        self._filter_selected_keys = {}
        self._ascending_order_for_key = {'name': True,
                                         'country': True,
                                         'region': True,
                                         'mountain_range': True,
                                         'self_catering': True,
                                         'height': True,
                                         'distance': True,
                                         'data_requested': True,
                                         'response': True,
                                         'open': True,
                                         'available': False}
        for room in ROOM_TYPES:
            self._ascending_order_for_key[room] = False

        reference_location = config.REFERENCE_LOCATION
        if reference_location is None:
            reference_location = _DEFAULT_REFERENCE_LOCATION
        self.set_reference_location(*reference_location)

        self._load_huts_dictionary()

        self._load_cached_results_dictionary()

        selected = config.SELECTED
        if selected is not None:
            for s in selected:
                if s in self._huts_dictionary:
                    self._all_selected.append(s)

        self._display_all_selected()
        self._display_all()

    @property
    def request_dates(self):
        """Return the list of currently requested dates.

        :return: the list of currently requested dates
        """
        return [self._request_date + i * _DAY_DELTA for i in range(self._number_days)]

    @property
    def hut_errors(self):
        """Return the dictionary of errors detected during hut data retrieval.

        :return: the dictionary of errors detected during hut data retrieval
        """
        errors = []
        for index, hut in self._results_dictionary.items():
            if hut['error'] is not None:
                hut_name = self._huts_dictionary[index]['name']
                hut_error = {'message': hut['error'],
                             'type': f'Hut error ({index}, {hut_name})'}
                errors.append(hut_error)
        return errors

    @property
    def hut_warnings(self):
        """Return the dictionary of warnings detected during hut data retrieval.

        :return: the dictionary of warnings detected during hut data retrieval
        """
        warnings = []
        for index, hut in self._results_dictionary.items():
            if hut['warning'] is not None:
                hut_name = self._huts_dictionary[index]['name']
                hut_warning = {'message': hut['warning'],
                               'type': f'Hut warning ({index}, {hut_name})'}
                warnings.append(hut_warning)
        return warnings

    def reload_huts_data(self):
        """Reload the huts dictionary after an update; the previous selections, filters and sorting are reapplied.

        :return: dictionary containing the new huts data and the list of displayed and selected huts for view update
        """
        self._huts_dictionary.clear()
        self._load_huts_dictionary()

        selected = self._all_selected.copy()
        self.clear_selected()
        for s in selected:
            if s in self._huts_dictionary:
                self._all_selected.append(s)

        return self.get_all_data_after_retrieve()

    def get_lang_code(self, index):
        """Get the native language code of the hut, which is needed to open the correct web page.

        :param index: the index of the desired hut
        :return: the corresponding language code (string)
        """
        return self._huts_dictionary[index]['lang_code']

    def get_hut_info(self, index):
        """Get the whole data about a hut for the current request dates.

        :param index: the index of the desired hut
        :return: a dictionary containing all the current data about the hut
        """
        request_dates = self.request_dates
        return self._get_hut_info_for_dates(index, request_dates)

    def get_results_dictionary(self):
        """Get the dictionary containing the retrieved results about free places.

        :return: the dictionary containing the retrieved results about free places
        """
        return self._results_dictionary

    def set_reference_location(self, lat_ref, lon_ref):
        """Set the reference location to the specified coordinates.

        :param lat_ref: the latitude of the new reference location [degrees]
        :param lon_ref: the longitude of the new reference location [degrees]
        :return: a dictionary with the new reference location for view update
        """
        if -90. < lat_ref < 90. and -180. < lon_ref < 180.:
            self._reference_location = {'lat': lat_ref, 'lon': lon_ref}
        self.sort_displayed()
        self.sort_selected()
        return {'displayed': self._get_displayed(),
                'selected': self.get_selected(),
                'huts_data': self._huts_data_table,
                'reference_location': self.get_reference_location()}

    def set_reference_location_from_hut(self, hut_number):
        """Set the reference location to the location of a hut.

        :param hut_number: the index of the desired hut
        :return: a dictionary with the new reference location for view update
        """
        if hut_number in self._huts_dictionary:
            return self.set_reference_location(self._huts_dictionary[hut_number]['lat'],
                                               self._huts_dictionary[hut_number]['lon'])
        else:
            return {}

    def update_results_for_displayed(self, initial=None, observer=None, final_observer=None):
        """Retrieve the result about free places for all the displayed huts.

        :param initial: function to be executed before starting the retrieve process (signature: (callable, int))
        :param observer: function to be executed after each step of the retrieve process (signature: (int))
        :param final_observer: function to be executed at the end of the retrieve process (signature: ())
        """
        if self._request_date is not None and self._number_days is not None:
            displayed = self._displayed.copy()
            if initial is not None:
                initial(self._cancel_results, len(displayed))
            self._get_results_for_date(displayed, self._request_date, observer, final_observer)

    def update_results_for_selected(self, initial=None, observer=None, final_observer=None):
        """Retrieve the result about free places for all the selected huts.

        :param initial: function to be executed before starting the retrieve process (signature: (callable, int))
        :param observer: function to be executed after each step of the retrieve process (signature: (int))
        :param final_observer: function to be executed at the end of the retrieve process (signature: ())
        """
        if self._request_date is not None and self._number_days is not None:
            selected = self._selected.copy()
            if initial is not None:
                initial(self._cancel_results, len(selected))
            self._get_results_for_date(selected, self._request_date, observer, final_observer)

    def update_results_for_indexes(self, request_indexes, initial=None, observer=None, final_observer=None):
        """Retrieve the result about free places for a group of huts defined by a list of indexes.

        :param request_indexes: the list of indexes of the huts for which free places have to be retrieved
        :param initial: function to be executed before starting the retrieve process (signature: (callable, int))
        :param observer: function to be executed after each step of the retrieve process (signature: (int))
        :param final_observer: function to be executed at the end of the retrieve process (signature: ())
        """
        if self._request_date is not None and self._number_days is not None:
            if initial is not None:
                initial(self._cancel_results, len(request_indexes))
            self._get_results_for_date(request_indexes, self._request_date, observer, final_observer)

    def update_dates(self, request_date, number_days):
        """Update the request dates, based on the selected first day and the number of days.

        :param request_date: the selected request first day
        :param number_days: the number of days
        :return: a dictionary of huts data and dates for view update
        """
        self._request_date = request_date
        self._number_days = number_days
        self.sort_displayed()
        self.sort_selected()
        return {'displayed': self._get_displayed(),
                'selected': self.get_selected(),
                'huts_data': self._huts_data_table,
                'dates': self.request_dates}

    def select_all(self):
        """Add all the huts in the list of selected ones.

        :return: a dictionary with the list of selected huts for view update
        """
        for index in self._displayed:
            self.add_to_selected(index)
        return {'selected': self.get_selected()}

    def clear_selected(self):
        """Remove all huts from the list of selected ones.

        :return: a dictionary with the list of selected huts for view update
        """
        self._all_selected.clear()
        self._selected.clear()
        return {'selected': self.get_selected()}

    def filter_displayed_by(self, key, parameters):
        """Filter the list of displayed huts using the provided key and parameters.

        :param key: the filter key
        :param parameters: dictionary containing the parameters which define the filter to apply
        :return: a dictionary with the list of displayed huts and the active filter keys for view update
        """
        if key not in self._filter_displayed_keys:
            self._displayed = self._filter_by(self._displayed, key, parameters)
            self._filter_displayed_keys[key] = parameters
        else:
            self._filter_displayed_keys.pop(key)
            self._filter_and_sort_displayed()
        return {'displayed': self._get_displayed(),
                'filter_displayed_keys': self._get_filter_displayed_keys()}

    def filter_selected_by(self, key, parameters):
        """Filter the list of selected huts using the provided key and parameters.

        :param key: the filter key
        :param parameters: dictionary containing the parameters which define the filter to apply
        :return: a dictionary with the list of selected huts and the active filter keys for view update
        """
        if key not in self._filter_selected_keys:
            self._selected = self._filter_by(self._selected, key, parameters)
            self._filter_selected_keys[key] = parameters
        else:
            self._filter_selected_keys.pop(key)
            self._filter_and_sort_selected()
        return {'selected': self.get_selected(),
                'filter_selected_keys': self._get_filter_selected_keys()}

    def sort_displayed_by(self, key):
        """Sort the list of displayed huts using the provided key.

        :param key: the sorting key
        :return: a dictionary with the list of displayed huts and the active sorting key for view update
        """
        if key == self._sort_displayed_key:
            self._sort_displayed_ascending = not self._sort_displayed_ascending
        else:
            self._sort_displayed_key = key
            self._sort_displayed_ascending = self._ascending_order_for_key[key]
        self.sort_displayed()
        return {'displayed': self._get_displayed(),
                'sort_displayed_key': self._get_sort_displayed_key()}

    def sort_displayed(self):
        """Sort the list of displayed huts using the active key.

        :return: a dictionary with the list of displayed huts for view update
        """
        self._displayed = self._sort_by(self._displayed, self._sort_displayed_key, self._sort_displayed_ascending)
        return {'displayed': self._get_displayed()}

    def sort_selected_by(self, key):
        """Sort the list of selected huts using the provided key.

        :param key: the sorting key
        :return: a dictionary with the list of selected huts and the active sorting key for view update
        """
        if key == self._sort_selected_key:
            self._sort_selected_ascending = not self._sort_selected_ascending
        else:
            self._sort_selected_key = key
            self._sort_selected_ascending = self._ascending_order_for_key[key]
        self.sort_selected()
        return {'selected': self.get_selected(),
                'sort_selected_key': self._get_sort_selected_key()}

    def sort_selected(self):
        """Sort the list of selected huts using the active key.

        :return: a dictionary with the list of selected huts for view update
        """
        self._selected = self._sort_by(self._selected, self._sort_selected_key, self._sort_selected_ascending)
        return {'selected': self.get_selected()}

    def add_to_selected(self, index):
        """Add the hut with the provided index to the list of selected ones.

        :param index: the index of the hut to add
        :return: a dictionary with the list of selected huts for view update
        """
        if index in self._huts_dictionary.keys() and index not in self._all_selected:
            self._all_selected.append(index)
        self._filter_and_sort_selected()
        return {'selected': self.get_selected()}

    def remove_from_selected(self, index):
        """Remove the hut with the provided index from the list of selected ones.

        :param index: the index of the hut to remove
        :return: a dictionary with the list of selected huts for view update
        """
        if index in self._all_selected:
            self._all_selected.remove(index)
        self._filter_and_sort_selected()
        return {'selected': self.get_selected()}

    def get_all_huts(self):
        """Get dummy lists of displayed and selected containing all huts (for correct table view configuring).

        :return: a dictionary with dummy lists of displayed and selected hut for view update
        """
        all_indexes = list(self._huts_dictionary.keys())
        return {'displayed': all_indexes,
                'selected': [all_indexes, all_indexes]}

    def get_displayed_selected_huts(self):
        """Get the lists of displayed and selected huts (for correct table view configuring).

        :return: a dictionary with the lists of displayed and selected huts for view update
        """
        return {'displayed': self._get_displayed(),
                'selected': self.get_selected()}

    def check_in_window(self, index, lat_min, lat_max, lon_min, lon_max):
        """Check if the hut with the specified index is located inside a geographical window.

        :param index: the index of the hut
        :param lat_min: the minimum latitude of the window
        :param lat_max: the maximum latitude of the window
        :param lon_min: the minimum longitude of the window
        :param lon_max: the maximum longitude of the window
        :return: True if the huts is located inside the window, False otherwise
        """
        lat, lon = self._huts_dictionary[index]['lat'], self._huts_dictionary[index]['lon']
        return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

    def get_selected(self):
        """Get copies of the lists of currently selected huts.

        :return: copies of the lists of currently selected huts
        """
        return [self._selected.copy(), self._all_selected.copy()]

    def get_reference_location(self):
        """Get the current reference location.

        :return: a dictionary with the coordinates of the current reference location
        """
        return self._reference_location.copy()

    def get_all_data(self):
        """Get all the data relative to huts.

        :return: a dictionary with all data relative to huts for view update
        """
        return {
            'huts_data': self._huts_data_table,
            'displayed': self._get_displayed(),
            'selected': self.get_selected(),
            'retrieve_enabled': self._retrieve_enabled,
            'reference_location': self.get_reference_location(),
            'dates': self.request_dates,
            'filter_displayed_keys': self._get_filter_displayed_keys(),
            'filter_selected_keys': self._get_filter_selected_keys(),
            'sort_displayed_key': self._get_sort_displayed_key(),
            'sort_selected_key': self._get_sort_selected_key()
        }

    def get_all_data_after_retrieve(self):
        """Get all the data which are affected by a data retrieval from web.

        :return: a dictionary with all data affected by a data retrieval for view update
        """
        self._filter_and_sort_displayed()
        self._filter_and_sort_selected()
        return {'huts_data': self._huts_data_table,
                'displayed': self._get_displayed(),
                'selected': self.get_selected()}

    def enable_retrieve(self, is_enabled):
        """Enable or disable the retrieval of data from the web.

        :param is_enabled: boolean which specified if the retrieve should be enabled (True) or disabled (False)
        :return: a dictionary with the retrieve enabled flag for view update
        """
        self._retrieve_enabled = is_enabled
        return {'retrieve_enabled': self._retrieve_enabled}

    def is_retrieve_enabled(self):
        """Get the current status of the retrieve enabled flag.

        :return: the current retrieve enabled flag (True if retrieve from web is enabled, False if disabled)
        """
        return self._retrieve_enabled

    @property
    def _huts_data_table(self):
        """Return a dictionary containing all current data about huts with hut index as key.

        :return: a dictionary containing all current data about huts with hut index as key
        """
        table = {}
        request_dates = self.request_dates
        for index in self._huts_dictionary:
            table[index] = self._get_hut_info_for_dates(index, request_dates)
        return table

    def _load_cached_results_dictionary(self):
        """Load the recent results about free places from the cache (i.e. the results file read by config module)."""
        cached_results_dictionary = config.RESULTS_DICTIONARY
        config_cache_expiration = config.RESULTS_CACHE_EXPIRATION
        if config_cache_expiration is None:
            cache_expiration = datetime.timedelta(days=_DEFAULT_RESULTS_CACHE_EXPIRATION)
        else:
            cache_expiration = datetime.timedelta(days=config_cache_expiration)
        if cached_results_dictionary is not None:
            for index, result in cached_results_dictionary.items():
                if result['request_time'] + cache_expiration > datetime.datetime.now():
                    self._results_dictionary[index] = result

    def _get_hut_info_for_dates(self, index, request_dates):
        """Get a dictionary of all huts data for the specified huts and dates.

        :param index: the index of the hut for which data are required
        :param request_dates: the dates for which data are required
        :return: a dictionary of all huts data for the specified huts and dates
        """
        data_requested = index in self._results_dictionary and \
                         all([d in self._results_dictionary[index]['requested_dates'] for d in request_dates])
        try:
            response = self._results_dictionary[index]['error'] is None
        except KeyError:
            response = True
        distance_from_ref = distance(self._huts_dictionary[index]['lat'], self._huts_dictionary[index]['lon'],
                                     self._reference_location['lat'], self._reference_location['lon'])
        is_open = self._check_open(self._results_dictionary, index, request_dates)
        available_places = self._available_places(self._results_dictionary, index, request_dates)
        available_places_for_room = self._available_places_for_room(self._results_dictionary, index, request_dates)
        detailed_places = self._detailed_places(self._results_dictionary, index, request_dates)

        if not response:
            status = HutStatus.NO_RESPONSE
        elif not data_requested:
            status = HutStatus.NO_REQUEST
        elif not is_open:
            status = HutStatus.CLOSED
        elif available_places == 0:
            status = HutStatus.NOT_AVAILABLE
        else:
            status = HutStatus.AVAILABLE

        hut_info = {
            'name': self._huts_dictionary[index]['name'],
            'country': self._huts_dictionary[index]['country'],
            'region': self._huts_dictionary[index]['region'],
            'mountain_range': self._huts_dictionary[index]['mountain_range'],
            'self_catering': self._huts_dictionary[index]['self_catering'],
            'height': self._huts_dictionary[index]['height'],
            'lat': self._huts_dictionary[index]['lat'],
            'lon': self._huts_dictionary[index]['lon'],
            'distance': distance_from_ref,
            'data_requested': data_requested,
            'response': response,
            'open': is_open,
            'available': available_places,
            'detailed_places': detailed_places,
            'status': status
        }
        for room in ROOM_TYPES:
            hut_info[room] = available_places_for_room[room] if room in available_places_for_room else None
        return hut_info

    def _load_huts_dictionary(self):
        """Load from the file the list of huts with all their characteristics (location, country etc.)."""
        try:
            with open(_HUTS_DATA_FILE, encoding='UTF-8-SIG') as tsv:
                for line in csv.reader(tsv, dialect='excel-tab'):
                    try:
                        if line[1] == _SKIP_CODE:
                            continue
                        id_no, name, country, region, mountain_range, self_catering, lat, lon, height, lang_code = line
                        hut = {'name': name, 'country': country, 'region': region, 'mountain_range': mountain_range,
                               'self_catering': distutils.util.strtobool(self_catering),
                               'lat': float(lat), 'lon': float(lon), 'height': float(height), 'lang_code': lang_code}
                        self._huts_dictionary[int(id_no)] = hut
                    except ValueError as e:
                        self.errors.append({'type': type(e), 'message': str(line) + ';' + str(e)})
        except FileNotFoundError:
            print(f"Fatal error: missing huts data file '{_HUTS_DATA_FILE}'")
            sys.exit(1)

    def _get_results_for_date(self, huts_list, start_date, observer, final_observer):
        """Start the retrieval of data about free places from the web for the specified huts and initial date.

        :param huts_list: list of huts indexes for which the information has to be retrieved
        :param start_date: initial date of the period for which information has to be retrieved
        :param observer: function to be executed after every data retrieval for each individual hut (signature: (int))
        :param final_observer: function to be executed at the end of the data retrieval (signature: ())
        """
        self._results_cancelled = False
        thread = Thread(target=self._perform_web_request,
                        args=(huts_list, start_date, observer, final_observer))
        thread.start()

    def _perform_web_request(self, huts_list, start_date, observer, final_observer):
        """Perform the retrieval of data about free places from the web for the specified huts and initial date.

        This method is executed in a separate thread.

        :param huts_list: list of huts indexes for which the information has to be retrieved
        :param start_date: initial date of the period for which information has to be retrieved
        :param observer: function to be executed after every data retrieval for each individual hut (signature: (int))
        :param final_observer: function to be executed at the end of the data retrieval (signature: ())
        """
        outstanding_requests = len(huts_list)
        results = {}

        for index in huts_list:
            if observer is not None:
                observer(outstanding_requests)
            if self._results_cancelled:
                break
            results[index] = web_request.perform_web_request_for_hut(index, self._huts_dictionary[index], start_date)
            outstanding_requests -= 1

        if observer is not None:
            observer(0)

        self._update_results_dictionary(results)

        if final_observer is not None:
            final_observer()

    @staticmethod
    def _check_open(results_dictionary, index, dates=None):
        """Check if the specified hut is open at all specified dates (or at all available date if no date is provided).

        :param results_dictionary: the dictionary containing the information about free places
        :param index: the index of the hut for which the check is required
        :param dates: the dates for which the check is required; if not provided, all available dates are considered
        :return: True if the hut is open, False otherwise
        """
        if index not in results_dictionary:
            return False
        response = results_dictionary[index]['error'] is None
        if not response:
            return False
        available_dates = set(results_dictionary[index]['places'].keys())
        check_dates = set(dates) if dates is not None else available_dates
        if not check_dates <= available_dates:
            return False
        is_open = True
        for date in check_dates:
            is_open = is_open and 'closed' not in results_dictionary[index]['places'][date]
        return is_open

    @staticmethod
    def _available_places(results_dictionary, index, dates=None):
        """Return the number of available places for a hut for all specified dates.

        :param results_dictionary: the dictionary containing the information about free places
        :param index: the index of the hut for which the number of available places is required
        :param dates: the dates for which the value is required; if not provided, all available dates are considered
        :return: the number of available places
        """
        if index not in results_dictionary:
            return 0
        response = results_dictionary[index]['error'] is None
        if not response:
            return 0
        available_dates = set(results_dictionary[index]['places'].keys())
        check_dates = set(dates) if dates is not None else available_dates
        if not check_dates <= available_dates:
            return 0
        available_places_for_date = {}
        for date in check_dates:
            available_places = 0
            for room_places in results_dictionary[index]['places'][date].values():
                available_places += room_places
            available_places_for_date[date] = available_places
        return min(available_places_for_date.values())

    @staticmethod
    def _available_places_for_room(results_dictionary, index, dates=None):
        """Return the number of available places in each room type for a hut for all specified dates.

        :param results_dictionary: the dictionary containing the information about free places
        :param index: the index of the hut for which the number of available places is required
        :param dates: the dates for which the values are required; if not provided, all available dates are considered
        :return: a dictionary with the number of available places with room type as key
        """
        if index not in results_dictionary:
            return {}
        if results_dictionary[index]['error'] is not None:
            return {}
        available_dates = set(results_dictionary[index]['places'].keys())
        check_dates = set(dates) if dates is not None else available_dates
        if not check_dates <= available_dates:
            return {}
        available_places = {}
        for date in check_dates:
            available_places_for_date = {}
            for room_name, room_places in results_dictionary[index]['places'][date].items():
                available_places_for_date[room_name] = room_places
            if not available_places:
                available_places = available_places_for_date
            else:
                for room in available_places:
                    if room not in available_places_for_date:
                        available_places[room] = 0
                    else:
                        available_places[room] = min(available_places_for_date[room], available_places[room])
        return available_places

    @staticmethod
    def _detailed_places(results_dictionary, index, dates=None):
        """Return the number of available places in each room type and for each date for a hut.

        :param results_dictionary: the dictionary containing the information about free places
        :param index: the index of the hut for which the number of available places is required
        :param dates: the dates for which the value are  required; if not provided, all available dates are considered
        :return: a dictionary of dictionaries with the number of available places with date and room type as key
        """
        if index not in results_dictionary:
            return {}
        response = results_dictionary[index]['error'] is None
        if not response:
            return {}
        available_dates = set(results_dictionary[index]['places'].keys())
        check_dates = set(dates) if dates is not None else available_dates
        detailed_places = {}
        for date in check_dates:
            if date in results_dictionary[index]['places']:
                detailed_places[date] = results_dictionary[index]['places'][date]
            else:
                detailed_places[date] = {}
        return detailed_places

    def _filter_and_sort_displayed(self):
        """Recreate the list of displayed huts applying all active filters and the active sorting."""
        self._display_all()
        self._displayed = self._apply_all_filters(self._displayed, self._filter_displayed_keys)
        self.sort_displayed()

    def _filter_and_sort_selected(self):
        """Recreate the list of selected huts applying all active filters and the active sorting."""
        self._selected = self._apply_all_filters(self._all_selected, self._filter_selected_keys)
        self.sort_selected()

    def _filter_by(self, to_filter, key, parameters):
        """
        Filter a list of huts keeping only those which fulfill the specified criteria.

        The filtering is delegated to the dedicated methods, one per key.

        :param to_filter: a list of hut indexes
        :param key: string defining the key to be used to filter
        :param parameters: dictionary containing the parameters defining the filter criteria
        :return: the updated list of hut indexes
        """
        if key == 'country':
            to_filter = self._filter_by_country(to_filter, parameters['value'])
        elif key == 'region':
            to_filter = self._filter_by_region(to_filter, parameters['value'])
        elif key == 'mountain_range':
            to_filter = self._filter_by_mountain_range(to_filter, parameters['value'])
        elif key == 'height':
            to_filter = self._filter_by_height(to_filter, parameters['min'], parameters['max'])
        elif key == 'self_catering':
            to_filter = self._filter_by_self_catering(to_filter, parameters['value'])
        elif key == 'distance':
            lat_ref = self._reference_location['lat']
            lon_ref = self._reference_location['lon']
            to_filter = self._filter_by_distance(to_filter, parameters['min'], parameters['max'],
                                                 lat_ref, lon_ref)
        elif key == 'response':
            to_filter = self._filter_by_response(to_filter)
        elif key == 'open':
            to_filter = self._filter_by_open(to_filter, self.request_dates)
        elif key == 'available':
            to_filter = self._filter_by_available(to_filter, parameters['min'], parameters['max'], self.request_dates)
        elif key in ROOM_TYPES:
            to_filter = self._filter_by_room(to_filter, key, parameters['min'], parameters['max'], self.request_dates)
        return to_filter

    def _filter_by_country(self, original_list, filter_country):
        """Filter a list of huts keeping only those in the specified country.

        :param original_list: a list of hut indexes
        :param filter_country: the country string to be used to filter
        :return: the updated list of hut indexes
        """
        filtered_list = []
        for index in original_list:
            if self._huts_dictionary[index]['country'] == filter_country:
                filtered_list.append(index)
        return filtered_list

    def _filter_by_region(self, original_list, filter_region):
        """Filter a list of huts keeping only those in the specified region.

        :param original_list: a list of hut indexes
        :param filter_region: the region string to be used to filter
        :return: the updated list of hut indexes
        """
        filtered_list = []
        for index in original_list:
            if self._huts_dictionary[index]['region'] == filter_region:
                filtered_list.append(index)
        return filtered_list

    def _filter_by_mountain_range(self, original_list, filter_mountain_range):
        """Filter a list of huts keeping only those in the specified mountain range.

        :param original_list: a list of hut indexes
        :param filter_mountain_range: the mountain range string to be used to filter
        :return: the updated list of hut indexes
        """
        filtered_list = []
        for index in original_list:
            if self._huts_dictionary[index]['mountain_range'] == filter_mountain_range:
                filtered_list.append(index)
        return filtered_list

    def _filter_by_height(self, original_list, filter_height_min, filter_height_max):
        """
        Filter a list of huts keeping only those in the specified height interval.

        It is possible to specify an open interval by passing a None value for one of the heights.

        :param original_list: a list of hut indexes
        :param filter_height_min: the minimum value of the height interval to be used to filter [meters]
        :param filter_height_max: the maximum value of the height interval to be used to filter [meters]
        :return: the updated list of hut indexes
        """
        if filter_height_min is None:
            filter_height_min = 0.
        if filter_height_max is None:
            filter_height_max = 10000.
        filtered_list = []
        for index in original_list:
            if filter_height_min <= self._huts_dictionary[index]['height'] <= filter_height_max:
                filtered_list.append(index)
        return filtered_list

    def _filter_by_self_catering(self, original_list, filter_self_catering):
        """Filter a list of huts keeping only those whose with the specified self-catering flag.

        :param original_list: a list of hut indexes
        :param filter_self_catering: the self catering flag to be used to filter [boolean]
        :return: the updated list of hut indexes
        """
        filtered_list = []
        for index in original_list:
            if self._huts_dictionary[index]['self_catering'] == filter_self_catering:
                filtered_list.append(index)
        return filtered_list

    def _filter_by_distance(self, original_list, filter_distance_min, filter_distance_max, lat_ref, lon_ref):
        """
        Filter a list of huts keeping only those in the specified distance interval from a reference location.

        It is possible to specify an open interval by passing a None value for one of the distances.

        :param original_list: a list of hut indexes
        :param filter_distance_min: the minimum value of the distance interval to be used to filter [km]
        :param filter_distance_max: the maximum value of the distance interval to be used to filter [km]
        :param lat_ref: latitude of the reference location [degrees]
        :param lon_ref: longitude of the reference location [degrees]
        :return: the updated list of hut indexes
        """
        if filter_distance_min is None:
            filter_distance_min = 0.
        if filter_distance_max is None:
            filter_distance_max = 20000.
        filtered_list = []
        for index in original_list:
            lat = self._huts_dictionary[index]['lat']
            lon = self._huts_dictionary[index]['lon']
            if filter_distance_min * 1000 <= distance(lat, lon, lat_ref, lon_ref) <= filter_distance_max * 1000:
                filtered_list.append(index)
        return filtered_list

    def _filter_by_response(self, original_list):
        """
        Filter a list of huts removing those for which an error occurred during data retrieval from the web.

        Huts for which no web request has been performed are not filtered out.

        :param original_list: a list of hut indexes
        :return: the updated list of hut indexes
        """
        filtered_list = []
        for index in original_list:
            if index in self._results_dictionary:
                response = self._results_dictionary[index]['error'] is None
                if not response:
                    continue
            filtered_list.append(index)
        return filtered_list

    def _filter_by_open(self, original_list, dates):
        """
        Filter a list of huts keeping only those which are open in all of the specified dates.

        Huts for which no web request has been performed are not filtered out.

        :param original_list: a list of hut indexes
        :param dates: the list of dates in which to check if the hut is open
        :return: the updated list of hut indexes
        """
        filtered_list = []
        for index in original_list:
            if index in self._results_dictionary:
                response = self._results_dictionary[index]['error'] is None
                data_requested = all([d in self._results_dictionary[index]['requested_dates'] for d in dates])
                is_open = self._check_open(self._results_dictionary, index, dates)
                if response and data_requested and not is_open:
                    continue
            filtered_list.append(index)
        return filtered_list

    def _filter_by_available(self, original_list, filter_available_min, filter_available_max, dates):
        """
        Filter a list of huts keeping only those which have
        a number of available places in the specified interval for all the specified dates.

        It is possible to specify an open interval by passing a None value for one of the distances.
        Huts for which no web request has been performed are not filtered out.

        :param original_list: a list of hut indexes
        :param filter_available_min: the minimum number of available places to be used to filter
        :param filter_available_max: the maximum number of available places to be used to filter
        :param dates: the list of dates in which to check if the hut has available places
        :return: the updated list of hut indexes
        """
        if filter_available_min is None:
            filter_available_min = 0.
        if filter_available_max is None:
            filter_available_max = 1000.
        filtered_list = []
        for index in original_list:
            available_places = self._available_places(self._results_dictionary, index, dates)
            if filter_available_min <= available_places <= filter_available_max:
                filtered_list.append(index)
        return filtered_list

    def _filter_by_room(self, original_list, room, filter_available_min, filter_available_max, dates):
        """
        Filter a list of huts keeping only those which have a number of available places in a certain room type
        in the specified interval for all the specified dates.

        It is possible to specify an open interval by passing a None value for one of the distances.
        Huts for which no web request has been performed are not filtered out.

        :param original_list: a list of hut indexes
        :param room: the room type for which to check if the huts has available places
        :param filter_available_min: the minimum number of available places to be used to filter
        :param filter_available_max: the maximum number of available places to be used to filter
        :param dates: the list of dates in which to check if the hut has available places
        :return: the updated list of hut indexes
        """
        if filter_available_min is None:
            filter_available_min = 0.
        if filter_available_max is None:
            filter_available_max = 1000.
        filtered_list = []
        for index in original_list:
            available_places_for_room = self._available_places_for_room(self._results_dictionary, index, dates)
            available_places = available_places_for_room[room] if room in available_places_for_room else 0
            if filter_available_min <= available_places <= filter_available_max:
                filtered_list.append(index)
        return filtered_list

    def _sort_by(self, to_sort, key, ascending):
        """
        Sort a list of huts by the specified key.

        The sorting is delegated to the dedicated methods, one per key.

        :param to_sort: a list of hut indexes
        :param key: string defining the key to be used to sort
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        if key == 'name':
            to_sort = self._sort_by_name(to_sort, ascending)
        elif key == 'country':
            to_sort = self._sort_by_country(to_sort, ascending)
        elif key == 'region':
            to_sort = self._sort_by_region(to_sort, ascending)
        elif key == 'mountain_range':
            to_sort = self._sort_by_mountain_range(to_sort, ascending)
        elif key == 'height':
            to_sort = self._sort_by_height(to_sort, ascending)
        elif key == 'self_catering':
            to_sort = self._sort_by_self_catering(to_sort, ascending)
        elif key == 'distance':
            lat_ref = self._reference_location['lat']
            lon_ref = self._reference_location['lon']
            to_sort = self._sort_by_distance(to_sort, lat_ref, lon_ref, ascending)
        elif key == 'available':
            to_sort = self._sort_by_available(to_sort, self.request_dates, ascending)
        elif key in ROOM_TYPES:
            to_sort = self._sort_by_room(to_sort, key, self.request_dates, ascending)
        else:
            to_sort = to_sort.copy()
        return to_sort

    def _sort_by_name(self, original_list, ascending=True):
        """Sort a list of huts alphabetically by name.

        :param original_list: a list of hut indexes
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        return sorted(original_list, key=lambda index: self._huts_dictionary[index]['name'], reverse=not ascending)

    def _sort_by_country(self, original_list, ascending=True):
        """Sort a list of huts alphabetically by country.

        :param original_list: a list of hut indexes
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        return sorted(original_list, key=lambda index: self._huts_dictionary[index]['country'], reverse=not ascending)

    def _sort_by_region(self, original_list, ascending=True):
        """Sort a list of huts alphabetically by region.

        :param original_list: a list of hut indexes
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        return sorted(original_list,
                      key=lambda index: i18n.regions_labels[self._huts_dictionary[index]['region']].casefold(),
                      reverse=not ascending)

    def _sort_by_mountain_range(self, original_list, ascending=True):
        """Sort a list of huts alphabetically by mountain range.

        :param original_list: a list of hut indexes
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        return sorted(original_list,
                      key=lambda index: i18n.mountain_ranges_labels[
                          self._huts_dictionary[index]['mountain_range']
                      ].casefold(),
                      reverse=not ascending)

    def _sort_by_height(self, original_list, ascending=True):
        """Sort a list of huts by height.

        :param original_list: a list of hut indexes
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        return sorted(original_list, key=lambda index: self._huts_dictionary[index]['height'], reverse=not ascending)

    def _sort_by_self_catering(self, original_list, ascending=True):
        """Sort a list of huts by self-catering flag.

        :param original_list: a list of hut indexes
        :param ascending: boolean which specifies the sorting direction (True: self-catering first; False: last)
        :return: the sorted list of hut indexes
        """
        return sorted(original_list, key=lambda index: self._huts_dictionary[index]['self_catering'],
                      reverse=not ascending)

    def _sort_by_distance(self, original_list, lat_ref, lon_ref, ascending=True):
        """Sort a list of huts by distance from a reference location.

        :param original_list: a list of hut indexes
        :param lat_ref: latitude of the reference location [degrees]
        :param lon_ref: longitude of the reference location [degrees]
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        def f_key(index):
            lat = self._huts_dictionary[index]['lat']
            lon = self._huts_dictionary[index]['lon']
            return distance(lat, lon, lat_ref, lon_ref)
        return sorted(original_list, key=f_key, reverse=not ascending)

    def _sort_by_available(self, original_list, dates=None, ascending=False):
        """Sort a list of huts by number of available places for all the specified dates.

        :param original_list: a list of hut indexes
        :param dates: the list of dates for which the available places are considered
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        def f_key(index):
            return self._available_places(self._results_dictionary, index, dates)
        return sorted(original_list, key=f_key, reverse=not ascending)

    def _sort_by_room(self, original_list, room, dates=None, ascending=False):
        """Sort a list of huts by number of available places for all the specified dates.

        :param original_list: a list of hut indexes
        :param room: the room type for which the available places are considered
        :param dates: the list of dates for which the available places are considered
        :param ascending: boolean which specifies the sorting direction (True: ascending; False: descending)
        :return: the sorted list of hut indexes
        """
        def f_key(index):
            available_places_for_room = self._available_places_for_room(self._results_dictionary, index, dates)
            return available_places_for_room[room] if room in available_places_for_room else -1
        return sorted(original_list, key=f_key, reverse=not ascending)

    def _update_results_dictionary(self, results):
        """Update the dictionary containing the retrieved results about free places by merging new results.

        :param results: a dictionary containing new retrieved results to be merged
        """
        for index, result in results.items():
            if index not in self._results_dictionary:
                self._results_dictionary[index] = result
            else:
                self._results_dictionary[index]['error'] = result['error']
                self._results_dictionary[index]['warning'] = result['warning']
                self._results_dictionary[index]['requested_dates'].update(result['requested_dates'])
                self._results_dictionary[index]['request_time'] = result['request_time']
                for book_date, rooms in result['places'].items():
                    self._results_dictionary[index]['places'][book_date] = rooms

    def _cancel_results(self, obj):
        """
        Set the flag to indicate that the retrieval of results from the web has been cancelled by the user.

        This method is called by a view widget.

        :param obj: object which calls the method
        """
        self._results_cancelled = True

    def _display_all(self):
        """Reset the list of displayed huts to contain all the huts in the dictionary i.e. removes all filters."""
        self._displayed = list(self._huts_dictionary.keys())

    def _display_all_selected(self):
        """Reset the list of selected huts to contain all the selected huts i.e. removes all filters."""
        self._selected = list(self._all_selected)

    def _apply_all_filters(self, to_filter, filter_keys):
        """Apply all the specified filters to a list of huts.

        :param to_filter: a list of hut indexes
        :param filter_keys: a dictionary of filtering keys and parameters
        :return: the filtered list of huts indexes
        """
        for key, parameters in filter_keys.items():
            to_filter = self._filter_by(to_filter, key, parameters)
        return list(to_filter)

    def _get_filter_displayed_keys(self):
        """Get a copy of the current keys used to filter the list of displayed huts.

        :return: a copy of the current keys used to filter the list of displayed huts
        """
        return self._filter_displayed_keys.copy()

    def _get_filter_selected_keys(self):
        """Get a copy of the current keys used to filter the list of selected huts.

        :return: a copy of the current keys used to filter the list of selected huts
        """
        return self._filter_selected_keys.copy()

    def _get_displayed(self):
        """Get a copy of the current list of displayed huts.

        :return: a copy of the current list of displayed huts
        """
        return self._displayed.copy()

    def _get_sort_displayed_key(self):
        """Get a list with the current key and direction used to sort the list of displayed huts.

        :return: a list with the current key and direction used to sort the list of displayed huts
        """
        return [self._sort_displayed_key, self._sort_displayed_ascending]

    def _get_sort_selected_key(self):
        """Get a list with the current key and direction used to sort the list of selected huts.

        :return: a list with the current key and direction used to sort the list of selected huts
        """
        return [self._sort_selected_key, self._sort_selected_ascending]
