import bpy
import math
import mathutils
from math import sin, cos, radians, pi
from . import addon_updater_ops


#--------------#
#   Functions  #
#--------------#

def calculate_position_vertex(obj, axis):
    max_pos = -999999.0
    axis = axis.lower()
    
    
    if "x" in axis:        
        if "-" in axis:
            # Axis -X
            for vertex in obj.data.vertices:                
                world_pos = obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
                
                if world_pos[0] > max_pos:
                    max_pos = world_pos[0]
        
        else:
            # Axis X
            max_pos = max_pos * -1
            for vertex in obj.data.vertices:                
                world_pos = obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
                if world_pos[0] < max_pos:
                    max_pos = world_pos[0]
    
    
    elif "y" in axis:
        if "-" in axis:
            for vertex in obj.data.vertices:                
                world_pos = obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
                
                if world_pos[1] > max_pos:
                    max_pos = world_pos[1]
        
        else:
            max_pos = max_pos * -1
            for vertex in obj.data.vertices:                
                world_pos = obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
                if world_pos[1] < max_pos:
                    max_pos = world_pos[1]
                    
                    
    elif "z" in axis:
        if "-" in axis:
            for vertex in obj.data.vertices:                
                world_pos = obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
                
                if world_pos[2] > max_pos:
                    max_pos = world_pos[2]
        
        else:
            max_pos = max_pos * -1
            for vertex in obj.data.vertices:                
                world_pos = obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
                if world_pos[2] < max_pos:
                    max_pos = world_pos[2]
    else:
        max_pos = 1
        
    return max_pos
    

# Calculate object vertex top position
def obj_top_position(obj):
    max_z = -999999.0
    for vertex in obj.data.vertices:                
        # object vertices are in object space, translate to world space
        y_world = obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
        if y_world[2] > max_z:
            max_z = y_world[2]    
    return max_z
    
# Calculate object vertex bottom position    
def obj_bottom_position(obj):                                           
    min_z = 999999.0
    for vertex in obj.data.vertices:                
        # object vertices are in object space, translate to world space
        v_world = obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
        if v_world[2] < min_z:
            min_z = v_world[2]            
    return min_z
             
# Calculate Angle Curve
def point_pos(x0, y0, d, theta):
    theta_rad = pi/2 - radians(theta)
    return x0 + d*cos(theta_rad), y0 + d*sin(theta_rad)
    
# Reset selection and active object
def reset_state(active_obj, selected_objects):
    bpy.context.scene.objects.active = active_obj
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected_objects:
        obj.select = True

# Adding Empty
def add_empty(name, location, type, size):
    empty = bpy.data.objects.new(name, None)
    bpy.context.scene.objects.link(empty)
    empty.location = location
    empty.empty_draw_size = size
    empty.empty_draw_type = type
    if type == "IMAGE":
        empty.empty_image_offset[0] = -0.5
        empty.empty_image_offset[1] = -0.5
    return empty

# Setting Parent    
def set_parent(obj_a, obj_b):
    active_obj = bpy.context.scene.objects.active
    selected_objects = bpy.context.selected_objects
    
    # Set parent
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select = True
    obj_b.select = True   
    bpy.context.scene.objects.active = obj_b
    bpy.ops.object.parent_set()
    
    # Resets child's orgin to parent
    obj_a.select = True
    obj_b.select = False
    bpy.ops.object.location_clear(clear_delta=False)
    bpy.ops.object.origin_clear()

    reset_state(active_obj, selected_objects)
        
# Lock Objects Transform
def lock_transform(obj, lock=True):
    if lock:
        for index in range(len(obj.lock_location)):
            obj.lock_location[index] = True
            
        for index in range(len(obj.lock_rotation)):
            obj.lock_rotation[index] = True
            
        for index in range(len(obj.lock_scale)):
            obj.lock_scale[index] = True 
    
    else:
        for index in range(len(obj.lock_location)):
            obj.lock_location[index] = False
            
        for index in range(len(obj.lock_rotation)):
            obj.lock_rotation[index] = False
            
        for index in range(len(obj.lock_scale)):
            obj.lock_scale[index] = False 

def add_prop(obj, name, index, type, modifier_name):
    prop = obj.SimpleDeform.add()
    prop.name = name  
    prop.index = index
    prop.type = type
    prop.axis = 2
    prop.display_size = 0.0
    prop.slider_pos = 0.0
    prop.modifier_name = modifier_name


