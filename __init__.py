from os import remove
import time
import math
import struct

import bpy
import bmesh

from bpy_extras.io_utils import ExportHelper
from bpy.props import BoolProperty, IntProperty, EnumProperty

from .io_export_jms import Vec3, ExportItem, Header, Node, Material, Marker, Region, Vertex, Face, JMS, Quat4

bl_info = {
    "name": "Blade Exporter (.jms)",
    "author": "Joel Johnston (NightRipper)",
    "version": (1, 1, 1),
    "blender": (2, 79, 0),
    "location": "File > Export > JMS (.jms)",
    "description": "Export mesh as JMS (.jms)",
    "warning": "",
    "category": "Import-Export"}

def do_export(context, props, filepath):
    file = open(filepath, "w")
    try:
        frame = bpy.data.objects['frame']
    except KeyError:
        return False, 'No frame object found in the scene'

    nodes = [Node("frame", Quat4(0, 0, 0, 1.), Vec3(frame.matrix_world.translation*props.export_scale_factor))]
    materials = [] 
    markers = []
    regions = []
    verts = []
    faces = []

    for mat in bpy.data.materials:
        materials.append(Material(mat.name))

    for i, child in enumerate(frame.children):
        regions.append(Region(child.name))
        bm = bmesh.new()
        bm.from_mesh(child.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        mat = child.matrix_world
        uv_layer = bm.loops.layers.uv.active
        for face_idx, f in enumerate(bm.faces):
            mat_idx = bpy.data.materials[:].index(child.material_slots[f.material_index].material)
            for loop in f.loops:
                uv = loop[uv_layer].uv
                v = loop.vert
                verts.append(Vertex(0, Vec3(mat*v.co*props.export_scale_factor), Vec3(v.normal), uv[0], uv[1]))
            faces.append(Face(i, mat_idx, Vec3((face_idx*3+0, face_idx*3+1, face_idx*3+2))))
            
    jms = JMS(nodes, materials, markers, regions, verts, faces)

    file.write(jms.export())
    file.flush()
    file.close()
    return True


###### EXPORT OPERATOR #######
class Export_jms(bpy.types.Operator, ExportHelper):
    bl_idname = "geometry.jms"
    bl_label = "Export JMS (.jms)"

    filename_ext = ".jms"

    export_scale_factor = IntProperty(name='Export Scale Factor',
            description='Model will be scaled up by this factor',
            default=10,
            )

    def execute(self, context):
        start_time = time.time()
        print('\n_____START_____')
        props = self.properties
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        exported = do_export(context, props, filepath)

        if exported[0]:
            print('finished export in %s seconds' %((time.time() - start_time)))
            print(filepath)
        else:
            self.report({'ERROR'}, exported[1])

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if True:
            # File selector
            wm.fileselect_add(self) # will run self.execute()
            return {'RUNNING_MODAL'}
        elif True:
            # search the enum
            wm.invoke_search_popup(self)
            return {'RUNNING_MODAL'}
        elif False:
            # Redo popup
            return wm.invoke_props_popup(self, event)
        elif False:
            return self.execute(context)


### REGISTER ###

def menu_func(self, context):
    self.layout.operator(Export_jms.bl_idname, text="JMS (.jms)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()
