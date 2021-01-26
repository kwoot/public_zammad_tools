#!/bin/bash

cd /home/jeroen/Projecten/Zammad

export DISPLAY=:2.0


export DISPLAY

. venv/bin/activate

python3 ./weekly.py
