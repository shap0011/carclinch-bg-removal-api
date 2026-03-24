import os
import base64
from io import BytesIO

import requests
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

API_URL = os.getenv("BG_REMOVE_API_URL", "http://127.0.0.1:8000").rstrip("/")


def to_data_url(file_bytes: bytes, mime_type: str) -> str:
    return f"data:{mime_type};base64,{base64.b64encode(file_bytes).decode('utf-8')}"


def to_bool(value: str | None) -> bool:
    return str(value).lower() in {"1", "true", "on", "yes"}


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/replace")
def replace():
    car_file = request.files.get("image")
    bg_file = request.files.get("background")

    if not car_file or not car_file.filename:
        return render_template("index.html", error="Please choose a car image.")

    if not bg_file or not bg_file.filename:
        return render_template("index.html", error="Please choose a background image.")

    car_bytes = car_file.read()
    bg_bytes = bg_file.read()

    if not car_bytes:
        return render_template("index.html", error="The car image is empty.")

    if not bg_bytes:
        return render_template("index.html", error="The background image is empty.")

    car_preview = to_data_url(car_bytes, car_file.mimetype or "image/jpeg")
    background_preview = to_data_url(bg_bytes, bg_file.mimetype or "image/jpeg")

    car_size = request.form.get("car_size", "60")
    smart_placement = to_bool(request.form.get("smart_placement", "true"))

    endpoint = f"{API_URL}/replace-background"

    files = {
        "image": (car_file.filename, car_bytes, car_file.mimetype or "application/octet-stream"),
        "background": (bg_file.filename, bg_bytes, bg_file.mimetype or "application/octet-stream"),
    }

    data = {
        "car_size": car_size,
        "smart_placement": str(smart_placement).lower(),
    }

    try:
        response = requests.post(endpoint, files=files, data=data, timeout=180)
        response.raise_for_status()
        payload = response.json()

        output_filename = payload.get("output_filename")
        if not output_filename:
            return render_template(
                "index.html",
                error="The API finished, but no output image was returned.",
                car_preview=car_preview,
                background_preview=background_preview,
                car_size=car_size,
                smart_placement=smart_placement,
            )

        output_url = f"{API_URL}/output/{output_filename}"

        result = {
            "model": "isnet-general-use",
            "preview_url": output_url,
            "download_url": f"/download?file_url={output_url}&filename={output_filename}",
            "output_filename": output_filename,
        }

        return render_template(
            "index.html",
            car_preview=car_preview,
            background_preview=background_preview,
            result=result,
            car_size=car_size,
            smart_placement=smart_placement,
        )

    except requests.HTTPError:
        error_message = "Background replacement failed."
        try:
            error_json = response.json()
            error_detail = error_json.get("detail", error_json)
            error_message = f"API error: {error_detail}"
        except ValueError:
            error_message = f"API error: {response.text[:300]}"

        return render_template(
            "index.html",
            error=error_message,
            car_preview=car_preview,
            background_preview=background_preview,
            car_size=car_size,
            smart_placement=smart_placement,
        )

    except requests.RequestException as e:
        return render_template(
            "index.html",
            error=f"Connection error: {e}",
            car_preview=car_preview,
            background_preview=background_preview,
            car_size=car_size,
            smart_placement=smart_placement,
        )
        
@app.get("/download")
def download():
    file_url = request.args.get("file_url")
    filename = request.args.get("filename", "result.png")

    if not file_url:
        return "Missing file URL", 400

    try:
        response = requests.get(file_url, timeout=180)
        response.raise_for_status()

        return send_file(
            BytesIO(response.content),
            mimetype="image/png",
            as_attachment=True,
            download_name=filename,
        )
    except requests.RequestException as e:
        return f"Download failed: {e}", 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
    
