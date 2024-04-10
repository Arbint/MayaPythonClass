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

        upperStream = GetUpperStream(modelShape)
        print(upperStream)


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