#!/bin/bash

pip install -r /app/requirement.txt
python /app/manage.py makemigrations
python /app/manage.py migrate

