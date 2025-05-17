from PySide import QtCore, QtGui
import FreeCAD as App
import math
##===========================================================================##
'''                         Graphical user interface code                   '''
class GuiClass(QtGui.QDialog):
    def __init__(self):
        super(GuiClass, self).__init__()
        self.initUI()

    class focusSpinBox(QtGui.QDoubleSpinBox):
        focusSignal = QtCore.Signal()

        def focusOutEvent(self, event):
            self.focusSignal.emit()
            super(QtGui.QDoubleSpinBox, self).focusOutEvent(event)


    ##  Error "handling"
    def callInformation(self):
        if(self.warnAllowed):
            self.warnAllowed = False
            QtGui.QMessageBox.information(None, "Nyaa",
                                      "Whole spring height must be:"+
                                      "\n- bigger than two times base height (but base height can be zero!);"+
                                      "\n- bigger than two times base height and two times radius in case of hook mode;"+
                                      "\n- bigger than two times base height and four times radius in case of circle mode."+
                                      "\n\nWire diameter, radius and height must be non-zero."+
                                      "\n\nPitch value must be above the wire diameter."+
                                      "\n\nAmount of spring revolutions can not be equal to zero."
                                      )

    def areValuesBad(self):
        return (self.ds_wd.value() == 0 or 
            self.ds_h.value() == 0 or 
            self.ds_r.value() == 0 or
            self.ds_re.value() == 0 or
            self.ds_ch.value() <= 0 or 
            self.ds_p.value() - self.ds_wd.value() <= 0 or
            self.ds_ch.value()/self.ds_re.value() < self.ds_wd.value())
    ##  Error "handling" end
    ##  Utility functions
    def setupSpinBox(self, box, max, min = 0, step = 1, default = 0):
        box.setRange(min, max)
        box.setSingleStep(step)
        box.setValue(default)

    def tryQuit(self, success):
        if(success):
            if(self.areValuesBad()):
                self.callInformation()
                return
        self.success = success
        self.close()
    ##  Utility functions end
    ##  Event handler methods
    ### Update handlers
    def updateCentralHeight(self):
        central_height = self.ds_h.value() - self.ds_bh.value()*2
        if(self.springtype == "hook"):
            central_height -= self.ds_r.value()*2
        elif(self.springtype == "circle"):
            central_height -= self.ds_r.value()*4
        self.ds_ch.setValue(central_height)
        ### After updating the height, if there are no bad values, update the pitch.
        if(self.areValuesBad()):
            self.callInformation()
        else:
            self.updatePitch()

    def updatePitch(self):
        ### If some of the input values are bad, warn and abort.
        if(self.areValuesBad()):
           self.callInformation()
        else:
            self.ds_p.setValue(self.ds_ch.value()/self.ds_re.value())

    def updateRevolutions(self):
        ### If some of the input values are bad, warn and abort.
        if(self.areValuesBad()):
           self.callInformation()
        else:
            self.ds_re.setValue(self.ds_ch.value()/self.ds_p.value())
    ### Update handlers end
    def onValueChanged(self):
        self.warnAllowed = True

    def onFlatChosen(self):
        self.springtype = "flat"
        self.updateCentralHeight()

    def onHookChosen(self):
        self.springtype = "hook"
        self.updateCentralHeight()

    def onCircleChosen(self):
        self.springtype = "circle"
        self.updateCentralHeight()

    def onPitchChosen(self):
        self.rotmode = "pitch"
        self.ds_p.setEnabled(True)
        self.ds_re.setEnabled(False)

    def onRevolutionsChosen(self):
        self.rotmode = "revolutions"
        self.ds_re.setEnabled(True)
        self.ds_p.setEnabled(False)

    def onOk(self):
        self.tryQuit(True)

    def onCancel(self):
        self.tryQuit(False)
    ##  Event handler methods end


    def initUI(self): 
        self.success = False
        self.springtype = "flat"
        self.rotmode = "pitch" 
        self.warnAllowed = True    #   A variable that allows a warning dialog to appear once and then wait until any value is altered.
        self.setGeometry(250, 250, 320, 400)
        self.setFixedSize(320, 480)
        self.setWindowTitle("Nya")

        ##  Labels and inputs.

        self.l_wd = QtGui.QLabel("Wire diameter [mm]:", self)
        self.l_wd.move(20, 20) 
        self.ds_wd = QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_wd, max=1000000, min=0.000001, step=0.1, default=0.5)
        self.ds_wd.valueChanged[float].connect(self.onValueChanged)
        self.ds_wd.setFixedWidth(80)
        self.ds_wd.move(220, 20)

        self.l_h = QtGui.QLabel("Height [mm]:", self)
        self.l_h.move(20, 70)
        self.ds_h = self.focusSpinBox(self)
        self.setupSpinBox(box=self.ds_h, max=1000000, min=0.000001, step=1, default=30)
        self.ds_h.valueChanged[float].connect(self.onValueChanged)
        self.ds_h.focusSignal.connect(self.updateCentralHeight)
        self.ds_h.setFixedWidth(80)
        self.ds_h.move(220, 70)

        self.l_bh = QtGui.QLabel("Base height [mm]:", self)
        self.l_bh.move(20, 120)
        self.ds_bh =self.focusSpinBox(self)
        self.setupSpinBox(box=self.ds_bh, max=1000000, min=0, step=1, default=2)
        self.ds_bh.valueChanged[float].connect(self.onValueChanged)
        self.ds_bh.focusSignal.connect(self.updateCentralHeight)
        self.ds_bh.setFixedWidth(80)
        self.ds_bh.move(220, 120)

        self.l_r = QtGui.QLabel("Radius [mm]:", self)
        self.l_r.move(20, 170)
        self.ds_r = self.focusSpinBox(self)
        self.setupSpinBox(box=self.ds_r, max=1000000, min=0.000001, step=1, default=2.5)
        self.ds_r.valueChanged[float].connect(self.onValueChanged)
        self.ds_r.focusSignal.connect(self.updateCentralHeight)
        self.ds_r.setFixedWidth(80)
        self.ds_r.move(220, 170)

        self.grp_pitch = QtGui.QButtonGroup(self)

        self.rb_p = QtGui.QRadioButton("Pitch [mm]:", self)
        self.rb_p.clicked.connect(self.onPitchChosen)
        self.rb_p.move(20, 220)
        self.grp_pitch.addButton(self.rb_p)
        self.rb_p.toggle()
        self.ds_p = self.focusSpinBox(self)
        self.setupSpinBox(box=self.ds_p, max=1000000, min=0.001, step=1, default=3)
        self.ds_p.valueChanged[float].connect(self.onValueChanged)
        self.ds_p.focusSignal.connect(self.updateRevolutions)
        self.ds_p.setFixedWidth(80)
        self.ds_p.move(220, 220)

        self.rb_re = QtGui.QRadioButton("Revolutions:", self)
        self.rb_re.clicked.connect(self.onRevolutionsChosen)
        self.rb_re.move(20, 270)
        self.grp_pitch.addButton(self.rb_re)
        self.ds_re = self.focusSpinBox(self)
        self.setupSpinBox(box=self.ds_re, max=1000000, min=0.001, step=1, default=8.67)
        self.ds_re.valueChanged[float].connect(self.onValueChanged)
        self.ds_re.focusSignal.connect(self.updatePitch)
        self.ds_re.setFixedWidth(80)
        self.ds_re.move(220, 270)
        self.ds_re.setEnabled(False)

        self.l_ch = QtGui.QLabel("Central part height:", self)
        self.l_ch.move(20, 320)
        self.ds_ch= QtGui.QDoubleSpinBox(self)
        self.setupSpinBox(box=self.ds_ch, max=1000000, min=-1000000, step=1, default=26)
        self.ds_ch.setFixedWidth(80)
        self.ds_ch.move(220, 320)
        self.ds_ch.setEnabled(False)
        ##  Labels and inputs end.

        ##  Additional options.
        self.grp_shape = QtGui.QButtonGroup(self)
        
        self.rb_flat = QtGui.QRadioButton("flat end", self)
        self.rb_flat.clicked.connect(self.onFlatChosen)
        self.rb_flat.move(20, 360)
        self.grp_shape.addButton(self.rb_flat)
        self.rb_flat.toggle()
        

        self.rb_hook = QtGui.QRadioButton("hook end", self)
        self.rb_hook.clicked.connect(self.onHookChosen)
        self.rb_hook.move(210, 360)
        self.grp_shape.addButton(self.rb_hook)

        self.rb_circle = QtGui.QRadioButton("circle end", self)
        self.rb_circle.clicked.connect(self.onCircleChosen)
        self.rb_circle.move(120, 390)
        self.grp_shape.addButton(self.rb_circle)
        ##  Additional options end.


        ##  Confirm/Cancel buttons.
        bt_cancel = QtGui.QPushButton("Cancel", self)
        bt_cancel.clicked.connect(self.onCancel)
        bt_cancel.move(20, 440)

        bt_ok = QtGui.QPushButton("Make the spring", self)
        bt_ok.clicked.connect(self.onOk)
        bt_ok.setAutoDefault(True)
        bt_ok.move(190, 440)
        ##  Confirm/Cancel buttons end.


        self.show()

