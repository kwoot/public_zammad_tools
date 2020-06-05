#!/bin/bash

cd /home/jeroen/Projecten/Zammad

export DISPLAY=:50.0

. venv/bin/activate

python3 ./weekly.py
