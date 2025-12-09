from OpenGL.GL import *
from PIL import Image

import os

class ModelLoader:
    def __init__(self, obj_filepath=None, mtl_filepath=None):
        self.vertices = []
        self.faces = []
        self.normals = []
        self.sex_coords = []
        self.has_model = False
        self.texture_id = None
        self.material = None

        if (obj_filepath and os.path.exists(obj_filepath)):
            self._load_obj(obj_filepath)
            if (os.path.exists(mtl_filepath)):
                self._load_mtl(mtl_filepath)
            print(f"Loaded: {obj_filepath}")
            self.has_model = True
        else:
            print(f"{obj_filepath}: Model not found")
            print(f"Exiting")
            sys.exit()

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
                elif parts[0] == 'vn':
                    normal = [float(parts[1]),
                              float(parts[2]),
                              float(parts[3])]
                    self.normals.append(normal)
                elif parts[0] == "f":
                    face = []
                    for vertex_data in parts[1:]:
                        indices = vertex_data.split('/')
                        vertex_index = int(indices[0]) - 1
                        face.append(vertex_index)
                    if len(face) == 3:
                        self.faces.append(face)
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
        
        # save cur transofrmation matrix
        glPushMatrix()
        # draw solid model
        # set material color
        glColor3f(0.6, 0.7, 0.8)
        # begin drawing triangles
        glBegin(GL_TRIANGLES)
        #draw all faces
        for face in self.faces:
            for vertex_index in face:
                if vertex_index < len(self.vertices):
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