def find_parent(obj):
    current_obj = ""
    parent_obj = obj
    for x in range(len(bpy.data.objects)):
        current_obj = parent_obj
        parent_obj = parent_obj.parent
        if not parent_obj:
            break
    return current_obj
    
def find_connected(obj):    
    active_obj = bpy.context.scene.objects.active
    selected_objects = bpy.context.selected_objects
    parent_obj = find_parent(obj)    
    bpy.ops.object.select_all(action='DESELECT')    
    
    # Select all objects    
    bpy.context.scene.objects.active = parent_obj
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    parent_obj.select = True
    connected_objects = bpy.context.selected_objects
    
    reset_state(active_obj, selected_objects)
    return connected_objects
    
def return_prop_obj(obj_list, prop_name):
    for obj in obj_list:
        try:
            if obj.SimpleDeform[0].name == prop_name:
                return obj 
        except:
            pass
    return None
    
def has_prop_type(obj, prop_type):
    try:
        if obj.SimpleDeform[0].name == prop_type:
            return True        
        elif obj.SimpleDeform[0].type == prop_type:
            return True
        else:
            return False
    except:
        return False
        
def find_deform_empty():
    active_obj = bpy.context.scene.objects.active
    deform_objects = find_children(active_obj, True)
    
    e_deform_axis = return_prop_obj(deform_objects, "E_Deform_" + str(1))
    if e_deform_axis != None:
        return e_deform_axis
    else:
        return None

def find_children(obj, include_parent=False):
    selected_objects = bpy.context.selected_objects
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')            
    modified_selected_objects = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected_objects:
        obj.select = True
    if include_parent == True:
        modified_selected_objects.append(bpy.context.scene.objects.active)
    return modified_selected_objects
    
def find_child_with_prop(obj, prop_name):
    all_objects = []
    
    if obj.parent != None and len(obj.parent.SimpleDeform) > 0:
        if obj.SimpleDeform[0].name != "MainDeformEmpty":
            obj = obj.parent
    
    # Collect All Children
    all_objects.append(obj)
    for obj in obj.children:
        all_objects.append(obj)
    
    try:
        for child in all_objects:
            if child.SimpleDeform[0].name == prop_name:
                return child
    except:
        return None
    return None    
    
    
#--------------------------------#
#   Deform Modifier Properties   #
#--------------------------------#

### Set Curve Amount ###
def set_curve_angle(self, value):
    active_obj = self
    deformObject = find_child_with_prop(active_obj, "DeformObject")
    deformObject.modifiers[self.SimpleDeform[0].modifier_name].angle = value

def get_display_angle(self):
    active_obj = self
    deformObject = find_child_with_prop(active_obj, "DeformObject")
    angle_amount = deformObject.modifiers[self.SimpleDeform[0].modifier_name].angle
    return angle_amount
    
bpy.types.Object.DeformCurveAngle = bpy.props.FloatProperty(
                                    name = 'Bend Angle',
                                    description = 'Angle of bend deformation',
                                    subtype='ANGLE',
                                    get=get_display_angle,
                                    set=set_curve_angle,
                                    step=10)  



### Set Curve Amount ###
def set_curve_amount(self, value):
    # Check has property
    active_obj = self
    
    deform_axis = find_child_with_prop(active_obj, "DeformEmpty")
    active_obj.SimpleDeform[0].display_size = value

    curve_amount = value
    angle = math.degrees(active_obj.DeformCurveRotation) * -1
    
    if active_obj.SimpleDeform[0].axis == 2:
        deform_axis.location[0] = point_pos(0,0,curve_amount,angle)[0]
        deform_axis.location[1] = point_pos(0,0,curve_amount,angle)[1]
        
    if active_obj.SimpleDeform[0].axis == 1:
        deform_axis.location[2] = point_pos(0,0,curve_amount,angle)[0]*-1
        deform_axis.location[1] = point_pos(0,0,curve_amount,angle)[1]
        
    if active_obj.SimpleDeform[0].axis == 0:
        deform_axis.location[0] = point_pos(0,0,curve_amount,angle)[0]
        deform_axis.location[2] = point_pos(0,0,curve_amount,angle)[1]*-1


def get_display_amount(self):
    # Check has property
    active_obj = self
    
    if active_obj.SimpleDeform[0].display_size:
        return active_obj.SimpleDeform[0].display_size
    else:
        return 0
    
        
    
