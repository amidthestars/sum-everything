install:
	sudo apt update
	sudo apt install -y python3-pip unzip
	sudo pip3 install -r data/requirements.txt
	sudo pip3 install -r train/requirements.txt

compress.datasets:
	tar -czvf datasets.tar.gz datasets