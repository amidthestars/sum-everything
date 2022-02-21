#!/bin/bash

cd "/home/ubuntu/sum-everything"
git reset --hard
git checkout web_page
git pull --force
mv startup.sh /home/ubuntu/startup.sh
chmod +x /home/ubuntu/startup.sh
chmod +x autodeploy.sh
sudo -H pip3 install -U -r requirements.txt

tmux new -s killall -d
tmux send-keys -t killall "sudo fuser -k 80/tcp" Enter
sleep 1
tmux kill-session -t killall
tmux kill-session -t webserver
sleep 1

tmux new -s webserver -d
tmux send-keys -t webserver "cd /home/ubuntu/sum-everything" Enter
tmux send-keys -t webserver "sudo gunicorn --worker-class eventlet -w 1 main:app --bind=0.0.0.0:80" Enter