# -*- mode: python -*-
import os

block_cipher = None
base = r'C:\Users\ukaxa036\Documents\PycharmProjects\FileFInder\app'
# base = os.path.dirname(__file__)

a = Analysis(['app/gui.py'],
             pathex=[base],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.datas += [('logo.ico', fr'{base}\icons\logo.ico', 'DATA'), ]

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          Tree(fr'{base}\icons', prefix=r'icons\\'),
          a.zipfiles,
          a.datas,
          name='Data Hunter',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)

