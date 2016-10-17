import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import skimage.io as io
import sys
import girderProcessor as GP
import getpass
from markup import annoImage
import dicom
import sys
def get_dicom_series(ddir):
    files = glob.glob(os.path.join(ddir,"*.dcm"))
    return [dicom.read_file(f) for f in files]
def main():
    ddir = sys.argv[1]


    dicom_data = get_dicom_series(ddir)

    vol, meta = GP.get_vol_image_from_stack(dicom_data)
    print(meta)

    fig1, ax1 = plt.subplots(1)
    a1 =annoImage(ax1, vol, meta)

    return a1, fig1


if __name__ == '__main__':
    ai, fig = main()
    ai.display_coronal()
    plt.show()

