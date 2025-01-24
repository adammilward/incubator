screen -dmS watch bash -c 'python /home/adam/python/watchdog.py' &&
sleep 5 &&
screen -dmS heat5 bash -c 'python /home/adam/python/incubate.py' &&
sleep 10 &&
screen -dmS heat15 bash -c 'python /home/adam/python/incubate.py'