#bpy.types.Object.SimpleDeform[0].display_size = bpy.props.FloatProperty()    
bpy.types.Object.DeformCurveAmount = bpy.props.FloatProperty(
                                     name = 'Bend Size',
                                     description = "This affects how large the curve is.",
                                     get = get_display_amount,
                                     set = set_curve_amount,
                                     step = 1)    



### Set Curve Angle ###
def set_curve_rotation(self, value):
    # Check has property
    active_obj = self
    flip = 1
    deform_axis = find_child_with_prop(active_obj, "DeformEmpty")
    
    # Calculate Rotation
    if active_obj.SimpleDeform[0].axis == 2:
        deform_axis.rotation_euler[2] = value
    elif active_obj.SimpleDeform[0].axis == 1:
        deform_axis.rotation_euler[0] = value
    elif active_obj.SimpleDeform[0].axis == 0:
        deform_axis.rotation_euler[1] = value
    
    # Calculate Vector Length
    empty_location = deform_axis.location
    angle = math.degrees(value) * -1

    # Check if Size is less than 0
    if active_obj.SimpleDeform[0].display_size < 0:
        flip = -1
        
        
    if active_obj.SimpleDeform[0].axis == 2:
        world_location = mathutils.Vector([0,0,deform_axis.location[2]])
        distance = (world_location - empty_location).length
        deform_axis.location[0] = point_pos(0,0,distance,angle)[0]*flip
        deform_axis.location[1] = point_pos(0,0,distance,angle)[1]*flip
        
    elif active_obj.SimpleDeform[0].axis == 1:
        world_location = mathutils.Vector([deform_axis.location[0],0,0])
        distance = (world_location - empty_location).length
        deform_axis.location[1] = point_pos(0,0,distance,angle+90)[0]*flip
        deform_axis.location[2] = point_pos(0,0,distance,angle+90)[1]*flip
        
    elif active_obj.SimpleDeform[0].axis == 0:
        world_location = mathutils.Vector([deform_axis.location[0],0,0])
        distance = (world_location - empty_location).length
        deform_axis.location[1] = point_pos(0,0,distance,angle+90)[0]*flip
        deform_axis.location[2] = point_pos(0,0,distance,angle+90)[1]*flip
    
    bpy.context.scene.update()
    
def get_display_rotation(self):
    # Check has property
    active_obj = self
    if find_child_with_prop(active_obj, "DeformEmpty") != None:
        deform_axis = find_child_with_prop(active_obj, "DeformEmpty")
        
        # Calculate Rotation
        if active_obj.SimpleDeform[0].axis == 2:
            return deform_axis.rotation_euler[2]
        elif active_obj.SimpleDeform[0].axis == 1:
            return deform_axis.rotation_euler[0]
        elif active_obj.SimpleDeform[0].axis == 0:
            return deform_axis.rotation_euler[1]
    else:
        return 0
        
bpy.types.Object.DeformCurveRotation = bpy.props.FloatProperty(
                                       name = 'Bend Turn',
                                       description = 'This turns the bend deform around the axis',
                                       subtype = 'ANGLE',
                                       get = get_display_rotation,
                                       set = set_curve_rotation,
                                       step = 7)



#-------------------------#
#   Axis Deform Modifier  #
#-------------------------#

def set_deform_axis(self, value):
    # Check has property
    active_obj = self
    deform_axis = find_child_with_prop(active_obj, "DeformEmpty")
    rotation = active_obj.DeformCurveRotation
    
    active_obj.SimpleDeform[0].axis = value
    active_obj.DeformCurveAmount = 0
        
    # Set XYZ Axis
    if value == 2:
        # Rotation
        deform_axis.location = [0,0,0]
        deform_axis.rotation_euler = [0,0,0]
        deform_axis.rotation_euler[0] = radians(0)
        deform_axis.rotation_euler[1] = radians(90)
        
        # Location
        active_obj.DeformCurveRotation = radians(0)
        bpy.context.scene.update()
        
    elif value == 1:
        # Rotation
        deform_axis.location = [0,0,0]
        deform_axis.rotation_euler = [0,0,0]
        deform_axis.rotation_euler[0] = radians(90)
        deform_axis.rotation_euler[1] = radians(180)
        
        # Location
        active_obj.DeformCurveRotation = radians(0)
        bpy.context.scene.update()
        
    elif value == 0:
        # Rotation
        deform_axis.location = [0,0,0]
        deform_axis.rotation_euler = [0,0,0]
        deform_axis.rotation_euler[0] = radians(-90)
        deform_axis.rotation_euler[1] = radians(0)
        
        # Location
        active_obj.DeformCurveRotation = radians(0)
        bpy.context.scene.update()
        
    
