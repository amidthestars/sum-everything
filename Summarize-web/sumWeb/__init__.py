import os

from flask import Flask, render_template

def create_app(test_config=None):
	# Flask instance; allows for instance (database) outside folder
	app = Flask(__name__, instance_relative_config=True)

	@app.route('/')
	def index():
		return render_template("index.html", )

	return app