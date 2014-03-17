serve:
	python -m SimpleHTTPServer

push:
	-git branch -D gh-pages
	git checkout -b gh-pages
	git push -f -u origin gh-pages
	git checkout d3version

lint:
	jshint bracket.js

.PHONY: serve push
