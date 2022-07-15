import bpy

# Enum property.
mode_items = [
    ("ALL_COLLIDER", "all", "Show/Hide all collisions", 1),
    ("SIMPLE_COMPLEX", "simple_and_complex", "Show/Hide all simple-complex collisions", 2),
    ("SIMPLE", "simple", "Show/Hide all simple collisions", 4),
    ("COMPLEX", "complex", "Show/Hide all complex collisions", 8),
    ("OBJECTS", "objects", "Show/Hide all complex collisions", 16),
]


class COLLISION_OT_Visibility(bpy.types.Operator):
    """Hide/Show collision objects"""
    bl_idname = "object.hide_collisions"
    bl_label = "Hide Collision Meshes"
    bl_description = 'Hide/Show collision objects'
    bl_options = {"REGISTER", "UNDO"}

    hide: bpy.props.BoolProperty(
        name='Hide/Unhide',
        default=True
    )

    mode: bpy.props.EnumProperty(items=mode_items,
                                 name='Hide Mode',
                                 default='ALL_COLLIDER'
                                 )

    def execute(self, context):
        scene = context.scene
        count = 0

        # objects = [ob.hide_set(True) for ob in bpy.context.view_layer.objects if ob.get('isCollider')]
        for ob in bpy.context.view_layer.objects:
            if self.mode == 'ALL_COLLIDER':
                if ob.get('isCollider') == True:
                    ob.hide_viewport = self.hide
                    count += 1

            elif self.mode == 'OBJECTS':
                if not ob.get('isCollider'):
                    ob.hide_viewport = self.hide
                    count += 1

            else:  # if self.mode == 'SIMPLE' or self.mode == 'COMPLEX'
                if ob.get('isCollider') and ob.get('collider_type') == self.mode:
                    ob.hide_viewport = self.hide
                    count += 1

        if count == 0:
            if self.hide:
                self.report({'INFO'}, 'No objects to hide.')
            else:
                self.report({'INFO'}, 'No objects to show.')
            return {'CANCELLED'}

        return {'FINISHED'}

class COLLISION_OT_simple_show(COLLISION_OT_Visibility):
    bl_idname = "object.simple_show_collisions"
    bl_label = "Show Simple Colliders"
    bl_description = 'Show all objects that are defined as simple colliders'

class COLLISION_OT_simple_hide(COLLISION_OT_Visibility):
    bl_idname = "object.simple_hide_collisions"
    bl_label = "Hide Simple Colliders"
    bl_description = 'Hide all objects that are defined as simple colliders'

class COLLISION_OT_complex_show(COLLISION_OT_Visibility):
    bl_idname = "object.complex_show_collisions"
    bl_label = "Show Complex Colliders"
    bl_description = 'Show all objects that are defined as complex colliders'

class COLLISION_OT_complex_hide(COLLISION_OT_Visibility):
    bl_idname = "object.complex_hide_collisions"
    bl_label = "Hide Complex Colliders"
    bl_description = 'Hide all objects that are defined as complex colliders'

class COLLISION_OT_simple_complex_show(COLLISION_OT_Visibility):
    bl_idname = "object.simple_complex_show_collisions"
    bl_label = "Show Simple and Complex Colliders"
    bl_description = 'Show all objects that are defined as simple and complex colliders'

class COLLISION_OT_simple_complex_hide(COLLISION_OT_Visibility):
    bl_idname = "object.simple_complex_hide_collisions"
    bl_label = "Hide Simple and Complex Colliders"
    bl_description = 'Hide all objects that are defined as simple and complex colliders'

class COLLISION_OT_all_show(COLLISION_OT_Visibility):
    bl_idname = "object.all_show_collisions"
    bl_label = "Show all Colliders"
    bl_description = 'Show all collider objects: Simple, Complex, Simple and Complex.'

class COLLISION_OT_all_hide(COLLISION_OT_Visibility):
    bl_idname = "object.all_hide_collisions"
    bl_label = "Hide all Colliders"
    bl_description = 'Hide all collider objects: Simple, Complex, Simple and Complex.'

class COLLISION_OT_non_collider_show(COLLISION_OT_Visibility):
    bl_idname = "object.non_collider_show_collisions"
    bl_label = "Show non Colliders"
    bl_description = 'Show all objects that are not colliders.'

class COLLISION_OT_non_collider_hide(COLLISION_OT_Visibility):
    bl_idname = "object.non_collider_hide_collisions"
    bl_label = "Hide non Colliders"
    bl_description = 'Hide all objects that are not colliders.'


