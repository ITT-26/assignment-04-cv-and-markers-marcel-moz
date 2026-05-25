import cv2
import numpy as np
import pyglet
from PIL import Image
import sys, opencv_pyglet
from aruco_detector import ArucoDetector
import perspective_transformation.image_extractor as extractor

video_id = 0

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])


cap = cv2.VideoCapture(video_id)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


window = pyglet.window.Window(frame_width, frame_height)

aruco = ArucoDetector()

def create_circles(frame, corners):

    for corner in corners:
        position = (int(corner[0][:, 0].mean()), int(corner[0][:, 1].mean()))
        radius = 25
        color = (0, 0, 255)
        border_width = 3  # -1 means that the shape is filled
        frame = cv2.circle(frame, position, radius, color, border_width)
    return frame


@window.event
def on_draw():
    window.clear()
    ret, cv_frame = cap.read()
    
    corners, ids, rejectedImgPoints = aruco.get_markers(cv_frame)
    
    create_circles(cv_frame, corners=corners)
    sorted_markers = extractor.sort_markers(corners)
    transformed_frame = extractor.get_warped_image(cv_frame, sorted_markers, frame_width, frame_height)
    
    
    img = opencv_pyglet.cv2glet(transformed_frame, 'BGR')
    img.blit(0, 0, 0)

pyglet.app.run()
