#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# ⚠️ TEMPORARY: Reset broken homework migration state
python manage.py migrate homework zero --fake || true

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput