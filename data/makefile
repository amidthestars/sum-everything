build:
	python3 gen-cnn.py
	python3 gen-scisummnet.py
	python3 gen-idt.py

clean:
	rm -rf __pycache__ __MACOSX
	rm -rf cnn cnn_stories.tgz
	rm -rf scisummnet_release1.1__20190413 scisummnet scisummnet.zip
	rm -rf hindu_indian_times_guardian_news.zip idt

spotless:
	rm -rf __pycache__ __MACOSX
	rm -rf cnn cnn_stories*
	rm -rf scisummnet_release1.1__20190413 scisummnet*
	rm -rf hindu_indian_times_guardian_news.zip idt