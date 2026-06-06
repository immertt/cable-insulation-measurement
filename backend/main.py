import cv2
from pathlib import Path
import json


from image_processing import (
    load_image,
    preprocess_image,
    preprocess_color_cable,
    find_all_contours,
    select_outer_and_inner_contours,
    get_contour_center,
    get_min_enclosing_circle

)

from measurements import (
    calculate_eccentricity,
    calculate_insulation_thickness,
    calculate_radial_thicknesses,
    calculate_thickness_statistics
)


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE_PATH = BASE_DIR / "data" / "som_telli_1.jpg"
DEFAULT_OUTPUT_PATH = BASE_DIR / "outputs" / "result_measurement.png"


def save_image(path, image):
    cv2.imencode(".png", image)[1].tofile(str(path))


def process_image(image_path, output_path=DEFAULT_OUTPUT_PATH, pixel_to_mm=0.02):
    image = load_image(str(image_path))

    image_name = str(image_path).lower()

    if "cok_telli_1" in image_name:
        threshold = preprocess_color_cable(image)
    else:
        gray, blurred, threshold = preprocess_image(image)

    contours, hierarchy = find_all_contours(threshold)

    outer_contour, inner_contour = select_outer_and_inner_contours(
        contours,
        hierarchy
    )

    outer_center = get_contour_center(outer_contour)
    inner_center = get_contour_center(inner_contour)

    _, outer_diameter, _ = get_min_enclosing_circle(outer_contour)
    _, inner_diameter, _ = get_min_enclosing_circle(inner_contour)

    eccentricity_px = calculate_eccentricity(outer_center, inner_center)

    insulation_thickness_px = calculate_insulation_thickness(
        outer_diameter,
        inner_diameter
    )

    thickness_measurements_px, measurement_angles_deg = calculate_radial_thicknesses(
        outer_contour,
        inner_contour,
        outer_center,
        measurement_count=6
    )

    thickness_stats = calculate_thickness_statistics(
        thickness_measurements_px
    )

    output = image.copy()

    cv2.drawContours(output, [outer_contour], -1, (255, 0, 0), 2)
    cv2.drawContours(output, [inner_contour], -1, (0, 0, 255), 2)

    cv2.circle(output, outer_center, 5, (255, 0, 0), -1)
    cv2.circle(output, inner_center, 5, (0, 0, 255), -1)

    cv2.line(output, outer_center, inner_center, (0, 255, 255), 2)

    cv2.putText(output, f"Outer D: {outer_diameter:.1f}px", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    cv2.putText(output, f"Inner D: {inner_diameter:.1f}px", (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.putText(output, f"Thickness: {insulation_thickness_px:.1f}px", (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 150, 0), 2)

    cv2.putText(output, f"Eccentricity: {eccentricity_px:.1f}px", (20, 125),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 150, 150), 2)

    save_image(output_path, output)
    save_image(BASE_DIR / "outputs" / "threshold.png", threshold)

    results = {
        "image_path": str(image_path),
        "output_path": str(output_path),

        "pixel_to_mm": pixel_to_mm,

        "outer_center_px": outer_center,
        "inner_center_px": inner_center,

        "outer_diameter_px": round(float(outer_diameter), 2),
        "inner_diameter_px": round(float(inner_diameter), 2),

        "outer_diameter_mm": round(
            float(outer_diameter) * pixel_to_mm,
            2
        ),

        "inner_diameter_mm": round(
            float(inner_diameter) * pixel_to_mm,
            2
        ),

        "insulation_thickness_px": round(
            float(insulation_thickness_px),
            2
        ),

        "insulation_thickness_mm": round(
            float(insulation_thickness_px) * pixel_to_mm,
            2
        ),

        "eccentricity_px": round(
            float(eccentricity_px),
            2
        ),

        "eccentricity_mm": round(
            float(eccentricity_px) * pixel_to_mm,
            2
        ),

        "measurement_count": 6,

        "thickness_measurements_px":
            thickness_measurements_px,

        "thickness_measurements_mm": [
            round(value * pixel_to_mm, 2)
            for value in thickness_measurements_px
        ],

        "min_thickness_px":
            thickness_stats["min_thickness_px"],

        "max_thickness_px":
            thickness_stats["max_thickness_px"],

        "mean_thickness_px":
            thickness_stats["mean_thickness_px"],

        "min_thickness_mm":
            round(
                thickness_stats["min_thickness_px"] * pixel_to_mm,
                2
            ),

        "max_thickness_mm":
            round(
                thickness_stats["max_thickness_px"] * pixel_to_mm,
                2
            ),

        "mean_thickness_mm":
            round(
                thickness_stats["mean_thickness_px"] * pixel_to_mm,
                2
            ),

        "measurement_angles_deg":
            measurement_angles_deg
    }

    json_path = BASE_DIR / "outputs" / "results.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    return results


def main():
    results = process_image(DEFAULT_IMAGE_PATH)

    print("Cable measurement completed.")
    for key, value in results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()