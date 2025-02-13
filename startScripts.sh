screen -dmS watch bash -c 'python /home/adam/python/watchdog.py' &&
screen -dmS heat0 bash -c 'python /home/adam/python/incubate.py' &&
sleep 60 &&
screen -dmS heat1 bash -c 'python /home/adam/python/incubate.py' &&
sleep 30 &&
screen -dmS heat2 bash -c 'python /home/adam/python/incubate.py' &&
sleep 30 &&
screen -dmS heat3 bash -c 'python /home/adam/python/incubate.py' &&
sleep 30 &&
screen -dmS heat4 bash -c 'python /home/adam/python/incubate.py' &&
sleep 30 &&
screen -dmS heat5 bash -c 'python /home/adam/python/incubate.py' &&
sleep 30 &&
screen -dmS heat6 bash -c 'python /home/adam/python/incubate.py' &&
sleep 30 &&
screen -dmS heat7 bash -c 'python /home/adam/python/incubate.py' &&
sleep 30 &&
screen -dmS heat8 bash -c 'python /home/adam/python/incubate.py' &&
sleep 30 &&
screen -dmS heat9 bash -c 'python /home/adam/python/incubate.py' &&
sleep 5 &&
screen -dmS finished bash -c 'ping 192.168.4.0'
