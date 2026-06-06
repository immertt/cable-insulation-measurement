import cv2
import numpy as np


def load_image(image_path: str):
    image_array = np.fromfile(image_path, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise FileNotFoundError(f"Image could not be loaded: {image_path}")

    return image


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    _, threshold = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    return gray, blurred, threshold


def find_all_contours(threshold):
    contours, hierarchy = cv2.findContours(
        threshold,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    return contours


def get_largest_contour(contours):
    if not contours:
        raise ValueError("No contour found.")

    return contours[0]


def get_contour_center(contour):
    moments = cv2.moments(contour)

    if moments["m00"] == 0:
        raise ValueError("Contour center could not be calculated.")

    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])

    return cx, cy


def get_min_enclosing_circle(contour):
    (x, y), radius = cv2.minEnclosingCircle(contour)

    center = (int(x), int(y))
    diameter = 2 * radius

    return center, diameter, radius