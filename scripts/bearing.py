from PySide import QtCore, QtGui
import Part
import math
from FreeCAD import Base

'''==========================================================='''
'''                     Modelling code                        '''
def makeBearing(inner_r, outer_R, thick, ball_amount):
    ball_r = min((outer_R-inner_r)/2, thick/2)/2

    middle_r = (inner_r + outer_R)/2

    inner_R = middle_r-ball_r/2
    outer_r = middle_r+ball_r/2

    fillet_r = 0.1

# Ball center as offset.
    ball_hoffset = ((outer_r - inner_R)/2 + inner_R)
    ball_voffset = thick / 2



    o_line_1 = Part.makeLine((outer_R, 0, thick - fillet_r), (outer_R, 0, fillet_r))
    o_line_2 = Part.makeLine((outer_R - fillet_r, 0, 0), (outer_r+fillet_r, 0, 0))
    o_line_3 = Part.makeLine((outer_r, 0, fillet_r), (outer_r, 0, thick - fillet_r))
    o_line_4 = Part.makeLine((outer_r + fillet_r, 0, thick), (outer_R-fillet_r, 0, thick))

    o_rnding_1 = Part.makeCircle(fillet_r, Base.Vector(outer_R - fillet_r, 0, fillet_r), Base.Vector(0, 1, 0), 0, 90)
    o_rnding_2 = Part.makeCircle(fillet_r, Base.Vector(outer_r + fillet_r, 0, fillet_r), Base.Vector(0, 1, 0), 90, 180)
    o_rnding_3 = Part.makeCircle(fillet_r, Base.Vector(outer_r + fillet_r, 0, thick - fillet_r), Base.Vector(0, 1, 0), 180, 270)
    o_rnding_4 = Part.makeCircle(fillet_r, Base.Vector(outer_R - fillet_r, 0, thick - fillet_r), Base.Vector(0, 1, 0), 270, 360)

    o_wire = Part.Wire([o_line_1, o_rnding_1, o_line_2, o_rnding_2, o_line_3, o_rnding_3, o_line_4, o_rnding_4])
    o_wire = Part.Face(o_wire)
    o_wire = o_wire.revolve(Base.Vector(0, 0, 1), Base.Vector(0, 0, 360))
    o_circle = Part.makeCircle(ball_r, Base.Vector(ball_hoffset, 0, ball_voffset), Base.Vector(0, 1, 0), 0, 360)
    o_circwire = Part.Wire([o_circle])
    o_circwire = Part.Face(o_circwire)
    o_circwire = o_circwire.revolve(Base.Vector(0, 0, 1), Base.Vector(0, 0, 360))
    o_wire = o_wire.cut(o_circwire)
    Part.show(o_wire)



    i_line_1 = Part.makeLine((inner_R, 0, thick - fillet_r), (inner_R, 0, fillet_r))
    i_line_2 = Part.makeLine((inner_R - fillet_r, 0, 0), (inner_r+fillet_r, 0, 0))
    i_line_3 = Part.makeLine((inner_r, 0, fillet_r), (inner_r, 0, thick - fillet_r))
    i_line_4 = Part.makeLine((inner_r + fillet_r, 0, thick), (inner_R - fillet_r, 0, thick))

    i_rnding_1 = Part.makeCircle(fillet_r, Base.Vector(inner_R - fillet_r, 0, fillet_r), Base.Vector(0, 1, 0), 0, 90)
    i_rnding_2 = Part.makeCircle(fillet_r, Base.Vector(inner_r + fillet_r, 0, fillet_r), Base.Vector(0, 1, 0), 90, 180)
    i_rnding_3 = Part.makeCircle(fillet_r, Base.Vector(inner_r + fillet_r, 0, thick - fillet_r), Base.Vector(0, 1, 0), 180, 270)
    i_rnding_4 = Part.makeCircle(fillet_r, Base.Vector(inner_R - fillet_r, 0, thick - fillet_r), Base.Vector(0, 1, 0), 270, 360)

    i_wire = Part.Wire([i_line_1, i_rnding_1, i_line_2, i_rnding_2, i_line_3, i_rnding_3, i_line_4, i_rnding_4])
    i_wire = Part.Face(i_wire)
    i_wire = i_wire.revolve(Base.Vector(0, 0, 1), Base.Vector(0, 0, 360))
    i_circle = Part.makeCircle(ball_r, Base.Vector(ball_hoffset, 0, ball_voffset), Base.Vector(0, 1, 0), 0, 360)
    i_circwire = Part.Wire([i_circle])
    i_circwire = Part.Face(i_circwire)
    i_circwire = i_circwire.revolve(Base.Vector(0, 0, 1), Base.Vector(0, 0, 360))
    i_wire = i_wire.cut(i_circwire)
    Part.show(i_wire)


    for i in range(ball_amount):
        ball = Part.makeSphere(ball_r)
        angle = (i*2*math.pi)/ball_amount
        ball_placement = (ball_hoffset*math.cos(angle), ball_hoffset*math.sin(angle), ball_voffset)
        ball.translate(ball_placement)
        Part.show(ball)

    App.ActiveDocument.recompute()
    Gui.ActiveDocument.ActiveView.viewAxometric()
    Gui.SendMsgToActiveView("ViewFit")
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
        makeBearing(self.ds_id.value()/2, self.ds_od.value()/2, self.s_h.value(), self.s_b.value())
        self.close()

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
        self.s_h = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.s_h, max = 1000000, min = 1, step = 1, default = 6)
        self.s_h.setFixedWidth(80)
        self.s_h.move(220, 120)

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
form.exec()
'''               Graphical user interface end                '''
'''==========================================================='''




