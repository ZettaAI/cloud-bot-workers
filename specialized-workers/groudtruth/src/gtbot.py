from CloudBotWorkersCommon.slack import Response as SlackResponse
from .utils import get_username


def preview_helper(p: str, slack_response: SlackResponse) -> None:
    from .data_io import load_metadata
    from .uploader import upload

    slack_response.send("Parsing metadata.")
    meta = load_metadata(p)
    if meta is None:
        p += "/export"
        meta = load_metadata(p)

    if not meta:
        raise ValueError("Could not load meta, cannot proceed.")

    upload(p, meta, get_username(slack_response.event["user"]), slack_response)
    slack_response.send("Job completed.")


def cutout_helper(url: str, slack_response: SlackResponse) -> None:
    from .cutout import create_cutouts

    cutout_parameters = {"mip": 1, "pad": [256, 256, 4], "prefix": "."}
    create_cutouts(
        url,
        cutout_parameters,
        get_username(slack_response.event["user"]),
        slack_response,
    )
    slack_response.send("Job completed.")


def bbox_helper(url: str, slack_response: SlackResponse) -> None:
    from .bbox import convert_pt_to_bbox

    bbox_parameters = {"dim": [40920, 40920, 2048]}
    result = convert_pt_to_bbox(url, bbox_parameters)
    slack_response.send(result, broadcast=True)
    slack_response.send("Job completed.")
