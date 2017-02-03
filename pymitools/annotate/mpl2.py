from matplotlib.patches import Circle
from collections import OrderedDict, defaultdict
from scipy.ndimage import zoom
import gzip
import pickle

def onclick(event):
    print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          (event.button, event.x, event.y, event.xdata, event.ydata))

class annoImageMIP(object):

    _display_modes = ("axial", "sagittal", "coronal")
  
    def __init__(self, ax, vol, meta, anatomy_scheme=None, color_scheme=None):
        """
        Constructor for annoImaeMIP

        Arguments:

        ax -- matplotlib axis
        vol -- numpy array representing a volumetric image
        meta -- dictionary containing metadata for vol. meta must contain key/value pairs for
            "SliceThickness" and "PixelSpacing"

        anatomy_scheme --  a dictionary contining the anatomical scheme to annotate. Each values
            in the dictionary must contain a purl value 

        color_scheme -- a dictionary containing the colors to use for the annotation. All keys in 
            anatomy_scheme must also be present in color_scheme or a ValueError will be raised
        """
        self.ax = ax 

# Assumes the standard numpy z, y, x ordering
        self.mips = {"axial":vol.max(axis=0), "coronal":vol.max(axis=2), "sagittal":vol.max(axis=1)}
        self.meta = meta
        for a in anatomy_scheme.keys():
            if a not in color_scheme:
                raise ValueError("No color provided for %s"%a)
        for a, resource in anatomy_scheme.items():
            if "purl" not in resource:
                raise ValueError("Improper resource provided for %s"%a)
        self.anatomy = anatomy_scheme
        self.current_anatomy = None
        self.colors = color_scheme

        self.scale_ = meta["SliceThickness"]/meta["PixelSpacing"][0]

        self.annotations = defaultdict(OrderedDict)
        self.canvas = ax.figure.canvas
        self.cidrelease =  ax.figure.canvas.mpl_connect('button_release_event', 
                                                        self.button_release_callback)
        self.keyrelease =  ax.figure.canvas.mpl_connect('key_press_event', 
                                                        self.key_press_callback)
        cid = ax.figure.canvas.mpl_connect('button_press_event', onclick)
        self.display_mode = None
        self.patches = defaultdict(list)
        print("Constructor completed")

    def get_img_crds(self, event):
        """
        Take the mosue event location contained in event and convert to the i, j, k location of vol

        Conversion is determined by the current display_mode
        """
        print("in get_img_crds")
        if self.display_mode == "axial":
            return (event.xdata, event.ydata, -1)
        elif self.display_mode == "sagittal":
            return (event.xdata, -1, self.mips["sagittal"].shape[0]-event.ydata/self.scale_)
        elif self.display_mode == "coronal":
            return (-1, event.xdata, self.mips["coronal"].shape[0]-event.ydata/self.scale_)

    def save_patches(self):
        if self.display_mode:
            self.patches[self.display_mode] = self.ax.patches

    def list_anatomy(self):
        return {v:k for k,v in self._anatomy.items()}

    def set_anatomy(self, anatomy):
        if anatomy not in self.anatomy:
            raise KeyError("not a valid anatomy")
        self.current_anatomy = anatomy


    def display_axial(self):
        self.save_patches()
        self.display_mode = "axial"
        self.ax.patches = self.patches[self.display_mode]
        self.ax.imshow(self.mips[self.display_mode], cmap='gray')
        self.ax.figure.canvas.draw()


    def display_coronal(self):
        self.save_patches()
        self.display_mode = "coronal"
        self.ax.patches = self.patches[self.display_mode]
        self.ax.imshow(zoom(self.mips[self.display_mode], (self.scale_, 1.0))[::-1,:], cmap='gray')
        self.ax.figure.canvas.draw()

    def display_sagittal(self):
        self.save_patches()
        self.display_mode = "sagittal"
        self.ax.patches = self.patches[self.display_mode]
        self.ax.imshow(zoom(self.mips[self.display_mode], (self.scale_, 1.0))[::-1,:], cmap='gray')
        self.ax.figure.canvas.draw()

    def save_annotations(self, fname):
        with gzip.open(fname,"wb") as f0:
            pickle.dump((self._anatomy, self.color, self.annotations), f0)

    def export_annotations(self):
        """
        return annotations as a list of dictionaries. Each dictionary contains the anatomical
        location and the pixel (i,j,k) coordinates of the annotation
        """
        annotations = []
        for anatomy, values in self.annotations.items():
            for circ, crd in values.items():
                annotations.append({"anatomy":anatomy, "i":crd[0], "j":crd[1], "k":crd[2]})
        return annotations


    def button_release_callback(self, event):
        print("in button_release_callback")
        if event.inaxes!=self.ax:
            print("axes mismatch")
            return
        circ = Circle((event.xdata, event.ydata), radius=5,
                    color = self.clrs.get(self._anatomy[self.anatomy],(1,1,0)), alpha=0.3)
        self.annotations[self.anatomy][circ] = self.get_img_crds(event)
        self.ax.add_patch(circ)
        self.ax.figure.canvas.draw()

    def key_press_callback(self, event):
        if event.inaxes!=self.ax:
            return
        if event.key == 'd':
            circ = self.ax.patches.pop()
            if circ:
                del self.annotations[self.anatomy][circ]

        self.ax.figure.canvas.draw()

