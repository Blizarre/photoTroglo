# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\unpackTK.py'), os.path.join(HOMEPATH,'support\\useTK.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'photosTroglo.py', os.path.join(HOMEPATH,'support\\removeTK.py')],
             pathex=['C:\\Users\\Mamour\\Documents\\programmation\\photoTroglo'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'photosTroglo.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False )