class COLLISION_OT_Selection(bpy.types.Operator):
    """Select/Deselect collision objects"""
    bl_idname = "object.select_collisions"
    bl_label = "Select Collision Meshes"
    bl_description = 'Select/Deselect collision objects'
    bl_options = {"REGISTER", "UNDO"}

    select: bpy.props.BoolProperty(
        name='Select/Un-Select',
        default=True
    )

    mode: bpy.props.EnumProperty(items=mode_items,
                                 name='Hide Mode',
                                 default='ALL_COLLIDER'
                                 )

    def execute(self, context):
        scene = context.scene
        count = 0

        if self.select:
            for ob in bpy.context.view_layer.objects:
                if self.mode == 'ALL_COLLIDER':
                    if ob.get('isCollider') == True:
                        count += 1
                        ob.select_set(self.select)
                    else:
                        ob.select_set(not self.select)

                elif self.mode == 'OBJECTS':
                    if not ob.get('isCollider'):
                        count += 1
                        ob.select_set(self.select)
                    else:
                        ob.select_set(not self.select)

                else:  # if self.mode == 'SIMPLE' or self.mode == 'COMPLEX'
                    if ob.get('isCollider') and ob.get('collider_type') == self.mode:
                        count += 1
                        ob.select_set(self.select)
                    else:
                        ob.select_set(not self.select)

        else: # self.select = False
            for ob in bpy.context.view_layer.objects:
                if self.mode == 'ALL_COLLIDER':
                    if ob.get('isCollider') == True:
                        count += 1
                        ob.select_set(self.select)
                elif self.mode == 'OBJECTS':
                    if not ob.get('isCollider'):
                        count += 1
                        ob.select_set(self.select)
                else:  # if self.mode == 'SIMPLE' or self.mode == 'COMPLEX'
                    if ob.get('isCollider') and ob.get('collider_type') == self.mode:
                        count += 1
                        ob.select_set(self.select)

        if count == 0:
            if self.select:
                self.report({'INFO'}, 'No objects to select.')
            else:
                self.report({'INFO'}, 'No objects to deselect.')
            return {'CANCELLED'}

        return {'FINISHED'}


class COLLISION_OT_simple_select(COLLISION_OT_Selection):
    bl_idname = "object.simple_select_collisions"
    bl_label = "Select Simple Colliders"
    bl_description = 'Select all objects that are defined as simple colliders'


class COLLISION_OT_simple_deselect(COLLISION_OT_Selection):
    bl_idname = "object.simple_deselect_collisions"
    bl_label = "Deselect Simple Colliders"
    bl_description = 'Deselect all objects that are defined as simple colliders'


class COLLISION_OT_complex_select(COLLISION_OT_Selection):
    bl_idname = "object.complex_select_collisions"
    bl_label = "Select Complex Colliders"
    bl_description = 'Select all objects that are defined as complex colliders'


class COLLISION_OT_complex_deselect(COLLISION_OT_Selection):
    bl_idname = "object.complex_deselect_collisions"
    bl_label = "Deselect Complex Colliders"
    bl_description = 'Deselect all objects that are defined as complex colliders'


class COLLISION_OT_simple_complex_select(COLLISION_OT_Selection):
    bl_idname = "object.simple_complex_select_collisions"
    bl_label = "Select Simple and Complex Colliders"
    bl_description = 'Select all objects that are defined as simple and complex colliders'


class COLLISION_OT_simple_complex_deselect(COLLISION_OT_Selection):
    bl_idname = "object.simple_complex_deselect_collisions"
    bl_label = "Deselect Simple and Complex Colliders"
    bl_description = 'Deselect all objects that are defined as simple and complex colliders'


class COLLISION_OT_all_select(COLLISION_OT_Selection):
    bl_idname = "object.all_select_collisions"
    bl_label = "Select all Colliders"
    bl_description = 'Select all collider objects: Simple, Complex, Simple and Complex.'


class COLLISION_OT_all_deselect(COLLISION_OT_Selection):
    bl_idname = "object.all_deselect_collisions"
    bl_label = "Deselect all Colliders"
    bl_description = 'Deselect all collider objects: Simple, Complex, Simple and Complex.'


class COLLISION_OT_non_collider_select(COLLISION_OT_Selection):
    bl_idname = "object.non_collider_select_collisions"
    bl_label = "Select non Colliders"
    bl_description = 'Select all objects that are not colliders.'


class COLLISION_OT_non_collider_deselect(COLLISION_OT_Selection):
    bl_idname = "object.non_collider_deselect_collisions"
    bl_label = "Deselect non Colliders"
    bl_description = 'Deselect all objects that are not colliders.'


class COLLISION_OT_Deletion(bpy.types.Operator):
    """Select/Deselect collision objects"""
    bl_idname = "object.delete_collisions"
    bl_label = "Delete Collision Meshes"
    bl_description = 'Delete collision objects'
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.EnumProperty(items=mode_items,
                                 name='Hide Mode',
                                 default='ALL_COLLIDER'
                                 )

    def execute(self, context):
        scene = context.scene
        count = 0
        selected_objs = context.selected_objects.copy()
        objects_to_remove = []

        for ob in bpy.context.view_layer.objects:
            if ob.parent in selected_objs:

                if self.mode == 'ALL_COLLIDER':
                    if ob.get('isCollider') == True:
                        objects_to_remove.append(ob)

                elif self.mode == 'OBJECTS':
                    if not ob.get('isCollider'):
                        objects_to_remove.append(ob)

                elif ob.get('isCollider') and ob.get('collider_type') == self.mode:
                    objects_to_remove.append(ob)

        if len(objects_to_remove) == 0:
            self.report({'INFO'}, 'No objects to delete.')

        # Call the delete oparator


        else:
            for obj in objects_to_remove:
                bpy.data.objects.remove(obj, do_unlink=True)
            #     scene.objects.unlink(obj)
            #     # bpy.data.objects.remove(obj)

        return {'FINISHED'}