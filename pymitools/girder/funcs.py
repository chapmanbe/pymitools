"""

"""

from io import BytesIO 
import SimpleITK as sitk
import skimage.io as io
import json
import tempfile
import os 

from .. girder import girderProcessor as girder
from .. girder import girderUploader as girderUploader
from .. imgs.utils import get_img_suffix

def get_item_fileID(gp, itemID, fnum=0, mimeType='application/json'):
    fid = [f['_id'] for f in gp._client.listFile(itemID) if 
           f["mimeType"]==mimeType][fnum]
    return fid

def download_img_file(gp, itemID=None, fnum=0):
    """

    """
    if not itemID:
        raise ValueError("itemID must be Valid")
    f = [f for f in gp._client.listFile(itemID) ][fnum]
    fid = f["_id"]
    fname = f["name"]
    suffix = os.path.splitext(fname)[1]
    osh, fname = tempfile.mkstemp(suffix=suffix)
    gp._client.downloadFile(fid, fname)
    img = io.imread(fname)
    os.remove(fname)
    return img
def download_json_file(gp, fid=None, itemID=None):
    if itemID and not fid:
        fid = get_item_fileID(gp,itemID, mimeType="application/json")
    output = BytesIO()
    gp._client.downloadFile(fid, output)
    return json.loads(output.getvalue().decode())
def download_sitk_file(gp, itemID=None, fnum=0):
    if not itemID:
        raise ValueError("itemID must be Valid")
    f = [f for f in gp._client.listFile(itemID) ][fnum]
    fid = f["_id"]
    fname = f["name"]
    suffix = get_img_suffix(fname)
    osh, fname = tempfile.mkstemp(suffix=suffix)
    gp._client.downloadFile(fid, fname)
    img = sitk.ReadImage(fname)
    os.remove(fname)
    return img
def upload_sitk_file(gp, img, name, folderID):
    
    #suffix = os.path.splitext(name)[1]
    #osh, fname = tempfile.mkstemp(suffix=suffix)
    #img = io.WriteImage(img, fname)
    #with open(fname,'rb') as f0:
    #    gp._client.uploadFile(folderID, f0, name, os.path.getsize(fname), parentType='folder')

    #os.remove(fname)

    with tempfile.TemporaryDirectory() as tmpdir:
        fname = os.path.join(tmpdir, name)
        img = sitk.WriteImage(img, fname)
        with open(fname,'rb') as f0:
            gp._client.uploadFile(folderID, 
                    f0, name, 
                    os.path.getsize(fname), 
                    parentType='folder')


def upload_img_file(gp, img, name, folderID):
    

    with tempfile.TemporaryDirectory() as tmpdir:
        fname = os.path.join(tmpdir, name)
        img = io.imsave(fname, img)
        with open(fname,'rb') as f0:
            gp._client.uploadFile(folderID, 
                    f0, name, 
                    os.path.getsize(fname), 
                    parentType='folder')

def get_gp(folder, url, username, password):


    gp = girder.GirderProcessor(url, username, password, 
                                        folder_path=folder)
    return gp

def get_uploader(url, user, password):
    return girderUploader.GirderUploader(url, user, password)

def get_cases(gp, folderId):

    _, cases = gp.query_folder(folderId)
    citems = list(cases.items())
    print("%d cases identified"%len(citems))
    return citems

def match_sub_volumes(case, sub_volumes):
    for s in sub_volumes:
        if case in s:
            return s
    else:
        return ""
    
def get_image(gp, case_series, definition):
    try:
        def_file = case_series[[k for k in case_series.keys() if definition in k][0]]
    except IndexError:
        def_file = None

    return def_file
    
    
def find_uploaded_item(gp, current_case, uname):
    current_items = gp.get_case_series(current_case)
    for key in current_items.keys():
        if uname in key:
            return current_items[key] 
