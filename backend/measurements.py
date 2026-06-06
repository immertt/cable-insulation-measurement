import math
import statistics


def calculate_eccentricity(center1, center2):
    return math.dist(center1, center2)


def calculate_insulation_thickness(
    outer_diameter,
    inner_diameter
):
    return (outer_diameter - inner_diameter) / 2


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
        "mean_thickness_px": round(
            statistics.mean(thickness_values),
            2
        )
    }