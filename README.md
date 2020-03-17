# Deadline2
An update of the Anki Deadline addon for GUI configuration. 

Work was originally started at https://gist.github.com/eshapard/12c14947d31dfcb8f0915761fb649c32
I had originally started off by just making this into an Anki 2.1 compatible addon (move deadline.py into __init__.py and you're off to the races)

Next, folks asked if I could make it a little bit easier to use by creating a configuration menu. 
Inspiration was taken from https://ankiweb.net/shared/info/1102281552 and https://ankiweb.net/shared/info/1374772155 , along with bits of their code. 

## Work In Progress
1. Check if a config already exists for a given deck when adding
	This is necessary as you’re able currently to overwrite configs by adding the same one multiple times. this will create multiple option groups
2. Add labels to the config screen, detailing what the calendar and dropdown are
3. Clean up old code; remove unnecessary bits
4. Submit addon to https://ankiweb.net/shared/addons/2.1
