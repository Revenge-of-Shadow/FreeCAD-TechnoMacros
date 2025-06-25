from PySide import  QtGui
import math
import json

filename = "last_bearing.json"
'''==========================================================='''
'''                       Class  code                         '''
'''==========================================================='''
def obj_dict(obj):
    return obj.__dict__

class Bearing:
    def __init__(self, inner_r, outer_R, height, ball_amount):
        self.inner_r = inner_r
        self.outer_R = outer_R
        self.height = height
        self.ball_amount = ball_amount

def bearing_to_json(obj):
    with open(filename, "w") as file:
        json.dump(obj, file, default = obj_dict)

def bearing_from_json():
    with open(filename, "r") as file:
        data = json.load(file)
        return Bearing(data["inner_r"], data["outer_R"], data["height"], data["ball_amount"])

'''==========================================================='''
'''                     Class code end                        '''
'''==========================================================='''
'''==========================================================='''
'''                     Modelling code                        '''
'''==========================================================='''
def removeBody(doc, body):
    body.removeObjectsFromDocument()
    doc.removeObject(body.Name)
    body = None

def remakeBody(doc, body):
    if(body is not None):
        removeBody(doc, body)
    return  doc.addObject('PartDesign::Body', 'BearingBody')


def revolveSketchZ(body, sketch):
    revolution = body.newObject('PartDesign::Revolution', 'Revolution')
    revolution.Profile = (sketch, ['',])
    revolution.ReferenceAxis = (sketch, ['V_Axis'])
    revolution.Angle = 360

    return revolution


def makeBearingBody(bearing):
    global body
    global doc
    body    =   remakeBody(doc, body)

    inner_r = bearing.inner_r
    outer_R = bearing.outer_R
    height = bearing.height
    ball_amount = bearing.ball_amount

    ball_r = min((outer_R-inner_r)/2, height/2)/2

    middle_r = (inner_r + outer_R)/2

    inner_R = middle_r-ball_r/2
    outer_r = middle_r+ball_r/2


    sketch_bearing  =   body.newObject('Sketcher::SketchObject', 'BearingSketch')
    sketch_bearing.AttachmentSupport    =   (doc.getObject('XZ_Plane'), [''])
    sketch_bearing.MapMode  =   'FlatFace'

    angle  =    math.acos((outer_r - middle_r)/ball_r)

    ##  Inner half of the sketch
    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(inner_r, -height/2, 0),
                               App.Vector(inner_r, height/2, 0)
                            ),  False)

    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(inner_r, height/2, 0),
                               App.Vector(inner_R, height/2, 0)
                            ),  False)

    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(inner_R, height/2, 0),
                               App.Vector(inner_R, ball_r*math.sin(angle), 0)
                            ),  False)

    sketch_bearing.addGeometry(Part.ArcOfCircle(
        Part.Circle(App.Vector(middle_r, 0, 0), App.Vector(0, 0, 1), ball_r),
        math.pi-angle, math.pi+angle)
                               )
    

    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(inner_R, -ball_r*math.sin(angle), 0),
                               App.Vector(inner_R, -height/2, 0)
                            ),  False)

    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(inner_R, -height/2, 0),
                               App.Vector(inner_r, -height/2, 0)
                            ),  False)
    ##  Inner half of the sketch end

    ##  Outer half of the sketch
    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(outer_R, -height/2, 0),
                               App.Vector(outer_R, height/2, 0)
                            ),  False)

    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(outer_R, height/2, 0),
                               App.Vector(outer_r, height/2, 0)
                            ),  False)

    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(outer_r, height/2, 0),
                               App.Vector(outer_r, ball_r*math.sin(angle), 0)
                            ),  False)

    sketch_bearing.addGeometry(Part.ArcOfCircle(
        Part.Circle(App.Vector(middle_r, 0, 0), App.Vector(0, 0, 1), ball_r),
        -angle, angle)
                               )
    

    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(outer_r, -ball_r*math.sin(angle), 0),
                               App.Vector(outer_r, -height/2, 0)
                            ),  False)

    sketch_bearing.addGeometry(Part.LineSegment(
                               App.Vector(outer_r, -height/2, 0),
                               App.Vector(outer_R, -height/2, 0)
                            ),  False)
    ##  Outer half of the sketch end
    sketch_bearing.Visibility   =   False
    
    revolveSketchZ(body, sketch_bearing)

    return body

