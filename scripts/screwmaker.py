import math
import json
from PySide import QtGui

filename = "last_screw.json"
'''==================================================================================='''
'''                                       Class                                       '''
'''==================================================================================='''
def obj_dict(obj):
    return obj.__dict__

class Screw:
    def __init__(self, wire_diameter, diameter, length, pitch, head_height, head_diameter, drive_diameter, drive_thickness, head_type, drive_type):
        self.wire_diameter      =   wire_diameter
        self.diameter           =   diameter
        self.length             =   length
        self.pitch              =   pitch
        self.head_height        =   head_height
        self.head_diameter      =   head_diameter
        self.drive_diameter     =   drive_diameter
        self.drive_thickness    =   drive_thickness
        self.head_type          =   head_type
        self.drive_type         =   drive_type

def screw_to_json(obj):
    with open(filename, "w") as file:
        json.dump(obj, file, default = obj_dict)

def screw_from_json():
    with open(filename, "r") as file:
        data = json.load(file)
        return Screw(data["wire_diameter"], data["diameter"], data["length"], data["pitch"], data["head_height"], data["head_diameter"], data["drive_diameter"], data["drive_thickness"], data["head_type"], data["drive_type"]) 

'''==================================================================================='''
'''                                     Class end                                     '''
'''==================================================================================='''
'''==================================================================================='''
'''                                Modelling functions                                '''
'''==================================================================================='''
def removeBody(doc, body):
    body.removeObjectsFromDocument()
    doc.removeOvject(body)
    body = None

def remakeBody(doc, body):
    if(body is not None):
        removeBody(doc, body)
    return doc.addObject('PartDesign::Body','ScrewBody')


def makeCylinderPad(body, diameter, length):
    sketch_cylinder = body.newObject('Sketcher::SketchObject','CylinderSketch')
    sketch_cylinder.AttachmentSupport = (doc.getObject('XY_Plane'),[''])
    sketch_cylinder.MapMode = 'FlatFace'

    sketch_cylinder.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), diameter/2),False)
    sketch_cylinder.Visibility = False

    pad_cylinder = body.newObject('PartDesign::Pad','CylinderPad')
    pad_cylinder.Profile = (sketch_cylinder, ['',])
    pad_cylinder.ReferenceAxis = (sketch_cylinder,['N_Axis'])
    pad_cylinder.Length = length
    pad_cylinder.TaperAngle = 0
    pad_cylinder.UseCustomVector = 0
    pad_cylinder.Direction = (0, 0, 1)
    pad_cylinder.AlongSketchNormal = 1
    pad_cylinder.Type = 0
    pad_cylinder.UpToFace = None
    pad_cylinder.Reversed = 0
    pad_cylinder.Midplane = 0
    pad_cylinder.Offset = 0

    return pad_cylinder


def makeSubtractiveHelix(body, length, diameter, wire_diameter, pitch):
    height = length + wire_diameter

    sketch_helix = body.newObject('Sketcher::SketchObject','HelixSketch')
    sketch_helix.AttachmentSupport = (doc.getObject('YZ_Plane'),[''])
    sketch_helix.MapMode = 'FlatFace'

    sketch_helix.addGeometry(Part.Circle(App.Vector(diameter/2, -wire_diameter/2, 0), App.Vector(0, 0, 1), wire_diameter/2),False)
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


def makeHeadConeSketch(body, diameter, bigger_diameter, height):
    sketch_head = body.newObject('Sketcher::SketchObject','HeadSketch')
    sketch_head.AttachmentSupport = (doc.getObject('YZ_Plane'),[''])
    sketch_head.MapMode = 'FlatFace'

    sketch_head.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(diameter/2, 0, 0)), False)
    sketch_head.addGeometry(Part.LineSegment(App.Vector(diameter/2, 0, 0), App.Vector(bigger_diameter/2, -height, 0)), False)
    sketch_head.addGeometry(Part.LineSegment(App.Vector(bigger_diameter/2, -height, 0), App.Vector(0, -height, 0)), False)
    sketch_head.addGeometry(Part.LineSegment(App.Vector(0, -height, 0), App.Vector(0, 0, 0)), False)
    sketch_head.Visibility = False

    return sketch_head


