from PySide import QtCore, QtGui
import FreeCAD as App
import math
import json

filename = "last_gearwheel.json"
'''==========================================================='''
'''                       Class  code                         '''


def obj_dict(obj):
    return obj.__dict__


class Gearwheel:
    def __init__(self, outer_r, inner_r, teeth, tooth_h, extrusion, tolerance_a):
        self.outer_r = outer_r
        self.inner_r = inner_r
        self.teeth = teeth
        self.tooth_h = tooth_h
        self.extrusion = extrusion
        self.tolerance_a = tolerance_a


def gearwheel_to_json(obj):
    with open(filename, "w") as file:
        json.dump(obj, file, default=obj_dict)


def gearwheel_from_json():
    with open(filename, "r") as file:
        data = json.load(file)
        return Gearwheel(
            data["outer_r"], data["inner_r"], data["teeth"], data["tooth_h"], data["extrusion"], data["tolerance_a"]
        )


'''                     Class code end                        '''
'''==========================================================='''

'''==========================================================='''
'''                     Modelling code                        '''
sketch = None
body = None
pad = None
doc = App.activeDocument()

##  FreeCAD object functions
def removePrev():
    global body
    global sketch
    global pad

    if(pad is not None):
        doc.removeObject(pad.Name)
        pad = None
    if(sketch is not None):
        doc.removeObject(sketch.Name)
        sketch = None
    if(body is not None):
        doc.removeObject(body.Name)
        body = None


def makeSketch(gearwheel):
    outer_r = gearwheel.outer_r
    inner_r = gearwheel.inner_r
    teeth = gearwheel.teeth
    tooth_h = gearwheel.tooth_h
    tolerance_a = gearwheel.tolerance_a

    removePrev()

    global body
    global sketch

    body = doc.addObject('PartDesign::Body', 'gearBody')

    sketch = body.newObject('Sketcher::SketchObject', 'gearSketch')
    sketch.AttachmentSupport = (doc.getObject('XY_Plane'), [''])
    sketch.MapMode = 'FlatFace'

    if(inner_r > 0):
        geoList = []
        geoList.append(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), inner_r))
        sketch.addGeometry(geoList, False)
        del geoList
    elif(inner_r < 0):
        geoList = []
        geoList.append(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), outer_r - inner_r))
        sketch.addGeometry(geoList, False)
        del geoList


    points = []
    angle_step = math.pi*2/(teeth*2)
    short_angle_step = (angle_step-tolerance_a)/2 * tooth_h / outer_r
        #   Displacement of tooth point against tooth base for perpendiculatity.

    angle = -angle_step/2  + tolerance_a/2# For axial symmetry "out of the box".

    for i in range(teeth*2):
        angle += angle_step + tolerance_a * (1 if i%2 else -1);

        if(i % 2):  # Radius without tooth, then perpendicular tooth.
            points.append(
                App.Vector(math.cos(angle), math.sin(angle), 0)*(outer_r - tooth_h)
            )

            points.append(
                App.Vector(math.cos(angle + short_angle_step),
                     math.sin(angle + short_angle_step), 0) * outer_r
            )
        else:
            points.append(
                App.Vector(math.cos(angle - short_angle_step),
                     math.sin(angle - short_angle_step), 0) * outer_r
            )

            points.append(
                App.Vector(math.cos(angle), math.sin(angle), 0)*(outer_r - tooth_h)
            )

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
    
    doc.recompute()

    return sketch

def makeGearWheel(gearwheel):
    extrusion = gearwheel.extrusion
    
    makeSketch(gearwheel)

    if(extrusion == 0):
        return

    global pad
    

    pad = body.newObject('PartDesign::Pad', 'gearPad')
    pad.Profile = (sketch, [''])
    pad.Length = abs(extrusion)
    pad.ReferenceAxis = (sketch, ['N_Axis'])
    pad.Reversed = (extrusion < 0)

    sketch.Visibility = False
    doc.recompute()
##  FreeCAD object functions end