def get_deform_axis(self):
    return self.SimpleDeform[0].axis


#bpy.types.Object.SimpleDeform[0].axis = bpy.props.IntProperty(default=2)
bpy.types.Object.DeformAxis = bpy.props.EnumProperty(
            name = "Bend Axis",
            description = "This is the axis for the Modifier",
            default = "2",
            items = [
            ("0" , "X" , "Description..."),
            ("1", "Y", "Some other description"),
            ("2", "Z", "Some other description")
            ],
            get = get_deform_axis,
            set = set_deform_axis)  

            
#-------------------------#
#   Deform Curve Limits   #
#-------------------------#
'''
Saved
elif active_obj.SimpleDeform[0].axis == 1:
        #obj_origin = deform_object.matrix_world.translation
        #obj_height = obj_max_x - obj_origin.x
        #deform_axis.location[0] = obj_height - (obj_height * value)
        """
        normalized_amount = height_x - (height_x * value)
        deform_axis.location[0] =  normalized_amount * -1
        """
# Check Object Height
    deform_modifier.show_viewport = False
    
    height_z = deform_object.dimensions[2]
    height_y = deform_object.dimensions[1]
    height_x = deform_object.dimensions[0]
    deform_modifier.show_viewport = True
'''

def move_empty_bottom_limits(deform_object, active_obj, axis):
    deform_axis = find_child_with_prop(active_obj, "DeformEmpty")
    bpy.context.scene.update()

    modifier_name = deform_object.SimpleDeform[0].modifier_name 
    curve_limits = deform_object.modifiers[modifier_name].limits
    
    top_value = 1 - curve_limits[0]
    bottom_value = curve_limits[1]
    
    # Objects Position    
    obj_max = calculate_position_vertex(deform_object, "-" + axis)
    obj_min = calculate_position_vertex(deform_object, axis)
    
    
    if active_obj.SimpleDeform[0].axis == 2:
        obj_origin = deform_object.matrix_world.translation
        obj_top_height = obj_max - obj_origin.z
        obj_bottom_height = obj_origin.z - obj_min
        
        distance_1 = obj_bottom_height - (obj_bottom_height * top_value)
        distance_2 = obj_top_height - (obj_top_height * bottom_value)
        final_distance = distance_2 - distance_1
        
        deform_axis.location[2] = final_distance
        
    elif active_obj.SimpleDeform[0].axis == 1:
        obj_origin = deform_object.matrix_world.translation
        obj_top_height = obj_max - obj_origin.x
        obj_bottom_height = obj_origin.x - obj_min
        
        distance_1 = obj_bottom_height - (obj_bottom_height * top_value)
        distance_2 = obj_top_height - (obj_top_height * bottom_value)
        final_distance = distance_2 - distance_1
        
        deform_axis.location[0] = final_distance
        
        #obj_origin = deform_object.matrix_world.translation
        #obj_height = obj_max_x - obj_origin.x
        #deform_axis.location[0] = obj_height - (obj_height * value)
        
    elif active_obj.SimpleDeform[0].axis == 0:
        obj_origin = deform_object.matrix_world.translation
        obj_top_height = obj_max - obj_origin.x
        obj_bottom_height = obj_origin.x - obj_min
        
        distance_1 = obj_top_height - (obj_top_height * top_value)
        distance_2 = obj_bottom_height - (obj_bottom_height * bottom_value)
        final_distance =  distance_1 - distance_2
        
        deform_axis.location[0] = final_distance



            
