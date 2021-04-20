import datetime
import os
import subprocess
import sys
from concurrent import futures
from time import time

import wx

from app.WXVirtualList import VirtualList
from app.wx_helpers import resource_path, make_button, setup_menu, create_text_control_box
from app.wx_decorators import submit_to_pool_executor, wx_call_after
from app.models import ProjectArea, available_paths, get_file_matches, zip_up_files
from app.db import session
from app.uploader import upload_file

thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)


class GUI(wx.Frame):
    def __init__(self, parent, id, title):
        self.first_run = True
        wx.Frame.__init__(self, parent, id, title, (-1, -1), wx.Size(1100, 800))

        self.SetBackgroundColour('white')
        setup_menu(self)
        self.sb = self.CreateStatusBar()
        self.project_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.results_list_ctrl = None
        self.search_paths_list = None
        self.key_phrase_input_box = None
        self.file_extension_input = None
        self.project_sizer.Add(self.setup_primary_column(), 2, flag=wx.TOP | wx.LEFT | wx.RIGHT, border=10)
        self.project_sizer.Add(self.setup_file_results_area(), 6, flag=wx.EXPAND | wx.LEFT | wx.TOP, border=10)
        self.available_paths: list[ProjectArea] = available_paths()
        self.refresh_search_paths_list()
        self.SetSizer(self.project_sizer)
        self.Centre()
        self.Maximize()

        self.selected_match = None
        self.selected_path = None
        self.dialog = None
        self.data = {}

    def setup_primary_column(self):
        col1 = wx.BoxSizer(wx.VERTICAL)

        path_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label='1. Add a directory to search')
        add_folder_button = make_button(self, resource_path(r'icons\add.png'), 60,
                                        tooltip='Add a new location to the saved search areas',
                                        func=self.add_search_path)
        path_sizer.Add(add_folder_button, 0, wx.ALL, border=5)
        col1.Add(path_sizer)

        self.search_paths_sizer = wx.BoxSizer(wx.VERTICAL)
        self.search_paths_list = wx.ListCtrl(self, -1, size=(450, 100),
                                             style=wx.LC_REPORT
                                                   | wx.BORDER_NONE
                                                   | wx.LC_SORT_ASCENDING)

        self.search_paths_list.InsertColumn(0, 'Search Directory', width=300)
        self.search_paths_list.InsertColumn(1, 'Archived', width=150)
        self.search_paths_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.catch_selected_path)
        self.search_paths_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.remove_selected_path)

        self.search_paths_sizer.Add(wx.StaticText(self, label='[Double click path to remove]'), 0, wx.ALL, border=5)
        self.search_paths_sizer.Add(self.search_paths_list, 0, wx.ALL, border=5)
        col1.Add(self.search_paths_sizer)
        self.key_phrase_input_box, search_box = create_text_control_box(self, self.catch_key_press,
                                                                        "2. Enter some part of File Name (Optional)")
        self.file_extension_input, extension_box = create_text_control_box(self, self.catch_key_press,
                                                                           "3. Enter the File Extension (Optional)")

        col1.Add(search_box, 0, wx.ALL, border=0)
        col1.Add(extension_box, 0, wx.ALL, border=0)

        search_button = make_button(self, resource_path(r'icons/search.png'), 60,
                                    tooltip='Search all your paths.', func=self.initiate_search_process)
        col1.Add(search_button, 0, wx.ALL, border=10)
        zip_button = make_button(self, resource_path(r'icons\send_to.png'), 60,
                                 tooltip='Compress results into a neat zip file.', func=self.upload_matches_to_cloud)
        col1.Add(zip_button, 0, wx.ALL, border=10)

        return col1

    def setup_file_results_area(self):
        """Creates the search results area with all the matching files listed out"""
        col2 = wx.BoxSizer(wx.VERTICAL)
        col2.Add(wx.StaticText(self, label='Search results: '))

        # tee up the list_ctrl mixin
        self.results_list_ctrl = VirtualList(self)

        # line below enables double clicking of items in the list
        self.results_list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.open_search_match_file)
        self.results_list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.catch_selected_match)

        col2.Add(self.results_list_ctrl, 1, wx.EXPAND | wx.TOP, 3)
        col2.Add((-1, 10))
        return col2

    def refresh_search_paths_list(self):
        self.search_paths_list.DeleteAllItems()

        for path in self.available_paths:
            index = self.search_paths_list.InsertItem(0, path.path)
            self.search_paths_list.SetItem(index, 1, str(path.last_archived_str))
        self.search_paths_sizer.ShowItems(show=len(self.available_paths))
        self.Layout()

    def add_search_path(self, event):
        some_place_in_folder = self.file_selector_popup('Select Search Directory')
        if not some_place_in_folder:
            return
        p = ProjectArea(path=some_place_in_folder)
        session.add(p)
        session.commit()
        self.available_paths.append(p)
        self.sb.SetStatusText(f'{some_place_in_folder} Added to search paths...')
        self.refresh_search_paths_list()
        start = time()
        self.archive_location(p)
        self.refresh_search_paths_list()
        self.sb.SetStatusText(f'{some_place_in_folder} archived in {time() - start:.1f} seconds.')

    def remove_selected_path(self, event):
        self.available_paths.remove(self.selected_path)
        self.sb.SetStatusText(f'{self.selected_path.path} Removed from search paths...')
        project_area_to_go = self.selected_path
        self.selected_path = None
        project_area_to_go.delete()
        self.refresh_search_paths_list()

    def initiate_search_process(self, event):
        """This is executed whenever the 'Search' button is clicked"""
        if not self.available_paths:
            self.sb.SetStatusText(f'No paths available...')
            return

        self.dialog = wx.BusyInfo(f"Searching your saved location for {self.key_phrase_input_box.GetValue()}...")
        self.search(self.search_phrase, self.search_extension, True)

    @wx_call_after
    def set_sb_text(self, text=''):
        self.sb.SetStatusText(text)

    @wx_call_after
    def results_box_update(self, data):
        self.results_list_ctrl.add_data(data)

    def archive_location(self, path: ProjectArea):
        path.discover_files()

    @property
    def search_phrase(self):
        return self.key_phrase_input_box.GetValue() if self.key_phrase_input_box.GetValue() != '' else None

    @property
    def search_extension(self):
        return self.file_extension_input.GetValue() if self.file_extension_input.GetValue() != '' else None

    def search(self, phrase, ext, ignore_case):
        self.set_sb_text('Searching...')
        start = time()
        self.all_matches = get_file_matches(phrase=phrase, ext=ext)

        self.data = {}

        for count, match in enumerate(self.all_matches):
            self.data[count] = [str(match.file_name),
                                str(match.created),
                                str(match.modified),
                                str(match.accessed),
                                str(match.file_type),
                                match.size,
                                str(match.path),
                                ]

        self.results_box_update(self.data)
        self.set_sb_text(f'Search complete in {time() - start:.1f} seconds. {len(self.data)} results found.')
        self.dialog = None

    def catch_key_press(self, event):
        # if main enter key (13) or numpad enter key (370) is pressed
        if event.GetKeyCode() in [13, 370]:
            self.initiate_search_process(event)
        else:
            event.Skip()

    def catch_selected_match(self, event):
        number = event.Index
        self.selected_match = event.EventObject.itemDataMap[number]

    def catch_selected_path(self, event):
        path = event.GetText()
        self.selected_path = next(p for p in self.available_paths if p.path == path)

    def upload_matches_to_cloud(self, event):
        files = [f.path for f in self.all_matches]
        now = datetime.datetime.now()
        archive_type = f'{self.search_phrase or ""}-{self.search_extension or ""}'
        zip_file_name = f'{archive_type}-{now.year}-{now.month}-{now.day}'
        archive_path = zip_up_files(files, zip_file_name)

        upload_file(archive_path, os.path.basename(archive_path))
        os.remove(archive_path)
        self.sb.SetStatusText('Results zipped up to cloud...')

    def open_search_match_file(self, event):
        for sel in self.results_list_ctrl.get_selected_items():
            filepath = self.results_list_ctrl.GetItemText(sel, 6)
            '''nice little code chunk below opens the file in file path with 
            the default program for that file extension.'''
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', filepath))
            elif os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(('xdg-open', filepath))

    def on_close_event(self, event):
        self.Close()

    def file_selector_popup(self, promptmessage):
        dlg = wx.DirDialog(
            self, message=promptmessage,
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            Dir = dlg.GetPath()
            dlg.Destroy()
            return Dir
        else:
            dlg.Destroy()
            return None


class MyApp(wx.App):
    def OnInit(self):
        frame = GUI(None, -1, 'Data Hunter')
        # frame.SetIcon(wx.Icon(resource_path('logo.ico'), wx.BITMAP_TYPE_ICO))
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


app = MyApp(0)
app.MainLoop()