form = GuiClass()
form.exec()
'''                         Graphical user interface end                    '''
##===========================================================================##

##===========================================================================##
'''                             Modelling code                              '''
##  FreeCAD object functions
def makeHelix(doc, height, pitch, radius, wire_diameter = 0.5):
    body = doc.addObject('PartDesign::Body','springBody')
    
    circle_sketch = body.newObject('Sketcher::SketchObject', 'circleSketch')
    circle_sketch.AttachmentSupport = (doc.getObject('XZ_Plane'),[''])
    circle_sketch.MapMode = 'FlatFace'

    geoList = []
    geoList.append(Part.Circle(App.Vector(radius, 0, 0), App.Vector(0, 0, 1), wire_diameter/2))
    circle_sketch.addGeometry(geoList,False)
    del geoList

    helix = body.newObject('PartDesign::AdditiveHelix','AdditiveHelix')
    helix.Profile = (circle_sketch, ['',])
    helix.ReferenceAxis = (circle_sketch,['V_Axis'])

    if(pitch < 0):
        helix.Pitch = -pitch
        helix.LeftHanded = 1
    else:
        helix.Pitch = pitch
        helix.LeftHanded = 0


    helix.Mode = 0
    helix.Height = height
    helix.Turns = height/pitch
    helix.Angle = 0
    helix.Growth = 0
    helix.Reversed = 0

    return body

