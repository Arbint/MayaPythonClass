import maya.cmds as mc
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget

class Ghost():
    def __init__(self):
        self.srcMeshs = set()

    def InitSrcMeshesWithSel(self):
        selection = mc.ls(sl=True)
        self.srcMeshs.clear()  
        for sel in selection:
            shapes = mc.listRelatives(sel, s=True)
            for s in shapes:
                if mc.objectType(s) == "mesh":
                    self.srcMeshs.add(sel)
        
class GhostWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ghost = Ghost()
        self.setWindowTitle("Ghoster")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.CreateMeshSelSection()

    def CreateMeshSelSection(self):
        self.SrcMeshList = QListWidget()
        self.masterLayout.addWidget(self.SrcMeshList)
        setSrcMeshBtn = QPushButton("Set Selected as Source")
        setSrcMeshBtn.clicked.connect(self.SetSrcMeshBtnClicked)
        self.masterLayout.addWidget(setSrcMeshBtn)

    def SetSrcMeshBtnClicked(self):
        self.ghost.InitSrcMeshesWithSel()
        self.SrcMeshList.clear()
        self.SrcMeshList.addItems(self.ghost.srcMeshs)



ghostWidget = GhostWidget()
ghostWidget.show()