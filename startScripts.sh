screen -dmS watch bash -c 'python /home/adam/webBarron/watchdog.py' &&
sleep 30 &&
screen -dmS heat1 bash -c 'python /home/adam/webBarron/pidIncubate.py' &&
sleep 60 &&
screen -dmS heat2 bash -c 'python /home/adam/webBarron/pidIncubate.py' &&
sleep 60 &&
screen -dmS heat3 bash -c 'python /home/adam/webBarron/pidIncubate.py' &&
sleep 5 &&
screen -dmS finished bash -c 'ping 192.168.4.0'
