"""
Functions to extract skin surface from a binary image
"""


import numpy as np
import scipy.ndimage as ndi 
import skimage.morphology as morph
import skimage.measure as meas 
import SimpleITK as sitk
from skimage.measure import label
import scipy.stats as stats

def get_ll(l, num):
    """find the largest labeled region in mask"""
    lbls = [(np.sum(np.where(l==i,1,0)),i) for i in range(1,num+1)]
    lbls.sort(reverse=True)
    return lbls[0][1]    
def get_2dmax_mask(aimg):
    """

    """
    mask1 = np.zeros(aimg.shape,dtype=np.uint16)

    for k in range(aimg.shape[0]):
        sl = aimg[k,:,:]
        if np.any(sl):
            l, num = meas.label(sl, return_num=True)
            inds = np.where(l==get_ll(l, num))
            mask1[k,:,:][inds] = 1 
    return mask1
def get_skin(aimg):
    """

    """
    mask1 = get_2dmax_mask(aimg) 
    mask1 = morph.closing(mask1,selem=np.ones((7,3,3)))
    for k in range(mask1.shape[0]):
        mask1[k,:,:] = morph.remove_small_holes(mask1[k,:,:], 
                                                min_size=1500)
    l, num = meas.label(mask1, return_num=True)
    mask2 = np.where(meas.label(mask1)==get_ll(l,num), 1,0)
    mask3 = np.where(mask2==0, 1, 0)
    l,num = meas.label(mask3, return_num=True)
    mask4 = np.where(l==get_ll(l, num), 1, 0)
    mask5 = morph.dilation(mask4)-mask4
    return mask5
def array_to_image(img,ref, zoom=1):
    spacing = np.array(ref.GetSpacing())/zoom
    skin_img = sitk.GetImageFromArray(img.astype(np.uint16))
    skin_img.SetSpacing(spacing)
    skin_img.SetOrigin(ref.GetOrigin())
    skin_img.SetDirection(ref.GetDirection())
    return skin_img
def image_to_array(img, value=255, zoom=1):
    aimg = sitk.GetArrayFromImage(img)
    aimg = np.where(aimg==255,1,0)
    aimg = ndi.zoom(aimg, zoom)
    return aimg
def extract_skin_from_mask(img, new_label=3, value=255, zoom=1):
    """

    """

    aimg = image_to_array(img, zoom=zoom, value=value)
    mask = get_skin(aimg)
    skin_img = array_to_image(new_label*mask, img)
    return skin_img


def get_com_label_mode(cms):
    return stats.mode(cms).mode[0]

def get_slice_contour_means(aimg):
    labels = label(aimg.max()-aimg, connectivity=1)
    cms = []
    for k in range(aimg.shape[0]):
        inds = np.nonzero(aimg[k,:,:])
        
        com_label = labels[k, int(np.mean(inds[0])),int(np.mean(inds[1]))]
        cms.append(com_label)
    return cms
def get_modal_com_label(aimg):
    return get_com_label_mode(get_slice_contour_means(aimg))

def fill_shell(img):
    aimg = sitk.GetArrayFromImage(img)
    labels = label(aimg.max()-aimg, connectivity=1)
    com_label = get_modal_com_label(aimg)
    filled = np.where(labels == com_label, 1,0).astype(np.uint8)
    newImg = sitk.GetImageFromArray(filled)
    newImg.SetSpacing(img.GetSpacing())
    newImg.SetDirection(img.GetDirection())
    newImg.SetOrigin(img.GetOrigin())
    return newImg
