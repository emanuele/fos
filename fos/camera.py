from pyglet.gl import *
from vsml import vsml
import numpy as np

class Camera(object):

    def __init__(self):
        pass

    def update(self):
        " This should update the camera "
        pass

    def draw(self):
        pass

    def info(self):
        pass

# for ideas:
# http://code.enthought.com/projects/mayavi/docs/development/html/mayavi/auto/mlab_camera.html
# http://www.opengl.org/resources/faq/technical/viewing.htm

class VSMLCamera(Camera):

    def __init__(self):
        super(VSMLCamera, self).__init__()

    def draw(self):
        # use the modelview in the OpenGL fixed-pipeline
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(vsml.get_modelview())

    def reset(self):
        # load identity for modelview when initializing
        vsml.loadIdentity(vsml.MatrixTypes.MODELVIEW)

    def translate(self, x, y, z):
        # need to update .lu and call init identity and lookat again
        # or direclty change the modelview
        vsml.translate(x, y, z, vsml.MatrixTypes.MODELVIEW)

    def scale(self, x, y, z):
        vsml.scale(x, y, z, vsml.MatrixTypes.MODELVIEW)

    def rotate(self, angle, x, y, z):
        vsml.rotate(angle, x, y, z, vsml.MatrixTypes.MODELVIEW)


# http://www.lighthouse3d.com/tutorials/glut-tutorial/keyboard-example-moving-around-the-world/
class SimpleRotationCamera(VSMLCamera):

    def __init__(self):
        """ This camera uses the lookAt function to move """
        super(SimpleRotationCamera, self).__init__()

        self.setup()
        
        #self.camera_right_vector = [1, 0, 0]

        self.scroll_speed = 10
        self.mouse_speed = 0.1
        self.update()

    def setup(self):
        self.look_at_point = [0, 0, 0]
        self.camera_distance_from_lookat = 20
        self.angle = 0.0
        self.camera_line_of_sight = [0, 0, -1]
        self.camera_up_vector = [0, 1, 0]


    def rotate_xz(self, angle):
        """ Move on a circle on the xz plane
        """
        self.angle += angle
        self.camera_line_of_sight[0] = np.sin( self.angle )
        self.camera_line_of_sight[2] = -np.cos( self.angle )
        #print("Rotate camera")
        #print self.angle
        #print self.camera_line_of_sight
        self.update()

    def move(self, amount):
        """ Move along the light of sight
        """
        #self.look_at_point[0] += self.camera_line_of_sight[0] * amount
        #self.look_at_point[2] += self.camera_line_of_sight[2] * amount
        self.camera_distance_from_lookat += amount
        #print("Move camera")
        #print self.look_at_point
        self.update()

    def reset(self):
        self.setup()
        self.update()

    def update(self):
        super(SimpleRotationCamera, self).reset()
        # setup the initial look at updating the modelview
        # vsml.lookAt(*self.lu)
        camera_position = [
            self.look_at_point[0] + self.camera_line_of_sight[0] * self.camera_distance_from_lookat,
            self.look_at_point[1] + self.camera_line_of_sight[1] * self.camera_distance_from_lookat,
            self.look_at_point[2] - self.camera_line_of_sight[2] * self.camera_distance_from_lookat
        ]
        lu = camera_position + self.look_at_point + self.camera_up_vector
        super(SimpleRotationCamera, self).reset()
        vsml.lookAt(*lu )
        #print("Camera update called.")
        #print lu


