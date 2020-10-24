from os import path
from io import BytesIO
from typing import Union

import numpy as np
from PIL import Image
from cloudfiles import CloudFiles
from cloudvolume import Storage


def load_metadata(p: str) -> dict:
    from json import loads

    cf = CloudFiles(p)
    fnames = ["params.json", "metadata.json", "README.md", "raw/README.md"]
    cf.get(fnames, raw=True)
    for f in fnames:
        try:
            return loads(cf[f])
        except Exception:
            pass
    return {}


def _load_image(p: bytes):
    """
    Open TIF image and convert to numpy ndarray of dtype.
    Currently tested for only for uint8 -> uint8, uint32 or uint24 -> uint32
    """
    img_arr = np.array(Image.open(BytesIO(p)))
    print("img_arr.shape", img_arr.shape)
    if len(img_arr.shape) == 3:
        img_arr = np.dstack((np.zeros(img_arr.shape[:2] + (1,)), img_arr))
        img_arr = img_arr[:, :, ::-1]
        img_arr = img_arr.astype(np.uint8).view(np.uint32)
        img_arr = img_arr.reshape(img_arr.shape[:2]).T
    return img_arr.astype(np.uint32)


def load_from_stor(p: str, extension: str = "tif") -> dict:
    stor = Storage(p)
    files = stor.list_files(flat=True)  # pylint: disable=no-member

    names = []
    for f in sorted(files):
        if extension in f:
            names.append(f)

    print("count", len(names))
    imgs = []
    for f in names:
        imgs.append(_load_image(stor.get_file(f)))  # pylint: disable=no-member
    return {"seg": np.asarray(imgs).transpose(2, 1, 0)}


def load_from_dir(p: str, extension: str = "tif") -> dict:
    """Assume directory contains only the images to be stored"""
    files = CloudFiles(p)
    names = []
    for f in sorted(files.list()):
        if extension in f:
            names.append(f)

    print("count", len(names))
    files.get(names, raw=True)
    files_bytes = [files[k] for k in names]

    imgs = []
    for f in files_bytes:
        imgs.append(_load_image(f))
    return {"seg": np.asarray(imgs).transpose(2, 1, 0)}


def load_from_omni_h5(f) -> dict:
    from h5py import File

    omni_types = {"working": 1, "valid": 2, "uncertain": 3}
    dirpath = path.split(f)[0]
    with File(f, "r") as f:
        data = np.squeeze(np.array(f["main"])).transpose(2, 1, 0)
        if len(data.shape) > 3:
            print("only support 3 dimensional dataset")
            return None
        if data.dtype == np.uint8 or data.dtype == np.float32:
            return {"raw_image": data}
    try:
        seg_type = np.loadtxt(
            path.join(dirpath, "segments.txt"),
            dtype=(int, int),
            delimiter=",",
            skiprows=2,
        )
    except IOError:
        return {"seg": data.astype(np.uint32)}

    seg_data = {"seg": data.astype(np.uint32)}
    seg_type = dict(seg_type)
    for k in omni_types:
        seg = np.copy(data)
        fltr = np.vectorize(
            lambda x: True
            if x not in seg_type or seg_type[x] != omni_types[k]
            else False
        )
        mask = fltr(seg)
        seg[mask] = 0
        seg_data[k] = seg.astype(np.uint32)
    return seg_data


def write_to_dir(dst_dir, img_arr, extension="tif"):
    """Split 3d ndimgay along z dim into 2d sections & save as tifs"""
    for k in range(img_arr.shape[2]):
        f = path.join(dst_dir, "{0:03d}.{1}".format(k + 1, extension))
        img = Image.fromarray(img_arr[:, :, k].T)
        img.save(f)


def write_to_cloud_bucket(dst_dir, img_arr, extension="tif"):
    cf = CloudFiles(dst_dir)
    for k in range(img_arr.shape[2]):
        img = Image.fromarray(img_arr[:, :, k].T)
        img_bytes = BytesIO()
        img.save(img_bytes, format="tiff" if extension == "tif" else extension)
        cf.put("{0:03d}.{1}".format(k + 1, extension), img_bytes.getvalue())
