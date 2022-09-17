# encoding: utf-8

__all__ = ["StockImage", "StockImageException", "TK_IMAGE_FORMATS"]

import logging
import os
import tkinter as tk
from pathlib import Path

logger = logging.getLogger(__name__)


class StockImageException(Exception):
    pass


BITMAP_TEMPLATE = "@{0}"
TK_BITMAP_FORMATS = [".xbm"]
TK_PHOTO_FORMATS = [".gif", ".pgm", ".ppm"]


if os.name == "nt":
    TK_BITMAP_FORMATS.append(".ico")
    BITMAP_TEMPLATE = "{0}"

if tk.TkVersion >= 8.6:
    TK_PHOTO_FORMATS.append(".png")


TK_IMAGE_FORMATS = TK_PHOTO_FORMATS + TK_BITMAP_FORMATS


_img_notsupported = """\
R0lGODlhZAAyAIQAAAAAAAsLCxMTExkZGSYmJicnJ11dXYGBgZubm5ycnJ2dnbGxsbOzs8TExMXF
xdXV1dbW1uTk5PLy8v39/f7+/v///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEK
AB8ALAAAAABkADIAAAX+4CeOZGmeaKqubOu+cCzPMmDfeK7vfO//QJ5rQCwaj8ikcslsOpUswGBC
qVqv2Kx2y+16v9nJAKAaFCiVtHrNbrvf8Lh83qYUBigplc7v+/9yFGJkJVJogIiJinAUYyaGi5GS
iI2EJJBuDQ0UChFqmmkNCAqHnAijFKKnnmoRpwgNoagVrqexFaBpEaS0qxWms26VjwOHbaeNDJ4Q
BwgVEAsICQ8SEg8Jp6QIBr5qEAG2z9HTEt+nCxAVCAfpEQzFEQ6nDhGcBga8wo6FxW/IAwISTCAA
rtEDQQMgQChmRR2CKmwWUqmS8FdCiRQenEEQgMCEBAKKIaNwKk1JRvv+LvVz8+/BA4//Qo5RWEyB
GZIBiKTzJmUAqYqNFPZMgObUQJcicw4AZ9IZSksjMB17mLCcw2QQHgigScGdSHYQJKyBIOABhHpA
L5Zt1vRZua8K2TqMM4yfMTb/dl5Ne3YaBAfawIr1tpKTg6wJIixMhW5umsUnIzt9U1fl3TUKSBXQ
m9lOOs+/7ihIY1Pn2DOYbz5DDeFMZm+uR1d4PVs25ZRRV9ZBcxeisd8QfzVkc3n4LzW8ewtPEzz4
bagipE6aTl0f9A/Sq2unXjm3cuTImxtfc2X58vLMxztHL9x3Q/bIcUfX3brU5tA+SRfRy/zOTdqd
+cdaEbYtBJSAaBj+6JMdRLi2H3HyYUcfOJ4EFYFfgHXFQFmD6eKXQo79wwBiipX1FykNoAPNJgOM
eE0E1gigDFbprKPQArcwF6FU5tAT1GLP9APkGheaxYpkWL1IllkZItkiiRZ99mSNTp2k43U81iTQ
RUJ2eRl+RIVIVUis9SSbkwKEVEpaZJJU5WQWYUkfQw/MBOSdupGX0UZvGhQcRoc4idSaUh5U1Jvk
7TgnGjGGdQ0CjQV5WS2QtiMPAj5WRNhd8cyDlqOJRWlRM9pwgykrVxJjzC6ldPKLArC0kk8rr+RY
S4WuyjqpL5zg6uur2aTyCqqp2rXdsdwp+iWyzP7R3Xx7NCutHwiGXSeCatNmS9cdKugBxre7fSvu
uFcMwsIT6KKGnH/otuuuES4EIW+elchr77050ECDdM/q6++/M/AbIcAEF5yCwNYarLDC2P5i7sIQ
K+ztunhEbHHBUlV78cb/YsIgxyDr663GIZcMgw3wmqxyvPmu7HIeCb8sc1Qxz2zzzTjnrPPOPPcs
QwgAOw==
"""

STOCK_DATA = {
    "img_not_supported": {
        "type": "data",
        "data": _img_notsupported,
        "format": "gif",
    }
}


