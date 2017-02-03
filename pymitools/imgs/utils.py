"""
Basic utilities for working with common medical imaging types.

"""
import os
def get_img_suffix(img_name):

    if img_name.endswith(".nii.gz"):
        return ".nii.gz"
    else:
        return os.path.splitext(img_name)[1]

