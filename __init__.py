# Anki Deadline
# Anki 2.1 plugin
# Author: EJS
# Version 0.1
# Description: Adjusts 'New Cards per Day' setting of options group to ensure all cards
#              are seen by deadline.
# License: GNU GPL v3 <www.gnu.org/licenses/gpl.html>
from __future__ import division
import datetime, time, math
from PyQt5.QtWidgets import *
from anki.hooks import wrap, addHook
from aqt import *
from aqt.main import AnkiQt
from anki.utils import intTime
from aqt.utils import showWarning, openHelp, getOnlyText, askUser, showInfo, openLink
from .config import DeadlineDialog

deadlines = mw.addonManager.getConfig(__name__)
# deadlines={}

# ADD DEADLINES HERE
# One definition for each profile (default profile is User 1)
#    deadlines['User 1'] = ... for User 1
#    deadlines['Tom'] = ... for Tom's profile
#    deadlines['Jerry'] = ... for Jerry's profile
#    etc.
#
# Format:  ["OGName", "DeadlineDate"]
#        OGName = "Options Group Name"
#        DeadlineDate = last day of studying ("YYYY-MM-DD")
# Examples:
# deadlines['profile name'] = [
#           ["Silly Cards", "2017-01-01"],
#           ["Options Group 2", "2018-01-01"],
#           etc... (**no comma afer the last pair**)
#         ]
#
#     Tip: The whole string must be enclosed within square brackets 
#          and each name/date pair must be enclosed within its own 
#          set of square brackets. INCLUDE a COMMA between deadlines,
#          but not between the last deadline and the final ] bracket.
#
#  *Deadline date is the *last day of new cards*, not the day after
#   all new card should be seen.
# Format:  [["OGName", "YYYY-MM-DD"]]
mw.addonManager.setConfigAction(__name__, DeadlineDialog)
# deadlines['User 1'] = [
#         ["ETC", "2019-09-05"], ["NeuralFx", "2019-09-19"], ["IHP", "2019-10-03"], ["Nutrition", "2019-10-17"], ["EBM", "2019-10-24"], ["Endocrine", "2019-10-24"], ["AgingDying", "2019-11-14"], ["Prologue2", "2019-12-19"], ["SMBJ", "2020-01-30"], ["Pulmonary", "2020-03-05"], ["Cardiovascular", "2020-04-09"], ["GI_Oral", "2020-05-14"], ["GI_Written", "2020-05-17"], ["Renal", "2020-06-18"], ["Endo/Repro", "2020-08-13"], ["Heme", "2020-09-03"], ["Neuro1", "2020-10-08"], ["Neuro2", "2020-11-05"]
#         ]

# IF YOU FIND THIS ADDON HELPFUL, PLEASE CONSIDER MAKING A $1 DONATION
# USING THIS LINK: https://paypal.me/eshapard/1

# ------------Nothing to edit below--------------------------------#
DeadlineMenu = QMenu("Deadline", mw)
mw.form.menuTools.addMenu(DeadlineMenu)


# count new cards in a deck
def new_cards_in_deck(deck_id):
    new_cards = mw.col.db.scalar("""select
        count()
        from cards where
        type = 0 and
        queue != -1 and
        did = ?""", deck_id)
    return new_cards


# Find settings group ID
def find_settings_group_id(name):
    dconf = mw.col.decks.dconf
    for k in dconf:
        if dconf[k]['name'] == name:
            return k
    return False


# Find decks in settings group
def find_decks_in_settings_group(group_id):
    members = []
    decks = mw.col.decks.decks
    for d in decks:
        if 'conf' in decks[d] and int(decks[d]['conf']) == int(group_id):
            members.append(d)
    return members


# Count new cards in settings group
def new_cards_in_settings_group(name):
    new_cards = 0
    new_today = 0
    group_id = find_settings_group_id(name)
    if group_id:
        # Find decks and cycle through
        decks = find_decks_in_settings_group(group_id)
        for d in decks:
            new_cards += new_cards_in_deck(d)
            new_today += first_seen_cards_in_deck(d)
    return new_cards, new_today


# Count cards first seen today
def first_seen_cards_in_deck(deck_id):
    #return mw.col.decks.decks[deck_id]["newToday"][1] #unreliable
        #a new Anki day starts at 04:00 AM (by default); not midnight
        dayStartTime = datetime.datetime.fromtimestamp(mw.col.crt).time()
        midnight = datetime.datetime.combine(datetime.date.today(), dayStartTime)
        midNight = int(time.mktime(midnight.timetuple()) * 1000)
        query = ("""select count() from
                (select r.id as review, c.id as card, c.did as deck
                from revlog as r, cards as c
                where r.cid = c.id
                and r.type = 0
                order by c.id, r.id DESC)
                where deck = %s
                and review >= %s
                group by card""" % (deck_id, midNight))
        ret = mw.col.db.scalar(query)
        if not ret:
                ret = 0
        return ret


# find days until deadline
def days_until_deadline(deadline_date, include_today=True):
    if not deadline_date:
        # No deadline date
        return False
    date_format = "%Y-%m-%d"
    today = datetime.datetime.today()
    deadline_date = datetime.datetime.strptime(deadline_date, date_format)
    delta = deadline_date - today
    if include_today:
        days_left = delta.days + 1  # includes today
    else:
        days_left = delta.days  # today not included
    if days_left < 1:
        days_left = 0
    return days_left


# calculate cards per day
def cards_per_day(new_cards, days_left):
    if new_cards % days_left == 0:
        per_day = int(new_cards / days_left)
    else:
        per_day = int(new_cards / days_left) + 1
    #sanity check
    if per_day < 0:
                per_day = 0
    return per_day


# update new cards per day of a settings group
def update_new_cards_per_day(name, per_day):
    group_id = find_settings_group_id(name)
    if group_id:
        if group_id in mw.col.decks.dconf:
            mw.col.decks.dconf[group_id]["new"]["perDay"] = int(per_day)
            # utils.showInfo("updating deadlines disabled")
            mw.col.decks.save(mw.col.decks.dconf[group_id])
            #mw.col.decks.flush()


# Calc new cards per day
def calc_new_cards_per_day(name, days_left, silent=True):
    new_cards, new_today = new_cards_in_settings_group(name)
    per_day = cards_per_day((new_cards + new_today), days_left)
    logString="%s\n\nNew cards seen today: %s\nNew cards remaining: %s\nDays left: %s\nNew cards per day: %s" % (name, new_today, new_cards, days_left, per_day)
    if not silent:
        utils.showInfo(logString)
    update_new_cards_per_day(name, per_day)


# Main Function
def allDeadlines(silent=True):
    deadlines = mw.addonManager.getConfig(__name__)
    profile = str(aqt.mw.pm.name)
    include_today = True  # include today in the number of days left
    if profile in deadlines:
        for deck,date in deadlines.get(profile).items():
            # new_cards, new_today = new_cards_in_settings_group(name)
            days_left = days_until_deadline(date, include_today)
            # Change per_day amount if there's still time
            #    before the deadline
            if days_left:
                calc_new_cards_per_day(deck, days_left, silent)
    aqt.mw.deckBrowser.refresh()

#Manual Version
def manualDeadlines():
    allDeadlines(False)

manualDeadlineAction = QAction("Process Deadlines", mw)
manualDeadlineAction.triggered.connect(manualDeadlines)
DeadlineMenu.addAction(manualDeadlineAction)

# Add hook to adjust Deadlines on load profile
addHook("profileLoaded", allDeadlines)