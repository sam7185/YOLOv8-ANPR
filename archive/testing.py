import cv2
import os
import requests
from ultralytics import YOLO

# Constants
MODEL_PATH = "yolo_model/yolov8n.pt"
VIDEO_PATH = "video_input/demo_footage.mp4"
CROPPED_DIR = "cropped_cars/"
ENTRY_LINE_Y = 394
EXIT_LINE_Y = 518
MOVEMENT_THRESHOLD = 15
PLATERECOGNIZER_API_TOKEN = "Token 9ca257db77f16745ffde4e79e28e63c906bbe821"
PLATERECOGNIZER_ENDPOINT = "https://api.platerecognizer.com/v1/plate-reader/"
REGIONS = ["in"]

# Create folder if not exists
os.makedirs(CROPPED_DIR, exist_ok=True)

def track_and_capture_vehicles():
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH)

    vehicle_id_counter = 0
    tracked_vehicles = {}
    saved_ids = set()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, conf=0.5)[0]

        cv2.line(frame, (0, ENTRY_LINE_Y), (frame.shape[1], ENTRY_LINE_Y), (255, 255, 0), 2)
        cv2.line(frame, (0, EXIT_LINE_Y), (frame.shape[1], EXIT_LINE_Y), (255, 0, 255), 2)

        updated_tracking = {}

        for box in results.boxes:
            cls = int(box.cls[0])
            if cls != 2:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center = ((x1 + x2) // 2, (y1 + y2) // 2)

            matched_id = None
            for vid, data in tracked_vehicles.items():
                prev_center = data["center"]
                if abs(center[0] - prev_center[0]) < 50 and abs(center[1] - prev_center[1]) < 50:
                    matched_id = vid
                    break

            if matched_id is None:
                matched_id = vehicle_id_counter
                vehicle_id_counter += 1

            prev_center = tracked_vehicles.get(matched_id, {}).get("center")
            moved = False
            if prev_center:
                dx = abs(center[0] - prev_center[0])
                dy = abs(center[1] - prev_center[1])
                moved = dx > MOVEMENT_THRESHOLD or dy > MOVEMENT_THRESHOLD

            crossed = tracked_vehicles.get(matched_id, {}).get("crossed", False)

            if not crossed and moved and ENTRY_LINE_Y < center[1] < EXIT_LINE_Y:
                crossed = True
                if matched_id not in saved_ids:
                    cropped = frame[y1:y2, x1:x2]
                    save_path = os.path.join(CROPPED_DIR, f"car_{matched_id}.jpg")
                    cv2.imwrite(save_path, cropped)
                    saved_ids.add(matched_id)

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

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


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
    elif response.status_code == 429:
        print(f"[RATE LIMIT] {image_path}: Too many requests.")
        return None
    else:
        print(f"[ERROR] {image_path}: API failed with {response.status_code}")
        return None


def process_unique_plates():
    unique_plates = {}

    for img_name in os.listdir(CROPPED_DIR):
        if not img_name.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        path = os.path.join(CROPPED_DIR, img_name)
        result = send_to_plate_recognizer(path)
        if not result or not result.get("results"):
            continue

        plate_data = result["results"][0]
        plate = plate_data["plate"].upper()

        if plate not in unique_plates:
            unique_plates[plate] = {
                "image": img_name,
                "confidence": plate_data["score"],
                "vehicle_type": plate_data.get("vehicle", {}).get("type", "Unknown"),
                "region": plate_data.get("region", {}).get("code", "N/A")
            }

    print("\n--- Unique Plates Detected ---")
    for plate, data in unique_plates.items():
        print(f"Plate: {plate}")
        print(f"Image: {data['image']}")
        print(f"Confidence: {data['confidence']:.3f}")
        print(f"Vehicle Type: {data['vehicle_type']}")
        print(f"Region: {data['region']}")
        print("-" * 30)


# Usage
if __name__ == "__main__":
    track_and_capture_vehicles()
    process_unique_plates()