def makeHeadShroomSketch(body, diameter, height, curve_radius):
    sketch_head = body.newObject('Sketcher::SketchObject', 'HeadSketch')
    sketch_head.AttachmentSupport = (doc.getObject('YZ_Plane'),[''])
    sketch_head.MapMode = 'FlatFace'

    end_angle = -math.acos(diameter/2/curve_radius)
    end_y     = curve_radius + curve_radius*math.sin(end_angle)-height
    sketch_head.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(diameter/2, 0, 0)), False)
    sketch_head.addGeometry(Part.LineSegment(App.Vector(diameter/2, 0, 0), App.Vector(diameter/2, end_y, 0)), False)
    sketch_head.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(0, curve_radius-height, 0), App.Vector(0, 0, 1), curve_radius), -math.pi/2, end_angle))
    sketch_head.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(0, -height, 0)), False)
    sketch_head.Visibility = False

    return sketch_head


def revolveSketchZ(body, sketch):
    revolution = body.newObject('PartDesign::Revolution', 'Head')
    revolution.Profile = (sketch, ['',])
    revolution.ReferenceAxis = (sketch, ['V_Axis'])
    revolution.Angle = 360

    return revolution


def makeSlitSketch(body, diameter, thickness):
    sketch_drive = body.newObject('Sketcher::SketchObject', 'DriveSketch')
    sketch_drive.AttachmentSupport = (doc.getObject('XY_Plane'),[''])
    sketch_drive.MapMode = 'FlatFace'

    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, diameter/2, 0), App.Vector(thickness/2, diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, diameter/2, 0), App.Vector(thickness/2, -diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, -diameter/2, 0), App.Vector(-thickness/2, -diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, -diameter/2, 0), App.Vector(-thickness/2, diameter/2, 0)), False)
    sketch_drive.Visibility = False
    
    return sketch_drive


def makeFrearsonSketch(body, diameter, thickness):
    sketch_drive = body.newObject('Sketcher::SketchObject', 'DriveSketch')
    sketch_drive.AttachmentSupport = (doc.getObject('XY_Plane'),[''])
    sketch_drive.MapMode = 'FlatFace'

    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, diameter/2, 0), App.Vector(thickness/2, diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, diameter/2, 0), App.Vector(thickness/2, thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, thickness/2, 0), App.Vector(diameter/2, thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(diameter/2, thickness/2, 0), App.Vector(diameter/2, -thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(diameter/2, -thickness/2, 0), App.Vector(thickness/2, -thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, -thickness/2, 0), App.Vector(thickness/2, -diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, -diameter/2, 0), App.Vector(-thickness/2, -diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, -diameter/2, 0), App.Vector(-thickness/2, -thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, -thickness/2, 0), App.Vector(-diameter/2, -thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-diameter/2, -thickness/2, 0), App.Vector(-diameter/2, thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-diameter/2, thickness/2, 0), App.Vector(-thickness/2, thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, thickness/2, 0), App.Vector(-thickness/2, diameter/2, 0)), False)
    sketch_drive.Visibility = False
    
    return sketch_drive


