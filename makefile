install:
	sudo apt update
	sudo apt upgrade
	sudo apt install -y python3-pip unzip
	/usr/bin/python3 -m pip install -y --upgrade pip
	sudo pip3 install -r data/requirements.txt
	sudo pip3 install -r train/requirements.txt

tpu:
	sudo apt update
	sudo apt upgrade -y
	sudo apt install -y python3-pip unzip
	/usr/bin/python3 -m pip install -y --upgrade pip
	sudo pip3 install -r data/requirements.txt
	sudo pip3 install -r train/requirements.txt
	sudo pip3 install --upgrade "cloud-tpu-profiler>=2.3.0"
	sudo pip3 install --user --upgrade -U "tensorboard>=2.3" "tensorflow>=2.3"

compress.datasets:
	tar -czvf datasets.tar.gz datasets