from typing import Iterable
from . import PreviewMeta


def create_nglink(seg_layers: Iterable, meta: PreviewMeta) -> str:
    from os import environ
    from json import dumps
    from urllib import parse
    from collections import OrderedDict

    from ..utils import post_ngl_state_server

    layers = OrderedDict()
    layers["img"] = {"source": "precomputed://" + meta.em_layer, "type": "image"}
    for s in seg_layers:
        layers[s] = {
            "source": "precomputed://" + seg_layers[s],
            "type": "image" if ("img" in s or "image" in s) else "segmentation",
        }

    navigation = {
        "pose": {
            "position": {
                "voxelSize": meta.voxel_size,
                "voxelCoordinates": meta.center.tolist(),
            }
        },
        "zoomFactor": 4,
    }
    state = OrderedDict(
        [
            ("layers", layers),
            ("navigation", navigation),
            ("showSlices", False),
            ("layout", "xy-3d"),
        ]
    )

    url = f"{environ['NGL_APP_HOST']}/#!{parse.quote(dumps(state))}"
    try:
        r = post_ngl_state_server(state)
    except:
        return f"neuroglancer link: {url}"
    if r.ok:
        link = r.text.strip()
        link = link[1:-1]
        return f"Neuroglancer link: {environ['NGL_APP_HOST']}/?json_url={link}"
    return f"Neuroglancer link: {url}"
