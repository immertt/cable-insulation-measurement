import math
import statistics
import cv2


def calculate_eccentricity(center1, center2):
    return math.dist(center1, center2)


def calculate_insulation_thickness(outer_diameter, inner_diameter):
    return (outer_diameter - inner_diameter) / 2


def calculate_radial_thicknesses(
    outer_contour,
    inner_contour,
    center,
    measurement_count=6
):
    thicknesses = []
    angles = []

    for i in range(measurement_count):
        angle_deg = i * (360 / measurement_count)
        angle_rad = math.radians(angle_deg)

        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        inner_distance = None
        outer_distance = None

        for r in range(1, 2000):
            x = int(center[0] + dx * r)
            y = int(center[1] + dy * r)

            inner_value = cv2.pointPolygonTest(
                inner_contour,
                (x, y),
                False
            )

            outer_value = cv2.pointPolygonTest(
                outer_contour,
                (x, y),
                False
            )

            if inner_distance is None and inner_value < 0:
                inner_distance = r

            if outer_distance is None and outer_value < 0:
                outer_distance = r
                break

        if inner_distance is not None and outer_distance is not None:
            thickness = outer_distance - inner_distance
            thicknesses.append(round(float(thickness), 2))
            angles.append(round(float(angle_deg), 2))

    return thicknesses, angles


def calculate_thickness_statistics(thickness_values):
    if not thickness_values:
        return {
            "min_thickness_px": None,
            "max_thickness_px": None,
            "mean_thickness_px": None
        }

    return {
        "min_thickness_px": round(min(thickness_values), 2),
        "max_thickness_px": round(max(thickness_values), 2),
        "mean_thickness_px": round(statistics.mean(thickness_values), 2)
    }