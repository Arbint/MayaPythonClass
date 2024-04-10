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

def GetJntWithMostInfluence(vert, skin):
    weights = mc.skinPercent(skin, vert, q=True, v=True)
    jnts = mc.skinPercent(skin, vert, q=True, t=None)
    
    maxWeightIndex = 0
    maxWeight = weights[0]

    for i in range(1, len(weights)):
        if weights[i] > maxWeight:
            maxWeight = weights[i]
            maxWeightIndex = i
    
    return jnts[maxWeightIndex]





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

        jntVertsMap = self.GenerateJntVertsDict()
        
        segments = []
        for jnt, verts in jntVertsMap.items():
            newSeg = self.CreateProxyModelForJntAndVerts(jnt, verts)
            newSkinCluster = mc.skinCluster(self.jnts, newSeg)[0]
            print(newSkinCluster)
            mc.copySkinWeights(ss=self.skin, ds=newSkinCluster, nm=True, sa="closestPoint", ia="closestJoint")

    def CreateProxyModelForJntAndVerts(self, jnt, verts):
        if not verts:
            return None

        faces = mc.polyListComponentConversion(verts, fromVertex = True, toFace = True)
        faces = mc.ls(faces, flatten = True)

        Labels = set()
        for face in faces:
            Labels.add(face.replace(self.model, ""))

        dup = mc.duplicate(self.model)[0]

        allDupFaces = mc.ls(f"{dup}.f[*]", flatten = True)
        facesToDel = []
        for dupFace in allDupFaces:
            label = dupFace.replace(dup, "")
            if label not in Labels:
                facesToDel.append(dupFace)

        mc.delete(facesToDel)
        dupName = self.model + "_" + jnt + "_proxy"
        mc.rename(dup, dupName)
        return dupName
    



    def GenerateJntVertsDict(self):
        dict = {}
        for jnt in self.jnts:
            dict[jnt] = []

        verts = mc.ls(f"{self.model}.vtx[*]", flatten = True)
        for vert in verts:
            owningJnt = GetJntWithMostInfluence(vert, self.skin)
            dict[owningJnt].append(vert)

        return dict
    

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