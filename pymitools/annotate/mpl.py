from matplotlib.patches import Circle
from collections import OrderedDict, defaultdict
from scipy.ndimage import zoom
import gzip
import pickle

class annoImageMIP(object):
    _anatomy = {0:"jaw",
               1:"spine",
           2:"clavical head",
           3:"mandibular joint"}
  
    clrs = {"jaw":(1,0,0),
            "spine":"blue",
            "clavical head":"green",
            "mandibular joint":"pink"}
    def __init__(self, ax, vol, meta, anatomy='jaw'):
        self.ax = ax
        self.mips = {"axial":vol.max(axis=0), "coronal":vol.max(axis=2), "sagittal":vol.max(axis=1)}
        self.meta = meta
        self.anatomy = anatomy
        self.scale_ = meta["SliceThickness"]/meta["PixelSpacing"][0]
        self.circles = defaultdict(OrderedDict)
        self.canvas = ax.figure.canvas
        self.cidrelease =             ax.figure.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.keyrelease =             ax.figure.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self.display_mode = None
        self.patches = defaultdict(list)

    def get_img_crds(self, event):
        if self.display_mode == 0:
            return (event.xdata, event.ydata, -1)
        elif self.display_mode == 1:
            return (event.xdata, -1, self.mips["sagittal"].shape[0]-event.ydata/self.scale_)
        elif self.display_mode == 2:
            return (-1, event.xdata, self.mips["coronal"].shape[0]-event.ydata/self.scale_)

    def save_patches(self):
        if self.display_mode:
            self.patches[self.display_mode] = self.ax.patches

    def add_anatomy(self, anatomy, color):
        if anatomy not in self._anatomy.values():
            self._anatomy[max(self._anatomy.keys())+1] = anatomy
            self.clrs[anatomy] = color
        else:
            raise ValueError("%s already specified"%anatomy)
            self.clrs[anatomy] = color
    def list_anatomy(self):
        return {v:k for k,v in self._anatomy.items()}
    def set_anatomy(self, anatomy):
        if anatomy not in self._anatomy:
            raise KeyError("not a specified anatomy")
        self.anatomy = anatomy
    def display_axial(self):
        self.save_patches()
        self.display_mode = 0
        self.ax.patches = self.patches[self.display_mode]
        self.ax.imshow(self.mips["axial"], cmap='gray')
        self.ax.figure.canvas.draw()
    def display_coronal(self):
        self.save_patches()
        self.display_mode = 2
        self.ax.patches = self.patches[self.display_mode]
        self.ax.imshow(zoom(self.mips["coronal"],(self.scale_, 1.0))[::-1,:], cmap='gray')
        self.ax.figure.canvas.draw()
    def display_sagittal(self):
        self.save_patches()
        self.display_mode = 1
        self.ax.patches = self.patches[self.display_mode]
        self.ax.imshow(zoom(self.mips["sagittal"],(self.scale_, 1.0))[::-1,:], cmap='gray')
        self.ax.figure.canvas.draw()

    def save_annotation(self, fname):
        with gzip.open(fname,"wb") as f0:
            pickle.dump((self._anatomy, self.color, self.circles), f0)

    def button_release_callback(self, event):
        if event.inaxes!=self.ax:
            return
        circ = Circle((event.xdata, event.ydata), radius=5,
                    color = self.clrs.get(self._anatomy[self.anatomy],(1,1,0)), alpha=0.3)
        self.circles[self.anatomy][circ] = self.get_img_crds(event)
        self.ax.add_patch(circ)
        self.ax.figure.canvas.draw()

    def key_press_callback(self, event):
        if event.inaxes!=self.ax:
            return
        if event.key == 'd':
            circ = self.ax.patches.pop()
            if circ:
                del self.circles[self.anatomy][circ]

        self.ax.figure.canvas.draw()

