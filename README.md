
---

## ✅ `README.md` File


# YOLOv8 Automatic Number Plate Recognition (ANPR) System 🚗📹

A Django-based web application that detects vehicles in videos using YOLOv8, extracts their license plates via OCR (AWS Textract + PlateRecognizer API), and displays the results in an interactive dashboard. The system allows uploading videos, filtering results, and downloading cropped car images and annotated videos.

---

## 🔧 Features

- 📤 Upload vehicle video directly from the web interface
- 🎯 Detect cars using YOLOv8 when crossing two user-defined lines
- 🔍 Extract license plates using PlateRecognizer APIs
- 🧾 Validate plate format using regex and store in SQLite database
- 📊 View results in a paginated and filterable table
- 📸 Download cropped car images and individual car videos
- 🎥 Preview full annotated video (looped)
- 📂 Download entire plate data as CSV

---

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/yolov8-anpr.git
cd yolov8-anpr
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the Server

```bash
python manage.py runserver
```

---

## 🧪 How It Works

1. User uploads a video + sets entry and exit line Y-coordinates.
2. `main.py` runs:

   * YOLOv8 detects vehicles.
   * Crops vehicles crossing both lines.
   * OCR extracts plate text (PlateRecognizer).
   * Saves plate data in DB and cropped image + video.
   * Copies full annotated video to `static/` for display.
3. `/plates/` page displays:

   * Annotated video
   * Filterable plate table
   * Download options per vehicle

---

## ⚙️ Tech Stack

* **Frontend**: HTML + Tailwind CSS
* **Backend**: Django (Python)
* **Detection**: YOLOv8 (Ultralytics)
* **OCR**: PlateRecognizer API
* **DB**: SQLite (via Django ORM)

---

## 📦 Future Improvements

* ✅ Pagination & filtering on results table
* ✅ Download buttons per row
* ⏳ Real-time video stream input
* ⏳ Admin login dashboard
* ⏳ Host on cloud (e.g., AWS EC2)

---

## 🧑‍💻 Author

**Samarth Nilkanth**
Final Year CMPN – VESIT, Mumbai

---
