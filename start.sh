# !/usr/bin/fish

cd /home/pi/gpad-servo

source .venv/bin/activate.fish

git pull

sudo ./.venv/bin/python stream.py