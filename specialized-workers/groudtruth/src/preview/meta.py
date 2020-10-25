from typing import Tuple

from cloudvolume.lib import Vec
from cloudvolume.lib import Bbox


class Meta:
    def __init__(self, path: str, author: str = "cloudbot_gt_bot"):
        self.path = path
        self.voxel_size: Tuple = None
        self.author: str = author

        self.em_layer: str = None
        self.src_bbox: Bbox = None
        self.dst_bbox: Bbox = None
        self.center: Vec = None
        self.src_mip: int = 0
        self.dst_mip: int = 0

        self._fetch()

    def _fetch(self) -> None:
        from json import loads
        from cloudfiles import CloudFiles

        raw_meta = {}
        cf = CloudFiles(self.path)
        fnames = ["params.json", "metadata.json"]
        cf.get(fnames, raw=True)
        for f in fnames:
            try:
                raw_meta = loads(cf[f])
                break
            except:
                pass
        if not raw_meta:
            raise ValueError("Could not load meta, cannot proceed.")
        self._parse(raw_meta)

    def _parse(self, raw_meta: dict) -> None:
        try:
            parameters = raw_meta["raw"]
        except KeyError:
            parameters = raw_meta["processing"]
        except KeyError as e:
            raise ValueError(f"Could not understand meta: {repr(e)}")

        try:
            self.em_layer = parameters["cv_path"]
        except KeyError:
            self.em_layer = parameters["src_path"]
        except KeyError as e:
            raise ValueError(f"Could not find image path: {repr(e)}")

        try:
            self.voxel_size = parameters["voxel_size"]
        except KeyError:
            pass

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
            except KeyError as e:
                raise ValueError(f"Bounding box parameters missing: {repr(e)}")

        try:
            pad = Vec(*parameters["pad"])
        except KeyError as e:
            pad = Vec([256, 256, 10])

        self.src_mip = parameters["src_mip"]
        self.dst_mip = parameters["dst_mip"]
        self.dst_bbox = Bbox(vol_start, vol_stop)
        self.src_bbox = Bbox(self.dst_bbox.minpt - pad, self.dst_bbox.maxpt + pad)
        self.center = (vol_start + vol_stop) // 2

    def __str__(self) -> str:
        result = f"Path: {self.path}\n"
        result += f"Voxel Size: {self.voxel_size}\n"
        result += f"Author: {self.author}\n"
        result += f"EM layer: {self.em_layer}\n"
        result += f"src_bbox: {self.src_bbox}\n"
        result += f"dst_bbox: {self.dst_bbox}\n"
        result += f"center: {self.center}\n"
        result += f"src_mip: {self.src_mip}\n"
        result += f"dst_mip: {self.dst_mip}\n"
        return result
