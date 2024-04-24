from PySide2.QtCore import QRegExp, Signal
from PySide2.QtGui import QIntValidator, QRegExpValidator
import maya.cmds as mc
from PySide2.QtWidgets import QCheckBox, QLineEdit, QSizePolicy, QWidget, QPushButton, QListWidget, QAbstractItemView, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox

class AnimEntry:
    def __init__(self):
        self.subfix = ""
        self.frameMin = mc.playbackOptions(q=True, min=True)
        self.frameMax = mc.playbackOptions(q=True, max=True)
        self.shouldExport = True

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.models = set()
        self.animations = []
        self.fileName = ""
        self.saveDir = ""

    def SetFileName(self, newFileName):
        self.fileName = newFileName

    def RemoveEntry(self, entryToRemove):
        self.animations.remove(entryToRemove)

    def AddNewAnimEntry(self):
        self.animations.append(AnimEntry())
        return self.animations[-1]
    
    def AddSelectedMeshes(self):
        selection = mc.ls(sl=True)
        if not selection:
            return False, "No Mesh Selected"
        
        meshes = set()
        
        for sel in selection:
            shapes = mc.listRelatives(sel, s=True)
            for s in shapes:
                if mc.objectType(s) == "mesh":
                    meshes.add(sel)

        if len(meshes) == 0:
            return False, "No Mesh Selected"
        
        self.models = meshes
        return True, ""


    def AddRootJnt(self):
        if not self.rootJnt:
            return False, "No Root Joint Assigned"

        if mc.objExists(self.rootJnt):
            # q means we are querying, t means transform, ws means world space
            currentRootPos = mc.xform(self.rootJnt, q=True, t=True, ws=True)
            if currentRootPos[0] == 0 and currentRootPos[1] == 0 and currentRootPos[2] == 0:
                return False, "Root Joint Already Exists"
            
        mc.select(cl=True)
        rootJntName = self.rootJnt + "_root"
        mc.joint(n = rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName
        return True, ""

    def GetSelectionAsRootJnt(self):
        selection = mc.ls(sl=True, type= "joint")
        if not selection:
            return False, "No Joint Selected"
        
        self.rootJnt = selection[0]
        return True, ""
    
class AnimEntryWidget(QWidget):
    entryRemoved = Signal(AnimEntry)
    def __init__(self, entry:AnimEntry):
        super().__init__()
        self.entry = entry
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        enableCheckbox = QCheckBox()
        enableCheckbox.setChecked(self.entry.shouldExport)
        self.masterLayout.addWidget(enableCheckbox)
        enableCheckbox.toggled.connect(self.EnableCheckboxToggled)

        subfixLabel = QLabel("Subfix: ")
        self.masterLayout.addWidget(subfixLabel)
        subfixLineEdit = QLineEdit()
        subfixLineEdit.setValidator(QRegExpValidator(QRegExp('\w+')))
        subfixLineEdit.setText(self.entry.subfix)
        subfixLineEdit.textChanged.connect(self.SubfixTextChanged)
        self.masterLayout.addWidget(subfixLineEdit)

        minFrameLabel = QLabel("Min: ")
        self.masterLayout.addWidget(minFrameLabel)
        minFrameLineEdit = QLineEdit()
        minFrameLineEdit.setValidator(QIntValidator())
        minFrameLineEdit.setText(str(int(self.entry.frameMin)))
        minFrameLineEdit.textChanged.connect(self.MinFrameChanged)
        self.masterLayout.addWidget(minFrameLineEdit)

        maxFrameLabel = QLabel("Max: ")
        self.masterLayout.addWidget(maxFrameLabel)
        maxFrameLineEdit = QLineEdit()
        maxFrameLineEdit.setValidator(QIntValidator())
        maxFrameLineEdit.setText(str(int(self.entry.frameMax)))
        maxFrameLineEdit.textChanged.connect(self.MaxFrameChanged)
        self.masterLayout.addWidget(maxFrameLineEdit)

        setRangeBtn = QPushButton("[-]")
        setRangeBtn.clicked.connect(self.SetRangeBtnClicked) 
        self.masterLayout.addWidget(setRangeBtn)

        DeleteBtn = QPushButton("X")
        DeleteBtn.clicked.connect(self.DeleteBtnClicked) 
        self.masterLayout.addWidget(DeleteBtn)
    
    def DeleteBtnClicked(self):
        self.close()
        self.entryRemoved.emit(self.entry)
        self.deleteLater()

    def SetRangeBtnClicked(self):
        mc.playbackOptions(e=True, min = self.entry.frameMin, max = self.entry.frameMax)
        mc.playbackOptions(e=True, ast = self.entry.frameMin, aet = self.entry.frameMax)
        
    def MaxFrameChanged(self, newVal):
        self.entry.frameMax = int(newVal) 

    def MinFrameChanged(self, newVal):
        self.entry.frameMin = int(newVal)

    def SubfixTextChanged(self, newVal):
        self.entry.subfix = newVal 

    def EnableCheckboxToggled(self):
        self.entry.shouldExport = not self.entry.shouldExport

class MayaToUEWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()        
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootJntText)

        setSelectionAsRootJntBtn = QPushButton("Set Root Joint")
        setSelectionAsRootJntBtn.clicked.connect(self.SetSelectionAsRootJntBtnClicked)
        self.masterLayout.addWidget(setSelectionAsRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntBtnClicked)
        self.masterLayout.addWidget(addRootJntBtn)

        self.meshList = QListWidget()
        self.masterLayout.addWidget(self.meshList)
        self.meshList.setFixedHeight(80)
        addMeshBtn = QPushButton("Add Meshes")
        addMeshBtn.clicked.connect(self.AddMeshBtnClicked)
        self.masterLayout.addWidget(addMeshBtn)

        addNewAnimEntryBtn = QPushButton("Add Animation Clip")
        addNewAnimEntryBtn.clicked.connect(self.AddNewAnimEntryBtnClicked)
        self.masterLayout.addWidget(addNewAnimEntryBtn)

        self.animEntryLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.animEntryLayout)

        self.setFixedWidth(500)
        self.resize(self.minimumSizeHint())
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.saveFileLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.saveFileLayout)
        fileNameLabel = QLabel("File Name: ")
        self.saveFileLayout.addWidget(fileNameLabel)
        self.fileNameLineEdit = QLineEdit()
        self.fileNameLineEdit.setValidator(QRegExpValidator(QRegExp("\w+")))
        self.fileNameLineEdit.textChanged.connect(self.FileNameLineEditChanged)
        self.saveFileLayout.addWidget(self.fileNameLineEdit)

        #Add a common file director widget here
        self.saveDirLineEdit = QLineEdit()
        self.saveFileLayout.addWidget(self.saveDirLineEdit)
        self.pickDirBtn = QPushButton("...")
        self.saveFileLayout.addWidget(self.pickDirBtn)

    def FileNameLineEditChanged(self, newVal):
        self.mayaToUE.SetFileName(newVal)

    def AddNewAnimEntryBtnClicked(self):
        newEntry = self.mayaToUE.AddNewAnimEntry()
        newAnimEntryWidget = AnimEntryWidget(newEntry)
        newAnimEntryWidget.entryRemoved.connect(self.EntryRemoved)
        self.animEntryLayout.addWidget(newAnimEntryWidget)

    def EntryRemoved(self, entry):
        self.resize(self.minimumSizeHint())
        self.mayaToUE.RemoveEntry(entry)

    def AddMeshBtnClicked(self):
        success, msg = self.mayaToUE.AddSelectedMeshes()
        if not success:
            QMessageBox.warning(self, "Warning", msg)
        else:
            self.meshList.clear()
            self.meshList.addItems(self.mayaToUE.models)

    def AddRootJntBtnClicked(self):
        success, msg = self.mayaToUE.AddRootJnt()
        if not success:
            QMessageBox.warning(self, "Waring", msg)
        else:
            self.rootJntText.setText(self.mayaToUE.rootJnt)

    def SetSelectionAsRootJntBtnClicked(self):
        success, msg = self.mayaToUE.GetSelectionAsRootJnt()
        if not success:
            QMessageBox.warning(self, "Warning", msg)
        else:
            self.rootJntText.setText(self.mayaToUE.rootJnt)

mayaToUEWidget = MayaToUEWidget()
mayaToUEWidget.show()