# Set Curve Top Limits
def set_curve_top_limits(self, value):
    active_obj = self
    deform_object = find_child_with_prop(active_obj, "DeformObject")
    modifier_name = self.SimpleDeform[0].modifier_name 
    curve_limits = deform_object.modifiers[modifier_name].limits
    #value_2 = self.deform_curve_bottom_limits
    
    
    # Set slider if greater
    offset = 0.02
    top_value = value
    bottom_value = self.deform_curve_bottom_limits
    
    if top_value > (bottom_value - offset):    
        bottom_value = value + offset
        curve_limits[1] = bottom_value
        move_empty_bottom_limits(deform_object, active_obj, "Z")
    
    if top_value > (1 - offset):
        value = 1 - offset
        
    curve_limits[0] = value
    
    if active_obj.SimpleDeform[0].axis == 2:
        move_empty_bottom_limits(deform_object, active_obj, "Z")
        
    elif active_obj.SimpleDeform[0].axis == 1:
        move_empty_bottom_limits(deform_object, active_obj, "X")
        
    elif active_obj.SimpleDeform[0].axis == 0:
        move_empty_bottom_limits(deform_object, active_obj, "X")
    
    
    
    
    
def get_display_top_limits(self):
    active_obj = self
    deform_object = find_child_with_prop(active_obj, "DeformObject")
    modifier_name = self.SimpleDeform[0].modifier_name  
    return deform_object.modifiers[modifier_name].limits[0]
    
bpy.types.Object.deform_curve_top_limits = bpy.props.FloatProperty(
                                           name = "Bend Top Limits",
                                           description = "This is the top limits of the bend curve.",
                                           min = 0,
                                           max = 1,
                                           get = get_display_top_limits,
                                           set = set_curve_top_limits,
                                           step = 0.5)


                                           

# Set Curve Bottom Limits
def set_curve_bottom_limits(self, value):
    active_obj = self
    
    deform_object = find_child_with_prop(active_obj, "DeformObject")
    modifier_index = 1
    modifier_name = self.SimpleDeform[0].modifier_name  
    deform_modifier = deform_object.modifiers[modifier_name]
    #value = value + self.SimpleDeform[0].slider_pos
    
    # Slider Value
    offset = 0.02
    value_2 = self.deform_curve_top_limits
    if value < (self.deform_curve_top_limits + offset):
        if self.deform_curve_top_limits <= 0:
            value =  0 + offset
            value_2 = 0
        else:
            value_2 =  value - 0.02
        #value = self.deform_curve_top_limits + 0.01
    
    
    deform_modifier.limits[0] = value_2
    deform_modifier.limits[1] = value
    
    if active_obj.SimpleDeform[0].axis == 2:
        move_empty_bottom_limits(deform_object, active_obj, "Z")
        
    elif active_obj.SimpleDeform[0].axis == 1:
        move_empty_bottom_limits(deform_object, active_obj, "X")
        
    elif active_obj.SimpleDeform[0].axis == 0:
        move_empty_bottom_limits(deform_object, active_obj, "X")
        
        

def get_display_bottom_limits(self):
    active_obj = self
    deform_object = find_child_with_prop(active_obj, "DeformObject")
    modifier_name = self.SimpleDeform[0].modifier_name 
    return deform_object.modifiers[modifier_name].limits[1]
    
bpy.types.Object.deform_curve_bottom_limits = bpy.props.FloatProperty(
                                              name = "Bend Bottom Limits",
                                              description = "This is the bottom limits of the bend curve.",
                                              min = 0,
                                              max = 1,
                                              get = get_display_bottom_limits,
                                              set = set_curve_bottom_limits,
                                              step = 0.5)


#-----------------#        
#   Slider Limits #
#-----------------#  

def set_slider_limits(self, value):
    top_limits = self.deform_curve_top_limits - self.SimpleDeform[0].slider_pos
    bottom_limits = self.deform_curve_bottom_limits - self.SimpleDeform[0].slider_pos
    
    current_value = self.SimpleDeform[0].slider_pos
    seperate_amount = bottom_limits - top_limits
    
    top_pos = top_limits + value
    bottom_pos = bottom_limits + value    
    self.SimpleDeform[0].slider_pos = value  
    
    # Activate sliders
    active_obj = self
    deform_object = find_child_with_prop(active_obj, "DeformObject")
    modifier_name = self.SimpleDeform[0].modifier_name 
    curve_limits = deform_object.modifiers[modifier_name].limits
    
    
    # Clamp Values
    if top_pos <= 0:
        top_pos = 0
        bottom_pos = seperate_amount
        self.SimpleDeform[0].slider_pos = current_value 
        
    elif bottom_pos >= 1:
        top_pos = 1 - seperate_amount
        bottom_pos = 1
        self.SimpleDeform[0].slider_pos = current_value 
    
    curve_limits[0] = top_pos
    curve_limits[1] = bottom_pos
    
    if active_obj.SimpleDeform[0].axis == 2:
        move_empty_bottom_limits(deform_object, active_obj, "Z")
        
    elif active_obj.SimpleDeform[0].axis == 1:
        move_empty_bottom_limits(deform_object, active_obj, "X")
        
    elif active_obj.SimpleDeform[0].axis == 0:
        move_empty_bottom_limits(deform_object, active_obj, "X")
    
    
    
    
