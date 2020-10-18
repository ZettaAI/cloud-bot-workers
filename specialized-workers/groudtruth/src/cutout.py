"""
T Macrina
190423

Create VAST directory from CloudVolume cutout
"""
import os


def get_first_image_layer(layers: list) -> str:
    for l in layers:
        if l["type"] == "image":
            return l["source"].replace("precomputed://", "")


def get_bboxes(layers: list) -> list:
    from secrets import token_hex

    bboxes = []
    for l in layers:
        try:
            annotations = l["annotations"]
        except KeyError:
            continue

        for a in annotations:
            if a["type"] != "axis_aligned_bounding_box":
                continue
            pointA = list(map(int, a["pointA"]))
            pointB = list(map(int, a["pointB"]))
            bbox = pointA + pointB
            name = token_hex(8)
            if "description" in a:
                retain = (" ", ".", "_")
                safe_name = "".join(
                    c if c.isalnum() or c in retain else "_" for c in a["description"]
                ).rstrip()
                name = safe_name[:16] + "_" + name
            bboxes.append({"name": name, "bbox": bbox})
    return bboxes


def create_cutouts(url, parameters, author: str = "cloud_bot_gtbot"):
    from .utils import get_ng_state

    state = get_ng_state(url)
    if state is None:
        return "Nothing to do."
    cv_path = get_first_image_layer(state["layers"])
    bboxes = get_bboxes(state["layers"])
    if not bboxes:
        return "Nothing to do."

    try:
        voxel_size = state["navigation"]["pose"]["position"]["voxelSize"]
    except:
        raise ValueError(f"Could not get voxelSize from {url}")
    parameters["voxel_size"] = voxel_size

    responses = []
    for b in bboxes:
        dst_path = os.path.join(author, b["name"])
        msg = cloudvolume_to_dir(cv_path, dst_path, b["bbox"], parameters, author)
        responses.append(f"```{msg}```")
    return responses


def _draw_bounding_cube(cv_path, bbox, mip, pad):
    from cloudvolume import CloudVolume
    from cloudvolume.lib import Vec
    from cloudvolume.lib import Bbox
    from .utils import draw_bounding_cube

    cv = CloudVolume(cv_path, mip=mip, fill_missing=True)
    pad = Vec(*pad)

    mip0_bbox = Bbox.from_list(bbox)
    vol_start = mip0_bbox.minpt
    vol_stop = mip0_bbox.maxpt
    vol_bbox = cv.bbox_to_mip(  # pylint: disable=no-member
        Bbox(vol_start - pad, vol_stop + pad), 0, mip
    )
    draw_bbox = cv.bbox_to_mip(mip0_bbox, 0, mip)  # pylint: disable=no-member
    arr = cv[vol_bbox.to_slices()][:, :, :, 0]  # pylint: disable=unsubscriptable-object
    local_draw_bbox = draw_bbox - vol_bbox.minpt
    if any(x != 0 for x in pad):
        draw_bounding_cube(arr, local_draw_bbox, val=255)
    return arr, draw_bbox


def cloudvolume_to_dir(
    cv_path: str, dst_path: str, bbox, parameters: dict, author: str, extension="tif"
):
    """Save bbox from src_path to directory of tifs at dst_path."""
    from datetime import datetime
    from json import dumps
    from cloudfiles import CloudFiles
    from .data_io import write_to_cloud_bucket

    mip = parameters["mip"]
    pad = parameters["pad"]

    img_arr, draw_bbox = _draw_bounding_cube(cv_path, bbox, mip, pad)
    dst_path = os.path.join(os.environ["GT_BUCKET_PATH"], dst_path)
    write_to_cloud_bucket(os.path.join(dst_path, "raw"), img_arr, extension=extension)
    params = {
        "raw": {
            "pad": pad,
            "bbox": bbox,
            "mip": mip,
            "voxel_size": parameters["voxel_size"],
            "user": author,
            "timestamp": str(datetime.utcnow()),
            "cv_path": cv_path,
            "dst_path": dst_path,
        }
    }

    CloudFiles(dst_path).put(
        "params.json", dumps(params, indent=2), content_type="application/json"
    )

    msg = f"Cutout Volume `{dst_path}`\n"
    msg += f"Image layer: `{cv_path}`"
    msg += f"Bounding box: [{', '.join(str(x) for x in bbox)}]\n"
    msg += f"Size: [{', '.join(str(int(x)) for x in draw_bbox.size3())}]\n"
    msg += f"Mip level: {mip}\n"
    msg += f"Padding: [{', '.join(str(x) for x in pad)}]\n"
    return msg