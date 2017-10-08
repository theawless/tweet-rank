install:
	pip3 install --upgrade pip
	pip3 install --user pymongo
	pip3 install --user autopep8
	pip3 install --user nltk networkx matplotlib scipy scikit-learn
	python3 -c "import nltk; nltk.download('stopwords')"
	python3 -c "import nltk; nltk.download('punkt')"

setup:
	mongoimport data/tweets.json  --collection tweets --db vegas
	python3 mongo.py
	mongo vegas --eval 'db.tweets.createIndex({"timestamp_ms" : 1})'

main:
	python3 main.py

codestyle:
	autopep8 . --recursive --in-place --verbose --max-line-length 120
