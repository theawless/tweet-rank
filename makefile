install:
	pip3 install --user --upgrade pip
	pip3 install --user --upgrade pymongo autopep8 tqdm
	pip3 install --user --upgrade twarc

	pip3 install --user --upgrade networkx matplotlib scipy scikit-learn
	pip3 install --user --upgrade nltk
	python3 -c "import nltk; nltk.download('stopwords')"
	python3 -c "import nltk; nltk.download('punkt')"

load_sample:
	mongoimport data/sample-tweets.json --collection full_tweets --db vegas

assemble:
	python3 -m fetch.assemble
	mongo vegas --eval 'db.tweets.createIndex({"timestamp_ms" : 1})'
	mongo vegas --eval 'db.tweets.createIndex({"hour" : 1})'

download:
	python3 -m fetch.download

docs:
	python3 -m fetch.docs

urls:
	python3 -m fetch.urls

main:
	python3 -m network.main

tweet_top_terms:
	python3 -m stats.stuff tweet_top_terms

annotate:
	python3 -m fetch.annotate

codestyle:
	autopep8 . --recursive --in-place --verbose --max-line-length 120