def makeHook(doc, radius, wire_diameter = 0.5):
    body = doc.addObject("Part::Torus", "Torus")

    body.Radius1 = radius
    body.Radius2 = wire_diameter/2
    body.Angle1 = -180
    body.Angle2 = 180
    body.Angle3 = 150

    return body

def makeCircle(doc, radius, wire_diameter = 0.5):
    body = doc.addObject("Part::Torus", "Torus")

    body.Radius1 = radius
    body.Radius2 = wire_diameter/2
    body.Angle1 = -180
    body.Angle2 = 180
    body.Angle3 = 360

    return body
##  FreeCAD object functions end


if(form.success):
    doc = App.activeDocument()

    if(doc is None):
        QtGui.QMessageBox.information(None, "No nya", "Select a document first.")
    else:
        links = []

        ##  Get input
        wire_diameter = form.ds_wd.value()
        radius = form.ds_r.value()
        radius = radius - wire_diameter/2
        height = form.ds_h.value()
        base_height = form.ds_bh.value()
        base_rotation = base_height/wire_diameter*360

        revolutions = form.ds_re.value()
        pitch = form.ds_p.value()
        center_height = form.ds_ch.value()
        
          
        ##  Input values end 


        
        ##  Hooked spring
        if(form.springtype == "hook"):
            center_rotation = center_height/pitch*360

            lower_hook = makeHook(doc, radius, wire_diameter)
            lower_hook.Placement = App.Placement(App.Vector(0,0,radius),App.Rotation(App.Vector(-1,0,0),90))
            lower_hook.Label = "Lower hook"
            links.append(lower_hook)

            lower_placement = App.Placement(App.Vector(0, 0, radius), 
                                            App.Rotation(0, 0, 0))
            center_placement = App.Placement(App.Vector(0, 0, radius+base_height), 
                                             App.Rotation(base_rotation, 0, 0))
            upper_placement = App.Placement(App.Vector(0, 0, radius+base_height+center_height), 
                                            App.Rotation(base_rotation+center_rotation, 0, 0))

            upper_hook = makeHook(doc, radius, wire_diameter)
            upper_hook.Placement = App.Placement(App.Vector(0, 0, radius+base_height+center_height+base_height), 
                                                 App.Rotation(base_rotation+center_rotation+base_rotation, 0, 90), App.Vector(0,0,0))
            upper_hook.Label = "Upper hook"
            links.append(upper_hook)

        ##  Circle end
        elif(form.springtype == "circle"):
            center_rotation = center_height/pitch*360

            lower_circle = makeCircle(doc, radius, wire_diameter)
            lower_circle.Placement = App.Placement(App.Vector(radius,0,radius),
                                                   App.Rotation(90,0,90))
            lower_circle.Label = "Lower circle"
            links.append(lower_circle)

            lower_placement = App.Placement(App.Vector(0, 0, radius*2), 
                                            App.Rotation(0, 0, 0))
            center_placement = App.Placement(App.Vector(0, 0, radius*2+base_height), 
                                             App.Rotation(base_rotation, 0, 0))
            upper_placement = App.Placement(App.Vector(0, 0, radius*2+base_height+center_height), 
                                            App.Rotation(base_rotation+center_rotation, 0, 0))

            upper_circle = makeCircle(doc, radius, wire_diameter)
            upper_circle.Placement = App.Placement(App.Vector(radius*math.cos((base_rotation+center_rotation+base_rotation)/180*math.pi), radius*math.sin((base_rotation+center_rotation+base_rotation)/180*math.pi), radius*2+base_height+center_height+base_height+radius), 
                                                   App.Rotation(base_rotation+center_rotation+base_rotation+90, 0, 90), 
                                                   App.Vector(0,0,0))
            upper_circle.Label = "Upper circle"
            links.append(upper_circle)
            
        ##  Flat-end spring as default
        else:
            center_rotation = center_height/pitch*360

            lower_placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0))
            center_placement = App.Placement(App.Vector(0, 0, base_height), App.Rotation(base_rotation, 0, 0))
            upper_placement = App.Placement(App.Vector(0, 0, base_height+center_height), App.Rotation(base_rotation+center_rotation, 0, 0))
        ##  Spring end creation end
        

        ##  Spring center segment (common for all spring types)
        center = makeHelix(doc, center_height, pitch, radius, wire_diameter)
        center.Placement = center_placement
        center.Label = "Central segment"
        links.append(center) 
        ##  Spring center end
        
        
        ##  If possible, add spring base segments
        if(base_height >= wire_diameter):
            lower = makeHelix(doc, base_height, wire_diameter, radius, wire_diameter)
            lower.Placement = lower_placement
            lower.Label = "Lower segment"
            links.append(lower)
            upper = makeHelix(doc, base_height, wire_diameter, radius, wire_diameter)
            upper.Placement = upper_placement
            upper.Label = "Upper segment"
            links.append(upper)
        ##  Spring base segments end


        compound = doc.addObject("Part::Compound", "springCompound")
        compound.Links = links 


        doc.recompute()

'''                           Modelling code end                            '''
##===========================================================================##
