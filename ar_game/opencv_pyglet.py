import pyglet
from PIL import Image


# converts OpenCV image to PIL image and then to pyglet texture
# https://gist.github.com/nkymut/1cb40ea6ae4de0cf9ded7332f1ca0d55
def cv2glet(img, fmt):
    """Assumes image is in BGR color space. Returns a pyimg object"""
    if fmt == "GRAY":
        rows, cols = img.shape
        channels = 1
    else:
        rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()

    top_to_bottom_flag = -1
    bytes_per_row = channels * cols
    pyimg = pyglet.image.ImageData(
        width=cols,
        height=rows,
        fmt=fmt,
        data=raw_img,
        pitch=top_to_bottom_flag * bytes_per_row,
    )
    return pyimg


def convert_pyglet_to_cv_coords(window_height, pyglet_x, pyglet_y):
    cv_x = pyglet_x
    cv_y = window_height - pyglet_y
    return cv_x, cv_y