def makePhillipsSketch(body, diameter, thickness):
    sketch_drive = body.newObject('Sketcher::SketchObject', 'DriveSketch')
    sketch_drive.AttachmentSupport = (doc.getObject('XY_Plane'),[''])
    sketch_drive.MapMode = 'FlatFace'

    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, diameter/2, 0), App.Vector(thickness/2, diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, diameter/2, 0), App.Vector(thickness/2, thickness, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, thickness, 0), App.Vector(thickness, thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness, thickness/2, 0), App.Vector(diameter/2, thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(diameter/2, thickness/2, 0), App.Vector(diameter/2, -thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(diameter/2, -thickness/2, 0), App.Vector(thickness, -thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness, -thickness/2, 0), App.Vector(thickness/2, -thickness, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, -thickness, 0), App.Vector(thickness/2, -diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(thickness/2, -diameter/2, 0), App.Vector(-thickness/2, -diameter/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, -diameter/2, 0), App.Vector(-thickness/2, -thickness, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, -thickness, 0), App.Vector(-thickness, -thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness, -thickness/2, 0), App.Vector(-diameter/2, -thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-diameter/2, -thickness/2, 0), App.Vector(-diameter/2, thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-diameter/2, thickness/2, 0), App.Vector(-thickness, thickness/2, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness, thickness/2, 0), App.Vector(-thickness/2, thickness, 0)), False)
    sketch_drive.addGeometry(Part.LineSegment(App.Vector(-thickness/2, thickness, 0), App.Vector(-thickness/2, diameter/2, 0)), False)
    sketch_drive.Visibility = False
    
    return sketch_drive


def subtractDrive(body, sketch, height):
    pocket_drive = body.newObject('PartDesign::Pocket', 'DrivePocket')
    sketch.AttachmentOffset = App.Placement(App.Vector(0, 0, -height), App.Rotation(0,0,0))
    pocket_drive.Profile = (sketch, ['',])
    pocket_drive.Length = height/2          #   Possibly can be made customizable but eh.
    pocket_drive.ReferenceAxis = (sketch, ['N_Axis'])
    pocket_drive.Reversed = 1

    return pocket_drive


def makeScrew(screw):
    return
'''==================================================================================='''
'''                             Modelling functions end                               '''
'''==================================================================================='''
'''==================================================================================='''
'''                                     Interface                                     '''
'''==================================================================================='''
class GuiClass(QtGui.QDialog):
    def __init__(self, screw):
        super(GuiClass, self).__init__()
        self.screw = screw
        self.initUI()
    
    def setupSpinBox(self, box, max, min = 0, step = 1, default = 0, width = 80, offset_multiplier = 0):
        box.setRange(min, max)
        box.setSingleStep(step)
        box.setValue(default)
        box.setFixedWidth(width)
        box.move(220, 20+50*offset_multiplier)


    def areValuesBad(self):
        return false
    

    def onMake(self):
        makeScrew(self.screw)

    def onQuit(self):
        self.close()


    def putLabel(self, varname, text, offset_multiplier):
        exec(f"self.l_{varname} = QtGui.QLabel(\"{text}\", self)")
        exec(f"self.l_{varname}.move(20, 20+50*{offset_multiplier})")
    

    def initUI(self):
        self.setFixedSize(320, 700)
        self.setWindowTitle("Nya")

        ##  Labels and inputs
        self.putLabel("d", "Screw diameter [mm]:", 0)
        self.ds_d   =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_d, max = 100000, min = 0, step = 0.1, default = self.screw.diameter, offset_multiplier = 0)

        self.putLabel("rd", "Root diameter [mm]:", 1)
        self.ds_rd  =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_rd, max = 100000, step = 0.1, default = self.screw.diameter-self.screw.wire_diameter, offset_multiplier = 1)

        self.putLabel("l", "Thread length [mm]:",  2)
        self.ds_l   =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_l, max = 100000, step = 1, default = self.screw.length, offset_multiplier =  2)

        self.putLabel("p", "Pitch [mm]:", 3)
        self.ds_p   =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_p, max = 100000, step = 0.1, default = self.screw.pitch, offset_multiplier = 3)

        self.putLabel("ht", "Head type:", 5)


        self.putLabel("hh", "Head length [mm]:", 6)
        self.ds_hh  =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_hh, max = 100000, step = 1, default = self.screw.head_height, offset_multiplier = 6)

        self.putLabel("hd", "Head diameter [mm]:", 7)
        self.ds_hd    =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_hd, max = 100000, step = 1, default = self.screw.head_diameter, offset_multiplier = 7)

        self.putLabel("dt", "Drive type:", 9)

        self.putLabel("dd", "Drive diameter [mm]:", 10)
        self.ds_dd    =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_dd, max = 100000, step = 1, default = self.screw.drive_diameter, offset_multiplier = 10)

        self.putLabel("dt", "Drive thickness [mm]:", 11)
        self.ds_dt    =   QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(self.ds_dt, max = 100000, step = 0.1, default = self.screw.drive_thickness, offset_multiplier = 11)
        ##  Labels and inputs end
        self.b_q = QtGui.QPushButton("Quit", self)
        self.b_q.clicked.connect(self.onQuit)
        self.b_q.move(20, 20+50*12.5)

        self.b_m = QtGui.QPushButton("Make the screw", self)
        self.b_m.clicked.connect(self.onMake)
        self.b_m.move(190, 20+50*12.5) 

        self.show()
'''==================================================================================='''
'''                                   Interface end                                   '''
'''==================================================================================='''



doc = App.activeDocument()

if(doc is None):
    QtGui.QMessageBox.information(None, "No nya", "Select a document first.")
    close()

wire_diameter = 0.5
diameter = 3
length = 10
pitch = wire_diameter + wire_diameter/2
head_height = 2
head_diameter = 5
drive_diameter = head_diameter/2
drive_thickness = wire_diameter
head_type = "Mushroom"
drive_type = "Phillips"

last = Screw(wire_diameter, diameter, length, pitch, head_height, head_diameter, drive_diameter, drive_thickness, head_type, drive_type)


try:
    last = screw_from_json()
    #   Reads from file.
    #   Otherwise throws.
except  FileNotFoundError:
    #   Default values are used.
    pass
finally:
    form = GuiClass(last)
    form.exec()
    screw_to_json(form.screw)

