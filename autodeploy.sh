#!/bin/bash

cd "/home/ubuntu/sum-everything"
git reset --hard
git checkout web_page
git pull --force
mv startup.sh /home/ubuntu/startup.sh
chmod +x /home/ubuntu/startup.sh
chmod +x autodeploy.sh
pip3 install -U -r requrements.txt

tmux new -s killall -d
tmux send-keys -t killall "sudo fuser -k 443/tcp" Enter
sleep 1
tmux kill-session -t webserver
sleep 1

tmux new -s webserver -d
tmux send-keys -t webserver "cd /home/ubuntu/" Enter
tmux send-keys -t webserver "sudo gunicorn --worker-class eventlet -w 2 main:app --bind=0.0.0.0:443" Enter