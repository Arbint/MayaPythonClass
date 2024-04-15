import maya.cmds as mc
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QAbstractItemView, QPushButton, QLabel, QListWidget

def GetCurrentFrame():
    return int(mc.currentTime(q=True))

class Ghost():
    def __init__(self):
        self.srcMeshs = set()
        self.InitGhostGrpIfNotExist()

    def InitGhostGrpIfNotExist(self):
        if not mc.objExists(self.GetGhostGrpName()):
            mc.createNode("transform", n = self.GetGhostGrpName())
            
    def GetGhostGrpName(self):
        return "Ghost_grp"

    def GoToNextGhost(self):
        currentFrame = GetCurrentFrame()
        frames = self.GetGhostFramesSorted()
        nextFrame = frames[0]
        for frame in frames:
            if frame > currentFrame:
                nextFrame = frame
                break
        
        mc.currentTime(nextFrame, e=True)

    def GoToPrevGhost(self):
        pass

    def GetGhostFramesSorted(self):
        ghosts = mc.listRelatives(self.GetGhostGrpName(), c=True)
        frames = set() 
        for ghost in ghosts:
            frame = mc.getAttr(ghost + "." + self.GetFrameAttr())
            frames.add(frame)

        frames = list(frames)
        frames.sort()
        return frames

    def AddGhost(self):
        for srcMesh in self.srcMeshs:
            ghostName = srcMesh + "_ghost_" + str(GetCurrentFrame())
            if mc.objExists(ghostName):
                mc.delete(ghostName)

            mc.duplicate(srcMesh, n = ghostName)
            mc.addAttr(ghostName, ln = self.GetFrameAttr(), dv = GetCurrentFrame())
            mc.parent(ghostName, self.GetGhostGrpName())

    

    def GetFrameAttr(self):
        return "frame"

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
        self.CreateCtrlSection()

    def CreateCtrlSection(self):
        layout = QHBoxLayout()
        self.masterLayout.addLayout(layout)

        addGhostBtn = QPushButton("Add")
        addGhostBtn.clicked.connect(self.ghost.AddGhost) 
        layout.addWidget(addGhostBtn)

        prevBtn = QPushButton("<<<")
        prevBtn.clicked.connect(self.ghost.GoToPrevGhost)
        layout.addWidget(prevBtn)

        nextBtn = QPushButton(">>>")
        nextBtn.clicked.connect(self.ghost.GoToNextGhost)
        layout.addWidget(nextBtn)

    def CreateMeshSelSection(self):
        self.SrcMeshList = QListWidget()
        self.SrcMeshList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.SrcMeshList.itemSelectionChanged.connect(self.SrcMeshListSelecionChanged)
        self.masterLayout.addWidget(self.SrcMeshList)
        setSrcMeshBtn = QPushButton("Set Selected as Source")
        setSrcMeshBtn.clicked.connect(self.SetSrcMeshBtnClicked)
        self.masterLayout.addWidget(setSrcMeshBtn)

    def SetSrcMeshBtnClicked(self):
        self.ghost.InitSrcMeshesWithSel()
        self.SrcMeshList.clear()
        self.SrcMeshList.addItems(self.ghost.srcMeshs)

    def SrcMeshListSelecionChanged(self):
        mc.select(cl=True)
        for item in self.SrcMeshList.selectedItems():
            mc.select(item.text(), add=True)

ghostWidget = GhostWidget()
ghostWidget.show()