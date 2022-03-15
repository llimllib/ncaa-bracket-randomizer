# NCAA Bracket Randomizer

Generates a reasonable bracket for you, based on <a href="http://kenpom.com/">Ken Pomeroy's</a>
college basketball ratings.

For each matchup, it compares the two teams in the game, calculates the odds of the favorite
winning the game, and chooses the winner. There are three settings that determine how it
does so:

#### No randomness

Always picks the favorite

#### Some

Picks the underdog if they win twice in a row.

If team A has a 75% chance of beating team B, the program will generate two random numbers
between 0 and 100; if both of them are greater than 75, team B will advance. Otherwise,
team A will advance.

#### Lots of randomness

Picks the underdog if they win once

If team A has a 75% chance of beating team B, the program will generate a random number
between 0 and 100; if it's greater than 75, team B will advance. Otherwise,
team A will advance.

## Calculating the Odds

[This ipython notebook](https://github.com/llimllib/ncaa-bracket-randomizer/blob/master/fitting_kenpom/fitting%20kenpom.ipynb) shows how I fit a very simple exponential curve to kenpom's predictions to reverse-engineer his win percentages. I then use the curve that fitted his predctions to decide how likely one team is to beat another, based on the difference between their kenpom ratings.
