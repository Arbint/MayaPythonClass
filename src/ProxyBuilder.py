import maya.cmds as mc
from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton

def IsMesh(obj):
    shapes = mc.listRelatives(obj, s=True)
    if not shapes:
        return False
    for s in shapes:
        if mc.objectType(s) == "mesh":
            return True
        
    return False

def IsSkin(obj):
    return mc.objectType(obj) == "skinCluster"

def IsJoint(obj):
    return mc.objectType(obj) == "joint"

def GetUpperStream(obj):
    return mc.listConnections(obj, s=True, d=False, sh=True)

def GetLowerStream(obj):
    return mc.listConnections(obj, s=False, d=True, sh=True)

def GetAllConnectionIn(obj, NextFunc, Filter = None):
    AllFound = set()
    nexts = NextFunc(obj)
    while nexts:
        for next in nexts:
            AllFound.add(next)

        nexts = NextFunc(nexts)
        if nexts:
            nexts = [x for x in nexts if x not in AllFound]        

    if not Filter:
        return list(AllFound)
    
    filted = []
    for found in AllFound:
        if Filter(found):
            filted.append(found)

    return filted

class BuildProxy:
    def __init__(self):
        self.skin = ""
        self.model = ""
        self.jnts = []

    def BuildProxyForSelectedmesh(self):
        model = mc.ls(sl=True)[0]
        if not IsMesh(model):
            print("please select a model")
            return  
        self.model = model
        modelShape = mc.listRelatives(self.model, s=True)[0]

        skin = GetAllConnectionIn(modelShape, GetUpperStream, IsSkin)
        if skin:
            self.skin = skin[0]

        jnts = GetAllConnectionIn(modelShape, GetUpperStream, IsJoint)
        if jnts:
            self.jnts = jnts

        print(f"find mesh: {self.model}, skin: {self.skin}, jnts: {self.jnts}")
        mc.select(self.jnts, r=True)

class BuildProxyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.setWindowTitle("Build Rig Proxy") 
        self.setGeometry(0,0,100,100)
        buildBtn = QPushButton("Build Proxy")
        buildBtn.clicked.connect(self.BuildProxyBtnClicked)
        self.masterLayout.addWidget(buildBtn)
        self.adjustSize()
        
        self.builder = BuildProxy()

    def BuildProxyBtnClicked(self):
        self.builder.BuildProxyForSelectedmesh()

buildProxyWidget = BuildProxyWidget()
buildProxyWidget.show()