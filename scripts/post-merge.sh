#!/bin/bash
set -e

pip install -r requirements.txt --quiet
python manage.py migrate --settings=config.settings.local --no-input
