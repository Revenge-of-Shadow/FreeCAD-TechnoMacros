import math
'''==================================================================================='''
'''                                Modelling functions                                '''
'''==================================================================================='''
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


def makePhillipsSketch(body, diameter, thickness):
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


def subtractDrive(body, sketch, height):
    pocket_drive = body.newObject('PartDesign::Pocket', 'DrivePocket')
    sketch.AttachmentOffset = App.Placement(App.Vector(0, 0, -height), App.Rotation(0,0,0))
    pocket_drive.Profile = (sketch, ['',])
    pocket_drive.Length = height/2          #   Possibly can be made customizable but eh.
    pocket_drive.ReferenceAxis = (sketch, ['N_Axis'])
    pocket_drive.Reversed = 1

    return pocket_drive

'''==================================================================================='''
'''                             Modelling functions end                               '''
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


body = None
if(body is None):
    body = doc.addObject('PartDesign::Body','ScrewBody')
else:
    body.removeObjectsFromDocument()


makeCylinderPad(body, diameter, length)
makeSubtractiveHelix(body, length, diameter, wire_diameter, pitch)
#revolveSketchZ(body, makeHeadConeSketch(body, diameter, head_diameter, head_height))
revolveSketchZ(body, makeHeadShroomSketch(body, head_diameter, head_height, length/2))
subtractDrive(body, makePhillipsSketch(body, drive_diameter, drive_thickness), head_height)
doc.recompute()