def get_slider_limits(self):
    return self.SimpleDeform[0].slider_pos
                                              
# This adjust the current limits
bpy.types.Object.deform_curve_slider_limits = bpy.props.FloatProperty(
                                              name = "Bend Slider Limits",
                                              description = "This is the bottom limits of the bend curve.",
                                              default = 0.0,
                                              min = -1,
                                              max = 1,
                                              get = get_slider_limits,
                                              set = set_slider_limits,
                                              step = 0.1)                                             
                                              
#-------------------------#        
#   Delete Tool Modifier  #
#-------------------------# 
class DeleteDeformModifier(bpy.types.Operator):
    bl_idname = "object.delete_deform_modifier"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        # Check has property
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if bpy.context.scene.AddDeformModifier == True:                
                active_obj = obj
                
                MainDeformEmpty = find_child_with_prop(active_obj, "MainDeformEmpty")
                DeformObject = find_child_with_prop(active_obj, "DeformObject")
                DeformEmpty = find_child_with_prop(active_obj, "DeformEmpty")
                modifier_name = obj.SimpleDeform[0].modifier_name
                
                # Get Objects World Transform
                loc, rot, scale = DeformObject.matrix_world.decompose()
                
                # Delete 
                if obj.modifiers.find(modifier_name) >= 0:
                    bpy.ops.object.modifier_remove(modifier=modifier_name) 
                bpy.data.objects.remove(MainDeformEmpty, do_unlink = True)
                bpy.data.objects.remove(DeformEmpty, do_unlink = True)
                del DeformObject["SimpleDeform"]
                bpy.context.scene.AddDeformModifier = False
                
                # Prepare
                bpy.context.scene.objects.active = DeformObject
                DeformObject.select = True
                DeformObject.location = loc
                DeformObject.rotation_euler = rot.to_euler()
                DeformObject.scale = scale
                lock_transform(DeformObject, False)
            
        
        return {"FINISHED"}
            
#------------------------#
#   Add Tool Modifier    #
#------------------------#
        
def set_add_deform_modifier(self, value):
    global not_object
    if bpy.context.active_object is None:
        not_object = True
        return

    active_obj = bpy.context.active_object
    DeformEmpty = find_child_with_prop(active_obj, "DeformEmpty")
    
    if value == True and DeformEmpty == None:
        selected_objects = bpy.context.selected_objects
        correct_types = ['MESH', 'LATTICE', 'CURVE', 'SURFACE', 'FONT']
        select_empties = []
        prop_name = "Test"
        prop_type = "SimpleDeform"
        
        modifier_index = 1
        
        for obj in selected_objects:            
            if obj.type in correct_types:
            
                # Add Properties
                system_index = bpy.context.object.DeformModifierIndex + 1
                if len(obj.SimpleDeform) != 0:
                    modifier_index = obj.SimpleDeform[0].index + 1
                add_prop(obj, "DeformObject", modifier_index, prop_type, obj.DeformModifierName)

                # Create Names and Lock Object
                control_empty_name = 'E_' + obj.name + '_MainDeform'
                deform_empty_name = 'E_DeformAxis_' + str(modifier_index)                
                modifier_name = "BendDeformer_" + str(modifier_index)
                cage_name = 'E_' + obj.name + '_Cage'
                lock_transform(obj)
                
                # Get Object Dimensions
                obj_dimensions = list(obj.dimensions)
                del obj_dimensions[2]
                
                # Add Main Deform Empty
                empty_size = max(obj_dimensions) + 0.5
                main_deform_empty = add_empty(control_empty_name, obj.location, 'IMAGE', empty_size) 
                set_parent(obj, main_deform_empty)
                add_prop(main_deform_empty, "MainDeformEmpty", modifier_index, prop_type, obj.DeformModifierName)
                select_empties.append(main_deform_empty)
                main_deform_empty.show_x_ray = False
                
                # Add Modifier Deform Empty
                deform_empty = add_empty(deform_empty_name, obj.location, 'SINGLE_ARROW', 1.2)
                deform_empty.rotation_euler[1] = radians(90)     
                set_parent(deform_empty, main_deform_empty)
                add_prop(deform_empty, "DeformEmpty", modifier_index, prop_type, obj.DeformModifierName) 
                
                deform_empty.layers[19] = True
                deform_empty.layers[0] = False
                
                deform_empty.show_x_ray = True
                deform_empty.hide = True
                #deform_empty.hide_select = True
                
                
                
                # Add Bend Deform Modifier
                deform_modifer = obj.modifiers.new(obj.DeformModifierName, "SIMPLE_DEFORM")
                deform_modifer.deform_method = 'BEND'
                deform_modifer.angle = radians(45)
                deform_modifer.origin = deform_empty
                
                # Check if flat Plane
                if list(obj.dimensions)[2] == 0:
                    obj.DeformAxis = "0"
                    deform_modifer.angle = radians(-45)
            

            else:
                not_object = True
                '''
                ### Add Bend Cage
                bpy.ops.mesh.primitive_cube_add(enter_editmode=True, location=obj.location)                
                new_loc = list(mathutils.Vector(obj.location) + mathutils.Vector([0,0,1]))
                bpy.ops.transform.translate(value=new_loc)
                bpy.ops.mesh.subdivide(number_cuts=5)
                bpy.ops.object.editmode_toggle()
                
                # Change Bend Cage
                bpy.context.object.name = cage_name
                bpy.context.object.draw_type = 'WIRE'
                bpy.context.object.dimensions = obj_dimensions
                set_parent(bpy.context.object, main_deform_empty)
                '''
                
        
        
        reset_state(obj, [obj])
        
        
