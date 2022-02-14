#!/bin/bash

cd "/home/ubuntu/sum-everything"
git reset --hard
git checkout web_page
git pull --force
mv startup.sh /home/ubuntu/startup.sh
chmod +x /home/ubuntu/startup.sh
chmod +x autodeploy.sh
tmux new-session -d -n killall
tmux send-keys -t killall "sudo fuser -k 443/tcp" Enter
sleep 1
tmux kill-session -t webserver
tmux kill-session -t webhooks
sleep 1
tmux new-session -d -n webserver
tmux send-keys -t webserver "cd /home/ubuntu/" Enter
tmux send-keys -t webserver "sudo gunicorn --worker-class eventlet -w 2 main:app --bind=0.0.0.0:443" Enter
tmux new-session -d -n webhooks
tmux send-keys -t webserver "cd /home/ubuntu/sum-everything" Enter
tmux send-keys -t webserver "webhook -hooks autodeploy.json -verbose" Enter