def makeBearingBalls(bearing):
    if(bearing.ball_amount == 0):
        return
    
    global balls
    global doc
    for i in balls:
        doc.removeObject(i.Name)
    balls = []

    angle_step = math.pi*2/bearing.ball_amount
    offset  =   (bearing.inner_r + bearing.outer_R)/2
    ball_r = min((bearing.outer_R-bearing.inner_r)/2, bearing.height/2)/2       #   I could not figure out a way to avoid repeating it.

    for i in range(bearing.ball_amount):
        balls.append(doc.addObject('Part::Sphere', 'Ball_001'))
        balls[i].Placement = App.Placement(offset*App.Vector(math.cos(angle_step*i), math.sin(angle_step*i), 0), App.Rotation(0,0,0), App.Vector(0,0,0))
        balls[i].Radius = ball_r


def makeBearing(bearing):
    makeBearingBody(bearing)
    makeBearingBalls(bearing)
    doc.recompute()
'''==========================================================='''
'''                     Modelling code end                      '''
'''============================================================='''

'''============================================================='''
'''                Graphical user interface code                '''
'''==========================================================='''
class GuiClass(QtGui.QDialog):
    def __init__(self):
        super(GuiClass, self).__init__()
        self.initUI()

    ##  "Error handling"
    def callInformation(self):
        QtGui.QMessageBox.information(None, "Nya nya", "Outer diameter must be bigger than inner diameter.")
    ##  "Error handling" end

    
    ##  Utility functions
    def setupSpinBox(self, box, max, min = 0, step = 1, default = 0):
        box.setRange(min, max)
        box.setSingleStep(step)
        box.setValue(default)

    def areValuesBad(self):
        return self.ds_od.value() <= self.ds_id.value()
    ##  Utility functions end
    ##  Event handling
    def onConfirm(self):
        if(self.areValuesBad()):
            self.callInformation()
            return
        bearing = Bearing(self.ds_id.value()/2, self.ds_od.value()/2, self.ds_h.value(), self.s_b.value())
        makeBearing(bearing)

    def onCancel(self):
        self.close()
    ##  Event handling end
    
    def initUI(self):
        self.setGeometry(250, 250, 320, 400)
        self.setFixedSize(320, 480)
        self.setWindowTitle("Nya")

        ##  Labels and inputs
        self.l_id = QtGui.QLabel("Inner diameter [mm]:", self)
        self.l_id.move(20, 20)
        self.ds_id = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_id, max = 1000000, min = 0, step = 1, default = 6)
        self.ds_id.setFixedWidth(80)
        self.ds_id.move(220, 20)

        self.l_od = QtGui.QLabel("Outer diameter [mm]:", self)
        self.l_od.move(20, 70)
        self.ds_od = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_od, max = 1000000, min = 1, step = 1, default = 17)
        self.ds_od.setFixedWidth(80)
        self.ds_od.move(220, 70)

        self.l_h = QtGui.QLabel("Height [mm]:", self)
        self.l_h.move(20, 120)
        self.ds_h = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_h, max = 1000000, min = 1, step = 1, default = 6)
        self.ds_h.setFixedWidth(80)
        self.ds_h.move(220, 120)

        self.l_b = QtGui.QLabel("Ball amount:", self)
        self.l_b.move(20, 170)
        self.s_b = QtGui.QSpinBox(self)
        self.setupSpinBox(box=self.s_b, max = 1000000, min = 0, step = 1, default = 10)
        self.s_b.setFixedWidth(80)
        self.s_b.move(220, 170)
        ##  Labels and inputs end
        ##  Confirm/Cancel buttons
        self.bt_confirm = QtGui.QPushButton("Make the bearing", self)
        self.bt_confirm.clicked.connect(self.onConfirm)
        self.bt_confirm.move(190, 440)

        self.bt_cancel = QtGui.QPushButton("Quit", self)
        self.bt_cancel.clicked.connect(self.onCancel)
        self.bt_cancel.move(20, 440)
        ##  Confirm/Cancel buttons end
        self.show()

form = GuiClass()
'''==========================================================='''
'''               Graphical user interface end                '''
'''==========================================================='''
doc = App.activeDocument()

if(doc is None):
    QtGui.QMessageBox.information(None, "No nya", "Select a document first.")
    close()

body = None
balls = []


try:
    last = bearing_from_json()
    #   Reads from file.
    #   Otherwise throws.
    form.ds_id.setValue(last.inner_r)
    form.ds_od.setValue(last.outer_R)
    form.ds_h.setValue(last.height)
    form.s_b.setValue(last.ball_amount)
except FileNotFoundError:
    pass    #   Default values are used.
finally:
    form.exec()
    last = Bearing(form.ds_id.value(), form.ds_od.value(), form.ds_h.value(), form.s_b.value())
    bearing_to_json(last)