def get_display_add_modifier(self):
    correct_types = ['MESH', 'LATTICE', 'CURVE', 'SURFACE', 'FONT']
    active_obj = bpy.context.active_object
    global not_object
    
    if active_obj is not None:
        # Check if valid Object
        if active_obj.type in correct_types:
            not_object = False
        
        if has_prop_type(active_obj, "DeformObject"):
            return True
            
    return False
        
        
bpy.types.Scene.AddDeformModifier = bpy.props.BoolProperty(get=get_display_add_modifier, set=set_add_deform_modifier)                                  
        

#-----------------------#        
#   Select Deform Mesh  #
#-----------------------# 
class SelectDeformObjecct(bpy.types.Operator):
    bl_idname = "object.select_deform_object"
    bl_label = "Select Deform Obj"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        if find_child_with_prop(context.object, "DeformObject") != None:
            object = find_child_with_prop(context.object, "DeformObject")
            
            bpy.ops.object.select_all(action='DESELECT')
            object.select = True
            bpy.context.scene.objects.active = object
            
        return {"FINISHED"}
        
        
#=======================#        
#   Deform Properties   #
#=======================#          
class DeformProperties(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
            name='Deform Name',
            default='None',
            description='Parents deform name'
            )
    index = bpy.props.IntProperty(
            name='Modifier Index',
            default=0,
            description='Tells the addon how mny modifiers have been added'
            )
    type = bpy.props.StringProperty(
            name='Deform Name',
            default='None',
            description='Parents deform name'
            )
    axis = bpy.props.IntProperty(
            name='Deform Axis',
            default=0,
            description='This is the axis of the modifier'
            )
    display_size = bpy.props.FloatProperty(
            name='Display Size',
            default=0.0,
            description='This is the display size for the modifier'
            )
    slider_pos = bpy.props.FloatProperty(
            name='Slider Position',
            default=0.0,
            description='This is the display size for the modifier'
            )
    modifier_name = bpy.props.StringProperty(
            name='Modifier Name',
            default="",
            description='This is the Modifiers name'
            )
bpy.utils.register_class(DeformProperties) 
bpy.types.Object.SimpleDeform = bpy.props.CollectionProperty(type=DeformProperties)

# Properties
bpy.types.Object.DeformModifierIndex = bpy.props.IntProperty(
                                       name = 'Modifier Index',
                                       default = 0,
                                       description = 'Tells the addon how mny modifiers have been added'
                                       )     



def set_slider_limits(self, value):
    if self.modifiers.find(self.SimpleDeform[0].modifier_name) >= 0:
        self.modifiers[self.SimpleDeform[0].modifier_name].name = value
    self.SimpleDeform[0].modifier_name = value
    
   
