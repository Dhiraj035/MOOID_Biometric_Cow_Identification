import cv2
from ultralytics import YOLO

YOLO_PATH = r"F:\python_RENET50_TRAIN\runs\detect\train-2\weights\best.pt"

print("Loading YOLOv8...")
model = YOLO(YOLO_PATH)

print("Opening webcam...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

window_name = "Moo-ID - YOLO Muzzle Detection"

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

print("Webcam started.")
print("Press Q or close the window to exit.")

while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read webcam frame.")
        break

    # YOLO detection
    results = model.predict(
        source=frame,
        conf=0.25,
        imgsz=640,
        verbose=False
    )

    result = results[0]

    if result.boxes is not None:

        for i in range(len(result.boxes)):

            box = result.boxes.xyxy[i].cpu().numpy()

            confidence = float(
                result.boxes.conf[i].item()
            )

            x1, y1, x2, y2 = map(int, box)

            # Draw bounding box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                3
            )

            # Label
            label = f"Muzzle {confidence:.2f}"

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow(window_name, frame)

    # Q key
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == ord("Q"):
        break

    # X button
    if cv2.getWindowProperty(
        window_name,
        cv2.WND_PROP_VISIBLE
    ) < 1:
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)

print("Webcam released.")