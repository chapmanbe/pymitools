import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import skimage.io as io
import sys
import girderProcessor as GP
import getpass
from markup import annoImage

import sys

def main():

    username = sys.argv[1]
    girderURL = sys.argv[2]
    girder_folder = sys.argv[3]
    case = 'CCTSPhi_000084'
    series = '20160101/CTA NECK W CONT/CT CTA NECK 3'

    gp = GP.GirderProcessor(girderURL, username, getpass.getpass("Enter girder password"),
                         folder_path=girder_folder)

    _, cases = gp.query_folder(girder_folder)
    print(cases)
    citems = list(cases.items())

    sids = GP.get_case_series(cases[case])

    dicom_data = gp.get_dicom_series(sids[series])

    vol, meta = GP.get_vol_image_from_stack(dicom_data)
    print(meta)

    fig1, ax1 = plt.subplots(1)
    a1 =annoImage(ax1, vol, meta)

    return a1, fig1


if __name__ == '__main__':
    ai, fig = main()
    ai.display_coronal()
    plt.show()

