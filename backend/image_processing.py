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

    if hierarchy is not None:
        hierarchy = hierarchy[0]

    return contours, hierarchy

def select_outer_and_inner_contours(contours, hierarchy):
    if len(contours) < 2:
        raise ValueError("Outer and inner contours could not be detected.")

    contour_areas = [cv2.contourArea(c) for c in contours]

    outer_index = max(range(len(contours)), key=lambda i: contour_areas[i])
    outer_contour = contours[outer_index]

    child_indices = []

    if hierarchy is not None:
        for i, h in enumerate(hierarchy):
            parent_index = h[3]

            if parent_index == outer_index:
                child_indices.append(i)

    if child_indices:
        inner_index = max(child_indices, key=lambda i: contour_areas[i])
    else:
        candidates = [
            i for i in range(len(contours))
            if i != outer_index and contour_areas[i] > 100
        ]

        if not candidates:
            raise ValueError("Inner contour could not be detected.")

        inner_index = max(candidates, key=lambda i: contour_areas[i])

    inner_contour = contours[inner_index]

    return outer_contour, inner_contour


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

def preprocess_color_cable(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Yellow insulation mask
    lower_yellow = np.array([15, 40, 40])
    upper_yellow = np.array([45, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Green edge mask
    lower_green = np.array([35, 30, 30])
    upper_green = np.array([95, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    mask = cv2.bitwise_or(yellow_mask, green_mask)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    return mask