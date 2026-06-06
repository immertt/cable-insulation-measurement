from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, jsonify

from main import process_image

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("image")

    if not file or file.filename == "":
        return render_template("index.html", error="Lütfen bir görüntü yükleyin.")

    # ── Form alanlarını oku ──
    cable_type       = request.form.get("cable_type", "som_telli")
    section_id       = request.form.get("section_id", "")
    section_date     = request.form.get("section_date", "")
    pixel_to_mm      = float(request.form.get("pixel_to_mm", 0.02))
    measurement_count = int(request.form.get("measurement_count", 6))

    # ── Görüntüyü kaydet ──
    image_path  = UPLOAD_DIR / file.filename
    output_path = OUTPUT_DIR / "web_result.png"
    file.save(image_path)

    # ── İşle ──
    try:
        results = process_image(
            image_path=image_path,
            output_path=output_path,
            pixel_to_mm=pixel_to_mm,
            cable_type=cable_type,
            measurement_count=measurement_count,
            section_id=section_id,
            section_date=section_date,
        )
    except Exception as e:
        return render_template("index.html", error=f"İşlem hatası: {str(e)}")

    return render_template(
        "index.html",
        results=results,
        output_image="web_result.png",
    )


@app.route("/outputs/<filename>")
def outputs(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/report")
def report():
    """JSON raporu döndürür."""
    json_path = OUTPUT_DIR / "results.json"
    if not json_path.exists():
        return jsonify({"error": "Henüz sonuç yok."}), 404
    return send_from_directory(OUTPUT_DIR, "results.json",
                               mimetype="application/json",
                               as_attachment=True,
                               download_name="kablo_olcum_raporu.json")


if __name__ == "__main__":
    app.run(debug=True)
