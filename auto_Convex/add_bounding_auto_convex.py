import os
import time
import subprocess

import bmesh
import bpy
from bpy.types import Operator
import numpy
import coacd

from ..bmesh_operations.mesh_edit import bmesh_join
from ..collider_shapes.add_bounding_primitive import OBJECT_OT_add_bounding_object


class VHACD_OT_convex_decomposition(OBJECT_OT_add_bounding_object, Operator):
    bl_idname = 'collision.vhacd'
    bl_label = 'Convex Decomposition'
    bl_description = ('Create multiple convex hull colliders to represent any object using Hierarchical Approximate '
                      'Convex Decomposition')
    bl_options = {'REGISTER', 'PRESET'}

    @staticmethod
    def overwrite_executable_path(path):
        """Users can overwrite the default executable path. """
        # Check executable path
        executable_path = bpy.path.abspath(path)

        return executable_path if os.path.isfile(executable_path) else False

    @staticmethod
    def set_temp_data_path(path):
        """Set folder to temporarily store the exported data. """
        # Check data path
        data_path = bpy.path.abspath(path)

        return data_path if os.path.isdir(data_path) else False

    def __init__(self):
        super().__init__()
        self.use_decimation = True
        self.use_geo_nodes_hull = True
        self.use_modifier_stack = True
        self.use_recenter_origin = True
        self.shape = 'convex_shape'

    def invoke(self, context, event):
        super().invoke(context, event)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        status = super().modal(context, event)
        if status == {'FINISHED'}:
            return {'FINISHED'}
        if status == {'CANCELLED'}:
            return {'CANCELLED'}
        if status == {'PASS_THROUGH'}:
            return {'PASS_THROUGH'}

        # change bounding object settings
        if event.type == 'P' and event.value == 'RELEASE':
            self.my_use_modifier_stack = not self.my_use_modifier_stack
            self.execute(context)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.space_data.shading.color_type = self.color_type
        try:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        except ValueError:
            pass
        return {'CANCELLED'}

    def execute(self, context):
        # CLEANUP
        super().execute(context)

        overwrite_path = self.overwrite_executable_path(self.prefs.executable_path)
        data_path = self.set_temp_data_path(self.prefs.data_path)
        vhacd_exe = self.prefs.default_executable_path if not overwrite_path else overwrite_path

        if not vhacd_exe or not data_path:
            if not vhacd_exe:
                self.report({'ERROR'},
                            'V-HACD executable is required for Auto Convex to work. Please follow the installation '
                            'instructions and try it again')
            if not data_path:
                self.report({'ERROR'}, 'Invalid temporary data path')

            return self.cancel(context)

        for obj in self.selected_objects:
            obj.select_set(False)

        collider_data = []
        meshes = []
        matrices = []

        objs = self.get_pre_processed_mesh_objs(context, default_world_spc=True)

        for base_ob, obj in objs:
            context.view_layer.objects.active = obj

            if self.obj_mode == "EDIT" and base_ob.type == 'MESH' and self.active_obj.type == 'MESH' and not self.use_loose_mesh:
                new_mesh = self.get_mesh_Edit(
                    obj, use_modifiers=self.my_use_modifier_stack)
            else:  # self.obj_mode  == "OBJECT" or self.use_loose_mesh == True:
                new_mesh = self.mesh_from_selection(
                    obj, use_modifiers=self.my_use_modifier_stack)

            if new_mesh is None:
                continue

            creation_mode = self.creation_mode[self.creation_mode_idx] if self.obj_mode == 'OBJECT' else \
            self.creation_mode_edit[self.creation_mode_idx]
            if creation_mode in ['INDIVIDUAL'] or self.use_loose_mesh:
                convex_collision_data = {'parent': base_ob, 'mtx_world': base_ob.matrix_world.copy(), 'mesh': new_mesh}

                collider_data.append(convex_collision_data)

            # if self.creation_mode[self.creation_mode_idx] == 'SELECTION':
            else:
                meshes.append(new_mesh)
                matrices.append(obj.matrix_world)

        if self.creation_mode[self.creation_mode_idx] == 'SELECTION':
            convex_collision_data = {'parent': self.active_obj, 'mtx_world': self.active_obj.matrix_world.copy()}

            bmeshes = []

            for mesh in meshes:
                bm_new = bmesh.new()
                bm_new.from_mesh(mesh)
                bmeshes.append(bm_new)

            joined_mesh = bmesh_join(bmeshes, matrices)

            convex_collision_data['mesh'] = joined_mesh
            collider_data = [convex_collision_data]

        bpy.ops.object.mode_set(mode='OBJECT')
        convex_decomposition_data = []

        for convex_collision_data in collider_data:
            parent = convex_collision_data['parent']
            mesh = convex_collision_data['mesh']

            # bpy.data.meshes.remove(mesh)
            print("running coacd")
            # vhacd_process.wait()
            b_mesh = bmesh.new()
            b_mesh.from_mesh(mesh)
            t_mesh = bmesh.ops.triangulate(b_mesh, faces=b_mesh.faces)
            print(t_mesh)
            print(t_mesh["faces"])
            verts = numpy.array([vert.co for vert in b_mesh.verts])
            faces = numpy.array([[vert.index for vert in face.verts] for face in t_mesh["faces"]])
            print(verts)
            print(faces)
            c_mesh = coacd.Mesh(verts, faces)
            settings = context.scene.simple_collider
            parts = coacd.run_coacd(
                mesh = c_mesh,
                threshold = settings.threshold,
                max_convex_hull = settings.max_convex_hull,
                preprocess_mode = "Off",
                preprocess_resolution = 50,
                resolution = settings.resolution,
                mcts_nodes = settings.mcts_nodes,
                mcts_iterations = settings.mcts_iterations,
                mcts_max_depth = settings.mcts_max_depth,
                pca = settings.pca,
                merge = settings.merge,
                decimate = settings.decimate,
                max_ch_vertex = settings.max_ch_vertex,
                extrude = settings.extrude,
                extrude_margin = settings.extrude_margin,
                apx_mode = settings.apx_mode,
                seed = settings.seed,
            ) # a list of convex hulls.

            print(parts)

            imported = []
            for [p_verts, p_faces] in parts:
                # create mesh from verts and faces
                me = bpy.data.meshes.new("Mesh")
                me.from_pydata(p_verts, [], p_faces)

                # Add the mesh to the scene
                obj = bpy.data.objects.new("Collider", me)
                bpy.context.collection.objects.link(obj)
                imported.append(obj)

            for ob in imported:
                ob.select_set(False)

            convex_collisions_data = {'colliders': imported, 'parent': parent, 'mtx_world': parent.matrix_world.copy()}
            convex_decomposition_data.append(convex_collisions_data)

        context.view_layer.objects.active = self.active_obj

        for convex_collisions_data in convex_decomposition_data:
            convex_collision = convex_collisions_data['colliders']
            parent = convex_collisions_data['parent']
            mtx_world = convex_collisions_data['mtx_world']

            for new_collider in convex_collision:
                new_collider.name = super().collider_name(basename=parent.name)

                if self.creation_mode[self.creation_mode_idx] == 'INDIVIDUAL':
                    if not self.use_loose_mesh:
                        new_collider.matrix_world = mtx_world
                    self.apply_transform(
                        new_collider, rotation=True, scale=True)

                self.custom_set_parent(context, parent, new_collider)

                collections = parent.users_collection
                self.primitive_postprocessing(
                    context, new_collider, collections)
                self.new_colliders_list.append(new_collider)

        if len(self.new_colliders_list) < 1:
            self.report({'WARNING'}, 'No meshes to process!')
            return {'CANCELLED'}

        # Merge all collider objects
        if self.join_primitives:
            super().join_primitives(context)

        super().reset_to_initial_state(context)
        elapsed_time = self.get_time_elapsed()
        super().print_generation_time("Auto Convex Colliders", elapsed_time)
        self.report({'INFO'}, "Auto Convex Colliders: " +
                    str(float(elapsed_time)))

        return {'FINISHED'}
