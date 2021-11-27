#!/bin/bash
sudo chmod -R 777 /session
/opt/bin/entry_point.sh &
sleep 10s
python3 /opt/bin/MqttFindMyPhone.py