class StockImage:
    """Maintain references to image name and file.
    When image is used, the class maintains it on memory for tkinter"""

    _stock = STOCK_DATA
    _cached = {}
    _formats = TK_IMAGE_FORMATS

    @classmethod
    def clear_cache(cls):
        """Call this before closing tk root"""
        # Prevent tkinter errors on python 2 ??
        for key in cls._cached:
            cls._cached[key] = None
        cls._cached = {}

    @classmethod
    def register(cls, image_id, filename):
        """Register a image file using image_id"""

        if image_id in cls._stock:
            logger.info("Warning, replacing resource %s", image_id)
        cls._stock[image_id] = {"type": "custom", "filename": filename}
        logger.info("%s registered as %s", filename, image_id)

    @classmethod
    def register_from_data(cls, image_id, format, data):
        """Register a image data using image_id"""

        if image_id in cls._stock:
            logger.info("Warning, replacing resource %s", image_id)
        cls._stock[image_id] = {"type": "data", "data": data, "format": format}
        logger.info("%s registered as %s", "data", image_id)

    @classmethod
    def register_created(cls, image_id, image):
        """Register an already created image using image_id"""

        if image_id in cls._stock:
            logger.info("Warning, replacing resource {0}", image_id)
        cls._stock[image_id] = {"type": "created", "image": image}
        logger.info("data registered as %s", image_id)

    @classmethod
    def is_registered(cls, image_id):
        return image_id in cls._stock

    @classmethod
    def register_from_dir(cls, dir_path, prefix="", ext=None):
        """List files from dir_path and register images with
            filename as key (without extension)

        :param str dir_path: path to search for images.
        :param str prefix: Additionaly a prefix for the key can be provided,
            so the resulting key will be prefix + filename
        :param iterable ext: list of file extensions to load. Defaults to
            tk supported image extensions. Example ('.jpg', '.png')
        """
        if ext is None:
            ext = TK_IMAGE_FORMATS

        for filename in Path(dir_path).iterdir():
            name = filename.stem
            file_ext = filename.suffix
            if file_ext in ext:
                fkey = f"{prefix}{name}"
                cls.register(fkey, filename)

    @classmethod
    def _load_image(cls, image_id):
        """Load image from file or return the cached instance."""

        v = cls._stock[image_id]
        img = None
        itype = v["type"]
        from_ = itype
        if itype in ("stock", "data"):
            img = tk.PhotoImage(format=v["format"], data=v["data"])
        elif itype == "created":
            img = v["image"]
        else:
            # custom
            fpath = v["filename"]
            from_ = fpath
            file_ext = fpath.suffix.lower()

            if file_ext in TK_PHOTO_FORMATS:
                img = tk.PhotoImage(file=fpath)
            elif file_ext in TK_BITMAP_FORMATS:
                img = tk.BitmapImage(file=fpath)
            else:
                try:
                    from PIL import Image, ImageTk

                    aux = Image.open(fpath)
                    img = ImageTk.PhotoImage(aux)
                except ModuleNotFoundError:
                    msg = (
                        "Error loading image %s, try installing Pillow module."
                    )
                    logger.error(msg, fpath)
                    img = cls.get("img_not_supported")

        cls._cached[image_id] = img
        logger.info("Loaded resource %s from %s.", image_id, from_)
        return img

    @classmethod
    def get(cls, image_id):
        """Get image previously registered with key image_id.
        If key not exist, raise StockImageException
        """

        if image_id in cls._cached:
            logger.info("Resource %s is in cache.", image_id)
            return cls._cached[image_id]
        if image_id in cls._stock:
            img = cls._load_image(image_id)
            return img
        else:
            raise StockImageException(f"StockImage: {image_id} not registered.")

    @classmethod
    def as_iconbitmap(cls, image_id):
        """Get image path for use in iconbitmap property"""
        img = None
        if image_id in cls._stock:
            data = cls._stock[image_id]
            if data["type"] not in ("stock", "data", "image"):
                fpath = data["filename"]
                file_ext = fpath.suffix.lower()

                if file_ext in TK_BITMAP_FORMATS:
                    img = BITMAP_TEMPLATE.format(fpath)
        return img
