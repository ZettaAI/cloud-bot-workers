def convert_pt_to_bbox(url: str, parameters: dict) -> str:
    from os import environ
    from secrets import token_hex
    from json import dumps
    from requests import post
    from .utils import get_ng_state
    from .utils import post_ngl_state_server

    state = get_ng_state(url)
    layers = state["layers"]
    for l in layers:
        if l in layers:
            if "annotations" in l:
                new_bboxes = []
                for a in l["annotations"]:
                    if a["type"] == "point":
                        minpt = [
                            a["point"][i] - parameters["dim"][i] / 2 for i in range(3)
                        ]
                        maxpt = [minpt[i] + parameters["dim"][i] for i in range(3)]
                        bbox_annotation = {
                            "pointA": minpt,
                            "pointB": maxpt,
                            "type": "axis_aligned_bounding_box",
                            "id": token_hex(40),
                        }
                        new_bboxes.append(bbox_annotation)
                l["annotations"] += new_bboxes

    r = post_ngl_state_server(state)
    return f"{environ['NGL_APP_HOST']}/?json_url={r.text.strip()[1:-1]}"
