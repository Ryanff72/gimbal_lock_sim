from OpenGL.GL import *
from PIL import Image

import os
import sys


class ModelLoader:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.normals = []
        self.tex_coords = []
        self.has_model = False
        self.texture_id = None

        self.obj_filepath = "./assets/lowpolyplane.obj"
        self.mtl_filepath = "./assets/airplane.mtl"
        self.diffuse_filepath = "./assets/textures/diffuse.tga"

        self.material = {
            'diffuse': [0.8, 0.8, 0.8, 1.0],
            'ambient': [0.2,0.2,0.2,1.0],
            'specular': [0.0,0.0,0.0,1.0],
            'shininess': 0.0
        }

        self._load_model()

    def _clear_model(self):
        self.vertices = []
        self.faces = []
        self.normals = []
        self.tex_coords = []
        self.has_model = False
        self.texture_id = None
        self.material = {
            'diffuse': [0.8, 0.8, 0.8, 1.0],
            'ambient': [0.2,0.2,0.2,1.0],
            'specular': [0.0,0.0,0.0,1.0],
            'shininess': 0.0
        }

    def _load_model(self):
        if (self.obj_filepath and os.path.exists(self.obj_filepath)):
            self._load_obj()

            if not self.tex_coords:
                self._generate_uvs()

            if (self.mtl_filepath and os.path.exists(self.mtl_filepath)):
                self._load_mtl()
            elif (self.diffuse_filepath and os.path.exists(self.diffuse_filepath)):
                self._load_texture()
            print(f"Loaded: {self.obj_filepath}")
            self.has_model = True
        else:
            print(f"{self.obj_filepath}: Model not found")
            print(f"Exiting")
            sys.exit()

    def set_config(self,config):
        self.obj_filepath = config[0]
        self.mtl_filepath = config[1]
        self.diffuse_filepath = config[2]
        self._clear_model()
        self._load_model()

    def _generate_uvs(self):
        if not self.vertices:
            return
        # find bounds
        min_x = min(v[0] for v in self.vertices)
        max_x = max(v[0] for v in self.vertices)
        min_z = min(v[2] for v in self.vertices)
        max_z = max(v[2] for v in self.vertices)
        
        range_x = max_x - min_x if max_x != min_x else 1.0
        range_z = max_z - min_z if max_z != min_z else 1.0
        
        # make uvs for each vertex
        self.tex_coords = []
        for vertex in self.vertices:
            u = (vertex[0] - min_x) / range_x
            v = (vertex[2] - min_z) / range_z
            self.tex_coords.append([u, v])
        
        # make faces use uvs 
        for face in self.faces:
            verts = face['vertices']
            face['texcoords'] = verts  # Use same indices as vertices
        
        print(f"Generated {len(self.tex_coords)} UV coordinates")

    def _load_mtl(self):
        if not os.path.exists(self.mtl_filepath):
            print(f"No MTL file found at {self.mtl_filepath}")
            return

        print(f"loading mtl: {self.mtl_filepath}")
        obj_dir = os.path.dirname(self.obj_filepath)
        diffuse_map = None

        with open(self.mtl_filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if parts[0] == 'Kd':
                    self.material['diffuse'] = [float(parts[1]),
                                           float(parts[2]),
                                           float(parts[3]),
                                           1.0]
                elif parts[0] == 'Ka':
                    self.material['ambient'] = [float(parts[1]),
                                                float(parts[2]),
                                                float(parts[3]),
                                                1.0]
                elif parts[0] == 'Ks':
                    self.material['specular'] = [float(parts[1]),
                                                float(parts[2]),
                                                float(parts[3]),
                                                1.0]
                elif parts[0] == 'Ns':
                    self.material['shininess'] = min(max(float(parts[1]),0.0), 128.0)
                elif parts[0] == 'map_Kd':
                    texture_path = ' '.join(parts[1:])
                    texture_filename = os.path.basename(texture_path.replace('\\','/'))
                    if self.diffuse_filepath and os.path.exists(self.diffuse_filepath):
                        diffuse_map = self.diffuse_filepath
                    else:
                        textures_dir_path = os.path.join(obj_dir, 'textures', texture_filename)
                        if os.path.exists(textures_dir_path):
                            diffuse_map = textures_dir_path
                        else:
                            print(f"texture not found: {texture_filename}")
        if diffuse_map:
            print("using diffuse")
            self._load_texture()

    def _load_texture(self):
        if not self.diffuse_filepath or not os.path.exists(self.diffuse_filepath):
            return
        try:
            image = Image.open(self.diffuse_filepath)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            # opengl expects origin at bottom left
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            # make opengl texture
            img_data = image.tobytes()
            width, height = image.size
            # opengl texture
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            # set tex parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # upload tex data to GPU (?)
            glTexImage2D(
                GL_TEXTURE_2D,
                0, # mipmap level
                GL_RGBA, # internal format
                width,
                height,
                0, # border
                GL_RGBA, # format
                GL_UNSIGNED_BYTE, # data type
                img_data
            )
            print(f"texture loaded")
        except Exception as e:
            print(f"failed to load texture: {e}")
            self.texture_id = None

    def _load_obj(self):
        with open(self.obj_filepath, 'r') as o:
            # read file
            for line in o:
                # strip whitespace
                line = line.strip()
                # skip empty lines
                if (not line or 
                    line.startswith('usemtl') or 
                    line.startswith('g') or
                    line.startswith('#')):
                    continue
                parts = line.split()
                if parts[0] == 'v':
                    vertex = [float(parts[1]), 
                              float(parts[2]), 
                              float(parts[3])]
                    self.vertices.append(vertex)
                elif parts[0] == 'vt':
                    tex_coord = [float(parts[1]),
                              float(parts[2])]
                    self.tex_coords.append(tex_coord)
                elif parts[0] == 'vn':
                    normal = [float(parts[1]),
                              float(parts[2]),
                              float(parts[3])]
                    self.normals.append(normal)
                elif parts[0] == "f":
                    face_verts = []
                    face_texs = []
                    face_norms = []
                    for vertex_data in parts[1:]:
                        indices = vertex_data.split('/')
                        vertex_index = int(indices[0]) - 1
                        face_verts.append(vertex_index)
                        if len(indices) > 1 and indices[1]:
                            tex_index = int(indices[1]) - 1
                            face_texs.append(tex_index)
                        if len(indices) > 2 and indices[2]:
                            norm_index = int(indices[2]) - 1
                            face_norms.append(norm_index)
                    if len(face_verts) == 3:
                        self.faces.append({
                            'vertices': face_verts,
                            'texcoords': face_texs if face_texs else None
                        })
                    elif len(face_verts) == 4:
                        self.faces.append({
                            'vertices': [face_verts[0], face_verts[1], face_verts[2]],
                            'texcoords': [face_texs[0], face_texs[1], face_texs[2]] if face_texs else None,
                            'normals': [face_norms[0], face_norms[1], face_norms[2]] if face_norms else None
                        })
                        self.faces.append({
                            'vertices': [face_verts[0], face_verts[2], face_verts[3]],
                            'texcoords': [face_texs[0], face_texs[2], face_texs[3]] if face_texs else None,
                            'normals': [face_norms[0], face_norms[2], face_norms[3]] if face_norms else None
                        })
                elif parts[0] == 'l':
                    continue
        self.has_model = True

    def render(self):
        '''
            draw model
            steps:
            1. push matrix / save cur transformation
            2. set color
            3. Draw all triangles
            4. Draw wireframe overlay
            5. pop matrix / restore transformations 
        '''
        if not self.has_model:
            return
        # show all faces
        glDisable(GL_CULL_FACE)
        # apply material properties
        if self.material:
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.material['diffuse'])
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.material['ambient'])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.material['specular'])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.material['shininess'])
        #check if textures 
        if (self.texture_id):
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glColor3f(1,1,1)
        else:
            glColor3f(0.6, 0.7, 0.8)
        # save cur transofrmation matrix
        glPushMatrix()
        # draw solid model
        # set material color
        # begin drawing triangles
        glBegin(GL_TRIANGLES)
        #draw all faces
        for face in self.faces:
            vertices = face.get('vertices', face if isinstance(face, list) else [])
            texcoords = face.get('texcoords',None) if isinstance(face, dict) else []
            for i, vertex_index in enumerate(vertices):
                if vertex_index < len(self.vertices):
                    if texcoords and i < len(texcoords):
                        tex_index = texcoords[i]
                        if tex_index < len(self.tex_coords):
                            glTexCoord2fv(self.tex_coords[tex_index])
                    vertex = self.vertices[vertex_index]
                    # send vertex to opengl
                    glVertex3fv(vertex)
        # stop drawing triangles
        glEnd()

        # restore polygon to be filled (?)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_LIGHTING)

        # Restore transformation mateix
        glPopMatrix()
