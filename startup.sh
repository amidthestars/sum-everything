#!/bin/bash

cd /home/ubuntu
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y

tmux new -s killall -d
tmux send-keys -t killall "sudo fuser -k 3000/tcp" Enter
sleep 1
tmux kill-session -t killall
tmux kill-session -t tf-serving
tmux kill-session -t webhook
sleep 1

tmux new -s tf-serving -d
tmux send-keys -t tf-serving "cd /home/ubuntu/" Enter
tmux send-keys -t tf-serving "./tensorflow_model_server --rest_api_port=3000 --model_config_file='gs://sum-exported/models.config' --model_config_file_poll_wait_seconds=60 --rest_api_timeout_in_ms=3000000" Enter
tmux new -s webhook -d
tmux send-keys -t webhook "cd /home/ubuntu/sum-everything" Enter
tmux send-keys -t webhook "chmod +x autodeploy.sh" Enter
tmux send-keys -t webhook "./autodeploy.sh" Enter
tmux send-keys -t webhook "webhook -hooks autodeploy.json -verbose" Enter