.PHONY: install tpu

install:
	sudo apt update
	sudo apt upgrade -y
	sudo apt autoremove -y
	sudo apt install -y python3-pip unzip python-is-python3
	sudo -H pip3 install --upgrade pip
	sudo -H pip3 install -r data/requirements.txt
	sudo -H pip3 install -r train/requirements.txt

tpu: install
	sudo -H pip3 uninstall tensorflow tensorflow-text
	sudo -H pip3 install --upgrade --force-reinstall /usr/share/tpu/*.whl
	sudo -H pip3 install --upgrade tensorflow-text-nightly==2.7.0.dev20210924


compress.datasets:
	tar -czvf datasets.tar.gz datasets