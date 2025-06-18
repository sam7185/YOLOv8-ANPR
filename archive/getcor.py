import cv2

video_path = "video_input/demo_footage.mp4"
cap = cv2.VideoCapture(video_path)

clicked_points = []

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print(f"Clicked at: ({x}, {y})")

frame_number = 150  # Choose a frame number you want to inspect
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

ret, frame = cap.read()
if not ret:
    print("Failed to load frame.")
    exit()

cv2.imshow("Click to get coordinates", frame)
cv2.setMouseCallback("Click to get coordinates", click_event)

print("Click on the frame window. Press ESC to exit.")

while True:
    cv2.imshow("Click to get coordinates", frame)
    key = cv2.waitKey(1)
    if key == 27:  # ESC key to exit
        break

cv2.destroyAllWindows()
cap.release()

print("Final clicked coordinates:", clicked_points)
