import pygame
import sys
import os
import math
import imgui

from pygame.locals import *
from imgui.integrations.pygame import PygameRenderer
from OpenGL.GL import *
from OpenGL.GLU import *

from model_loader import ModelLoader
from gimbal_rings import create_ring_vertices

class Window:
    def __init__(self, width, height, title, model_path, mtl_path):
        self.width = width
        self.height = height
        self.title = title
        self.model_path = model_path
        self.mtl_path = mtl_path
        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = 60

        # control settings
        self.cam_step_rotate = 3
        self.cam_step_zoom = 1
        self.plane_step_rotate = 2

        # in euclidean coordinates
        self.in_quaternion = False

        # gimble lockable rotation
        self.plane_yaw = 0.0
        self.plane_pitch = 0.0
        self.plane_roll = 90.0

        # creates window
        self._init_pygame()
        # set up 3d rendering
        self._init_opengl()

        # load model
        # this will return a model data structure
        self.model = ModelLoader(model_path, mtl_path)

        # create rings
        self.ring_radius_outer = 150.0
        self.ring_radius_middle = 140.0
        self.ring_radius_inner = 130.0

        # create ring geometry
        self.ring_vertices_outer = create_ring_vertices(self.ring_radius_outer, 'x')
        self.ring_vertices_middle = create_ring_vertices(self.ring_radius_middle, 'y')
        self.ring_vertices_inner = create_ring_vertices(self.ring_radius_inner, 'z')


        # camera setup
        self.camera_distance = 150.0 # dist from origin
        self.camera_azimuth = 0.0 # rotation about z axis
        self.camera_elevation = 30.0 #angle above horizon (degs)

        # gui setup
        self.font = imgui.create_context()
        self.imgui_renderer = PygameRenderer()
        self.show_ui = True

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption(self.title)
    
    def _init_opengl(self):
        glViewport(0,0,self.width, self.height)

        # fix depth (make triangles drawn in front appear in front)
        glEnable(GL_DEPTH_TEST)
        #enable textures
        glEnable(GL_TEXTURE_2D)
        # pixel is allowed if its closer than whats there
        glDepthFunc(GL_LESS) 
        # matrix projection mode
        glMatrixMode(GL_PROJECTION)
        # reset to identity matrix(fresh/empty)
        glLoadIdentity()
        gluPerspective(
            #fov
            90,
            #aspect ratio (w/h)
            self.width / self.height,
            #draw distance min
            0.1,
            #draw distance max
            1000.0
        )
        # where cam position and obj transformations happen
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # enable lighting
        # turn on light calcs
        glEnable(GL_LIGHTING)
        #enable 'first' light source (opengl has 8)
        glEnable(GL_LIGHT0)

        # allows us to set color
        # without this we need to call glMaterial* for every
        # color change
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK,GL_AMBIENT_AND_DIFFUSE)

        # configure light0
        # [x,y,z,w]; w=0 means directional w=1 means positional
        glLightfv(GL_LIGHT0, GL_POSITION, [5,5,5,1])

        # ambient light (everywhere equally)
        # gray color
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2,0.2,0.2,1])

        # diffuse light (sun type light)
        # bright white color
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8,0.8,0.8,1])

    def _update_plane(self):
        # TODO 
        # make quaternions
        pass


    def _update_camera(self):
        # reset modelview matrix
        glLoadIdentity()
        # Need to clamp BEFORE conversion to prevent weird angles
        self.camera_elevation = max(-89.9, min(89.9, self.camera_elevation))
        #convert controls to rads
        azimuth_rad = math.radians(self.camera_azimuth)
        elevation_rad = math.radians(self.camera_elevation)

        # sphere -> cartesian conversion
        x = self.camera_distance * math.cos(elevation_rad) * math.sin(azimuth_rad)
        y = self.camera_distance * math.cos(elevation_rad) * math.cos(azimuth_rad)
        z = self.camera_distance * math.sin(elevation_rad)

        gluLookAt(
            # cam pos
            x,y,z,
            # look at
            0,0,0,
            #up vector
            0,0,1 # z axis is up
        )

    # process inputs 
    def _handle_events(self):
        for event in pygame.event.get():
            self.imgui_renderer.process_event(event)
            if event.type == QUIT:
                self.running = False
        keys = pygame.key.get_pressed()
        # exit
        if keys[K_ESCAPE]:
            self.running = False
        # control camera
        if keys[K_LEFT]:
            self.camera_azimuth -= self.cam_step_rotate
        if keys[K_RIGHT]:
            self.camera_azimuth += self.cam_step_rotate
        if keys[K_UP]:
            self.camera_elevation -= self.cam_step_rotate
        if keys[K_DOWN]:
            self.camera_elevation += self.cam_step_rotate
        if keys[K_w]:
            self.camera_distance -= self.cam_step_zoom
        if keys[K_s]:
            self.camera_distance += self.cam_step_zoom
        # update plane
        # yaw
        if keys[K_i]:
            self.plane_yaw -= self.plane_step_rotate
        if keys[K_j]:
            self.plane_yaw += self.plane_step_rotate
        # pitch
        if keys[K_u]:
            self.plane_pitch -= self.plane_step_rotate
        if keys[K_h]:
            self.plane_pitch += self.plane_step_rotate
        # roll
        if keys[K_o]:
            self.plane_roll -= self.plane_step_rotate
        if keys[K_k]:
            self.plane_roll += self.plane_step_rotate

    """
    Render function is called every frame
    During render this happens:
    1. Clear screen
    2. Set camera position
    3. Draw all 3d objects
    4. Show what was drawn
    """
    def _render(self):
        # clear color and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # reset transformations to identity matrix
        glLoadIdentity()
        # position camera
        self._update_camera()
        #gimbal rings, rotate with plane angles
        self._draw_gimbal_rings()
        # draw everything we need to
        #rotate plane
        glPushMatrix()
        glRotatef(self.plane_yaw, 0,0,1)
        glRotatef(self.plane_pitch, 0,1,0)
        glRotatef(self.plane_roll, 1,0,0)
        self.model.render()
        glPopMatrix()
        self._draw_axes()
        #gui
        self._render_gui()
        io = imgui.get_io()
        io.font_global_scale = 2.5
        io.display_size = self.width, self.height
        #initally we drew to a hidden 'back buffer'
        # this swaps it to the front buffer
        # prevents half drawn frames (called double buffering)
        pygame.display.flip()

    def _draw_gimbal_rings(self):
        glDisable(GL_LIGHTING)
        glLineWidth(3.0)

        # outer (yaw)
        glPushMatrix()
        glRotatef(self.plane_yaw, 0, 0, 1)
        glColor3f(1, 0, 0)
        glBegin(GL_LINE_LOOP)
        for vertex in self.ring_vertices_outer:
            glVertex3fv(vertex)
        glEnd()
        # yaw arrow
        glBegin(GL_LINES)
        glVertex(0,0,-4)
        glVertex(0,0,4)
        glEnd()
        # pitch - affected by yaw, then pitch.
        glRotatef(self.plane_pitch, 0, 1, 0)
        glColor3f(0, 1, 0)
        glBegin(GL_LINE_LOOP)
        for vertex in self.ring_vertices_middle:
            glVertex3fv(vertex)
        glEnd()
        # pitch arrow
        glBegin(GL_LINES)
        glVertex(0, -3.5, 0)
        glVertex3f(0, 3.5, 0)
        glEnd()
        # roll - affected by yaw, then pitch, then roll
        glRotatef(self.plane_roll, 1, 0, 0)
        glColor3f(0, 0, 1)
        glBegin(GL_LINE_LOOP)
        for vertex in self.ring_vertices_inner:
            glVertex3fv(vertex)
        glEnd()
        glBegin(GL_LINES)
        glVertex(-3, 0, 0)
        glVertex(3, 0, 0)
        glEnd()
        glPopMatrix() # pop all transformations
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    def _render_gui(self):
        io = imgui.get_io()
        io.display_size = self.width, self.height
        imgui.new_frame()
        # main control panel
        imgui.begin("Flight Controls", True)
        if (not self.in_quaternion):
            imgui.text("Rotation Mode: Euler Angles")
            imgui.separator()
            imgui.text(f"X: {abs(self.plane_pitch) % 360:.1f}")
            imgui.text(f"Y: {abs(self.plane_yaw) % 360:.1f}")
            imgui.text(f"Z: {abs(self.plane_roll) % 360:.1f}")
            if ((abs(self.plane_pitch) % 180) >= 86 and 
                (abs(self.plane_pitch) % 180) <= 94):
                imgui.separator()
                imgui.text(f"WARNING!!!!!!!!")
                imgui.text(f"you are gimble lock")

        else:
            # TODO
            #info about quaternion
            pass
        imgui.end()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    # axes are for reference
    def _draw_axes(self):
        # no light for drawing lines, solid color
        glDisable(GL_LIGHTING)
        # draw lines using 2 vertices for each
        glBegin(GL_LINES)
        # x
        glColor3f(1,0,0.05)
        glVertex3f(0,0,0)
        glVertex3f(2,0,0)
        # y
        glColor3f(0,1,0.05)
        glVertex3f(0,0,0)
        glVertex3f(0,2,0)
        # z
        glColor3f(0,0,1)
        glVertex3f(0,0,0)
        glVertex3f(0,0,2)
        # done drawing
        glEnd()
        glEnable(GL_LIGHTING)

    def run(self):
        print("running")
        while self.running:
            self._handle_events()
            self._update_plane()
            self._render()
            self.clock.tick(self.fps)

        self._cleanup()

    def _cleanup(self):
        self.imgui_renderer.shutdown()
        pygame.quit()
        sys.exit()