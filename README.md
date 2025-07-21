Awesome — congrats again on finishing the project! 🎉
Let’s now write a clean, well-structured `README.md` file for your **YOLOv8-based ANPR System using Django**.

---

## ✅ Final `README.md` File

```markdown
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

## 📁 Project Structure

```

YOLOV8-ANPR/
├── car\_videos/           # Individual car clip outputs
├── cropped\_cars/         # Cropped car images
├── output\_video/         # Full annotated video
├── static/
│   └── output\_video/     # Video copied here for frontend preview
├── video\_input/          # Stores latest uploaded video
├── yolo\_model/           # Contains YOLOv8 weights
├── templates/
│   ├── home.html
│   └── plates.html
├── main.py               # Core processing pipeline
├── views.py              # Django views
├── urls.py               # Django URL routes
├── models.py             # DB model for plate data
├── database.py           # DB insertion logic
├── utils/                # Line crossing, detection helpers
├── manage.py
└── README.md             # You're here!

````

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/yolov8-anpr.git
cd yolov8-anpr
````

### 2. Create and Activate Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure APIs

Set your API keys in a `.env` file:

```env
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
PLATE_RECOGNIZER_API_TOKEN=your_token
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Server

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
* ⏳ Host on cloud (e.g., AWS EC2 or Railway)

---

## 🧑‍💻 Author

**Samarth Nilkanth**
Final Year CMPN – VESIT, Mumbai

---
