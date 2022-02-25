pretty:
	autopep8 --global-config .ci/flake8.cfg --max-line-length 100 --in-place --recursive -a .
	npx prettier --config .ci/.prettierrc --write .

tests:
	./style.sh
	./unittests.sh

clean:
	rm -rf __pycache__ .pytest_cache

stackup:
	gunicorn --worker-class eventlet -w 1 main:app