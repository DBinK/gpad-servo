# !/usr/bin/fish
sudo su

cd /home/pi/gpad-servo

fish

source .venv/bin/activate.fish

git pull

python stream.py