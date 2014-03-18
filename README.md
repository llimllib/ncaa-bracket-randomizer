# NCAA Bracket Randomizer

Generates a reasonable bracket for you, based on <a href="http://kenpom.com/">Ken Pomeroy's</a>
college basketball ratings.

For each matchup, it compares the two teams in the game, calculates the odds of the favorite
winning the game, and chooses the winner. There are three settings that determine how it
does so:

## No randomness

Always picks the favorite

## Some

Picks the underdog if they win twice in a row.

If team A has a 75% chance of beating team B, the program will generate two random numbers
between 0 and 100; if both of them are greater than 75, team B will advance. Otherwise,
team A will advance.

## Lots of randomness

Picks the underdog if they win once

If team A has a 75% chance of beating team B, the program will generate a random number
between 0 and 100; if it's greater than 75, team B will advance. Otherwise,
team A will advance.

# Calculating the Odds

The odds for team A to beat team B are given by the <a
href="https://en.wikipedia.org/wiki/Log5">log5</a> of their Pomeroy ratings.
