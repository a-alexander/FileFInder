# -*- mode: python -*-

block_cipher = None


a = Analysis(['RandomNominator.PY'],
             pathex=['C:\\Users\\paperspace\\Dropbox\\Python\\Random Nominator'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.datas += [('logo2.ico','C:\Users\paperspace\Dropbox\Python\Random Nominator\logo2.ico' , 'DATA'),
		('Logo.png', 'C:\Users\paperspace\Dropbox\Python\Random Nominator\Logo.png', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Random Nominator',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='logo2.ico')
