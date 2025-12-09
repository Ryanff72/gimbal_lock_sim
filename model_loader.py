from OpenGL.GL import *

import os

class ModelLoader:
    def __init__(self, filepath=None):
        self.vertices = []
        self.faces = []
        self.normals = []
        self.has_model = False

        if filepath and os.path.exists(filepath):
            self._load_obj(filepath)
            print(f"Loaded: {filepath}")
            self.has_model = True
        else:
            print(f"{filepath}: Model not found")
            print(f"Exiting")
            sys.exit()
    
    def _load_obj(self, filepath):
        with open(filepath, 'r') as o:
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
