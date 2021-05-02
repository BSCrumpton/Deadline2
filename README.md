# Deadline2
An update of the Anki Deadline addon with GUI configuration.

Work was originally started at https://gist.github.com/eshapard/12c14947d31dfcb8f0915761fb649c32
I had originally started off by just making this into an Anki 2.1 compatible addon (move deadline.py into __init__.py and you're off to the races)

Next, folks asked if I could make it a little bit easier to use by creating a configuration menu. 
Inspiration was taken from https://ankiweb.net/shared/info/1102281552 and https://ankiweb.net/shared/info/1374772155 , along with bits of their code. 

This can be found on ankiweb at: https://ankiweb.net/shared/info/723639202

## Work In Progress
1. Clean up old code; remove unnecessary bits
2. clean up deck names on the add dialog. All items with 3 hierarchal levels should be pared down to 2 levels, to help reduce the width of the dropdown.
3. Better ensure that when you update the addon, no deadlines are "lost"
4. Whenever you delete a deadline, the original config should be re-applied to the deck
5. Add ability to choose multiple decks for a single deadline date 
6. Allow selection of parent deck + all subdecks, and apply deadline to all subdecks