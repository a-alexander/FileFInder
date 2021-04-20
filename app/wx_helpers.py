import os
import sys
from typing import Optional, Callable

import wx


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def scale_image(image_path, size):
    img = wx.Image(resource_path(image_path), wx.BITMAP_TYPE_ANY)
    w = img.GetWidth()
    h = img.GetHeight()

    if w > h:
        new_w = size
        new_h = int(size * h / w)
    else:
        new_h = size
        new_w = int(size * w / h)

    img = img.Scale(new_w, new_h, quality=wx.IMAGE_QUALITY_HIGH)
    return img


def make_button(frame: wx.Frame, path_to_button: str, size: int, but_id: int = wx.ID_ANY,
                tooltip: str = '', func=None) -> wx.BitmapButton:
    but_scaled = scale_image(path_to_button, size)
    but_bmp = wx.Bitmap(but_scaled, wx.BITMAP_TYPE_ANY)
    btn = wx.BitmapButton(frame, id=but_id, bitmap=but_bmp,
                          size=(but_bmp.GetWidth() + 15, but_bmp.GetHeight() + 15))

    btn.SetToolTip(wx.ToolTip(tooltip))
    if func:
        btn.Bind(wx.EVT_BUTTON, func)
    return btn


def create_text_control_box(frame: wx.Frame, handler: Callable, label_text: Optional[str] = None) -> tuple[
    wx.TextCtrl, wx.BoxSizer]:
    """"Creates a box with a text ctrl inside and staitc text above"""
    box = wx.StaticBoxSizer(wx.VERTICAL, frame, label=label_text)
    # search_st = wx.StaticText(frame, label=label_text)
    # box.Add(search_st, 0, wx.ALL, border=5)
    input_control = wx.TextCtrl(frame)
    input_control.Bind(wx.EVT_KEY_DOWN, handler)
    box.Add(input_control, flag=wx.EXPAND | wx.ALL, border=5)
    return input_control, box


def setup_menu(frame: wx.Frame):
    menubar = wx.MenuBar()
    file = wx.Menu()
    help = wx.Menu()
    menu_quit = file.Append(22, '&Quit', 'Exit Calculator')
    menubar.Append(file, '&File')
    help.Append(23, '&Get Help')
    menubar.Append(help, '&Help')
    frame.SetMenuBar(menubar)
    frame.Bind(wx.EVT_MENU, frame.on_close_event, menu_quit)
