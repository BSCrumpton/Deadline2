# Anki Deadline2
# Anki 2.1 plugin
# Author: BSC
# Version 2_2_1
# Description: Adjusts 'New Cards per Day' setting of options group to ensure all cards
#              are seen by deadline.
# License: GNU GPL v3 <www.gnu.org/licenses/gpl.html>

import datetime, time, math
from PyQt5.QtWidgets import *
from anki.hooks import wrap, addHook
from aqt import *
from . import ConfigForm, CalForm
from aqt.main import AnkiQt
from anki.utils import intTime
from aqt.utils import showWarning, openHelp, getOnlyText, askUser, showInfo, openLink


class DeadlineDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, parent=mw) #, Qt.Window)

        self.mw = aqt.mw
        self.deadlines = mw.addonManager.getConfig(__name__)
        self.deadlines.pop("test")
        self.form = ConfigForm.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle(_("Deadline") )
        self.form.ProcessDeadlineBox.clicked.connect(self.callDeadlines)
        self.fillFields()
        self.setupSignals()
        if(self.deadlines.get("oneOrMany","")=="Many"):
            self.form.OneOrManyBox.setCurrentIndex(1)
        else:
            self.form.OneOrManyBox.setCurrentIndex(0)
        self.resize(500, 500)
        self.Calwindow=QDialog(self)
        self.LayoutForCal=CalForm.Ui_Dialog()
        self.LayoutForCal.setupUi(self.Calwindow)
        self.LayoutForCal.pushButton.clicked.connect(self.readValues)
        self.exec_()

    def callDeadlines(self):
        from . import manualDeadlines
        tempString=str(self.form.OneOrManyBox.currentText())
        if(tempString.find("Single")!=-1):
            self.deadlines["oneOrMany"]="One"
        else:
            self.deadlines["oneOrMany"]="Many"
        mw.addonManager.writeConfig(__name__, self.deadlines)
        manualDeadlines()

    def fillFields(self):
        self.form.fieldList.clear()
        for user in self.deadlines["deadlines"]:
            if user != str(aqt.mw.pm.name):
                continue
            for deck, deadline in self.deadlines["deadlines"].get(user).items():
                if(deadline==""):
                    continue
                self.form.fieldList.addItem("user:{{{}}} deck:{{{}}} date:{{{}}}".format(user, deck,deadline))

    def setupSignals(self):
        f = self.form
        f.AddDeadlineButton.clicked.connect(self.onAdd)
        f.DeleteDeadlineButton.clicked.connect(self.onDelete)
        f.buttonBox.helpRequested.connect(self.onHelp)

    def readValues(self):
        user=str(aqt.mw.pm.name)
        deck=str(self.LayoutForCal.comboBox.currentText())
        year=self.LayoutForCal.calendarWidget.selectedDate().year()
        month=self.LayoutForCal.calendarWidget.selectedDate().month()
        day=self.LayoutForCal.calendarWidget.selectedDate().day()
        date="{}-{}-{}".format(year,str(month).zfill(2),str(day).zfill(2))
        self.user=user
        self.deck=deck
        self.date=date
        self.Calwindow.close()
        if(not self.user in self.deadlines["deadlines"]):
            self.deadlines["deadlines"][self.user]={}
        self.deadlines["deadlines"][self.user][self.deck]=self.date
        tempString=str(self.form.OneOrManyBox.currentText())
        if(tempString.find("Single")!=-1):
            self.deadlines["oneOrMany"]="One"
        else:
            self.deadlines["oneOrMany"]="Many"
        self.user=""
        self.deck=""
        self.date=""
        self.fillFields()
        mw.addonManager.writeConfig(__name__, self.deadlines)
        dconf = mw.col.decks.all_config()
        tempID=0
        for conf in dconf:
            if(conf['name']==deck):
                tempID=conf['id']
        if(tempID==0):
            tempID = mw.col.decks.confId(deck)
        deckToUpdate=mw.col.decks.byName(deck)
        deckToUpdate['conf']=tempID
        mw.col.decks.save(deckToUpdate)

    def onAdd(self):
        self.Calwindow.show()
        self.user = ""
        self.LayoutForCal.comboBox.clear()
        for deck in sorted(aqt.mw.col.decks.allNames()):
            deckId=mw.col.decks.byName(deck)['id']
            new_cards = mw.col.db.scalar("""select count() from cards where type = 0 and queue != -1 and did = ?""", deckId)
            if(new_cards<1):
                continue
            self.LayoutForCal.comboBox.addItem(deck)


    def onDelete(self):
        while self.form.fieldList.selectedIndexes():
            temp=self.form.fieldList.item(self.form.fieldList.selectedIndexes()[0].row()).text()
            self.form.fieldList.takeItem(self.form.fieldList.selectedIndexes()[0].row())
            fields=temp.split("}")
            user=fields[0].split("{")[1]
            deck=fields[1].split("{")[1]
            date=fields[2].split("{")[1]
            self.deadlines["deadlines"].get(user).pop(deck)
            mw.addonManager.writeConfig(__name__, self.deadlines)
            delConfId=mw.col.decks.byName(deck)['conf']
            mw.col.decks.remConf(delConfId)
        # self.fillFields()

    def onHelp(self):
        openLink('https://github.com/BSCrumpton/Deadline2')
