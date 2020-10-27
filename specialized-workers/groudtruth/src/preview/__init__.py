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
from ..utils import checkpoint_notify


def upload(
    p: str,
    author: str,
    voxel_size: Tuple,
    slack_response: SlackResponse,
    transpose: bool = False,
) -> None:
    from cloudvolume.lib import Vec
    from ..data_io import load_images
    from .utils import create_nglink

    checkpoint_notify("Parsing metadata.", slack_response)
    meta = PreviewMeta(p, author=author)
    if not meta.voxel_size:
        # use user input only when voxel size is not available in meta
        meta.voxel_size = voxel_size

    checkpoint_notify(f"Loading data from {p}.", slack_response)
    data = load_images(p)
    checkpoint_notify("Loading data complete.", slack_response)

    ng_layers = {}
    for k, d in data.items():
        checkpoint_notify(f"Creating layer: {k}", slack_response)
        ng_layers[k] = upload_seg(meta, d, slack_response, transpose=transpose)

    checkpoint_notify("Creating neuroglancer link.", slack_response)
    checkpoint_notify(create_nglink(ng_layers, meta), slack_response, broadcast=True)


def upload_seg(
    meta: PreviewMeta,
    data: ndarray,
    slack_response: SlackResponse,
    transpose: bool = False,
):
    from numpy import transpose as np_transpose

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

    checkpoint_notify("Processing data.", slack_response)
    crop_bbox = meta.dst_bbox - meta.src_bbox.minpt
    data = data[crop_bbox.to_slices()]
    dst_cv[meta.dst_bbox.to_slices()] = (
        np_transpose(data, (1, 0, 2)) if transpose else data
    )

    with LocalTaskQueue(parallel=16) as tq:
        tasks = tc.create_downsampling_tasks(
            output_layer, mip=0, fill_missing=True, preserve_chunk_size=True
        )
        tq.insert_all(tasks)

        checkpoint_notify("Creating meshing tasks.", slack_response)
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