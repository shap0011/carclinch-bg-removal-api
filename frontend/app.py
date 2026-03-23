import os
import base64

import requests
from flask import Flask, render_template, request

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

    endpoint = f"{API_URL}/replace-background-all-models"

    files = {
        "image": (car_file.filename, car_bytes, car_file.mimetype or "application/octet-stream"),
        "background": (bg_file.filename, bg_bytes, bg_file.mimetype or "application/octet-stream"),
    }

    data = {
        "car_size": car_size,
        "smart_placement": str(smart_placement).lower(),
    }

    try:
        response = requests.post(endpoint, files=files, data=data, timeout=300)
        response.raise_for_status()
        payload = response.json()

        results = []
        for item in payload.get("results", []):
            if item.get("status") != "success":
                continue

            output_url = item.get("output_url")
            if not output_url:
                continue

            full_output_url = f"{API_URL}{output_url}"

            results.append(
                {
                    "model": item.get("model", "Unknown model"),
                    "preview_url": full_output_url,
                    "download_url": full_output_url,
                    "output_filename": item.get("output_filename", "result.png"),
                }
            )

        if not results:
            return render_template(
                "index.html",
                error="The API finished, but no successful model results were returned.",
                car_preview=car_preview,
                background_preview=background_preview,
                car_size=car_size,
                smart_placement=smart_placement,
            )

        return render_template(
            "index.html",
            car_preview=car_preview,
            background_preview=background_preview,
            results=results,
            total_models=payload.get("total_models"),
            successful_models=payload.get("successful_models"),
            failed_models=payload.get("failed_models"),
            duration_seconds=payload.get("duration_seconds"),
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)