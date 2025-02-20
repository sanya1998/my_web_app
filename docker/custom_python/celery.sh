#!/bin/bash

if [[ "${1}" == "worker" ]]; then
  celery --app app.resources.celery_:celery worker --loglevel=INFO --pool=solo
elif [[ "$1" == "flower" ]]; then
  celery --app app.resources.celery_:celery flower
fi
