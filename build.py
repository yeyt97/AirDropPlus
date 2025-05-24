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
        '--noconsole',
        '--clean',
        'AirDropPlus.py'
    ])
    shutil.copytree('config', 'dist/AirDropPlus/config', dirs_exist_ok=True)
    shutil.copytree('static', 'dist/AirDropPlus/static', dirs_exist_ok=True)
    shutil.copytree('translations', 'dist/AirDropPlus/translations', dirs_exist_ok=True)

if __name__ == '__main__':
    build() 