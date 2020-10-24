from os import path
from os import environ
from json import dumps
from collections import OrderedDict


def get_username(user_id: str) -> str:
    from requests import get
    from CloudBotWorkersCommon import config

    try:
        headers = {"Authorization": f"Bearer {config.SLACK_API_BOT_ACCESS_TOKEN}"}
        response = get(
            config.SLACK_API_USER_INFO,
            headers=headers,
            params={"user": user_id},
        )
        response = response.json()
        return response["user"]["real_name"].lower().replace(" ", "_")
    except:
        return "cloud_bot_gtbot"


def post_ngl_state_server(state: dict):
    from requests import post

    token = environ.get("AUTH_SERVER_TOKEN", "")
    return post(
        f"{environ['NGL_STATE_SERVER']}/post?middle_auth_token={token}",
        data=dumps(state),
    )


def get_ng_state(url: str):
    from urllib import parse
    from json import loads
    from requests import get

    components = parse.urlparse(url)
    u = None
    try:
        if len(components.fragment) == 0:
            u = components.query.replace("json_url=", "")
            u = f"{u}?middle_auth_token={environ.get('AUTH_SERVER_TOKEN', '')}"
            r = get(u)
            state = r.content
        else:
            state = parse.unquote(components.fragment)[1:]
        return loads(state, object_pairs_hook=OrderedDict)
    except Exception as e:
        raise ValueError(f"Could not read json state at {u}: {repr(e)}")


def draw_bounding_cube(img, bbox, val=255, thickness=1):
    minpt = bbox.minpt
    maxpt = bbox.maxpt
    z_slice = slice(minpt.z, maxpt.z)
    for t in range(0, thickness):
        img[minpt.x + t, :, z_slice] = val
        img[maxpt.x + t, :, z_slice] = val
        img[:, minpt.y + t, z_slice] = val
        img[:, maxpt.y + t, z_slice] = val


def create_nglink(image_layer, seg_layers, center, voxel_size) -> str:
    from urllib import parse
    from collections import OrderedDict

    layers = OrderedDict()
    layers["img"] = {"source": "precomputed://" + image_layer, "type": "image"}
    for s in seg_layers:
        layers[s] = {
            "source": "precomputed://" + seg_layers[s],
            "type": "image" if ("img" in s or "image" in s) else "segmentation",
        }
    navigation = {
        "pose": {"position": {"voxelSize": voxel_size, "voxelCoordinates": center}},
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
        return f"neuroglancer link: {environ['NGL_APP_HOST']}/?json_url={link}"
    return f"neuroglancer link: {url}"
