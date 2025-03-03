"""
Controller of the application.

Classes:
    HutsController: controller of the application
"""
import shutil
import os
import tempfile
import tarfile

from src.view.frames import HutsTableView, HutsMapView, DetailedInfoView, SelectedInfoView, DeveloperInfoView, \
    AboutDialog, UpdateDialog
from src import view
from src import i18n
from src import map_tools
from src import config
from src import web_request


class HutsController:
    """Class defining the controller of the application.

    Methods:
        command_sort: command the model to sort the huts and the view to update
        command_filter: command the model to filter the huts and the view to update
        command_select: command the model to select a single hut and the view to update
        command_select_multi: command the model to select a group of huts and the view to update
        command_select_all: command the model to select all huts and the view to update
        command_select_window: command the model to select all huts in a window and the view to update
        command_update_results: command the model to retrieve the free beds data and the view to update
        command_update_dates: command the model to update the reference dates interval and the view to update
        command_update_reference_location: command the model to update the reference location and the view to update
        command_language: command the i18n module to set a new current language
        command_open_hut_page: command the default browser to open the hut web page
        command_open_table_view: open a new table view
        command_open_map_view: open a new map view
        command_open_info_frame: open a detailed info frame for a hut
        command_open_selected_frame: open an info frame for all selected huts
        command_open_about_dialog: open the about dialog
        command_open_warnings_frame: open a developer info frame with information about warnings
        command_open_errors_frame: open a developer info frame with information about errors
        command_search_for_updates: command the web_request module to search for application updates
        command_open_update_dialog: open a dialog for the application updates
        command_preference_gui: select a gui type in the preferences settings
        command_preference_view: select a view type in the preferences settings
    """
    def __init__(self, model, view_type='table'):
        """Initialize the controller and create the main view.

        :param model: the model object
        :param view_type: the view to be open as main ('table' - the default - or 'map')
        """
        self._model = model
        self._view = None
        self._temp_folder_for_updates = None
        if view_type == 'map':
            self.command_open_map_view()
        else:
            self.command_open_table_view()

    def command_sort(self, data):
        """Command the model to sort the huts and the view to update.

        :param data: dictionary containing the details about the sort
        """
        key = data['key']
        update_data = {}
        if data['which'] == 'displayed':
            update_data.update(self._model.sort_displayed_by(key))
        elif data['which'] == 'selected':
            update_data.update(self._model.sort_selected_by(key))
        self._view.update_gui(update_data)

    def command_filter(self, data):
        """Command the model to filter the huts and the view to update.

        :param data: dictionary containing the details about the filter
        """
        key = data['key']
        parameters = data['parameters']
        update_data = {}
        if data['which'] == 'displayed':
            update_data.update(self._model.filter_displayed_by(key, parameters))
        elif data['which'] == 'selected':
            update_data.update(self._model.filter_selected_by(key, parameters))
        self._view.update_gui(update_data)

    def command_select(self, data):
        """Command the model to select a single hut and the view to update.

        :param data: dictionary containing the details about the selection
        """
        index = data['which']
        _, all_selected = self._model.get_selected()
        update_data = {}
        if index not in all_selected:
            update_data.update(self._model.add_to_selected(index))
        else:
            update_data.update(self._model.remove_from_selected(index))
        self._view.update_gui(update_data)

    def command_select_multi(self, data):
        """Command the model to select a group of huts and the view to update.

        :param data: dictionary containing the details about the selection
        """
        indexes = data['which']
        update_data = {}
        if data['type'] == 'select':
            for index in indexes:
                update_data.update(self._model.add_to_selected(index))
        elif data['type'] == 'deselect':
            for index in indexes:
                update_data.update(self._model.remove_from_selected(index))
        self._view.update_gui(update_data)

    def command_select_all(self, data):
        """Command the model to select all huts and the view to update.

        :param data: dictionary containing the details about the selection
        """
        update_data = {}
        if data['which'] == 'displayed':
            update_data.update(self._model.select_all())
        elif data['which'] == 'selected':
            update_data.update(self._model.clear_selected())
        self._view.update_gui(update_data)

    def command_select_window(self, data):
        """Command the model to select all huts in a window and the view to update.

        :param data: dictionary containing the details about the selection
        """
        indexes = data['which']
        lat_min, lat_max, lon_min, lon_max = data['window']
        update_data = {}
        for index in indexes:
            is_in_window = self._model.check_in_window(index, lat_min, lat_max, lon_min, lon_max)
            if data['type'] == 'select' and is_in_window:
                update_data.update(self._model.add_to_selected(index))
            if (data['type'] == 'select only' and not is_in_window) or (data['type'] == 'deselect' and is_in_window):
                update_data.update(self._model.remove_from_selected(index))
        self._view.update_gui(update_data)

    def command_update_results(self, data):
        """
        Command the model to retrieve the data about the free beds in the huts and the view to update.

        Further retrieve attempts are disabled and the view is commanded to show a waiting message.
        The retrieve of data happens in a separate thread.

        :param data: dictionary containing the details about the data retrieval
        """
        if not self._model.is_retrieve_enabled():
            return
        update_data = {}
        update_data.update(self._model.enable_retrieve(False))
        self._view.update_gui(update_data)
        if data['which'] == 'displayed':
            self._model.update_results_for_displayed(
                self._show_waiting_message_huts,
                self._update_waiting_message_huts,
                self._update_gui_after_retrieve)
        elif data['which'] == 'selected':
            self._model.update_results_for_selected(
                self._show_waiting_message_huts,
                self._update_waiting_message_huts,
                self._update_gui_after_retrieve)
        elif data['which'] == 'huts':
            self._model.update_results_for_indexes(
                data['indexes'],
                self._view.show_waiting_message_huts,
                self._update_waiting_message_huts,
                self._update_gui_after_retrieve)

    def command_update_dates(self, data):
        """Command the model to update the reference dates interval and the view to update.

        :param data: dictionary containing the details about the reference dates interval
        """
        update_data = {}
        update_data.update(self._model.update_dates(data['request_date'], data['number_days']))
        self._view.update_gui(update_data)

    def command_update_reference_location(self, data):
        """Command the model to update the reference location and the view to update.

        :param data: dictionary containing the details about the reference location
        """
        update_data = {}
        if data['which'] == 'hut':
            update_data.update(self._model.set_reference_location_from_hut(data['index']))
        elif data['which'] == 'latlon':
            update_data.update(self._model.set_reference_location(data['lat'], data['lon']))
        self._view.update_gui(update_data)

    def command_language(self, lang):
        """Command the i18n module to set a new current language.

        :param lang: integer defining the new current language
        """
        i18n.set_language(lang)
        self._update_columns_width()
        update_data = {'language': None}
        update_data.update(self._model.sort_displayed())
        update_data.update(self._model.sort_selected())
        self._view.update_gui(update_data)

    def command_open_hut_page(self, data):
        """Command the default browser to open the hut web page.

        :param data: dictionary containing the details about the hut
        """
        index = data['which']
        web_request.open_hut_page(index)

    def command_open_table_view(self, parent=None):
        """Open a new table view.

        :param parent: the parent of the new table view (if None: makes the new view the default one)
        """
        table_view = HutsTableView(controller=self, parent=parent)
        if parent is None:
            if self._view is not None:
                self._view.close()
            self._view = table_view
        table_view.update_gui(self._get_all_update_data())
        self._update_columns_width()
        table_view.show()

    def command_open_map_view(self, parent=None):
        """Open a new map view.

        :param parent: the parent of the new map view (if None: makes the new view the default one)
        """
        map_view = HutsMapView(controller=self, parent=parent)
        if parent is None:
            if self._view is not None:
                self._view.close()
            self._view = map_view
        map_view.update_gui(self._get_all_update_data())
        map_view.show()

    def command_open_info_frame(self, index, parent):
        """Open a detailed info frame for a hut.

        :param index: index of the hut
        :param parent: the parent view of the detailed info frame
        """
        info_frame = DetailedInfoView(index=index, hut_info=self._model.get_hut_info(index),
                                      controller=self, parent=parent)
        info_frame.update_gui(self._get_all_update_data())
        info_frame.show()

    def command_open_selected_frame(self, parent):
        """Open an info frame for the selected huts.

        :param parent: the parent view of the detailed info frame
        """
        selected_frame = SelectedInfoView(controller=self, parent=parent)
        selected_frame.update_gui(self._get_all_update_data())
        selected_frame.show()

    def command_open_about_dialog(self, parent):
        """Open the about-dialog.

        :param parent: the parent view of the about-dialog
        """
        about_info = config.ABOUT
        if about_info is None:
            config.errors.append({'type': 'Configuration Error',
                                  'message': 'ABOUT information missing from configuration file'})
            return
        about_dialog = AboutDialog(parent=parent, dialog_info=about_info)
        about_dialog.show_modal()

    def command_open_warnings_frame(self, parent):
        """Open a developer info frame with information about warnings.

        :param parent: the parent view of the developer info frame
        """
        warnings = []
        self._add_to_developer_info(warnings, self._model.hut_warnings, 'Hut')
        self._command_open_developer_frame(parent, warnings, 'warning')

    def command_open_errors_frame(self, parent):
        """Open a developer info frame with information about errors.

        :param parent: the parent view of the developer info frame
        """
        errors = []
        self._add_to_developer_info(errors, self._model.hut_errors, 'Hut')
        self._add_to_developer_info(errors, self._model.errors, 'Model')
        self._add_to_developer_info(errors, i18n.errors, 'I18n')
        self._add_to_developer_info(errors, map_tools.errors, 'Map')
        self._add_to_developer_info(errors, config.errors, 'Config')
        self._add_to_developer_info(errors, web_request.errors, 'Web')
        self._add_to_developer_info(errors, view.errors, 'View')
        self._command_open_developer_frame(parent, errors, 'error')

    def command_search_for_updates(self):
        """Command the web_request module to search for application updates."""
        if not self._model.is_retrieve_enabled():
            return

        update_data = {}
        update_data.update(self._model.enable_retrieve(False))
        self._view.update_gui(update_data)

        self._temp_folder_for_updates = tempfile.mkdtemp()

        web_request.search_for_updates(
            self._temp_folder_for_updates,
            self._show_waiting_message_updates,
            self._update_waiting_message_updates,
            self._update_gui_after_updates)

    def command_open_update_dialog(self, parent, all_updates, update_cancelled):
        """Open a dialog for the application updates.

        :param parent: the parent view of the update dialog
        :param all_updates: dictionary containing the information about the available updates
        :param update_cancelled: flag which indicate if the update has been cancelled by the user
        """

        if not update_cancelled:

            # Show the update dialog
            available_updates = {}
            for _, values in all_updates.items():
                available_updates.update(values)
            with UpdateDialog(parent=parent, available_updates=available_updates) as update_dialog:
                result = update_dialog.show_modal()
                updates = update_dialog.approved_updates
    
            # Process the user inputs and apply the required updates
            if result and updates:
                for filename, update_path in updates.items():
                    if filename in all_updates['data_files']:
                        shutil.copy(update_path, str(config.ASSETS_PATH_DATA / filename))
                    elif filename in all_updates['tiles']:
                        dest_file = str(config.ASSETS_PATH_TILES / filename)
                        config.ASSETS_PATH_TILES.mkdir(parents=True, exist_ok=True)
                        shutil.copy(update_path, dest_file)
                        tarfile.open(dest_file).extractall(config.ASSETS_PATH_TILES)
                        os.remove(dest_file)

                # Reload the configuration and data files and reconfigure the modules
                config.load()
                i18n.configure()
                map_tools.configure()
                web_request.configure()
    
                update_data = {}
                update_data.update({'config': None})
                update_data.update(self._model.reload_huts_data())
                self._view.update_gui(update_data)
                self._update_columns_width()

        update_data = {}
        update_data.update(self._model.enable_retrieve(True))
        self._view.update_gui(update_data)

        shutil.rmtree(self._temp_folder_for_updates)
        self._temp_folder_for_updates = None

    def command_preference_gui(self, gui_type):
        """Select a gui type in the preferences settings.

        :param gui_type: the gui type to select in the preferences (string)
        """
        config.GUI = gui_type

    def command_preference_view(self, view_type):
        """Select a view type in the preferences settings.

        :param view_type: the view type to select in the preferences (string)
        """
        config.VIEW = view_type

    def _command_open_developer_frame(self, parent, developer_info, info_type):
        """Open a developer info frame.

        :param parent: the parent view of the developer info frame
        :param developer_info: developer info to be displayed
        :param info_type: type of developer info (warnings or errors)
        """
        developer_frame = DeveloperInfoView(parent=parent, info_type=info_type)
        developer_frame.update_gui({'developer_info': developer_info,
                                    'language': None})
        developer_frame.show()

    @staticmethod
    def _add_to_developer_info(info_list, info_dict, info_string):
        """Add the developer information from a dictionary to a list, for display to user.

        :param info_list: list where the developer information has to be added
        :param info_dict: dictionary from where the developer information is retrieved
        :param info_string: string defining the source of the information
        """
        for index, view_error in enumerate(info_dict):
            info_list.append({
                'name': info_string + ' #' + str(index),
                'type': view_error['type'],
                'message': view_error['message']
            })

    def _update_gui_after_retrieve(self):
        """
        Perform the operations required after the data about the free beds in the huts have been retrieved.

        The data retrieval is enabled again and the view is commanded to update.
        This method executes in a secondary thread.
        """
        update_data = {}
        update_data.update(self._model.enable_retrieve(True))
        update_data.update(self._model.get_all_data_after_retrieve())
        self._view.update_gui(update_data)

    def _update_gui_after_updates(self, all_updates, update_cancelled):
        """
        Command the view to update after the search for updates is complete.

        This method executes in a secondary thread.
        
        :param all_updates: dictionary containing the information about the available updates
        :param update_cancelled: flag which indicate if the update has been cancelled by the user
        """
        self._view.post_after_updates_event(all_updates, update_cancelled)

    def _update_columns_width(self):
        """Command the view to update the columns width of the table view."""
        update_data = {}
        update_data.update(self._model.get_all_huts())
        update_data.update({'columns_width': None})
        self._view.update_gui(update_data)
        self._view.update_gui(self._model.get_displayed_selected_huts())

    def _show_waiting_message_huts(self, cancel_function, outstanding):
        """Command the view to show the waiting message.

        :param cancel_function: the function to be executed if the user selects cancel
        :param outstanding: the number of outstanding huts for which data have to be retrieved
        """
        self._view.show_waiting_message_huts(cancel_function, outstanding)

    def _update_waiting_message_huts(self, outstanding):
        """
        Command the view to update or close the waiting message.

        This method executes in a secondary thread.

        :param outstanding: the number of outstanding huts for which data have to be retrieved
        """
        if outstanding > 0:
            self._view.update_waiting_message_huts(outstanding)
        else:
            self._view.close_waiting_message()

    def _show_waiting_message_updates(self, cancel_function, message_id):
        """Command the view to show the waiting message.

        :param cancel_function: the function to be executed if the user selects cancel
        :param message_id: id of the message to display (string)
        """
        self._view.show_waiting_message_updates(cancel_function, message_id)

    def _update_waiting_message_updates(self, message_id):
        """
        Command the view to update or close the waiting message.

        This method executes in a secondary thread.

        :param message_id: id of the message to display (string)
        """
        if message_id is not None:
            self._view.update_waiting_message_updates(message_id)
        else:
            self._view.close_waiting_message()

    def _get_all_update_data(self):
        """Get the dictionary of all update data to be sent to a newly-created view.

        :return: the dictionary of all update data
        """
        update_data = self._model.get_all_data()
        update_data['language'] = None
        update_data['config'] = None
        return update_data
