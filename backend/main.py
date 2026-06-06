import cv2
import math
from pathlib import Path
import json
from datetime import datetime

from image_processing import (
    load_image,
    preprocess_image,
    preprocess_color_cable,
    find_all_contours,
    select_outer_and_inner_contours,
    get_contour_center,
    get_min_enclosing_circle,
)

from measurements import (
    calculate_eccentricity,
    calculate_insulation_thickness,
    calculate_radial_thicknesses,
    calculate_thickness_statistics,
)

from visualization import draw_results

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE_PATH  = BASE_DIR / "data" / "som_telli_1.jpg"
DEFAULT_OUTPUT_PATH = BASE_DIR / "outputs" / "result_measurement.png"


def save_image(path, image):
    cv2.imencode(".png", image)[1].tofile(str(path))


# ─────────────────────────────────────────────
# Kablo tipine göre ön işleme seç
# ─────────────────────────────────────────────
def get_threshold(image, cable_type: str, image_name: str = ""):
    if cable_type == "cok_telli":
        color_thresh = preprocess_color_cable(image)
        contours_c, _ = find_all_contours(color_thresh)
        if len(contours_c) >= 2:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            return gray, blurred, color_thresh

    gray, blurred, threshold = preprocess_image(image)
    return gray, blurred, threshold


# ─────────────────────────────────────────────
# Üç damarlı kablo — t1, t2, t3 ölçümleri
# ─────────────────────────────────────────────
def process_three_core(image, outer_contour, inner_contour,
                       outer_center, inner_center,
                       outer_diameter, inner_diameter,
                       pixel_to_mm):
    """
    Üç damarlı kablo için her damarın en ince noktasını (t1,t2,t3) bulur.
    Damarlar yaklaşık 120° aralıklarla konumlandığından 0°, 120°, 240° açılarından
    radyal ölçüm alınır.
    """
    center = outer_center
    lobe_angles = [0, 120, 240]  # her damarın yaklaşık yönü
    thicknesses_px = []
    angles_used    = []

    for base_angle in lobe_angles:
        # Her damar etrafında ±30° tarayarak en ince noktayı bul
        min_t  = float("inf")
        best_a = base_angle

        for offset in range(-30, 31, 5):
            angle_deg = base_angle + offset
            angle_rad = math.radians(angle_deg)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)

            inner_dist = None
            outer_dist = None

            for r in range(1, 2000):
                x = int(center[0] + dx * r)
                y = int(center[1] + dy * r)

                if inner_dist is None:
                    iv = cv2.pointPolygonTest(inner_contour, (float(x), float(y)), False)
                    if iv < 0:
                        inner_dist = r

                if outer_dist is None:
                    ov = cv2.pointPolygonTest(outer_contour, (float(x), float(y)), False)
                    if ov < 0:
                        outer_dist = r
                        break

            if inner_dist is not None and outer_dist is not None:
                t = outer_dist - inner_dist
                if t < min_t:
                    min_t  = t
                    best_a = angle_deg

        if min_t < float("inf"):
            thicknesses_px.append(round(float(min_t), 2))
            angles_used.append(round(float(best_a), 2))

    stats = calculate_thickness_statistics(thicknesses_px)

    eccentricity_px = calculate_eccentricity(outer_center, inner_center)
    insulation_px   = calculate_insulation_thickness(outer_diameter, inner_diameter)

    return {
        "cable_type": "uc_damarli",
        "pixel_to_mm": pixel_to_mm,
        "outer_center_px": outer_center,
        "inner_center_px": inner_center,
        "outer_diameter_px": round(float(outer_diameter), 2),
        "inner_diameter_px": round(float(inner_diameter), 2),
        "outer_diameter_mm": round(float(outer_diameter) * pixel_to_mm, 2),
        "inner_diameter_mm": round(float(inner_diameter) * pixel_to_mm, 2),
        "insulation_thickness_px": round(float(insulation_px), 2),
        "insulation_thickness_mm": round(float(insulation_px) * pixel_to_mm, 2),
        "eccentricity_px": round(float(eccentricity_px), 2),
        "eccentricity_mm": round(float(eccentricity_px) * pixel_to_mm, 2),
        "measurement_count": len(thicknesses_px),
        "thickness_measurements_px": thicknesses_px,
        "thickness_measurements_mm": [round(v * pixel_to_mm, 2) for v in thicknesses_px],
        "measurement_angles_deg": angles_used,
        **stats,
        "min_thickness_mm":  round(stats["min_thickness_px"]  * pixel_to_mm, 2) if stats["min_thickness_px"]  else None,
        "max_thickness_mm":  round(stats["max_thickness_px"]  * pixel_to_mm, 2) if stats["max_thickness_px"]  else None,
        "mean_thickness_mm": round(stats["mean_thickness_px"] * pixel_to_mm, 2) if stats["mean_thickness_px"] else None,
    }


