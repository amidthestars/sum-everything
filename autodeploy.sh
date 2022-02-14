cd "/home/ubuntu"
git pull
chmod +x autodeploy.sh
tmux new-session -d -n killall
tmux send-keys -t killall "sudo fuser -k 443/tcp" Enter
sleep 1
tmux kill-server
sleep 1
tmux new-session -d -n webserver
tmux send-keys -t tf-serving "cd /home/ubuntu/" Enter
tmux send-keys -t tf-serving "sudo gunicorn --worker-class eventlet -w 2 main:app --bind=0.0.0.0:443" Enter