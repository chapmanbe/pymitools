import matplotlib.pyplot as plt
import glob
import os
import sys
import dicom
import sys
import pymitools.dicom.utils as dutils
import pymitools.annotate.mpl as ampl

def get_dicom_series(ddir):
    files = glob.glob(os.path.join(ddir,"*.dcm"))
    return [dicom.read_file(f) for f in files]
def main():
    ddir = sys.argv[1]


    dicom_data = dutils.get_dicom_series(ddir)

    vol, meta = dutils.get_vol_image_from_stack(dicom_data)
    print(meta)

    fig1, ax1 = plt.subplots(1)
    a1 = ampl.annoImage(ax1, vol, meta)

    return a1, fig1


if __name__ == '__main__':
    ai, fig = main()
    ai.display_coronal()
    ai.set_anatomy(0)
    ai.display_sagittal()
    plt.show()

