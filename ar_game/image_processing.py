import cv2
import cv2.aruco as aruco
import numpy as np


class ArucoDetector:
    def __init__(self):
        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        aruco_params = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(aruco_dict, aruco_params)

    # Define the ArUco dictionary, parameters, and detector

    def get_markers(self, frame):
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect ArUco markers in the frame
        corners, ids, rejectedImgPoints = self.detector.detectMarkers(gray)
        return corners, ids, rejectedImgPoints


def get_points_for_outer_rect(points):
    sum = np.sum(points, axis=1)
    diff = np.diff(points, axis=1)

    top_left = points[np.argmin(sum)]
    top_right = points[np.argmin(diff)]
    bottom_right = points[np.argmax(sum)]
    bottom_left = points[np.argmax(diff)]

    return np.float32(np.array([top_left, top_right, bottom_right, bottom_left]))



def process_frame(transformed_frame, show_result=False):
    

    frame_grey = cv2.cvtColor(transformed_frame, cv2.COLOR_BGR2GRAY)

    kernel_size = 8
    kernel = np.ones((kernel_size, kernel_size), np.float64)
    kernel /= kernel_size**2
    frame_blur = cv2.filter2D(frame_grey, -1, kernel)

    block_size = 7

    thresh_adaptive = cv2.adaptiveThreshold(
        frame_blur,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        block_size,
        2,
    )
    if show_result:
        WINDOW_NAME = "Processed"
        cv2.namedWindow(WINDOW_NAME)
        cv2.imshow(WINDOW_NAME, thresh_adaptive)
    return thresh_adaptive

