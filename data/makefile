build:
	python3 gen-cnn.py
	python3 gen-scisummnet.py
	python3 gen-idt.py
	python3 gen-xsum.py
	python3 gen-bbc.py
	python3 gen-dailymail.py
	python3 gen-tifu.py
	python3 gen-wiki.py

clean:
	rm -rf __pycache__ __MACOSX
	rm -rf cnn cnn_stories.tgz
	rm -rf dailymail dailymail_stories.tgz
	rm -rf scisummnet_release1.1__20190413 scisummnet scisummnet.zip
	rm -rf hindu_indian_times_guardian_news.zip idt
	rm -rf XSUM-EMNLP18-Summary-Data-Original.tar.gz bbc-summary-data
	rm -rf bbc.zip bbc
	rm -rf tifu_datasets.zip tifu
	rm -rf wikiHow.zip wikiHow

spotless:
	rm -rf __pycache__ __MACOSX
	rm -rf cnn cnn_stories*
	rm -rf dailymail dailymail_stories.tgz
	rm -rf scisummnet_release1.1__20190413 scisummnet*
	rm -rf hindu_indian_times_guardian_news.zip idt
	rm -rf XSUM-EMNLP18-Summary-Data-Original.tar.gz bbc-summary-data
	rm -rf hindu_indian_times_guardian_news.zip idt
	rm -rf bbc.zip bbc
	rm -rf XSUM-EMNLP18-Summary-Data-Original.tar.gz bbc-summary-data
	rm -rf tifu_datasets.zip tifu
	rm -rf wikiHow.zip wikiHow
