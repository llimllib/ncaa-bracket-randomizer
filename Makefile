serve:
	python -m SimpleHTTPServer

push:
	-git branch -D gh-pages
	git checkout -b gh-pages
	git push -f -u origin gh-pages
	git checkout master

lint:
	jshint bracket.js

update:
	wget https://raw.githubusercontent.com/fivethirtyeight/data/master/march-madness-predictions-2015/mens/bracket-00.tsv -O natesilver.tsv

.PHONY: serve push
