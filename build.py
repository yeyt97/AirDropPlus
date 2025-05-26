import os
import shutil
import subprocess

def build():
    # Clean previous build
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    subprocess.run(['pybabel', 'compile', '-d', 'translations'])

    subprocess.run([
        'pyinstaller',
        '--name=AirDropPlus',
        '--icon=static/icon.ico',
        '--add-data=translations;translations',
        '--add-data=static;static',
        '--add-data=config;config',
        '--add-data=templates;templates',
        '--noconsole',
        '--hidden-import=winrt.windows.foundation.collections',
        '--clean',
        'AirDropPlus.py'
    ])

if __name__ == '__main__':
    build() 