#!/bin/bash

cd /home/ubuntu
tmux new-session -d -n killall
tmux send-keys -t killall "sudo fuser -k 3000/tcp" Enter
sleep 1
tmux kill-session -t tf-serving
sleep 1
tmux new-session -d -n tf-serving
tmux send-keys -t tf-serving "cd /home/ubuntu/" Enter
tmux send-keys -t tf-serving "./tensorflow_model_server --rest_api_port=3000 --model_config_file='gs://sum-exported/models.config' --model_config_file_poll_wait_seconds=60 --rest_api_timeout_in_ms=3000000" Enter