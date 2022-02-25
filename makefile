pretty:
	autopep8 --global-config .ci/flake8.cfg --max-line-length 100 --in-place --recursive -a .
	npx prettier --config .ci/.prettierrc --write .

tests:
	./style.sh
	./unittests.sh

clean:
	rm -rf __pycache__ .pytest_cache
	rm -rf datasets node_modules data

requirements:
	sudo -H pip3 install -r .ci/requirements.txt
	sudo -H pip3 install -r requirements.txt

stackup:
	gunicorn --worker-class eventlet -w 1 main:app