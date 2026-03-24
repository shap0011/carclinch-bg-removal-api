# CarClinch – Background Replacement Application

## Demo

![Demo](/screenshots/demo.gif)

---

CarClinch is a web application that allows users to replace the background of a car image with a custom background image.

🔗 Live Demo: https://carclinch-bg-removal-api-1.onrender.com/

---

## Overview

The application:

- Uploads a car image
- Removes its background using AI
- Places the car onto a new background
- Allows preview and download of the final image

This project is an evolution of a background removal tool, extended with background replacement functionality.

---

## Features

- Upload car image
- Upload background image
- Smart background replacement
- Image preview (click to zoom)
- Download final image
- Mobile-first responsive UI

---

## Screenshots

### Upload

![Upload](/screenshots/upload-desktop-layout.png)
![Upload](/screenshots/upload-mobile-layout.png)

### Choose Files

![Choose Files](/screenshots/choose-files.png)

### Input Preview

![Inputs](/screenshots/inputs-preview-desktop.png)
![Inputs](/screenshots/inputs-preview-mobile.png)

### Result

![Result](/screenshots/final-result-desktop.png)
![Result](/screenshots/final-result-mobile.png)

### Preview

![Preview](/screenshots/preview-desktop.png)
![Preview](/screenshots/preview-mobile.png)

---

## Tech Stack

**Frontend**

- Flask
- HTML / CSS / JavaScript

**Backend**

- FastAPI
- rembg (ONNX model)
- Pillow / NumPy

**Deployment**

- Render (API + UI as separate services)

---

## Architecture

```mermaid
flowchart TD
    User -->|Upload Images| Frontend[Flask UI]
    Frontend -->|POST request| API[FastAPI Backend]
    API -->|AI Processing| Model[rembg / ONNX]
    Model --> API
    API -->|Processed Image| Frontend
    Frontend -->|Preview & Download| User
```

---

## Notes

- Multiple models were tested during development
- A single optimized model is used in deployment for performance and cost efficiency
- Designed for demonstration purposes
