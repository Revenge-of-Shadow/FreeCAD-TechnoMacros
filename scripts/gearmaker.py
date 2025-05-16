from PySide import QtCore, QtGui
import FreeCAD as App
import math

'''============================================================='''
'''                Graphical user interface code                '''
class GuiClass(QtGui.QDialog):
    def __init__(self):
        super(GuiClass, self).__init__()
        self.initUI()

    ##  "Error handling"
    def callInformation(self):
        QtGui.QMessageBox.information(None, "Nya nya",
                                      "Outer radius must be bigger than inner radius and tooth height together."+
                                      "\nZero inner radius is allowed."+
                                      "\nAmount of teeth must be above 2."+
                                      "\nAmound and outer radius influence tooth width."+
                                      "\nConnected gearwheels must have the same tooth width and height."+
                                      "\nExtrusion may be positive, negative (reversed) and nil (sketch only)."
                                      )

    ##  "Error handling" end

    ## Utility functions
    def setupSpinBox(self, box, max, min = 0, step = 1, default = 0):
        box.setRange(min, max)
        box.setSingleStep(step)
        box.setValue(default)

    def showToothWidth(self):
        self.ti_tw.setValue(math.tan(math.pi*2/float(self.is_at.value()))*(self.ds_or.value()-self.ds_th.value())*2)

    def onValueChanged(self):
        #   outer radius <= tooth height + inner radius
        if(self.ds_or.value() <= (self.ds_th.value()+self.ds_ir.value())):
            self.callInformation()
            return
        self.showToothWidth()

    def tryQuit(self, success):
        self.success = False
        #if(success):
        self.success = success
        self.close()
    ## Utility functions end
    
    ##  Event handling
    def onOk(self):
        self.tryQuit(True)

    def onCancel(self):
        self.tryQuit(False)
   ##  Event handling end
    

    def initUI(self):
        self.setGeometry(250, 250, 320, 400)
        self.setFixedSize(320, 480)
        self.setWindowTitle("Nya")

        ##  Labels and inputs
        self.l_or = QtGui.QLabel("Outer radius [mm]:", self)
        self.l_or.move(20, 20)
        self.ds_or = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_or, max=1000000, min=1, step = 1, default=5)
        self.ds_or.valueChanged[float].connect(self.onValueChanged)
        self.ds_or.setFixedWidth(80)
        self.ds_or.move(220, 20)

        self.l_ir = QtGui.QLabel("Inner radius [mm]:", self)
        self.l_ir.move(20, 70)
        self.ds_ir = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_ir, max=1000000, min=0, step=1, default=1) 
        self.ds_ir.valueChanged[float].connect(self.onValueChanged)
        self.ds_ir.setFixedWidth(80)
        self.ds_ir.move(220, 70)

        self.l_at = QtGui.QLabel("Amount of teeth:", self)
        self.l_at.move(20, 120)
        self.is_at = QtGui.QSpinBox(self)
        self.setupSpinBox(box=self.is_at, max = 1000, min = 2, step = 1, default = 16) 
        self.is_at.valueChanged[int].connect(self.onValueChanged)
        self.is_at.setFixedWidth(80)
        self.is_at.move(220, 120)

        self.l_th = QtGui.QLabel("Tooth height [mm]:", self)
        self.l_th.move(20, 170)
        self.ds_th = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_th, max=1000, min=0, step=0.1, default=1)
        self.ds_th.valueChanged[float].connect(self.onValueChanged)
        self.ds_th.setFixedWidth(80)
        self.ds_th.move(220, 170)

        self.l_tw = QtGui.QLabel("Tooth width [mm]:", self)
        self.l_tw.move(20, 220)
        self.ti_tw = QtGui.QDoubleSpinBox(self)
        self.ti_tw.setFixedWidth(80)
        self.ti_tw.move(220, 220)
        self.ti_tw.setEnabled(False)

        self.l_e = QtGui.QLabel("Extrusion [mm]:", self)
        self.l_e.move(20, 270)
        self.ds_e = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_e, 1000000, min=-1000000, step=1, default=2) 
        self.ds_e.valueChanged[float].connect(self.onValueChanged)
        self.ds_e.setFixedWidth(80)
        self.ds_e.move(220, 270)
        ##  Inputs and labels end

        ##  Confirm/Cancel buttons
        self.bt_cancel = QtGui.QPushButton("Cancel", self)
        self.bt_cancel.clicked.connect(self.onCancel)
        self.bt_cancel.move(20, 440)
        
        self.bt_ok = QtGui.QPushButton("Make the gear", self)
        self.bt_ok.clicked.connect(self.onOk)
        self.bt_ok.move(190, 440)
        ##  Confirm/Cancel buttons end
        
        self.show()

form = GuiClass()
form.exec()

'''               Graphical user interface end                '''
'''==========================================================='''

'''==========================================================='''
'''                     Modelling code                        '''
##  FreeCAD object functions
def makeGearWheel(doc, o_radius, i_radius, tooth_amount, tooth_h, extrusion):
    body = doc.addObject('PartDesign::Body', 'gearBody')

    sketch = body.newObject('Sketcher::SketchObject', 'gearSketch')
    sketch.AttachmentSupport = (doc.getObject('XY_Plane'), [''])
    sketch.MapMode = 'FlatFace'
    
    geoList = []
    geoList.append(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), i_radius))
    sketch.addGeometry(geoList, False)
    del geoList

    

    points = []
    for i in range(tooth_amount*2):
        angle = math.pi*2/(tooth_amount*2)*i
        
        if(i % 2 == 1):
            dist = o_radius - tooth_h
        else:
            dist = o_radius
        points.append(App.Vector(math.cos(angle)*dist, math.sin(angle)*dist, 0))

    #   I am sorry for this. I could not find any documentation to make it pretty.
    for i in range(len(points)-1):
        lastGeoId = len(sketch.Geometry)
        geoList = []
        geoList.append(Part.LineSegment(points[i], points[i+1]))
        sketch.addGeometry(geoList, False)
        del geoList

    lastGeoId = len(sketch.Geometry)
    geoList = []
    geoList.append(Part.LineSegment(points[0], points[len(points)-1]))
    sketch.addGeometry(geoList, False)
    del geoList

    if(extrusion == 0):
        return

    pad = body.newObject('PartDesign::Pad', 'gearPad')
    pad.Profile = (sketch, [''])
    pad.Length = abs(extrusion)
    pad.ReferenceAxis = (sketch, ['N_Axis'])
    pad.Reversed = (extrusion < 0)

    

##  FreeCAD object functions end

if(form.success):
    doc = App.activeDocument()
    if(doc is None):
        QtGui.QMessageBox.information(None, "No nya", "Select a document first.")
    else:
        ##  Processing
        o_radius = form.ds_or.value()
        i_radius = form.ds_ir.value()
        tooth_amount = form.is_at.value()
        tooth_h = form.ds_th.value()
        extrusion = form.ds_e.value()
        
        makeGearWheel(doc, o_radius, i_radius, tooth_amount, tooth_h, extrusion)

        ##  Processing end
        doc.recompute()