# ─────────────────────────────────────────────
# Ana işlem fonksiyonu
# ─────────────────────────────────────────────
def process_image(
    image_path,
    output_path=DEFAULT_OUTPUT_PATH,
    pixel_to_mm=0.02,
    cable_type="som_telli",
    measurement_count=6,
    section_id="",
    section_date="",
):
    image      = load_image(str(image_path))
    image_name = str(image_path)

    # Ön işleme
    gray, blurred, threshold = get_threshold(image, cable_type, image_name)

    # Kontur tespiti
    contours, hierarchy = find_all_contours(threshold)
    outer_contour, inner_contour = select_outer_and_inner_contours(contours, hierarchy)

    # Merkez ve çap
    outer_center = get_contour_center(outer_contour)
    inner_center = get_contour_center(inner_contour)
    _, outer_diameter, _ = get_min_enclosing_circle(outer_contour)
    _, inner_diameter, _ = get_min_enclosing_circle(inner_contour)

    # ── Kablo tipine göre ölçüm ──
    if cable_type == "uc_damarli":
        metrics = process_three_core(
            image, outer_contour, inner_contour,
            outer_center, inner_center,
            outer_diameter, inner_diameter,
            pixel_to_mm,
        )
        thickness_measurements_px = metrics["thickness_measurements_px"]
        measurement_angles_deg    = metrics["measurement_angles_deg"]
        thickness_stats = {
            "min_thickness_px":  metrics["min_thickness_px"],
            "max_thickness_px":  metrics["max_thickness_px"],
            "mean_thickness_px": metrics["mean_thickness_px"],
        }
    else:
        eccentricity_px    = calculate_eccentricity(outer_center, inner_center)
        insulation_px      = calculate_insulation_thickness(outer_diameter, inner_diameter)
        thickness_measurements_px, measurement_angles_deg = calculate_radial_thicknesses(
            outer_contour, inner_contour, outer_center,
            measurement_count=measurement_count,
        )
        thickness_stats = calculate_thickness_statistics(thickness_measurements_px)
        metrics = None  # aşağıda manuel doldurulacak

    # ── Görselleştirme ──
    output_image = draw_results(
        image=image,
        outer_contour=outer_contour,
        inner_contour=inner_contour,
        outer_center=outer_center,
        inner_center=inner_center,
        outer_diameter=outer_diameter,
        inner_diameter=inner_diameter,
        thickness_measurements_px=thickness_measurements_px,
        measurement_angles_deg=measurement_angles_deg,
        cable_type=cable_type,
    )

    save_image(output_path, output_image)
    save_image(BASE_DIR / "outputs" / "threshold.png", threshold)

    # ── Sonuç dict ──
    if metrics:
        results = metrics
    else:
        results = {
            "cable_type": cable_type,
            "pixel_to_mm": pixel_to_mm,
            "outer_center_px": outer_center,
            "inner_center_px": inner_center,
            "outer_diameter_px":  round(float(outer_diameter), 2),
            "inner_diameter_px":  round(float(inner_diameter), 2),
            "outer_diameter_mm":  round(float(outer_diameter)  * pixel_to_mm, 2),
            "inner_diameter_mm":  round(float(inner_diameter)  * pixel_to_mm, 2),
            "insulation_thickness_px": round(float(insulation_px), 2),
            "insulation_thickness_mm": round(float(insulation_px) * pixel_to_mm, 2),
            "eccentricity_px": round(float(eccentricity_px), 2),
            "eccentricity_mm": round(float(eccentricity_px) * pixel_to_mm, 2),
            "measurement_count": measurement_count,
            "thickness_measurements_px": thickness_measurements_px,
            "thickness_measurements_mm": [round(v * pixel_to_mm, 2) for v in thickness_measurements_px],
            "measurement_angles_deg": measurement_angles_deg,
            **thickness_stats,
            "min_thickness_mm":  round(thickness_stats["min_thickness_px"]  * pixel_to_mm, 2),
            "max_thickness_mm":  round(thickness_stats["max_thickness_px"]  * pixel_to_mm, 2),
            "mean_thickness_mm": round(thickness_stats["mean_thickness_px"] * pixel_to_mm, 2),
        }

    # Kesit meta bilgilerini ekle
    results["image_path"]   = str(image_path)
    results["output_path"]  = str(output_path)
    results["section_id"]   = section_id
    results["section_date"] = section_date
    results["analyzed_at"]  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # JSON kaydet
    json_path = BASE_DIR / "outputs" / "results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    return results


# ─────────────────────────────────────────────
# CLI çalıştırma
# ─────────────────────────────────────────────
def main():
    results = process_image(
        image_path=DEFAULT_IMAGE_PATH,
        cable_type="som_telli",
        measurement_count=6,
    )
    print("Kablo ölçümü tamamlandı.")
    for key, value in results.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
