@echo off
python -m celery -A targetpulse worker -l info -P eventlet 