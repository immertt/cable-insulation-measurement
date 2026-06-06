import cv2
from pathlib import Path

from image_processing import (
    load_image,
    preprocess_image,
    find_all_contours,
    get_contour_center,
    get_min_enclosing_circle
)
from measurements import (
    calculate_eccentricity,
    calculate_insulation_thickness
)

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_PATH = BASE_DIR / "data" / "som_telli_1.jpg"
OUTPUT_PATH = BASE_DIR / "outputs" / "result_measurement.png"


def main():
    image = load_image(str(IMAGE_PATH))

    gray, blurred, threshold = preprocess_image(image)

    contours = find_all_contours(threshold)

    if len(contours) < 2:
        raise ValueError("Outer and inner contours could not be detected.")

    outer_contour = contours[0]
    inner_contour = contours[1]

    outer_center = get_contour_center(outer_contour)
    inner_center = get_contour_center(inner_contour)

    _, outer_diameter, outer_radius = get_min_enclosing_circle(outer_contour)
    _, inner_diameter, inner_radius = get_min_enclosing_circle(inner_contour)

    eccentricity_px = calculate_eccentricity(outer_center, inner_center)

    insulation_thickness_px = calculate_insulation_thickness(
        outer_diameter,
        inner_diameter
    )

    print("Cable measurement completed.")
    print("Outer center:", outer_center)
    print("Inner center:", inner_center)
    print("Outer diameter(px):", round(outer_diameter, 2))
    print("Inner diameter(px):", round(inner_diameter, 2))
    print("Insulation thickness(px):", round(insulation_thickness_px, 2))
    print("Eccentricity(px):", round(eccentricity_px, 2))

    output = image.copy()

    cv2.drawContours(output, [outer_contour], -1, (255, 0, 0), 2)
    cv2.drawContours(output, [inner_contour], -1, (0, 0, 255), 2)

    cv2.circle(output, outer_center, 5, (255, 0, 0), -1)
    cv2.circle(output, inner_center, 5, (0, 0, 255), -1)

    cv2.line(output, outer_center, inner_center, (0, 255, 255), 2)

    cv2.putText(
        output,
        f"Outer D: {outer_diameter:.1f}px",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 0, 0),
        2
    )

    cv2.putText(
        output,
        f"Inner D: {inner_diameter:.1f}px",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2
    )

    cv2.putText(
        output,
        f"Thickness: {insulation_thickness_px:.1f}px",
        (20, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 150, 0),
        2
    )

    cv2.putText(
        output,
        f"Eccentricity: {eccentricity_px:.1f}px",
        (20, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 150, 150),
        2
    )

    cv2.imencode(".png", output)[1].tofile(str(OUTPUT_PATH))
    cv2.imencode(".png", threshold)[1].tofile(str(BASE_DIR / "outputs" / "threshold.png"))

    print(f"Result saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()