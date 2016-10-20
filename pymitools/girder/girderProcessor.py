"""Includes GirderDicomProcessor class.

GirderDicomProcessor class authenticates with girder instance and
processes dicom images.

Dicom files are downloaded from girder and the pixel data is extracted.
Can processes either a folder of dicom images or a single volumetric
dicom image file.

"""

import dicom
import girder_client
from io import BytesIO
import numpy as np
import os

class GirderProcessor:
    def __init__(self, api_url, username, password,
                 folder_path=None):
        """Authenticate with girder instance then process dicom images.

        :param api_url: The API URL of the girder server
        :param username: The username of the girder user
        :param password: The password of the girder user
        :param folder_path: the unix style path to the folder containing each
                            individual dicom image file on girder
                            (default None)
        :param file_path: the unix style path to the 3d dicom volumetric scan
                          (default None)

        """
        self._client = girder_client.GirderClient(apiUrl=api_url)
        self._client.authenticate(username, password)

        if folder_path:
            self.folder_path = folder_path
        self._images = []
        self._processed = False

    def get_items_folders(self, folderId):
        return {i['name']:i["_id"] for i in self._client.listItem(folderId)},\
               {f['name']:f["_id"] for f in self._client.listFolder(folderId)}


    def query_folder(self, folder_path):
        """Download and extract pixel data from images located in folder.

        Scan through the file at the already given folder path and store pixel
        information for each dicom image. Processed images can be accessed via
        get_image method.

        """
        folder = self._client.resourceLookup(folder_path)
        return self.get_items_folders(folder['_id'])


    def read_dicom(self, dfile, verbose=False):
        """
        """
        fileId = dfile['_id']
        # create file like opbject and download file to it
        output = BytesIO()
        if verbose:
            print("Downloading file...", fileId)
        self._client.downloadFile(fileId, output)
        if verbose:
            print("Download complete.")
        # seek file position back to the front
        output.seek(0)

        # read file as dicom image
        return dicom.read_file(output)
    def get_dicom_item_series_files(self, itemID):
        """
        Download and extract pixel data from dicom image file.

        Scan through the file at the already given file path and store pixel
        information for each dicom image slice. Processed images can be
        accessed via get_image method.

        """
        dfiles = [f for f in self._client.listFile(itemID) if f['mimeType'] == 'application/dicom']
        return dfiles
        return [self.read_dicom(dfile) for dfile in dfiles]


    def get_dicom_series(self, itemID):
        """
        Download and extract pixel data from dicom image file.

        Scan through the file at the already given file path and store pixel
        information for each dicom image slice. Processed images can be
        accessed via get_image method.

        """
        dfiles = self.get_dicom_item_series_files(itemID)
        return [self.read_dicom(dfile) for dfile in dfiles]


    def get_case_dates(self, caseID):
        _, dates = self.get_items_folders(caseID)
        return dates
    def get_date_exams(self, dateID):
        _, exams = self.get_items_folders(dateID)
        return exams
    def get_exam_series(self, examID):
        series, _ = self.get_items_folders(examID)
        return series


    def get_case_series(self, caseID):
        case_series = {}
        for d, did in self.get_case_dates(caseID).items():
            for e, eid in self.get_date_exams(did).items():
                for s, sid in self.get_exam_series(eid).items():
                    case_series[os.path.join(d,e,s)] = sid
        return case_series

def get_vol_image_from_stack(dd):
    dd.sort(key=lambda x: int(x.InstanceNumber))
    vol = np.dstack([d.pixel_array for d in dd]).transpose()
    meta = {"PixelSpacingX":float(dd[0].data_element("PixelSpacing").value[0]),
            "PixelSpacingY":float(dd[0].data_element("PixelSpacing").value[1]),
            "SliceThickness":float(dd[0].data_element("SliceThickness").value)}
    return vol, meta



