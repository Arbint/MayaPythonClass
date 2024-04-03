import maya.cmds as mc
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit

####################################
#            Facilities            #
####################################
def CreateControllerForJnt(jnt, size = 10):
    ctrlName = "ac_" + jnt
    ctrlGrpName = ctrlName + "_grp"

    mc.circle(n=ctrlName, nr=(1,0,0), r = size)
    mc.group(ctrlName, n = ctrlGrpName)
    mc.matchTransform(ctrlGrpName, jnt)
    mc.orientConstraint(ctrlName, jnt)

    return ctrlName, ctrlGrpName


def CreateBox(name, size = 10):
    #curve -d 1 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;
    p = ((-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5))
    mc.curve(n=name, d=1, p = p)

    mc.setAttr(name + ".scale", size,size,size, type = "float3")
    mc.makeIdentity(name, apply = True)

class ThreeJntChain:
    def __init__(self):
        self.root = ""
        self.middle = ""
        self.end = ""

    def AutoFindJntsBasedOnSel(self):
        self.root = mc.ls(sl=True, type = "joint")[0]
        self.middle = mc.listRelatives(self.root, c=True, type = "joint")[0]
        self.end = mc.listRelatives(self.middle, c=True, type ="joint")[0]

    def RigThreeJntChain(self):
        rootCtrl, rootCtrlGrp = CreateControllerForJnt(self.root)
        middleCtrl, middleCtrlGrp = CreateControllerForJnt(self.middle)
        endCtrl, endCtrlGrp = CreateControllerForJnt(self.end)

        mc.parent(middleCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, middleCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        CreateBox(ikEndCtrl)
        ikEndCtrlGrp = ikEndCtrl + "_grp"
        mc.group(ikEndCtrl, n = ikEndCtrlGrp)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        mc.orientConstraint(ikEndCtrl, self.end)



####################################
#                UI                #
####################################
class ThreeJntChainWiget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create Three Joint Chain")
        self.setGeometry(0, 0, 300, 300)
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout) 
        hintLabel = QLabel("Please Select the root of the joint chain:")        
        self.masterLayout.addWidget(hintLabel)

        autoFindBtn = QPushButton("Auto Find Jnts")
        self.masterLayout.addWidget(autoFindBtn)         
        autoFindBtn.clicked.connect(self.AutoFindBtnClicked)

        self.selectionDisplay = QLabel()
        self.masterLayout.addWidget(self.selectionDisplay)

        rigThreeJntChainBtn = QPushButton("Rig Three Jnt Chain")
        self.masterLayout.addWidget(rigThreeJntChainBtn)
        rigThreeJntChainBtn.clicked.connect(self.RigThreeJntChainBtnClicked)

        self.adjustSize()
        self.threeJntChain = ThreeJntChain()

    def RigThreeJntChainBtnClicked(self):
        self.threeJntChain.RigThreeJntChain()


    def AutoFindBtnClicked(self):
        print("button pressed")
        self.threeJntChain.AutoFindJntsBasedOnSel()
        self.selectionDisplay.setText(f"{self.threeJntChain.root}, {self.threeJntChain.middle}, {self.threeJntChain.end}") 

treeJntChainWidget = ThreeJntChainWiget()
treeJntChainWidget.show()
