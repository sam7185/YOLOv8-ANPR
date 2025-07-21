import cv2
import os
import requests
from ultralytics import YOLO
from dotenv import load_dotenv
import time
import shutil
from datetime import datetime
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")  # 🔁 Replace with your project name
django.setup()

from plates.models import DetectedPlate
from django.utils import timezone

# ---------- Load API Key ----------
load_dotenv()
PLATERECOGNIZER_API_TOKEN = os.getenv("PLATE_RECOGNIZER_API_KEY")
if not PLATERECOGNIZER_API_TOKEN:
    raise ValueError("API key not found in .env!")

# ---------- Config ----------
MODEL_PATH = "yolo_model/yolov8n.pt"
CROPPED_DIR = "cropped_cars/"
CAR_VIDEO_DIR = "media/car_videos/"
STATIC_OUTPUT_DIR = os.path.join("plates", "static", "output_video")
PLATERECOGNIZER_ENDPOINT = "https://api.platerecognizer.com/v1/plate-reader/"
REGIONS = ["in"]

# ---------- Ensure Directories ----------
os.makedirs(CROPPED_DIR, exist_ok=True)
os.makedirs(CAR_VIDEO_DIR, exist_ok=True)
os.makedirs("output_video", exist_ok=True)
os.makedirs(STATIC_OUTPUT_DIR, exist_ok=True)
os.makedirs("media/car_images", exist_ok=True)

# ---------- Tracking & Capture ----------
def track_and_capture_vehicles(video_path, output_video_path, entry_line_y, exit_line_y):
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        return

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    vehicle_id_counter = 0
    tracked_vehicles = {}
    saved_ids = set()
    car_video_writers = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, conf=0.5)[0]
        cv2.line(frame, (0, entry_line_y), (width, entry_line_y), (255, 255, 0), 2)
        cv2.line(frame, (0, exit_line_y), (width, exit_line_y), (255, 0, 255), 2)
        updated_tracking = {}

        for box in results.boxes:
            if int(box.cls[0]) != 2:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            matched_id = None

            for vid, data in tracked_vehicles.items():
                if abs(center[0] - data["center"][0]) < 50 and abs(center[1] - data["center"][1]) < 50:
                    matched_id = vid
                    break

            if matched_id is None:
                matched_id = vehicle_id_counter
                vehicle_id_counter += 1

            moved = False
            prev_center = tracked_vehicles.get(matched_id, {}).get("center")
            if prev_center:
                dx = abs(center[0] - prev_center[0])
                dy = abs(center[1] - prev_center[1])
                moved = dx > 15 or dy > 15

            crossed = tracked_vehicles.get(matched_id, {}).get("crossed", False)

            if not crossed and moved and entry_line_y < center[1] < exit_line_y:
                crossed = True
                if matched_id not in saved_ids:
                    cropped = frame[y1:y2, x1:x2]
                    save_path = os.path.join("media/car_images", f"car_{matched_id}.jpg")
                    cv2.imwrite(save_path, cropped)
                    print(f"[SAVED] Cropped image: {save_path}")
                    saved_ids.add(matched_id)

            if matched_id in saved_ids and matched_id not in car_video_writers:
                car_vid_path = os.path.join(CAR_VIDEO_DIR, f"car_{matched_id}.mp4")
                car_writer = cv2.VideoWriter(car_vid_path, fourcc, fps, (width, height))
                car_video_writers[matched_id] = car_writer

            if matched_id in car_video_writers:
                car_video_writers[matched_id].write(frame)

            updated_tracking[matched_id] = {
                "xyxy": (x1, y1, x2, y2),
                "center": center,
                "crossed": crossed
            }

            color = (0, 255, 0) if not crossed else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"ID {matched_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        tracked_vehicles = updated_tracking
        out.write(frame)
        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    out.release()
    for writer in car_video_writers.values():
        writer.release()
    cv2.destroyAllWindows()

    try:
        shutil.copy(output_video_path, os.path.join(STATIC_OUTPUT_DIR, "annotated_output.mp4"))
        print("[SUCCESS] Copied annotated video to static folder.")
    except Exception as e:
        print(f"[ERROR] Failed to copy video: {e}")

# ---------- PlateRecognizer ----------
def send_to_plate_recognizer(image_path):
    with open(image_path, 'rb') as fp:
        response = requests.post(
            PLATERECOGNIZER_ENDPOINT,
            data=dict(regions=REGIONS),
            files=dict(upload=fp),
            headers={'Authorization': PLATERECOGNIZER_API_TOKEN}
        )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"[ERROR] {image_path}: API failed with {response.status_code}")
        return None

# ---------- Process Cropped Plates ----------
def process_unique_plates():
    unique_plates = {}

    for img_name in os.listdir("media/car_images"):
        if not img_name.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        path = os.path.join("media/car_images", img_name)
        result = send_to_plate_recognizer(path)
        time.sleep(1)

        if not result or not result.get("results"):
            continue

        plate_data = result["results"][0]
        plate = plate_data["plate"].upper()

        if plate not in unique_plates:
            timestamp = timezone.now()
            video_name = img_name.replace(".jpg", ".mp4")

            unique_plates[plate] = {
                "image": img_name,
                "confidence": plate_data.get("score", 0.0),
                "vehicle_type": plate_data.get("vehicle", {}).get("type", "Unknown"),
                "region": plate_data.get("region", {}).get("code", "N/A"),
                "timestamp": timestamp
            }

            DetectedPlate.objects.create(
                plate_text=plate,
                vehicle_type=unique_plates[plate]["vehicle_type"],
                timestamp=timestamp,
                car_image_path=os.path.join("media/car_images", img_name),
                car_video_path=os.path.join("media/car_videos", video_name),
            )

            print(f"[DETECTED] Plate: {plate}")

# ---------- Entry Point ----------
def run_pipeline(video_path, output_video_path, entry_line_y, exit_line_y):
    track_and_capture_vehicles(video_path, output_video_path, entry_line_y, exit_line_y)
    process_unique_plates()

if __name__ == "__main__":
    run_pipeline(
        video_path="video_input/demo_footage.mp4",
        output_video_path="output_video/annotated_output.mp4",
        entry_line_y=394,
        exit_line_y=518
    )
