import math
import json
from PySide import QtGui

filename = "last_nut.json"

'''==================================================================================='''
'''                                       Class                                       '''
'''==================================================================================='''
def obj_dict(obj):
    return obj.__dict__

class Nut:
    def __init__(self, wire_diameter, diameter_outer, diameter_inner, length, edges, pitch):
        self.wire_diameter  =   wire_diameter
        self.diameter_outer =   diameter_outer
        self.diameter_inner =   diameter_inner
        self.length         =   length
        self.edges          =   edges
        self.edges          =   edges
        self.pitch          =   pitch
    
def nut_to_json(obj):
    with open(filename, "w") as file:
        json.dump(obj, file, default = obj_dict)

def nut_from_json():
    with open(filename, "r") as file:
        data = json.load(file)
        return  Nut(data["wire_diameter"], data["diameter_outer"], data["diameter_inner"], data["length"], data["edges"], data["pitch"])
'''==================================================================================='''
'''                                     Class end                                     '''
'''==================================================================================='''
'''==================================================================================='''
'''                                Modelling functions                                '''
'''==================================================================================='''
def removeBody(doc, body):
    body.removeObjectsFromDocument()
    doc.removeObject(body.Name)
    body = None

def remakeBody(doc, body):
    if(body is not None):
        removeBody(doc, body)
    return doc.addObject('PartDesign::Body','NutBody')


def makeNutPad(body, diameter_outer, diameter_inner, length, edges):
    sketch_nut = body.newObject('Sketcher::SketchObject','NutSketch')
    sketch_nut.AttachmentSupport = (doc.getObject('XY_Plane'),[''])
    sketch_nut.MapMode = 'FlatFace'

    sketch_nut.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), diameter_inner/2),False)

    angle_step = math.pi*2/edges
    for i in range(edges):
        sketch_nut.addGeometry(Part.LineSegment(
                               App.Vector(math.cos(angle_step*i)*diameter_outer, math.sin(angle_step*i)*diameter_outer, 0),
                               App.Vector(math.cos(angle_step*(i+1))*diameter_outer, math.sin(angle_step*(i+1))*diameter_outer, 0)
                                ), False)
    sketch_nut.Visibility = False

    pad_nut = body.newObject('PartDesign::Pad','NutPad')
    pad_nut.Profile = (sketch_nut, ['',])
    pad_nut.ReferenceAxis = (sketch_nut,['N_Axis'])
    pad_nut.Length = length
    pad_nut.TaperAngle = 0
    pad_nut.UseCustomVector = 0
    pad_nut.Direction = (0, 0, 1)
    pad_nut.AlongSketchNormal = 1
    pad_nut.Type = 0
    pad_nut.UpToFace = None
    pad_nut.Reversed = 0
    pad_nut.Midplane = 1
    pad_nut.Offset = 0

    return pad_nut


def makeSubtractiveHelix(body, length, diameter, wire_diameter, pitch):
    height = length + wire_diameter

    sketch_helix = body.newObject('Sketcher::SketchObject','HelixSketch')
    sketch_helix.AttachmentSupport = (doc.getObject('YZ_Plane'),[''])
    sketch_helix.MapMode = 'FlatFace'

    sketch_helix.addGeometry(Part.Circle(App.Vector(diameter/2, -(height)/2, 0), App.Vector(0, 0, 1), wire_diameter/2),False)
    sketch_helix.Visibility = False

    helix = body.newObject('PartDesign::SubtractiveHelix','SubtractiveHelix')
    helix.Profile = (sketch_helix, ['',])
    helix.ReferenceAxis = (sketch_helix, ['V_Axis'])
    helix.Mode = 0
    helix.Pitch = pitch
    helix.Height = height
    helix.Angle = 0
    helix.Growth = 0
    helix.LeftHanded = 0
    helix.Reversed = 0

    return helix


def makeNut(nut):
    global doc
    global body
    body    =   remakeBody(doc, body)

    makeNutPad(body, nut.diameter_outer, nut.diameter_inner, nut.length, nut.edges)
    makeSubtractiveHelix(body, nut.length, nut.diameter_inner, nut.wire_diameter, nut.pitch)

    doc.recompute()

    return body
