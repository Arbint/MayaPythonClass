import maya.cmds as mc
from PySide2.QtWidgets import QLineEdit, QWidget, QPushButton, QListWidget, QAbstractItemView, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.models = set()
    
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
        addMeshBtn = QPushButton("Add Meshes")
        addMeshBtn.clicked.connect(self.AddMeshBtnClicked)
        self.masterLayout.addWidget(addMeshBtn)


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