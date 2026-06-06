import cv2
import math
import numpy as np


# Renk paleti
COLOR_OUTER   = (255, 80,  0)    # turuncu — dış sınır
COLOR_INNER   = (0,  80, 255)    # mavi    — iç sınır
COLOR_CENTER  = (255, 255, 0)    # sarı    — merkez noktaları
COLOR_LINE    = (0,  220, 200)   # cyan    — eksen kaçıklığı çizgisi
COLOR_MEASURE = (180, 255, 80)   # açık yeşil — ölçüm çizgileri
COLOR_MIN     = (0,  80, 255)    # kırmızı — min kalınlık
COLOR_MAX     = (0, 220,  80)    # yeşil   — max kalınlık
COLOR_TEXT    = (240, 240, 240)  # beyaz metin
COLOR_SHADOW  = (0,   0,   0)    # metin gölgesi


def put_text_shadowed(img, text, pos, scale=0.55, color=COLOR_TEXT, thickness=1):
    """Gölgeli metin yazar — okunabilirliği artırır."""
    x, y = pos
    cv2.putText(img, text, (x + 1, y + 1),
                cv2.FONT_HERSHEY_SIMPLEX, scale, COLOR_SHADOW, thickness + 1, cv2.LINE_AA)
    cv2.putText(img, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def draw_info_panel(img, results_dict, cable_type):
    """
    Sol üst köşeye yarı saydam bilgi paneli çizer.
    """
    panel_x, panel_y = 10, 10
    panel_w, panel_h = 310, 230
    overlay = img.copy()
    cv2.rectangle(overlay, (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  (20, 20, 30), -1)
    cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)
    cv2.rectangle(img, (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  COLOR_OUTER, 1)

    cable_labels = {
        "som_telli":  "Som Telli",
        "cok_telli":  "Cok Telli",
        "uc_damarli": "Uc Damarli",
    }

    lines = [
        ("Kablo Tipi",     cable_labels.get(cable_type, cable_type)),
        ("Dis Cap",        f"{results_dict.get('outer_diameter_px', 0):.1f} px  "
                           f"/ {results_dict.get('outer_diameter_mm', 0):.2f} mm"),
        ("Ic Cap",         f"{results_dict.get('inner_diameter_px', 0):.1f} px  "
                           f"/ {results_dict.get('inner_diameter_mm', 0):.2f} mm"),
        ("Izolasyon Ort.", f"{results_dict.get('insulation_thickness_px', 0):.1f} px  "
                           f"/ {results_dict.get('insulation_thickness_mm', 0):.2f} mm"),
        ("Min Kalinlik",   f"{results_dict.get('min_thickness_px', 0):.1f} px  "
                           f"/ {results_dict.get('min_thickness_mm', 0):.2f} mm"),
        ("Max Kalinlik",   f"{results_dict.get('max_thickness_px', 0):.1f} px  "
                           f"/ {results_dict.get('max_thickness_mm', 0):.2f} mm"),
        ("Ort Kalinlik",   f"{results_dict.get('mean_thickness_px', 0):.1f} px  "
                           f"/ {results_dict.get('mean_thickness_mm', 0):.2f} mm"),
        ("Eksen Kacikligi",f"{results_dict.get('eccentricity_px', 0):.1f} px  "
                           f"/ {results_dict.get('eccentricity_mm', 0):.2f} mm"),
    ]

    for idx, (label, value) in enumerate(lines):
        y = panel_y + 22 + idx * 26
        put_text_shadowed(img, f"{label}:", (panel_x + 8, y), 0.45, (160, 200, 255))
        put_text_shadowed(img, value, (panel_x + 140, y), 0.45, COLOR_TEXT)

    return img


def draw_measurement_lines(img, outer_contour, inner_contour,
                            center, angles_deg,
                            thicknesses_px, min_t, max_t):
    """
    Her ölçüm açısı için iç sınırdan dış sınıra bir çizgi çizer.
    Min → kırmızı, Max → yeşil, diğerleri → açık yeşil.
    """
    for i, angle_deg in enumerate(angles_deg):
        angle_rad = math.radians(angle_deg)
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        inner_pt = None
        outer_pt = None

        for r in range(1, 2000):
            x = int(center[0] + dx * r)
            y = int(center[1] + dy * r)
            pt = (float(x), float(y))

            if inner_pt is None:
                if cv2.pointPolygonTest(inner_contour, pt, False) < 0:
                    inner_pt = (x, y)

            if outer_pt is None:
                if cv2.pointPolygonTest(outer_contour, pt, False) < 0:
                    outer_pt = (x, y)
                    break

        if inner_pt and outer_pt:
            t = thicknesses_px[i] if i < len(thicknesses_px) else 0

            if t == min_t:
                color = COLOR_MIN
                thickness_line = 2
            elif t == max_t:
                color = COLOR_MAX
                thickness_line = 2
            else:
                color = COLOR_MEASURE
                thickness_line = 1

            cv2.line(img, inner_pt, outer_pt, color, thickness_line, cv2.LINE_AA)
            cv2.circle(img, inner_pt, 3, color, -1)
            cv2.circle(img, outer_pt, 3, color, -1)

            # Ölçüm değerini çizginin ortasına yaz
            mid_x = (inner_pt[0] + outer_pt[0]) // 2
            mid_y = (inner_pt[1] + outer_pt[1]) // 2
            put_text_shadowed(img, f"{t:.0f}", (mid_x + 3, mid_y - 3), 0.38, color)

    return img


def draw_results(
    image,
    outer_contour,
    inner_contour,
    outer_center,
    inner_center,
    outer_diameter,
    inner_diameter,
    thickness_measurements_px,
    measurement_angles_deg,
    cable_type="som_telli",
    pixel_to_mm=0.02,
    section_id="",
):
    """
    Ölçüm sonuçlarını kablo görüntüsü üzerine işler ve açıklamalı görsel döner.

    Çizilen öğeler:
    - Dış kontur (turuncu)
    - İç kontur (mavi)
    - Dış merkez noktası (sarı)
    - İç merkez noktası (sarı)
    - Eksen kaçıklığı çizgisi (cyan)
    - Ölçüm çizgileri (yeşil / min=kırmızı / max=açık yeşil)
    - Bilgi paneli (sol üst)
    """
    output = image.copy()

    # ── Kontürler ──
    cv2.drawContours(output, [outer_contour], -1, COLOR_OUTER, 2, cv2.LINE_AA)
    cv2.drawContours(output, [inner_contour], -1, COLOR_INNER, 2, cv2.LINE_AA)

    # ── Eksen kaçıklığı çizgisi ──
    cv2.line(output, outer_center, inner_center, COLOR_LINE, 2, cv2.LINE_AA)

    # ── Merkez noktaları ──
    cv2.circle(output, outer_center, 6, COLOR_OUTER, -1)
    cv2.circle(output, outer_center, 8, COLOR_CENTER, 1)
    cv2.circle(output, inner_center, 6, COLOR_INNER,  -1)
    cv2.circle(output, inner_center, 8, COLOR_CENTER, 1)

    # ── Ölçüm çizgileri ──
    if thickness_measurements_px:
        min_t = min(thickness_measurements_px)
        max_t = max(thickness_measurements_px)
        output = draw_measurement_lines(
            output, outer_contour, inner_contour,
            outer_center, measurement_angles_deg,
            thickness_measurements_px, min_t, max_t,
        )

    # ── Bilgi paneli için geçici dict ──
    min_t_px  = min(thickness_measurements_px)  if thickness_measurements_px else 0
    max_t_px  = max(thickness_measurements_px)  if thickness_measurements_px else 0
    mean_t_px = (sum(thickness_measurements_px) / len(thickness_measurements_px)
                 if thickness_measurements_px else 0)

    info = {
        "outer_diameter_px":       round(float(outer_diameter),  2),
        "outer_diameter_mm":       round(float(outer_diameter)  * pixel_to_mm, 2),
        "inner_diameter_px":       round(float(inner_diameter),  2),
        "inner_diameter_mm":       round(float(inner_diameter)  * pixel_to_mm, 2),
        "insulation_thickness_px": round((outer_diameter - inner_diameter) / 2, 2),
        "insulation_thickness_mm": round((outer_diameter - inner_diameter) / 2 * pixel_to_mm, 2),
        "min_thickness_px":        round(min_t_px,  2),
        "min_thickness_mm":        round(min_t_px  * pixel_to_mm, 2),
        "max_thickness_px":        round(max_t_px,  2),
        "max_thickness_mm":        round(max_t_px  * pixel_to_mm, 2),
        "mean_thickness_px":       round(mean_t_px, 2),
        "mean_thickness_mm":       round(mean_t_px * pixel_to_mm, 2),
        "eccentricity_px":         round(math.dist(outer_center, inner_center), 2),
        "eccentricity_mm":         round(math.dist(outer_center, inner_center) * pixel_to_mm, 2),
    }

    output = draw_info_panel(output, info, cable_type)

    # ── Sağ alt: kesit ID ve tarih ──
    if section_id:
        h, w = output.shape[:2]
        put_text_shadowed(output, f"ID: {section_id}", (w - 200, h - 15), 0.45, (180, 180, 180))

    return output
