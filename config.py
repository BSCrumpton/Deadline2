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
from aqt.main import AnkiQt
from anki.utils import intTime
from aqt.utils import showWarning, openHelp, getOnlyText, askUser, showInfo, openLink


class DeadlineDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, parent=mw) #, Qt.Window)

        self.mw = aqt.mw
        self.deadlines = mw.addonManager.getConfig(__name__)
        self.deadlines.pop("test")
        self.form = aqt.forms.fields.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle(_("Deadline") )
        self.form.buttonBox.button(QDialogButtonBox.Help).setAutoDefault(False)
        self.form.buttonBox.button(QDialogButtonBox.Close).setAutoDefault(False)
        self.form.buttonBox.button(QDialogButtonBox.Close).setText('Process Deadlines')
        self.form.buttonBox.button(QDialogButtonBox.Close).clicked.connect(self.callDeadlines)
        self.fillFields()
        self.setupSignals()
        self.form.fieldList.setCurrentRow(0)
        self.form.rtl.setParent(None)
        self.form.fontFamily.setParent(None)
        self.form.fontSize.setParent(None)
        self.form.sticky.setParent(None)
        self.form.label_18.setParent(None)
        self.form.fontFamily.setParent(None)
        self.form.fieldRename.setParent(None)
        self.form.fieldPosition.setParent(None)
        self.form.label_5.setParent(None)
        self.form.sortField.setParent(None)
        self.popUpLayout=QHBoxLayout()
        self.popUpLabel = QLabel()
        self.popUpLabel.setText("Choose Pop-Up Style:")
        self.popUpBox = QComboBox()
        self.popUpBox.addItem("Single Summary Pop Up")
        self.popUpBox.addItem("One Pop Up per Deck")
        self.popUpLayout.addWidget(self.popUpLabel)
        self.popUpLayout.addWidget(self.popUpBox)
        self.form.verticalLayout.addLayout(self.popUpLayout)
        self.resize(500, 500)

        self.exec_()

    def callDeadlines(self):
        from . import manualDeadlines
        tempString=str(self.popUpBox.currentText())
        if(tempString.find("Single")!=-1):
            oneOrMany="One"
        else:
            oneOrMany="Many"
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
        f.fieldAdd.clicked.connect(self.onAdd)
        f.fieldDelete.clicked.connect(self.onDelete)
        f.buttonBox.helpRequested.connect(self.onHelp)

    def readValues(self):
        user=str(aqt.mw.pm.name)
        deck=str(self.deckBox.currentText())
        year=self.cal.selectedDate().year()
        month=self.cal.selectedDate().month()
        day=self.cal.selectedDate().day()
        date="{}-{}-{}".format(year,str(month).zfill(2),str(day).zfill(2))
        self.user=user
        self.deck=deck
        self.date=date
        self.window.close()
        if(not self.user in self.deadlines["deadlines"]):
            self.deadlines["deadlines"][self.user]={}
        self.deadlines["deadlines"][self.user][self.deck]=self.date
        self.user=""
        self.deck=""
        self.date=""
        self.fillFields()
        mw.addonManager.writeConfig(__name__, self.deadlines)
        dconf = mw.col.decks.dconf
        tempID=0
        for confId,conf in dconf.items():
            if(conf['name']==deck):
                tempID=confId
        if(tempID==0):
            tempID = mw.col.decks.confId(deck)
        mw.col.decks.byName(deck)['conf']=tempID

    def onAdd(self):
        self.user=""
        self.window=QDialog(self)
        self.window.setWindowTitle("Add new Deadline")
        self.window.resize(500,500)
        dropdownLayout=QVBoxLayout()
        dropdownLayout.addStretch()
        dropdownLabel=QLabel()
        dropdownLabel2=QLabel()
        dropdownLabel.setText("Select the deck you want to add a deadline to:")
        dropdownLabel2.setText("Note: The dealine is when you will see all NEW cards by")
        dropdownLayout.addWidget(dropdownLabel)
        layout=QHBoxLayout()
        self.cal=QCalendarWidget()
        self.cal.setGridVisible(True)
        self.cal.move(0, 0)
        self.cal.setGeometry(100,100,300,300)
        self.deckBox = QComboBox()
        for deck in sorted(aqt.mw.col.decks.allNames()):
            deckId=mw.col.decks.byName(deck)['id']
            new_cards = mw.col.db.scalar("""select count() from cards where type = 0 and queue != -1 and did = ?""", deckId)
            if(new_cards<1):
                continue
            self.deckBox.addItem(deck)
        dropdownLayout.addWidget(self.deckBox)
        dropdownLayout.addWidget(dropdownLabel2)
        dropdownLayout.addStretch()
        layout.addLayout(dropdownLayout)
        calLayout=QVBoxLayout()
        calLabel=QLabel()
        calLabel.setText("Select your deadline date:")
        calLayout.addWidget(calLabel)
        calLayout.addWidget(self.cal)
        layout.addLayout(calLayout)
        self.okButton = QDialogButtonBox.Ok
        self.buttonBox=QDialogButtonBox(self.okButton)
        self.buttonBox.button(self.okButton).clicked.connect(self.readValues)
        layout.addWidget(self.buttonBox)
        self.window.setLayout(layout)
        self.window.show()        

    def onDelete(self):
        toDelete=self.form.fieldList.currentRow()
        if(toDelete==-1):
            return
        temp=self.form.fieldList.item(toDelete).text()
        fields=temp.split("}")
        user=fields[0].split("{")[1]
        deck=fields[1].split("{")[1]
        date=fields[2].split("{")[1]
        self.deadlines["deadlines"].get(user).pop(deck)
        self.fillFields()
        mw.addonManager.writeConfig(__name__, self.deadlines)
        delConfId=mw.col.decks.byName(deck)['conf']
        mw.col.decks.remConf(delConfId)

    def onHelp(self):
        openLink('https://github.com/BSCrumpton/Deadline2')
