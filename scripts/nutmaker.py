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
    def __init__(self, wire_diameter, diameter_outer, diameter_inner, length, edges):
        self.wire_diameter  =   wire_diameter
        self.diameter_outer       =   diameter_outer
        self.diameter_inner       =   diameter_inner
        self.length         =   length
        self.edges          =   edges
    
def nut_to_json(obj):
    with open(filename, "w") as file:
        json.dump(obj, file, default = obj_dict)

def nut_from_json():
    with open(filename, "r") as file:
        data = json.load(file)
        print(data)
        return  Nut(data["wire_diameter"], data["diameter_outer"], data["diameter_inner"], data["length"], data["edges"])

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
    return doc.addObject('PartDesign::Body','ScrewBody')


def makeNutPad(body, diameter_outer, diameter_inner, length, edges):
    sketch_nut = body.newObject('Sketcher::SketchObject','NutSketch')
    sketch_nut.AttachmentSupport = (doc.getObject('XY_Plane'),[''])
    sketch_nut.MapMode = 'FlatFace'

    sketch_nut.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), diameter_inner/2),False)

    angle_step = math.pi*2/edges
    for i in range(edges-1):
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
    makeSubtractiveHelix(body, nut.length, nut.diameter, nut.wire_diameter, nut.pitch)

    doc.recompute()

    return body
'''==================================================================================='''
'''                             Modelling functions end                               '''
'''==================================================================================='''
'''==================================================================================='''
'''                                     Interface                                     '''
'''==================================================================================='''




