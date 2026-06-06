import math


def calculate_eccentricity(center1, center2):
    return math.dist(center1, center2)


def calculate_insulation_thickness(
    outer_diameter,
    inner_diameter
):
    return (outer_diameter - inner_diameter) / 2