#!/bin/bash
alembic upgrade head
python3 manage.py runserver