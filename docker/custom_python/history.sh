#!/bin/bash
python3 -m scripts.create_rmq_bindings
python3 manage.py run-history-consumer