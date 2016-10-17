"""
Utilities for working with DICOM images

"""

import dicom 
import numpy as np
import os
import glob


def get_dicom_series(ddir, sort="instance"):
    files = glob.glob(os.path.join(ddir,"*.dcm"))
    series = [dicom.read_file(f) for f in files]
    if sort.lower()=="instance":
        series.sort(key=lambda x: int(x.InstanceNumber))
    else:
        series.sort(key = lambda x: float(x[0x0018,0x0088].value))
    return series


def get_slice_spacing_from_series(dicom_stack, mode="median"):
    slice_locations = np.array([float(d.SliceLocation) for d in dicom_stack])
    spacings = np.abs(slice_locations[1:] - slice_locations[0:-1])
    if mode.lower() == 'mean':
        return np.mean(spacings)
    elif mode.lower() == 'median':
        return np.median(spacings)
    elif mode.lower() == 'min':
        return np.min(spacings)
    elif mode.lower() == 'max':
        return np.max(spacings)
    else:
        return spacings[0]
def get_slice_spacing(dicom_stack):
    try:
        return float(dicom_stack[0][0x0018,0x0088].value)
    except KeyError:
        return get_slice_spacing_from_series(dicom_stack)

def get_pixel_spacing(dicom_stack, mode="median"):
    """

    """
    pxs = np.array([float(d[0x0028,0x0030].value[0]) for d in dicom_stack])
    pys = np.array([float(d[0x0028,0x0030].value[1]) for d in dicom_stack])
    if mode.lower() == 'mean':
        return np.mean(pxs), np.mean(pys)
    elif mode.lower() == 'median':
        return np.median(pxs), np.median(pys)
    elif mode.lower() == 'min':
        return np.min(pxs), np.min(pys)
    elif mode.lower() == 'max':
        return np.max(pxs), np.max(pys)
    else:
        return pxs[0], pys[0]



def get_vol_image_from_stack(dicom_stack):
    """
    returns a numpy 3D array defined by a stack of pydicom objects along with a minimal meta data set

    """
    dicom_stack.sort(key=lambda x: int(x.InstanceNumber))
    vol = np.dstack([d.pixel_array for d in dicom_stack]).transpose()
    meta = {"PixelSpacing":get_pixel_spacing(dicom_stack),
            "SliceThickness":get_slice_spacing(dicom_stack)}
    return vol, meta


