import locale
from functools import cmp_to_key

import wx
from wx.lib.mixins import listctrl as listmix

from app.wx_helpers import resource_path


class VirtualList(wx.ListCtrl, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.BORDER_NONE)

        size = (16, 16)

        self.il = wx.ImageList(*size)

        down = wx.Image(resource_path('icons/Down.png'), wx.BITMAP_TYPE_ANY)
        down = down.Scale(*size)
        up = wx.Image(resource_path('icons/Up.png'), wx.BITMAP_TYPE_ANY)
        up = up.Scale(*size)

        self.sm_up = self.il.Add(wx.Bitmap(up))
        self.sm_dn = self.il.Add(wx.Bitmap(down))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        # building the columns
        titles = [('SearchMatch Title', 200),
                  ('Date Created', 120),
                  ('Date Modified', 120),
                  ('Last Accessed', 120),
                  ('File Type', 80),
                  ('File Size', 80),
                  ('File Path', 250),
                  ]

        for no, (titles, width) in enumerate(titles):
            self.InsertColumn(no, titles, width=width)

        self.itemDataMap = {}
        self.itemIndexMap = []
        self.SetItemCount(0)
        listmix.ColumnSorterMixin.__init__(self, 8)

        # sort by genre (column 2), A->Z ascending order (1)
        self.SortListItems(0, 1)

    def add_data(self, data: dict[int, list[str]]):
        self.DeleteAllItems()
        self.itemDataMap = {k: [str(x) for x in v] for k, v in data.items()}
        self.itemIndexMap = list(data.keys())
        self.SetItemCount(len(data))
        self.Refresh()

    def OnGetItemText(self, item, col):
        index = self.itemIndexMap[item]
        return self.itemDataMap[index][col]

    def SortItems(self, sorter=None):
        items = list(self.itemDataMap.keys())
        items.sort(key=cmp_to_key(sorter))
        self.itemIndexMap = items

        # redraw the list
        self.Refresh()

    def GetListCtrl(self):
        return self

    def GetSortImages(self):
        return self.sm_dn, self.sm_up

    def OnGetItemColumnImage(self, item, col):
        return -1

    def OnGetItemImage(self, item):
        return -1

    def GetColumnSorter(self):
        """Returns a callable object to be used for comparing column values when sorting."""
        return self.altered_column_sorter

    def altered_column_sorter(self, key1, key2):
        def cmp(a, b):
            return (a > b) - (a < b)

        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]

        try:
            item1 = float(item1)
            item2 = float(item2)
            cmpVal = cmp(item1, item2)

        except ValueError:
            cmpVal = locale.strcoll(item1.lower(), item2.lower())

        # If the items are equal then pick something else to make the sort value unique
        if cmpVal == 0:
            cmpVal = cmp(*self.GetSecondarySortValues(col, key1, key2))

        if ascending:
            return cmpVal
        else:
            return -cmpVal

    def get_selected_items(self):
        """
        Gets the selected items for the list control.
        Selection is returned as a list of selected indices,
        low to high.
        """
        selection = []

        # start at -1 to get the first selected item
        current = -1
        while True:
            next_one = self.GetNextSelected(current)
            if next_one == -1:
                return selection

            selection.append(next_one)
            current = next_one

    def GetNextSelected(self, current):
        """Returns next selected item, or -1 when no more"""
        return self.GetNextItem(current,
                                wx.LIST_NEXT_ALL,
                                wx.LIST_STATE_SELECTED)