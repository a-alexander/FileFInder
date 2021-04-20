import os
import sys
from typing import Optional, Callable
from PIL import Image, ImageFilter

import wx


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    print(f'{relative_path=}')
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

    path = os.path.join(base_path, relative_path)
    print(f'{path=}')
    return path


def wxImage_from_pil(pilImg):

    wxImg = wx.Image(*pilImg.size)  # Always created with no transparency plane.
    pilHasAlpha = pilImg.mode[-1] == 'A'

    # First extract just the RGB data from the data string and insert it into wx.Image .
    pilRgbStr = pilImg.convert('RGB').tobytes()
    wxImg.SetData(pilRgbStr)

    if pilHasAlpha:
        pilImgStr = pilImg.convert('RGBA').tobytes()  # Harmless if original image mode is already "RGBA".

        # Now, extract just the alpha data and insert it.
        pilAlphaStr = pilImgStr[3::4]  # start at byte index 3 with a stride (byte skip) of 4.
        wxImg.SetAlpha(pilAlphaStr)

    return wxImg


def scale_image(image_path, size):
    img = Image.open(resource_path(image_path))

    img = img.filter(ImageFilter.GaussianBlur(6))

    W, H = img.size

    if W > H:
        NewW = size

        NewH = int(size * H / W)
    else:
        NewH = size
        NewW = int(size * W / H)

    img = img.resize((NewH, NewW))

    wx_img = wxImage_from_pil(img)

    return wx_img


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
    """"Creates a box with a text ctrl inside and static text above"""
    box = wx.StaticBoxSizer(wx.VERTICAL, frame, label=label_text)
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
