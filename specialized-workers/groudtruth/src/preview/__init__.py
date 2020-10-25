# pylint: disable=no-member, unsupported-assignment-operation
from typing import Tuple
from os import environ
from datetime import datetime
from secrets import token_hex


from numpy import ndarray
import igneous.task_creation as tc
from cloudvolume import CloudVolume
from taskqueue import LocalTaskQueue
from CloudBotWorkersCommon.slack import Response as SlackResponse

from .meta import Meta as PreviewMeta


def upload(
    p: str, author: str, voxel_size: Tuple, slack_response: SlackResponse
) -> None:
    from cloudvolume.lib import Vec
    from ..data_io import load_images
    from .utils import create_nglink

    slack_response.send("Parsing metadata.")
    meta = PreviewMeta(p, author=author)

    if not meta.voxel_size:
        # use user input only when voxel size is not available in meta
        meta.voxel_size = voxel_size

    slack_response.send(f"Loading data from {p}.")
    data = load_images(p)
    slack_response.send("Loading data complete.")

    ng_layers = {}
    for k, d in data.items():
        slack_response.send(f"Creating layer: {k}")
        ng_layers[k] = upload_seg(meta, d, slack_response)

    slack_response.send("Creating neuroglancer link.")
    result = create_nglink(ng_layers, meta)
    print(result)
    slack_response.send(result, broadcast=True)


def upload_seg(meta: PreviewMeta, data: ndarray, slack_response: SlackResponse):
    from numpy import transpose

    em = CloudVolume(meta.em_layer, mip=meta.dst_mip)
    output_layer = f"{environ['GT_BUCKET_PATH']}/{meta.author}/preview/{token_hex(8)}"
    info = CloudVolume.create_new_info(
        num_channels=1,
        layer_type="segmentation",
        data_type="uint32",
        encoding="raw",
        resolution=em.resolution,
        voxel_offset=meta.dst_bbox.minpt,
        volume_size=meta.dst_bbox.size3(),
        mesh=f"mesh_mip_{meta.dst_mip}_err_0",
        chunk_size=(64, 64, 8),
    )

    dst_cv = CloudVolume(output_layer, info=info, mip=0, cdn_cache=False)
    dst_cv.provenance.description = "Image directory ingest"
    dst_cv.provenance.processing.append(
        {
            "method": {
                "task": "ingest",
                "image_path": meta.em_layer,
            },
            "date": str(datetime.today()),
            "script": "cloud_bot",
        }
    )
    dst_cv.provenance.owners = [meta.author]
    dst_cv.commit_info()
    dst_cv.commit_provenance()

    slack_response.send("Processing data.")
    crop_bbox = meta.dst_bbox - meta.src_bbox.minpt
    data = data[crop_bbox.to_slices()]
    dst_cv[meta.dst_bbox.to_slices()] = transpose(data, (1, 0, 2))

    with LocalTaskQueue(parallel=16) as tq:
        tasks = tc.create_downsampling_tasks(
            output_layer, mip=0, fill_missing=True, preserve_chunk_size=True
        )
        tq.insert_all(tasks)

        slack_response.send("Creating meshing tasks.")
        tasks = tc.create_meshing_tasks(
            output_layer,
            mip=meta.dst_mip,
            simplification=False,
            shape=(320, 320, 40),
            max_simplification_error=0,
        )
        tq.insert_all(tasks)
        tasks = tc.create_mesh_manifest_tasks(output_layer, magnitude=1)
        tq.insert_all(tasks)
    return output_layer