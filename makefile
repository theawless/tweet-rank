install_common:
	pip3 install --upgrade pip
	pip3 install --user pymongo
	pip3 install --user autopep8

install_fetch: install_common
	pip3 install --user twarc

install_analyse: install_common
	pip3 install --user nltk networkx matplotlib scipy scikit-learn
	python3 -c "import nltk; nltk.download('stopwords')"
	python3 -c "import nltk; nltk.download('punkt')"

load_sample:
	mongoimport data/sample-tweets.json  --collection full_tweets --db vegas

clean:
	python3 -m fetch.clean
	mongo vegas --eval 'db.tweets.createIndex({"timestamp_ms" : 1})'

download:
	python3 -m fetch.download

graph:
	python3 -m analyse.analyse

tweet_top_terms:
	python3 -m analyse.stuff tweet_top_terms

annotate:
	python3 -m fetch.annotate 57 500 600

codestyle:
	autopep8 . --recursive --in-place --verbose --max-line-length 120
