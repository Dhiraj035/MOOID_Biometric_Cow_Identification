from pathlib import Path
import cv2


BASE = Path(
    r"F:\python_RENET50_TRAIN\DATASET OF COW\YOLO_MUZZLE_DATASET"
)


images = [
    BASE / "14" / "N_15_muzzle.jpg",
    BASE / "16" / "P_10_muzzle.jpg",
]


for image_path in images:

    print("\n" + "=" * 70)
    print(f"Image: {image_path}")

    image = cv2.imread(str(image_path))

    if image is None:
        print("ERROR: Could not read image")
        continue

    print(
        f"Size: "
        f"{image.shape[1]} x {image.shape[0]}"
    )

    window = image_path.name

    cv2.imshow(window, image)

    print("Press any key to continue...")

    cv2.waitKey(0)

    cv2.destroyWindow(window)


cv2.destroyAllWindows()

print("\nInspection complete.")
