#!/usr/bin/python


import wx
import wx.lib.imagebrowser as ib
import random


class Toolframe(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, (-1, -1), wx.Size(810, 100))

        self.SetBackgroundColour('white')

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.Bind(wx.EVT_BUTTON, self.on_btn_press, id=1)

        self.tc1 = wx.TextCtrl(self)
        font = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.tc1.SetFont(font)
        sizer.Add(wx.Button(self, 1, 'Search Files'), 1, wx.EXPAND)
        sizer.Add(self.tc1, 4, flag=wx.EXPAND)

        self.SetSizer(sizer)
        self.Centre()

    def on_btn_press(self, event):
        s = f'{event}'
        self.tc1.SetValue(s)


class MyApp(wx.App):
    def OnInit(self):
        frame = Toolframe(None, -1, 'File Finder')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


app = MyApp(0)
app.MainLoop()
