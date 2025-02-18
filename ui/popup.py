import bpy

from .properties_panels import draw_auto_convex_settings


class VIEW3D_PT_auto_convex_popup(bpy.types.Panel):
    """Tooltip"""
    bl_idname = "POPUP_PT_auto_convex"
    bl_label = "Renaming Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    def draw(self, context):
        layout = self.layout

        colSettings = context.scene.simple_collider
        draw_auto_convex_settings(colSettings, layout)
        layout.label(text='May take up to a few minutes', icon='ERROR')
        layout.operator("collision.vhacd", text="Auto Convex", icon='MESH_ICOSPHERE')

        return
