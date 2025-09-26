import cv2
import time
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Open webcam
cap = cv2.VideoCapture(0)

# Distraction timer variables
focused = True
distracted_start = 0
total_distracted = 0  

def format_time(seconds):
    """Convert seconds to HH:MM:SS format"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 detection
    results = model(frame)

    person_detected = False
    for r in results:
        if r.boxes is not None:
            for i in range(len(r.boxes)):
                cls_id = int(r.boxes.cls[i])
                conf = float(r.boxes.conf[i])
                if cls_id == 0 and conf > 0.5:  # Person class
                    person_detected = True
                    x1, y1, x2, y2 = map(int, r.boxes.xyxy[i])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "Person", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Update distraction logic
    if person_detected:
        focused = True
        if distracted_start != 0:
            # Add running distraction to total when person returns
            total_distraction_time = time.time() - distracted_start
            total_distracted += total_distraction_time
            distracted_start = 0
    else:
        # Person is away
        if focused:
            distracted_start = time.time()
        focused = False

    # Calculate current running distraction
    current_distraction = total_distracted
    if distracted_start != 0:
        current_distraction += time.time() - distracted_start

    # Display distraction time in HH:MM:SS
    cv2.putText(frame, f"Distraction: {format_time(current_distraction)}",
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show video
    cv2.imshow("One Person Productivity Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
