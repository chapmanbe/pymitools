from matplotlib.patches import Circle
from collections import OrderedDict, defaultdict
from scipy.ndimage import zoom

class annoImage(object):
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
        self.vol = vol
        self.meta = meta
        self.anatomy = anatomy
        self.scale_ = meta["SliceThickness"]/meta["PixelSpacingX"]
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
            return (event.xdata, -1, self.vol.shape[0]-event.ydata/self.scale_)
        elif self.display_mode == 2:
            return (-1, event.xdata, self.vol.shape[0]-event.ydata/self.scale_)

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
        self.ax.imshow(self.vol.max(axis=0), cmap='gray')
        self.ax.figure.canvas.draw()
    def display_coronal(self):
        self.save_patches()
        self.display_mode = 2
        self.ax.patches = self.patches[self.display_mode]
        self.ax.imshow(zoom(self.vol.max(axis=2),(self.scale_, 1.0))[::-1,:], cmap='gray')
        self.ax.figure.canvas.draw()
    def display_sagittal(self):
        self.save_patches()
        self.display_mode = 1
        self.ax.patches = self.patches[self.display_mode]
        self.ax.imshow(zoom(self.vol.max(axis=1),(self.scale_, 1.0))[::-1,:], cmap='gray')
        self.ax.figure.canvas.draw()


    def button_release_callback(self, event):
        print("in callback")
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

