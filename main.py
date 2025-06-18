# main.py

import cv2
from ultralytics import YOLO
import os
import requests
import re
from datetime import datetime
import csv

# --- Configuration ---
PLATERECOGNIZER_API_TOKEN = "Token 9ca257db77f16745ffde4e79e28e63c906bbe821"
PLATERECOGNIZER_ENDPOINT = "https://api.platerecognizer.com/v1/plate-reader/"
REGIONS = ["in"]
ENTRY_LINE_Y = 300
EXIT_LINE_Y = 400

# --- Helper Functions ---
crossed_vehicles = set()

def check_crossing(center):
    x, y = center
    if ENTRY_LINE_Y < y < EXIT_LINE_Y:
        vehicle_id = f"{x}-{y}"
        if vehicle_id not in crossed_vehicles:
            crossed_vehicles.add(vehicle_id)
            return True
    return False

def extract_plate_text(image_path):
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return None, 0.0

    with open(image_path, 'rb') as fp:
        response = requests.post(
            PLATERECOGNIZER_ENDPOINT,
            data=dict(regions=REGIONS),
            files=dict(upload=fp),
            headers={'Authorization': PLATERECOGNIZER_API_TOKEN}
        )

    if response.status_code == 200:
        result = response.json()
        if result['results']:
            best_match = result['results'][0]
            plate = best_match['plate']
            score = best_match['score']
            return plate, score
        else:
            return "", 0.0
    else:
        print(f"[ERROR] API call failed: {response.status_code}")
        return "", 0.0

def is_valid_plate(plate):
    INDIAN_PLATE_REGEX = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$"
    plate = plate.upper().replace(" ", "").strip()
    return re.match(INDIAN_PLATE_REGEX, plate) is not None

# --- Load YOLO Model ---
model = YOLO("yolo_model/yolov8n.pt")

# --- Video Initialization ---
video_path = "video_input/demo_footage.mp4"
cap = cv2.VideoCapture(video_path)

# --- CSV Logging ---
csv_path = "logs/detections.csv"
if not os.path.exists(csv_path):
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["image", "plate", "timestamp", "source", "confidence"])

frame_count = 0
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame_count += 1
    if frame_count % 5 != 0:
        continue

    results = model.predict(frame, conf=0.5)
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls == 2:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center = ((x1 + x2) // 2, (y1 + y2) // 2)

                if check_crossing(center):
                    cropped = frame[y1:y2, x1:x2]
                    filename = f"car_{frame_count}.jpg"
                    filepath = f"cropped_cars/{filename}"
                    cv2.imwrite(filepath, cropped)

                    plate, conf = extract_plate_text(filepath)
                    if is_valid_plate(plate):
                        timestamp = str(datetime.now())
                        print("--- Detected Plate ---")
                        print("Image:", filename)
                        print("Plate:", plate)
                        print("Timestamp:", timestamp)
                        print("Source: PlateRecognizer")
                        print("Confidence:", conf)

                        with open(csv_path, 'a', newline='') as file:
                            csv.writer(file).writerow([filename, plate, timestamp, "PlateRecognizer", conf])

cap.release()
