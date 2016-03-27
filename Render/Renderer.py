import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from Core import logger, config
from Object import ObjectManager
from Render import CameraManager, GLFont, defaultFont
from Utilities import Singleton

#------------------------------#
# CLASS : Console
#------------------------------#
class Console:
    def __init__(self):
        self.glfont = None
        self.infos = []
        self.debugs = []
        self.padding = 10
        self.renderer = None

    def initialize(self):
        self.renderer = Renderer.instance()
        self.glfont = GLFont(defaultFont, 12)
        self.infos = []
        self.debugs = []

    def clear(self):
        self.infos = []

    # just print info
    def info(self, text):
        self.infos.append(text)

    # debug text - print every frame
    def debug(self, text):
        self.debugs.append(text)

    def render(self):
        '''
        # set orthographic view
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity( )
        glOrtho( 0, self.width, 0, self.height, -1, 1 )
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity( )

        # render state
        glEnable(GL_BLEND)
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        '''

        # render
        glColor(1,1,1,1)
        glPushMatrix( )
        glTranslate( self.padding, self.renderer.height - self.padding, 0 )
        glPushMatrix()
        # render text
        self.glfont.render("\n".join(self.debugs + self.infos))
        glPopMatrix( )
        glPopMatrix( )


#------------------------------#
# CLASS : Renderer
#------------------------------#
class Renderer(Singleton):
    def __init__(self):
        self.inited = False
        self.lastShader = None
        self.width = 0
        self.height = 0
        self.viewportRatio = 1.0
        self.camera = None
        self.coreManager = None
        self.objectManager = None
        self.cameraManager = None

        # timer
        self.fpsLimit = 1.0 / 60.0
        self.fps = 0.0
        self.delta = 0.0
        self.currentTime = 0.0

        # console font
        self.console = Console()

    def initialize(self, coreManager):
        self.coreManager = coreManager
        self.objectManager = ObjectManager.instance()
        self.cameraManager = CameraManager.instance()
        self.initGL()

    def initGL(self):
        glutInit()
        glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH )
        self.width, self.height = config.getValue("Screen", "size")
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(*config.Screen.position)
        glutCreateWindow(b"GuineaPig")
        glutDisplayFunc(self.renderScene)
        glutIdleFunc(self.renderScene)
        glutReshapeFunc(self.resizeScene)

        # bind keyboard, mouse interface
        glutKeyboardFunc(self.coreManager.keyboardFunc)
        glutKeyboardUpFunc(self.coreManager.keyboardUp)
        glutPassiveMotionFunc(self.coreManager.passiveMotionFunc)
        glutMouseFunc(self.coreManager.mouseFunc)
        glutMotionFunc(self.coreManager.motionFunc)

        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        # Start - fixed pipline light setting
        glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        # End - fixed pipline light setting

        # init console text
        self.console.initialize()

        # initialized flag
        logger.info("InitializeGL : %s" % glGetDoublev(GL_VIEWPORT))

    def close(self):
        x, y = glutGet(GLUT_WINDOW_X), glutGet(GLUT_WINDOW_Y)
        config.setValue("Screen", "position", [x, y])

    def resizeScene(self, width, height):
        if width <= 0 or height <= 0:
            return

        self.width = width
        self.height = height
        self.viewportRatio = float(width) / float(height)
        self.camera = self.cameraManager.getMainCamera()

        # resize scene
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.fov, self.viewportRatio, self.camera.near, self.camera.far)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.inited = True

    # render meshes
    def render_meshes(self):
        # set perspective view
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.fov, self.viewportRatio, self.camera.near, self.camera.far)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # set render state
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_CULL_FACE)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glShadeModel(GL_SMOOTH)

        # render
        glPushMatrix()
        glLoadIdentity()

        # Transform Camera
        glTranslatef(*self.camera.pos)

        # Transform Objects
        for obj in self.objectManager.getObjectList():
            # set shader
            curShader = obj.material.getShader()
            if self.lastShader != curShader:
                glUseProgram(curShader)
                self.lastShader = curShader

            glPushMatrix()
            glTranslatef(*obj.pos)
            glPopMatrix()
            obj.draw()
        # glut test
        glutSolidSphere(1.0, 32, 12)
        glutSolidCube( 1.0 )
        # Pop Camera Transform
        glPopMatrix()

    def render_postprocess(self):
        # set orthographic view
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity( )
        glOrtho( 0, self.width, 0, self.height, -1, 1 )
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity( )

        # set render state
        glEnable(GL_BLEND)
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)

    def renderScene(self):
        currentTime = time.time()
        delta = currentTime - self.currentTime

        if not self.inited or delta < self.fpsLimit:
            return

        # set timer
        self.currentTime = currentTime
        self.delta = delta
        self.fps = 1.0 / self.delta
        self.console.info("%.2f fps" % self.fps)
        self.console.info("%.2f ms" % (self.delta*1000))

        # clear buffer
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # render
        self.render_meshes()
        self.render_postprocess()
        self.console.render()
        self.console.clear()

        # final
        glFlush()
        glutSwapBuffers()

    def update(self):
        glutMainLoop()