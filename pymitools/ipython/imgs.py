"""
Functions for interacting with volumetric images in the IPython notebook
"""


import numpy as np

from ipywidgets import interact
import ipywidgets as widgets

import matplotlib.pyplot as plt


def win_lev(img, w, l, maxc=255):
    """
    Window (w) and level (l) data in img
    img: numpy array representing an image
    w: the window for the transformation
    l: the level for the transformation
    maxc: the maximum display color
    """

    m = maxc/(2.0*w)
    o = m*(l-w)
    return np.clip((m*img-o),0,maxc).astype(np.uint8)

def display_img(img, cmap="gray"):
    f, ax1 = plt.subplots(1)
    ax1.imshow(img, cmap=cmap)
    ax1.grid(False)
    ax1.yaxis.set_visible(False)
    ax1.xaxis.set_visible(False)
    return f, ax1

def view_volume(img):
    @interact(sl=widgets.IntSlider(min=0, max=img.shape[0]-1, value=int(img.shape[0]/2)),
                 win=widgets.IntSlider(min=1, max=2000, value=1000),
                 level=widgets.IntSlider(min=-1024, max=2000, value=0))
    def _view_slice(sl=0,win=1000,level=0):
        display_img(win_lev(img[sl,:,:],win,level))
