serve:
	devd -ol .

push:
	-git branch -D gh-pages
	git checkout -b gh-pages
	git push -f -u origin gh-pages
	git checkout master

lint:
	jshint bracket.js

update:
	wget http://projects.fivethirtyeight.com/march-madness-api/2016/fivethirtyeight_ncaa_forecasts.csv -O natesilver.csv

.PHONY: serve push
