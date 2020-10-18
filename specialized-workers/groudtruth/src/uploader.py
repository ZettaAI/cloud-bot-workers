# pylint: disable=no-member, unsupported-assignment-operation

from os import environ
from datetime import datetime
from secrets import token_hex

import igneous.task_creation as tc
from cloudvolume import CloudVolume
from cloudvolume.lib import Vec
from cloudvolume.lib import Bbox
from taskqueue import LocalTaskQueue


def upload(p, meta, author: str = "cloud_bot_gtbot") -> None:
    from .data_io import load_from_dir
    from .utils import create_nglink

    try:
        parameters = meta["raw"]
        image_layer = parameters["cv_path"]
    except KeyError:
        parameters = meta["processing"]
        image_layer = parameters["cv_path"]
    except KeyError:
        raise ValueError("Could not understand meta.")

    try:
        size = Vec(*parameters["size"])
        center = Vec(*parameters["center"])
        vol_start = center - size // 2
        vol_stop = center + size // 2 - Vec(1, 1, 0)
    except KeyError:
        try:
            bbox = parameters["bbox"]
            vol_start = Vec(*bbox[0:3])
            vol_stop = Vec(*bbox[3:6])
        except KeyError:
            raise ValueError("Bounding box parameters missing.")

    ng_layers = {}
    data = load_from_dir(p)
    for k, v in data.items():
        f = upload_img if ("img" in k or "image" in k) else upload_seg
        ng_layers[k] = f(v, vol_start, vol_stop, meta, author)
    center = [(vol_start[i] + vol_stop[i]) / 2 for i in range(3)]
    return create_nglink(image_layer, ng_layers, center, parameters["voxel_size"])


def upload_img(data, vol_start, vol_stop, meta, author):
    from numpy import uint8

    parameters = meta["raw"]
    pad = Vec(*parameters["pad"])
    image_layer = parameters["cv_path"]
    mip = parameters["mip"]

    output_layer = f"gs://{environ['GT_BUCKET_PATH']}/{author}/preview/{token_hex(8)}"
    dst_bbox = Bbox(vol_start, vol_stop)
    mip0_bbox = Bbox(dst_bbox.minpt - pad, dst_bbox.maxpt + pad)
    data_type = "uint8" if data.dtype == uint8 else "float32"
    info = CloudVolume.create_new_info(
        num_channels=1,
        layer_type="image",
        data_type=data_type,
        encoding="raw",
        resolution=CloudVolume(image_layer, mip=mip).resolution,
        voxel_offset=dst_bbox.minpt,
        volume_size=dst_bbox.size3(),
        chunk_size=(64, 64, 8),
    )

    cv = CloudVolume(output_layer, mip=0, info=info)
    for i in range(mip):
        cv.add_scale([1 << (i + 1), 1 << (i + 1), 1])
    cv.commit_info()
    cv.provenance.processing.append(
        {"owner": author, "timestamp": str(datetime.today()), "image_path": image_layer}
    )
    cv.commit_provenance()

    parallel = 16
    cv = CloudVolume(
        output_layer,
        mip=mip,
        parallel=parallel,
        bounded=False,
        autocrop=True,
        cdn_cache=False,
        fill_missing=True,
    )

    src_bbox = cv.bbox_to_mip(mip0_bbox, 0, mip)
    dst_bbox = cv.bbox_to_mip(dst_bbox, 0, mip)
    crop_bbox = dst_bbox - src_bbox.minpt
    data = data[crop_bbox.to_slices()]
    cv[dst_bbox.to_slices()] = data
    with LocalTaskQueue(parallel=parallel) as tq:
        tasks = tc.create_downsampling_tasks(
            output_layer, mip=mip, fill_missing=True, preserve_chunk_size=True
        )
        tq.insert_all(tasks)
    return output_layer


def upload_seg(data, vol_start, vol_stop, meta, author):
    parameters = meta["raw"]
    pad = Vec(*parameters["pad"])
    image_layer = parameters["cv_path"]
    mip = parameters["mip"]

    output_layer = f"gs://{environ['GT_BUCKET_PATH']}/{author}/preview/{token_hex(8)}"
    dst_bbox = Bbox(vol_start, vol_stop)
    mip0_bbox = Bbox(dst_bbox.minpt - pad, dst_bbox.maxpt + pad)
    info = CloudVolume.create_new_info(
        num_channels=1,
        layer_type="segmentation",
        data_type="uint32",
        encoding="raw",
        resolution=CloudVolume(image_layer, mip=mip).resolution,
        voxel_offset=dst_bbox.minpt,
        volume_size=dst_bbox.size3(),
        mesh=f"mesh_mip_{mip}_err_0",
        chunk_size=(64, 64, 8),
    )

    cv = CloudVolume(output_layer, mip=0, info=info)
    for i in range(mip):
        cv.add_scale([1 << (i + 1), 1 << (i + 1), 1])
    cv.commit_info()
    cv.provenance.processing.append(
        {"owner": author, "timestamp": str(datetime.today()), "image_path": image_layer}
    )
    cv.commit_provenance()

    parallel = 16
    cv = CloudVolume(
        output_layer,
        mip=mip,
        parallel=parallel,
        bounded=False,
        autocrop=True,
        cdn_cache=False,
        fill_missing=True,
    )

    src_bbox = cv.bbox_to_mip(mip0_bbox, 0, mip)
    dst_bbox = cv.bbox_to_mip(dst_bbox, 0, mip)
    crop_bbox = dst_bbox - src_bbox.minpt
    data = data[crop_bbox.to_slices()]
    cv[dst_bbox.to_slices()] = data

    with LocalTaskQueue(parallel=parallel) as tq:
        tasks = tc.create_downsampling_tasks(
            output_layer, mip=mip, fill_missing=True, preserve_chunk_size=True
        )
        tq.insert_all(tasks)
        tasks = tc.create_meshing_tasks(
            output_layer,
            mip=mip,
            simplification=False,
            shape=(320, 320, 40),
            max_simplification_error=0,
        )
        tq.insert_all(tasks)
        tasks = tc.create_mesh_manifest_tasks(output_layer, magnitude=1)
        tq.insert_all(tasks)
    return output_layer