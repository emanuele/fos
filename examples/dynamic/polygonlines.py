import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

def create_window():
    
    w = Window()

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm") )

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [5,10,0],
                       [10,5,0]], dtype = np.float32 )

    conn = np.array( [ 0, 1, 1, 2, 1, 3 ], dtype = np.uint32 )

    colt = np.zeros( (3,4,2), dtype = np.float32 )
    colt[:,:,0] = np.array( [
                      [0, 1, 0, 1],
                      [0, 0, 1, 1],
                      [1, 0, 0, 0.5]] , dtype = np.float32 )
    colt[:,:,1] = np.array( [
                      [1, 0, 0, 0.2],
                      [0, 1, 0, 0.2],
                      [0, 0, 1, 1.0]] , dtype = np.float32 )

    act = DynamicPolygonLinesSimple( name = "Polygon Lines", vertices = vert, connectivity = conn, colors = colt)

    region.add_actor( act )

    w.add_region( region )

    return w, act

if __name__ == '__main__':
    app = QApplication(sys.argv)
    create_window()
    sys.exit(app.exec_())