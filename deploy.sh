python bracket.py

rsync -avuz -e ssh --safe-links \
--exclude ".git" \
. llimllib@billmill.org:~/static/ncaa-bracket-randomizer/
