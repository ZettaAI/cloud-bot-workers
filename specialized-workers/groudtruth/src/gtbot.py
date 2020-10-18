from .utils import get_username


def preview_helper(p: str, user_id: str):
    from .data_io import load_metadata
    from .uploader import upload

    meta = load_metadata(p)
    if meta is None:
        p += "/export"
        meta = load_metadata(p)

    if not meta:
        raise ValueError("Could not load meta, cannot proceed.")

    try:
        author = get_username(user_id)
    except:
        author = "cloud_bot_gtbot"

    upload(p, meta, author)


def cutout_helper(url: str, user_id: str):
    from .cutout import create_cutouts

    try:
        author = get_username(user_id)
    except:
        author = "cloud_bot_gtbot"

    cutout_parameters = {"mip": 1, "pad": [256, 256, 4], "prefix": "."}
    return create_cutouts(url, cutout_parameters, author)


def bbox_helper(url: str, user_id: str):
    from .bbox import convert_pt_to_bbox

    bbox_parameters = {"dim": [40920, 40920, 2048]}
    return convert_pt_to_bbox(url, bbox_parameters)
