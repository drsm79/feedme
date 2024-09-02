# #! /usr/bin/env bash
cd /home/pi/feedme
source venv/bin/activate
flask --app feedme run --debug -p 3000 --host=0.0.0.0