class SimpleCamera(VSMLCamera):

    def __init__(self):
        """ This camera uses the lookAt function to move """
        super(SimpleCamera, self).__init__()
        self.reset()

    def setup(self):
        # The lookAt point
        self.focal = np.array( [0.0, 0.0, 0.0] )
        # Camera position
        self.location = np.array( [0.0, 0.0, 5.0] )
        # Need complete orientation of the camera, i.e. 3 orthogonal axes
        # They are almost implicit
        # look at direction = (self.focal - self.location).normalize()
        # Need the y up point, that is transformed together with the camera location
        self.yuppoint = np.array( [0.0, 1.0, 5.0] )
        # The y up vector is orthogonal to the look at direction
        # y up direction = self.yupoint - self.location
        # The the right vector is the crossproduct
        # right direction = crossp( lookatdirection, yupdirection )

        self.rotation_speed_factor = 1.5
        self.move_speed_factor = 1.0
        self.pan_speed_factor = 0.5

    def reset(self):
        self.setup()
        self.update()
        
    def get_lookatdir(self):
        a = self.focal - self.location
        return a / np.linalg.norm( a )

    def get_focal_location_distance(self):
        return np.linalg.norm( self.focal - self.location )

    def get_yup(self):
        a = self.yuppoint - self.location
        return a / np.linalg.norm( a )

    def get_right(self):
        a = np.cross( self.get_lookatdir(), self.get_yup() )
        return a / np.linalg.norm( a )
        
    def move_forward_all(self, amount):
        """ Move forward or backward, changing the camera position
        and the focal point
        """
        # need to change the three defining points
        # along the look at direction
        lookatdir = amount * self.move_speed_factor * self.get_lookatdir()
        self.focal += lookatdir
        self.location += lookatdir
        self.yuppoint += lookatdir

        self.update()

    def move_forward(self, amount):
        """ Move forward or backward, changing only the camera position
        and not the focal point
        """
        # need to change the three defining points
        # along the look at direction

        # TODO: do not move beyond the focal point!
        if self.get_focal_location_distance() < 5 and amount > 0:
            return
        
        lookatdir = amount * self.move_speed_factor * self.get_lookatdir()

        # TODO: depending on the distance focal to location, the amount is multiplied

        self.location += lookatdir
        self.yuppoint += lookatdir

        self.update()

    def rotate_around_focal(self, angle, cameraaxis):
        # rotates around the y up vector located at the focal point
        # needs formula for rotation around an arbitrary line
        # http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/
        from transform import general_rotation
        a,b,c = self.focal
        if cameraaxis == "yup":
            u,v,w = self.get_yup()
        elif cameraaxis == "right":
            u,v,w = self.get_right()
        else:
            u,v,w = self.get_yup()

        # rotate the camera location
        x,y,z = self.location
        self.location = general_rotation( x, y, z, a, b, c, u, v, w, angle * self.rotation_speed_factor )

        # rotate the yuppoint
        x,y,z = self.yuppoint
        self.yuppoint = general_rotation( x, y, z, a, b, c, u, v, w, angle * self.rotation_speed_factor )

        self.update()

    def pan(self, dx, dy):
        """ Pan the camera and not focal point on the plane spanned by the yup and right vector
        dx in right direction, dy in yup direction
        """
        panvect = ( self.get_right() * dx + self.get_yup() * dy ) * self.pan_speed_factor
        self.focal += panvect
        self.location += panvect
        self.yuppoint += panvect

        self.update()

    def update(self):
        """ Update the camera position, focal point and yup vector
        """
        vsml.loadIdentity(vsml.MatrixTypes.MODELVIEW)
        x,y,z = self.location
        a,b,c = self.focal
        u,v,w = self.get_yup()
        vsml.lookAt( x,y,z,a,b,c,u,v,w )

    def __repr__(self):
        ret = "Camera Information\n"
        ret += "Location: {0}\n".format(self.location)
        ret += "Focal point: {0}\n".format(self.focal)
        ret += "Look at direction : {0}\n".format(self.get_lookatdir())
        ret += "Y up direction : {0}\n".format(self.get_yup())
        ret += "Right direction : {0}\n".format(self.get_right())
        return ret



            

# http://nehe.gamedev.net/article/camera_class_tutorial/18010/
# http://www.flipcode.com/archives/OpenGL_Camera.shtml
# Google: OpenGL camera class
# VTK cameras
# Rotations: http://www.siggraph.org/education/materials/HyperGraph/modeling/mod_tran/3drota.htm