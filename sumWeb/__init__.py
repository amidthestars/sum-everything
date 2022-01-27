'''
Ideas:
	- If file empty & errmsg showing do nothing? (i.e don't refresh)
'''
import os

from flask import Flask, render_template, flash, request, redirect, url_for

from werkzeug.utils import secure_filename

# For file uploads
ALLOWED_EXTENSIONS = {'txt'}

# Flask instance; allows for instance (database) outside folder
app = Flask(__name__, instance_relative_config=True)

app.secret_key = os.urandom(12)

@app.route('/', methods = ['GET', 'POST'])
def index():
	if request.method=='POST':
		# Quick & dirty file upload
		file = request.files["txtFile"]

		if file.filename == '':
			msg = "No file selected OR incorrect file type (need .txt)"

			return render_template("index.html", noFileErr=msg)

		if file and checkFile(file.filename):
			filename = secure_filename(file.filename)

			return render_template("index.html", 
				message="File Uploaded!",
				file_name=filename
			)

	return render_template("index.html", )


# ***** CHECK THE 2nd COMMENT & MAKE SURE *****
# Taken from: https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
# I don't think this is needed as the HTML tag requires it to be .txt
def checkFile(file):
	return '.' in file and file.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run()