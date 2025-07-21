import h5py
import numpy as np
import get_xyz
import constants
from pathlib import Path
import hdf5plugin
import add_geometry_streaks
import sys
from tqdm import tqdm

from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import signal


def clip_scalar(val, vmin, vmax):
    """ convenience function to avoid using np.clip for scalar values """
    return vmin if val < vmin else vmax if val > vmax else val

class Application(QtWidgets.QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.Z = data.shape[0]

        self.data = data

        self.frame_index = -1

        self.in_replot = False

        self.geom = get_xyz.Geom_cor(np.float16)

        self.initUI()



    def initUI(self):
        # Define a top-level widget to hold everything
        w = QtWidgets.QWidget()

        # 2D plot for the cspad and mask
        self.plot = pg.ImageView()

        if self.Z > 1 :
            # add a z-slider for image selection
            z_sliderW = pg.PlotWidget()
            z_sliderW.plot(np.arange(self.Z), pen=(255, 150, 150))
            z_sliderW.setFixedHeight(100)

            # vline
            self.bounds = [0, self.Z-1]
            self.vline = z_sliderW.addLine(x = 0, movable=True, bounds = self.bounds)
            self.vline.setValue(0)
            self.vline.sigPositionChanged.connect(self.replot_frame)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.plot)
        vbox.addWidget(z_sliderW)

        self.replot_frame(True)

        ## Display the widget as a new window
        w.setLayout(vbox)
        self.setCentralWidget(w)
        self.resize(800, 480)


    def replot_frame(self, auto=False):
        print('reploting')
        if self.in_replot:
            print('already reploting')
            return
        try:
            self.in_replot = True
            i = int(self.vline.value())
            print(f'trying to replot {i}')
            if self.frame_index != i :
                self.frame_index = i
                self.updateDisplayRGB(auto)
        finally:
            self.in_replot = False

    def updateDisplayRGB(self, auto = False):
        """
        Make an RGB image (N, M, 3) (pyqt will interprate this as RGB automatically)
        with masked pixels shown in blue at the maximum value of the cspad.
        This ensures that the masked pixels are shown at full brightness.
        """
        print(f'{self.frame_index=}')
        im = self.geom.get(self.data[self.frame_index])
        if not auto :
            self.plot.setImage(im.T[::-1])
        else :
            self.plot.setImage(im.T[::-1], autoRange = False, autoLevels = False, autoHistogramRange = False)

    def keyPressEvent(self, event):
        super(Application, self).keyPressEvent(event)
        key = event.key()

        if key == QtCore.Qt.Key_Left :
            ind = clip_scalar(self.frame_index - 1, self.bounds[0], self.bounds[1]-1)
            self.vline.setValue(ind)
            self.replot_frame()

        elif key == QtCore.Qt.Key_Right :
            ind = clip_scalar(self.frame_index + 1, self.bounds[0], self.bounds[1]-1)
            self.vline.setValue(ind)
            self.replot_frame()

# run = int(sys.argv[1])
fnam = sys.argv[1]


# find pattern with a lot of streaks
# check that input dir exists
# run_dir = Path(f'{constants.raw}/run{run:>04}/data')
# assert(run_dir.is_dir())

# get file list
# fnams = sorted(list(run_dir.glob('acq*.JF07T32V02.h5')))
# fnam = fnams[0]


with h5py.File(fnam) as f:
    data = f['/data/JF07T32V02/data']

    # Always start by initializing Qt (only once per application)
    signal.signal(signal.SIGINT, signal.SIG_DFL) # allow Control-C
    app = QtWidgets.QApplication([])

    pg.setConfigOption('background', pg.mkColor(0.3))
    pg.setConfigOption('foreground', 'w')
    pg.setConfigOptions(antialias=True)
        
    a = Application(data)
    a.show()

    ## Start the Qt event loop
    app.exec_()
