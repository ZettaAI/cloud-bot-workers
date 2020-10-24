# pylint: disable=no-member, unsupported-assignment-operation

from os import environ
from datetime import datetime
from secrets import token_hex

import igneous.task_creation as tc
from cloudvolume import CloudVolume
from cloudvolume.lib import Vec
from cloudvolume.lib import Bbox
from taskqueue import LocalTaskQueue
from CloudBotWorkersCommon.slack import Response as SlackResponse


def upload(p: str, meta: dict, author: str, slack_response: SlackResponse) -> None:
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

    slack_response.send("Parsing parameters from metadata.")
    parameters["voxel_size"] = [10, 10, 40]
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

    print(f"Loading data from {p}")
    slack_response.send(f"Loading data from {p}")

    ng_layers = {}
    data = load_from_dir(p)
    print("Loading data complete.")
    slack_response.send("Loading data complete.")

    for k, v in data.items():
        print(f"Creating layer: {k}")
        slack_response.send(f"Creating layer: {k}")
        ng_layers[k] = upload_seg(v, vol_start, vol_stop, parameters, author)

    print("Creating neuroglancer link.")
    slack_response.send("Creating neuroglancer link.")

    center = [(vol_start[i] + vol_stop[i]) / 2 for i in range(3)]
    result = create_nglink(image_layer, ng_layers, center, parameters["voxel_size"])
    print(result)
    slack_response.send(result, broadcast=True)


def upload_seg(data, vol_start, vol_stop, parameters, author):
    from numpy import transpose

    print("upload_seg")
    pad = Vec(*parameters["pad"])
    image_layer = parameters["cv_path"]
    mip = parameters["dst_mip"]
    em = CloudVolume(image_layer, mip=mip)

    output_layer = f"{environ['GT_BUCKET_PATH']}/{author}/preview/{token_hex(8)}"
    dst_bbox = Bbox(vol_start, vol_stop)
    src_bbox = Bbox(dst_bbox.minpt - pad, dst_bbox.maxpt + pad)
    info = CloudVolume.create_new_info(
        num_channels=1,
        layer_type="segmentation",
        data_type="uint32",
        encoding="raw",
        resolution=em.resolution,
        voxel_offset=dst_bbox.minpt,
        volume_size=dst_bbox.size3(),
        mesh=f"mesh_mip_{mip}_err_0",
        chunk_size=(64, 64, 8),
    )

    dst_cv = CloudVolume(output_layer, info=info, mip=0, cdn_cache=False)
    dst_cv.provenance.description = "Image directory ingest"
    dst_cv.provenance.processing.append(
        {
            "method": {
                "task": "ingest",
                "image_path": image_layer,
            },
            "date": str(datetime.today()),
            "script": "cloud_bot",
        }
    )
    dst_cv.provenance.owners = [author]
    dst_cv.commit_info()
    dst_cv.commit_provenance()

    parallel = 16
    crop_bbox = dst_bbox - src_bbox.minpt
    data = data[crop_bbox.to_slices()]

    dst_cv[dst_bbox.to_slices()] = transpose(data, (1, 0, 2))
    with LocalTaskQueue(parallel=parallel) as tq:
        tasks = tc.create_downsampling_tasks(
            output_layer, mip=0, fill_missing=True, preserve_chunk_size=True
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