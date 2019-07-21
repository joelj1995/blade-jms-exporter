# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
from os import remove
import time
import math
import struct



class Vec3:

    def __init__(self, vec):
        self.x = vec[0]
        self.y = vec[1]
        self.z = vec[2]

    def __repr__(self):
        return "(%f, %f, %f)" % self.as_tuple()

    def as_tuple(self):
        return (self.x, self.y, self.z)

    def normalize(self):
        len = (abs(self.x ** 3) + abs(self.y ** 3) + abs(self.z ** 3)) ** (1. / 3)
        return Vec3(self.x / len, self.y / len, self.z / len)

    def export(self, asint=False):
        if asint:
            return "%d\t%d\t%d" % self.as_tuple()
        return "%f\t%f\t%f" % self.as_tuple()


class Quat4:

    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def as_tuple(self):
        return (self.x, self.y, self.z, self.w)

    def export(self):
        return "%f\t%f\t%f\t%f" % self.as_tuple()


class ExportItem:

    def export(self):
        raise NotImplementedError()

    def line(self, str):
        return str + '\n'

    def lines(self, strs):
        return "".join([self.line(str) for str in strs]) 


class Header(ExportItem):

    def export(self):
        return self.lines(["8200", "3251"])


class Node(ExportItem):

    def __init__(self, name, rotation, translation, first_child_index=-1, next_sibling_index=-1):
        self.name = name
        self.first_child_index = first_child_index
        self.next_sibling_index = next_sibling_index
        self.rotation = rotation
        self.translation = translation

    def export(self):
        return self.lines([
            self.name,
            str(self.first_child_index),
            str(self.next_sibling_index),
            self.rotation.export(),
            self.translation.export()
        ])


class Material(ExportItem):

    def __init__(self, name):
        self.name = name

    def export(self):
        return self.lines([self.name, "<none>"])
    

class Marker(ExportItem):
    pass


class Region(ExportItem):
    
    def __init__(self, name):
        self.name = name
    
    def export(self):
        return self.line(self.name)


class Vertex(ExportItem):

    def __init__(self, node0index, pos, normal, u, v, node1index=-1, node1weight=0):
        self.node0index = node0index
        self.pos = pos
        self.normal = normal
        self.node1index = node1index
        self.node1weight = node1weight
        self.u = u
        self.v = v

    def export(self):
        return self.lines([
            str(self.node0index),
            self.pos.export(),
            self.normal.export(),
            str(self.node1index),
            str(self.node1weight),
            str(self.u),
            str(self.v),
            "0"
        ])


class Face(ExportItem):

    def __init__(self, regionindex, shaderindex, verts):
        self.regionindex = regionindex
        self.shaderindex = shaderindex
        self.verts = verts

    def export(self):
        return self.lines([
            str(self.regionindex),
            str(self.shaderindex),
            self.verts.export(asint=True)
        ])


class JMS:

    def __init__(self, nodes, materials, markers, regions, verts, faces):
        self.header = Header()
        self.nodes = nodes
        self.materials = materials
        self.markers = markers
        self.regions = regions
        self.verts = verts
        self.faces = faces

    def _connect(self, loe):
        return "%d\n" % len(loe) + "".join([e.export() for e in loe])

    def export_nodes(self):
        return self._connect(self.nodes)

    def export_materials(self):
        return self._connect(self.materials)

    def export_markers(self):
        return self._connect(self.markers)

    def export_regions(self):
        return self._connect(self.regions)

    def export_verts(self):
        return self._connect(self.verts)

    def export_faces(self):
        return self._connect(self.faces)

    def export(self):
        return self.header.export() + self.export_nodes() + self.export_materials() + self.export_markers() + self.export_regions() + self.export_verts() + self.export_faces()
