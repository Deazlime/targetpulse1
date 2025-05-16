@echo off
set PYTHONPATH=%PYTHONPATH%;%CD%
set DJANGO_SETTINGS_MODULE=targetpulse.settings
python -m daphne -b 0.0.0.0 -p 8000 targetpulse.asgi:application 