'''                     Modelling code end                      '''
'''============================================================='''

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
                                      "\nAmount and outer radius influence tooth width."+
                                      "\nConnected gearwheels must have the same tooth width and the same tooth height."+
                                      "\nExtrusion may be positive, negative (reversed) and nil (sketch only)."
                                      )

    ##  "Error handling" end

    ## Utility functions
    def setupSpinBox(self, box, max, min = 0, step = 1, default = 0):
        box.setRange(min, max)
        box.setSingleStep(step)
        box.setValue(default)

    def areValuesBad(self):
        return self.ds_or.value() <= (self.ds_th.value()+self.ds_ir.value())

   
    ## Utility functions end
    
    ##  Event handling
   
    def onOk(self):
        if(self.areValuesBad()):
            self.callInformation()
            return

        gearwheel = Gearwheel(self.ds_or.value(),
                            self.ds_ir.value(),
                            self.is_at.value(),
                            self.ds_th.value(),
                            self.ds_e.value(),
                            self.ds_ta.value())

        makeGearWheel(gearwheel)

    def onCancel(self):
        self.close()
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
        self.ds_or.setFixedWidth(80)
        self.ds_or.move(220, 20)

        self.l_ir = QtGui.QLabel("Inner radius [mm]:", self)
        self.l_ir.move(20, 70)
        self.ds_ir = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_ir, max=1000000, min=-1000000, step=1, default=1) 
        self.ds_ir.setFixedWidth(80)
        self.ds_ir.move(220, 70)

        self.l_at = QtGui.QLabel("Amount of teeth:", self)
        self.l_at.move(20, 120)
        self.is_at = QtGui.QSpinBox(self)
        self.setupSpinBox(box=self.is_at, max = 1000, min = 2, step = 1, default = 16) 
        self.is_at.setFixedWidth(80)
        self.is_at.move(220, 120)

        self.l_th = QtGui.QLabel("Tooth height [mm]:", self)
        self.l_th.move(20, 170)
        self.ds_th = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_th, max=1000, min=0, step=0.1, default=1)
        self.ds_th.setFixedWidth(80)
        self.ds_th.move(220, 170)

        self.l_e = QtGui.QLabel("Extrusion [mm]:", self)
        self.l_e.move(20, 220)
        self.ds_e = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_e, 1000000, min=-1000000, step=1, default=0) 
        self.ds_e.setFixedWidth(80)
        self.ds_e.move(220, 220)

        self.l_ta = QtGui.QLabel("Tolerance angle [rad]:", self)
        self.l_ta.move(20, 270)
        self.ds_ta = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_ta, math.pi, min=-math.pi, step=0.01, default=0) 
        self.ds_ta.setFixedWidth(80)
        self.ds_ta.move(220, 270)
        ##  Inputs and labels end
        ##  Confirm/Cancel buttons
        self.bt_ok = QtGui.QPushButton("Make the gear", self)
        self.bt_ok.clicked.connect(self.onOk)
        self.bt_ok.move(190, 440)

        self.bt_cancel = QtGui.QPushButton("Quit", self)
        self.bt_cancel.clicked.connect(self.onCancel)
        self.bt_cancel.move(20, 440)
        ##  Confirm/Cancel buttons end
        
        self.show()


if (doc is None):
    QtGui.QMessageBox.information(None, "No nya", "Select a document first.")
else:
    form = GuiClass()

    try:
        last = gearwheel_from_json()
        #   Reads from file. 
        #   Otherwise throws.
        form.ds_or.setValue(last.outer_r)
        form.ds_ir.setValue(last.inner_r)
        form.is_at.setValue(last.teeth)
        form.ds_th.setValue(last.tooth_h)
        form.ds_e.setValue(last.extrusion)
        form.ds_ta.setValue(last.tolerance_a)
    except (FileNotFoundError):
        pass    #   Default values are used.
    finally:
        form.exec()
        last = Gearwheel(form.ds_or.value(), form.ds_ir.value(), form.is_at.value(), form.ds_th.value(), form.ds_e.value(), form.ds_ta.value())
        gearwheel_to_json(last)

'''               Graphical user interface end                '''
'''==========================================================='''


