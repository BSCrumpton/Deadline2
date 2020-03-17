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
        self.resize(500, 500)

        self.exec_()



    def fillFields(self):
        self.form.fieldList.clear()
        for user in self.deadlines:
            if user != str(aqt.mw.pm.name):
                continue
            for deck, deadline in self.deadlines.get(user).items():
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
        if(not self.user in self.deadlines):
            self.deadlines[self.user]={}
        self.deadlines[self.user][self.deck]=self.date
        self.user=""
        self.deck=""
        self.date=""
        self.fillFields()
        mw.addonManager.writeConfig(__name__, self.deadlines)
        dconf = mw.col.decks.dconf
        id = mw.col.decks.confId(deck)
        mw.col.decks.byName(deck)['conf']=id

    def onAdd(self):
        self.user=""
        self.window=QDialog(self)
        self.window.setWindowTitle("Add new Deadline")
        self.window.resize(500,500)
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
        layout.addWidget(self.deckBox)
        layout.addWidget(self.cal)
        self.okButton = QDialogButtonBox.Ok
        self.buttonBox=QDialogButtonBox(self.okButton)
        self.buttonBox.button(self.okButton).clicked.connect(self.readValues)
        layout.addWidget(self.buttonBox)
        self.window.setLayout(layout)
        self.window.show()        

    def onDelete(self):
        toDelete=self.form.fieldList.currentRow()
        temp=self.form.fieldList.item(toDelete).text()
        fields=temp.split("}")
        user=fields[0].split("{")[1]
        deck=fields[1].split("{")[1]
        date=fields[2].split("{")[1]
        self.deadlines.get(user).pop(deck)
        self.fillFields()
        mw.addonManager.writeConfig(__name__, self.deadlines)
        delConfId=mw.col.decks.byName(deck)['conf']
        mw.col.decks.remConf(delConfId)

    def onHelp(self):
        #openHelp("fields")
        openLink('http://www.ankingmed.com/how-to-update')