'''==================================================================================='''
'''                             Modelling functions end                               '''
'''==================================================================================='''
'''==================================================================================='''
'''                                     Interface                                     '''
'''==================================================================================='''
class   GuiClass(QtGui.QDialog):
    def __init__(self, nut):
        super(GuiClass, self).__init__()
        self.nut = nut
        self.initUI()

    def setupSpinBox(self, box, max, min = 0, step = 1, default = 0, width = 80, offset_multiplier = 0):
        box.setRange(min, max)
        box.setSingleStep(step)
        box.setValue(default)
        box.setFixedWidth(width)
        box.move(220, 20+50*offset_multiplier)

    def putLabel(self, varname, text, offset_multiplier):
        exec(f"self.l_{varname} = QtGui.QLabel(\"{text}\", self)")
        exec(f"self.l_{varname}.move(20, 20+50*{offset_multiplier})")


    def areValuesBad(self):
        return False

    
    def onMake(self):
        if(not self.areValuesBad()):
            self.nut = Nut(self.ds_di.value()-self.ds_dr.value(), self.ds_do.value(), self.ds_di.value(), self.ds_l.value(), self.s_e.value(), self.ds_p.value())
            makeNut(self.nut)

    def onQuit(self):
        if(not self.areValuesBad()):
            self.nut = Nut(self.ds_di.value()-self.ds_dr.value(), self.ds_do.value(), self.ds_di.value(), self.ds_l.value(), self.s_e.value(), self.ds_p.value())
        self.close()


    def initUI(self):
        self.setGeometry(250, 250, 320, 400)
        self.setFixedSize(320, 480)
        self.setWindowTitle("Nya")

        ##  Labels and inputs
        self.putLabel("do", "Outer diameter [mm]:", 0)
        self.ds_do  =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_do, max = 100000, min = 0, step = 1, default = self.nut.diameter_outer, offset_multiplier = 0)

        self.putLabel("di", "Inner diameter [mm]:", 1)
        self.ds_di  =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_di, max = 100000, min = 0, step = 1, default = self.nut.diameter_inner, offset_multiplier = 1)

        self.putLabel("dr", "Root diameter [mm]:",  2)
        self.ds_dr  =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_dr, max = 100000, min = 0, step = 1, default = self.nut.diameter_inner+self.nut.wire_diameter, offset_multiplier =  2)

        self.putLabel("l", "Thickness [mm]:", 3)
        self.ds_l  =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_l, max = 100000, min = 0, step = 1, default = self.nut.diameter_inner, offset_multiplier = 3)

        self.putLabel("e", "Edges:", 4)
        self.s_e  =   QtGui.QSpinBox(self)
        self.setupSpinBox(self.s_e, max = 100000, min = 0, step = 1, default = self.nut.edges, offset_multiplier = 4)
    
        self.putLabel("p", "Pitch [mm]:", 5)
        self.ds_p  =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_p, max = 100000, min = 0, step = 1, default = self.nut.pitch, offset_multiplier = 5)
     ##  Labels and inputs end
        self.b_q = QtGui.QPushButton("Quit", self)
        self.b_q.clicked.connect(self.onQuit)
        self.b_q.move(20, 20+50*7)

        self.b_m = QtGui.QPushButton("Make the nut", self)
        self.b_m.clicked.connect(self.onMake)
        self.b_m.move(190, 20+50*7+20) 

        self.show()
'''==================================================================================='''
'''                                   Interface end                                   '''
'''==================================================================================='''
doc = App.activeDocument()

if(doc is None):
    QtGui.QMessageBox.information(None, "No nya", "Select a document first.")
    close()

wire_diameter = 0.5
diameter_outer = 4
diameter_inner = 3
length = 2
edges = 6
pitch = wire_diameter + wire_diameter/2

last = Nut(wire_diameter, diameter_outer, diameter_inner, length, edges, pitch)

body = None

try:
    last = nut_from_json()
    #   Reads the file.
    #   Otherwise throws.
except  FileNotFoundError:
    #   Default values are used.
    pass
finally:
    form = GuiClass(last)
    form.exec()
    nut_to_json(form.nut)
