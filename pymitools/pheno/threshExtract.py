#! /usr/bin/env vtkpython

#
#  Adapted from dcm2stl by David T. Chen

#  Written by David T. Chen from the National Library of Medicine, dchen@mail.nih.gov.
#  It is covered by the Apache License, Version 2.0:
#      http://www.apache.org/licenses/LICENSE-2.0
#
import gc
import SimpleITK as sitk

def extract_tissue_component(img, threshInfo="", perform_aniso=False, perform_median=False):
    """
    img -- a SimpleITK image
    threshInfo -- a string specifying either a tissue type (bone, skin, soft, fat) or a
    4-tuple of threshold values

    returns a SimpleITK computed using the DoubleThrshold filter
    """

    if threshInfo.find("bone") > -1:
        thresholds = [200., 800., 1300., 1500.]
    elif threshInfo.find("skin") > -1:
        thresholds = [-200., 0., 500., 1500.]
    elif threshInfo.find("soft") > -1:
        thresholds = [-15., 30., 58., 100.]
    elif threshInfo.find("fat") > -1:
        thresholds = [-122., -112., -96., -70.]
    else:
        try:
            thresholds = [float(x) for x in threshInfo.split(",")]
        except:
            raise ValueError("could not convert threshInfo to 4-tuple")
    # check that there are 4 threshold values.
    if len(thresholds) != 4:
        raise ValueError("Error: Threshold is not of size 4.", thresholds)

    if perform_aniso:
        pixelType = img.GetPixelID()
        img = sitk.Cast(img, sitk.sitkFloat32)
        img = sitk.CurvatureAnisotropicDiffusion(img, .03)
        img = sitk.Cast(img, pixelType)
        gc.collect()

    img = sitk.DoubleThreshold(img, thresholds[0], thresholds[1], thresholds[2], thresholds[3], 255, 0)
    gc.collect()

    if perform_median:
        img = sitk.Median(img, [3,3,1])
        gc.collect()

    return img


