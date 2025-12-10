from OpenGL.GL import *
from PIL import Image

import os
import sys

class ModelLoader:
    def __init__(self, obj_filepath=None, mtl_filepath=None):
        self.vertices = []
        self.faces = []
        self.normals = []
        self.tex_coords = []
        self.has_model = False
        self.texture_id = None
        self.material = None

        if (obj_filepath and os.path.exists(obj_filepath)):
            self._load_obj(obj_filepath)
            if (os.path.exists(mtl_filepath)):
                self._load_mtl(obj_filepath, mtl_filepath)
            print(f"Loaded: {obj_filepath}")
            self.has_model = True
        else:
            print(f"{obj_filepath}: Model not found")
            print(f"Exiting")
            sys.exit()

    def _load_mtl(self, obj_filepath, mtl_filepath):
        if not os.path.exists(mtl_filepath):
            print(f"No MTL file found at {mtl_filepath}")
            return

        print(f"loading mtl: {mtl_filepath}")

        obj_dir = os.path.dirname(obj_filepath)

        diffuse_map = None
        with open(mtl_filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if parts[0] == 'map_Kd':
                    texture_path = ' '.join(parts[1:])
                    texture_filename = os.path.basename(texture_path.replace('\\','/'))
                    local_texture_path = "assets/textures/diffuse.dds"
                    textures_dir_path = os.path.join(obj_filepath, 'textures', texture_filename)

                    if os.path.exists(local_texture_path):
                        diffuse_map = local_texture_path
                    elif os.path.exists(textures_dir_path):
                        diffuse_map = textures_dir_path
                    else:
                        print(f"texture not found: {texture_filename}")
                        print(f" Tried: {local_texture_path}")
                        print(f" Tried: {textures_dir_path}")
        if diffuse_map:
            self._load_texture(diffuse_map)

    def _load_texture(self, mtl_filepath):
        try:
            image = Image.open(mtl_filepath)
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

    def _load_obj(self, obj_filepath):
        with open(obj_filepath, 'r') as o:
            # read file
            for line in o:
                print(f"loading info vertex:{line}")
                # strip whitespace
                line = line.strip()
                # skip empty lines
                if not line or line.startswith('#'):
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
                    for vertex_data in parts[1:]:
                        indices = vertex_data.split('/')
                        vertex_index = int(indices[0]) - 1
                        face_verts.append(vertex_index)
                        if len(indices) > 1 and indices[1]:
                            tex_index = int(indices[1]) - 1
                            face_texs.append(tex_index)
                    if len(face_verts) == 3:
                        self.faces.append({
                            'vertices': face_verts,
                            'texcoords': face_texs if face_texs else None
                        })
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
        #check if textures 
        if (self.texture_id):
            glEnable(GL_TEXTURE_2D)
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