def get_modifier_name(self):
    modifier_name = "Archway"
    if len(self.SimpleDeform) > 0:
        modifier_name = self.SimpleDeform[0].modifier_name
    return modifier_name
   
bpy.types.Object.DeformModifierName = bpy.props.StringProperty(
                                       name = 'Modifier Name',
                                       default = "Archway",
                                       description = 'The name of the modifier',
                                       get=get_modifier_name,
                                       set=set_slider_limits
                                       )
is_deform_object = False
not_object = False
select_mesh = False
has_modifier = False

class SimpleDeformPanel(bpy.types.Panel):
    bl_label = "Archway Pro"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    
    @classmethod
    def poll(cls, context):
        global is_deform_object
        global select_mesh
        global has_modifier
        
        # Check if object connected
        if has_prop_type(context.object, "DeformEmpty"):            
            select_mesh = True
        elif has_prop_type(context.object, "MainDeformEmpty"):
            select_mesh = True
        else:
            select_mesh = False
            
        # Check Object has Deform Tool
        if has_prop_type(context.object, "DeformObject"):
            if find_child_with_prop(context.object, "DeformEmpty") != None:
                is_deform_object = True
                has_modifier = False
                
                for modifier in context.object.modifiers:
                    if modifier.name == context.object.SimpleDeform[0].modifier_name and modifier.type == "SIMPLE_DEFORM":
                        has_modifier = True
            else:
                is_deform_object = False
        else:
            is_deform_object = False
        
        return True
        
    #----------------------------------#
    #   UI Panel for Deform Modifier   #
    #----------------------------------#
    def draw(self, context):
        object = context.object
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align=True)
        
        
        # Show Select Button
        if select_mesh == True:
            col.operator("object.select_deform_object")
            col.separator()
            
        # Add modifier
        elif not is_deform_object:
            col.prop(scene, 'AddDeformModifier', text="Add Modifier",icon='MOD_SIMPLEDEFORM')         
            col.separator()
            
        # Warning Message if trying to add modifier to invalid object
        if not_object == True:
            col.label(text="Select valid object")    
        
        
        
        # Show Modifier information if valid selection
        if is_deform_object:            
            box = layout.box()
            row = box.row(align=True)
            
            row.label(text="", icon="MOD_SIMPLEDEFORM")
            row.separator()
            row.prop(object, "DeformModifierName", "")
            #row.label("Arch-way")
            #row.separator()
            row.operator("object.delete_deform_modifier", emboss=True, icon="X")
            
            if has_modifier:
                row = box.row(align=True)
                row.prop(object, "DeformAxis", text="Angle", expand=True)
                col = box.column(align=True)
                col.separator()
                
                col.label(text="Deform") 
                col.prop(object, "DeformCurveAngle", text="Angle")
                col.prop(object, "DeformCurveAmount", text="Size")
                col.prop(object, "DeformCurveRotation", text="Turn")
                col.separator()
                col.separator()
                
                col.label(text="Limits") 
                col.prop(bpy.context.object, "deform_curve_top_limits", text="", slider=True)
                col.prop(bpy.context.object, "deform_curve_bottom_limits", text="", slider=True)
                
                row = col.row(align=True)
                row.label(text=" Slide", icon="ARROW_LEFTRIGHT") 
                row.prop(bpy.context.object, "deform_curve_slider_limits", text="")
            
            else:
                col = box.column(align=True)
                col.label(text="Missing Modifier") 
 

 
# Archway preferences
class ArchwayPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # addon updater preferences

    auto_check_update = bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False,
        )
    
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=7,
        min=0,
        )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )

    def draw(self, context):
        
        layout = self.layout

        # updater draw function
        addon_updater_ops.update_settings_ui(self,context)       
        
def register():
    #bpy.utils.register_module(__name__)
    addon_updater_ops.register(bl_info)    
    bpy.utils.register_class(ArchwayPreferences)
    
    bpy.utils.register_class(SimpleDeformPanel)
    bpy.utils.register_class(DeleteDeformModifier)
    bpy.utils.register_class(SelectDeformObjecct)
    
def unregister():    
    #bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(ArchwayPreferences)
    bpy.utils.unregister_class(SimpleDeformPanel)
    bpy.utils.unregister_class(DeformProperties)
    bpy.utils.unregister_class(DeleteDeformModifier)
    bpy.utils.unregister_class(SelectDeformObjecct)
    
if __name__ == '__main__':
    register()