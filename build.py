import PyInstaller.__main__
import shutil
import os

# Очистка предыдущих сборок
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# Параметры сборки
params = [
    'app.py',               # Главный файл приложения
    '--onefile',            # Собрать в один EXE-файл
    '--windowed',           # Для GUI-приложений (без консоли)
    '--icon=app.ico', 
    '--name=TripManager'
]

# Запуск сборки
PyInstaller.__main__.run(params)