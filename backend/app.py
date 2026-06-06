from pathlib import Path
from flask import Flask, render_template, request, send_from_directory

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

    if not file:
        return "No image uploaded", 400

    image_path = UPLOAD_DIR / file.filename
    output_path = OUTPUT_DIR / "web_result.png"

    file.save(image_path)

    pixel_to_mm = float(request.form.get("pixel_to_mm", 0.02))
    results = process_image(image_path, output_path, pixel_to_mm)

    return render_template(
        "index.html",
        results=results,
        output_image="web_result.png"
    )


@app.route("/outputs/<filename>")
def outputs(filename):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)