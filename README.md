# Deadline2
An update of the Anki Deadline addon with GUI configuration.

Work was originally started at https://gist.github.com/eshapard/12c14947d31dfcb8f0915761fb649c32
I had originally started off by just making this into an Anki 2.1 compatible addon (move deadline.py into __init__.py and you're off to the races)

Next, folks asked if I could make it a little bit easier to use by creating a configuration menu. 
Inspiration was taken from https://ankiweb.net/shared/info/1102281552 and https://ankiweb.net/shared/info/1374772155 , along with bits of their code. 

## Work In Progress
1. Add labels to the config screen, detailing what the calendar and dropdown are
2. Clean up old code; remove unnecessary bits
3. Submit addon to https://ankiweb.net/shared/addons/2.1
4. clean up deck names on the add dialog. All items with 3 hierarchal levels should be pared down to 2 levels, to help reduce the width of the dropdown.