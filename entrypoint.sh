#!/bin/bash

#python /app/manage.py makemigrations
#python /app/manage.py migrate

/etc/init.d/nginx start  &
uwsgi --ini /app/uwsgi.ini
