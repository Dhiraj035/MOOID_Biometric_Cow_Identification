import cv2
import torch
import numpy as np
import faiss

from pathlib import Path
from ultralytics import YOLO

from model import ResNet50Embedding


# ============================================================
# PATHS
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
ROOT_DIR = PROJECT_DIR.parent

MODEL_DIR = PROJECT_DIR / "models"

RESNET_PATH = MODEL_DIR / "best_resnet50_arcface_24c_yolo_texture.pth"

FAISS_PATH = MODEL_DIR / "cow_24_yolo_texture_train.faiss"
LABELS_PATH = MODEL_DIR / "cow_24_yolo_texture_train_labels.npy"
PATHS_PATH = MODEL_DIR / "cow_24_yolo_texture_train_paths.npy"

YOLO_PATH = (
    ROOT_DIR
    / "runs"
    / "detect"
    / "train-2"
    / "weights"
    / "best.pt"
)

LAST_MUZZLE_PATH = CURRENT_DIR / "last_detected_muzzle.jpg"
LAST_PROCESSED_PATH = CURRENT_DIR / "last_processed_muzzle.jpg"


# ============================================================
# SETTINGS
# ============================================================

IMAGE_SIZE = 224

# Temporary threshold.
# Change this later after proper unknown-cow calibration.
UNKNOWN_THRESHOLD = 0.50

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD YOLO
# ============================================================

print("\nLoading YOLO model...")

yolo_model = YOLO(str(YOLO_PATH))

print("YOLO loaded successfully.")


# ============================================================
# LOAD RESNET50
# ============================================================

print("\nLoading ResNet50 model...")

resnet_model = ResNet50Embedding(
    embedding_size=512
)

checkpoint = torch.load(
    RESNET_PATH,
    map_location=DEVICE
)

# Handle different checkpoint formats
if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    resnet_model.load_state_dict(
        checkpoint["model_state_dict"]
    )
elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
    resnet_model.load_state_dict(
        checkpoint["state_dict"]
    )
else:
    resnet_model.load_state_dict(checkpoint)

resnet_model.to(DEVICE)
resnet_model.eval()

print("ResNet50 loaded successfully.")
print("Device:", DEVICE)


# ============================================================
# LOAD FAISS
# ============================================================

print("\nLoading FAISS database...")

faiss_index = faiss.read_index(
    str(FAISS_PATH)
)

gallery_labels = np.load(
    LABELS_PATH
)

gallery_paths = np.load(
    PATHS_PATH,
    allow_pickle=True
)

print("FAISS database loaded.")
print("Gallery size:", faiss_index.ntotal)
print("Embedding dimension:", faiss_index.d)


# ============================================================
# IMAGE SELECTION
# ============================================================

print("\n" + "=" * 70)
print("SELECT FULL-COW IMAGE")
print("=" * 70)

print("""
Enter the complete path of the cow image.

Example:
F:\\python_RENET50_TRAIN\\DATASET OF COW\\Raw\\1\\A_14.jpg
""")

image_path = input("Image path: ").strip()

# Remove quotation marks if user pasted path with quotes
image_path = image_path.strip('"').strip("'")

image_path = Path(image_path)

if not image_path.exists():

    print("\nERROR: Image file does not exist.")
    print("Path:", image_path)
    raise SystemExit


print("\nSelected image:")
print(image_path)


# ============================================================
# READ FULL COW IMAGE
# ============================================================

full_image = cv2.imread(
    str(image_path)
)

if full_image is None:

    print("\nERROR: OpenCV could not read the image.")
    raise SystemExit


# ============================================================
# YOLO MUZZLE DETECTION
# ============================================================

print("\nRunning YOLO muzzle detection...")

results = yolo_model.predict(
    source=full_image,
    conf=0.25,
    imgsz=640,
    device=0 if torch.cuda.is_available() else "cpu",
    verbose=False
)

result = results[0]

if result.boxes is None or len(result.boxes) == 0:

    print("\nERROR: No muzzle detected.")
    print("Try another image.")

    raise SystemExit


# ============================================================
# SELECT HIGHEST CONFIDENCE MUZZLE
# ============================================================

boxes = result.boxes

confidences = boxes.conf.cpu().numpy()

best_index = int(
    np.argmax(confidences)
)

best_box = boxes.xyxy[best_index].cpu().numpy()

x1, y1, x2, y2 = best_box.astype(int)

yolo_confidence = float(
    confidences[best_index]
)


# Keep coordinates inside image boundaries

height, width = full_image.shape[:2]

x1 = max(0, min(x1, width - 1))
x2 = max(0, min(x2, width))

y1 = max(0, min(y1, height - 1))
y2 = max(0, min(y2, height))


print("\nYOLO confidence: {:.4f}".format(
    yolo_confidence
))

print(
    f"Muzzle box: ({x1}, {y1}) -> ({x2}, {y2})"
)


# ============================================================
# CROP MUZZLE
# ============================================================

muzzle_crop = full_image[
    y1:y2,
    x1:x2
]

if muzzle_crop.size == 0:

    print("\nERROR: Muzzle crop is empty.")
    raise SystemExit


# Save original YOLO crop

cv2.imwrite(
    str(LAST_MUZZLE_PATH),
    muzzle_crop
)

print("\nMuzzle crop saved:")
print(LAST_MUZZLE_PATH)


# ============================================================
# OPENCV TEXTURE PREPROCESSING
# ============================================================

print("\nApplying OpenCV grayscale preprocessing...")

# ------------------------------------------------------------
# STEP 1: Convert BGR muzzle crop to GRAYSCALE
# ------------------------------------------------------------

gray = cv2.cvtColor(
    muzzle_crop,
    cv2.COLOR_BGR2GRAY
)

print("1. OpenCV grayscale: DONE")


# ------------------------------------------------------------
# STEP 2: CLAHE
# ------------------------------------------------------------

clahe = cv2.createCLAHE(
    clipLimit=2.0,
    tileGridSize=(8, 8)
)

enhanced = clahe.apply(
    gray
)

print("2. CLAHE enhancement: DONE")


# ------------------------------------------------------------
# STEP 3: SHARPENING
# ------------------------------------------------------------

blur = cv2.GaussianBlur(
    enhanced,
    (0, 0),
    1.0
)

sharpened = cv2.addWeighted(
    enhanced,
    1.5,
    blur,
    -0.5,
    0
)

print("3. Sharpening: DONE")


# ------------------------------------------------------------
# STEP 4: NORMALIZATION
# ------------------------------------------------------------

normalized = cv2.normalize(
    sharpened,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)

print("4. Pixel normalization: DONE")


# ------------------------------------------------------------
# STEP 5: GRAYSCALE -> RGB
#
# ResNet50 expects 3 channels.
# The three channels contain the same grayscale information.
# ------------------------------------------------------------

rgb = cv2.cvtColor(
    normalized,
    cv2.COLOR_GRAY2RGB
)

print("5. Grayscale -> RGB: DONE")


# ============================================================
# SAVE PROCESSED IMAGE
# ============================================================

cv2.imwrite(
    str(LAST_PROCESSED_PATH),
    cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
)

print("\nProcessed grayscale image saved:")
print(LAST_PROCESSED_PATH)


# ============================================================
# RESIZE
# ============================================================

rgb = cv2.resize(
    rgb,
    (IMAGE_SIZE, IMAGE_SIZE),
    interpolation=cv2.INTER_AREA
)


# ============================================================
# CONVERT TO PYTORCH TENSOR
# ============================================================

image_tensor = torch.from_numpy(
    rgb
).permute(2, 0, 1).float() / 255.0


# ============================================================
# IMAGENET NORMALIZATION
# ============================================================

mean = torch.tensor(
    [0.485, 0.456, 0.406]
).view(3, 1, 1)

std = torch.tensor(
    [0.229, 0.224, 0.225]
).view(3, 1, 1)

image_tensor = (
    image_tensor - mean
) / std


# Add batch dimension

image_tensor = image_tensor.unsqueeze(0)

image_tensor = image_tensor.to(
    DEVICE
)


# ============================================================
# RESNET50 EMBEDDING
# ============================================================

print("\nExtracting ResNet50 embedding...")

with torch.no_grad():

    embedding = resnet_model(
        image_tensor
    )

embedding = embedding.cpu().numpy().astype(
    "float32"
)


# Normalize embedding

faiss.normalize_L2(
    embedding
)


# ============================================================
# FAISS SEARCH
# ============================================================

print("\nSearching registered cow database...")

TOP_K = 10

similarities, indices = faiss_index.search(
    embedding,
    TOP_K
)


# ============================================================
# TOP 10 MATCHES
# ============================================================

print("\n")
print("=" * 70)
print("TOP 10 MATCHES")
print("=" * 70)

for rank in range(TOP_K):

    index = int(
        indices[0][rank]
    )

    similarity = float(
        similarities[0][rank]
    )

    label = int(
        gallery_labels[index]
    )

    cow_id = label + 1

    print(
        f"{rank + 1:2d}. Cow {cow_id} | "
        f"Similarity: {similarity:.4f}"
    )


# ============================================================
# TOP MATCH INFORMATION
# ============================================================

top_index = int(
    indices[0][0]
)

top_similarity = float(
    similarities[0][0]
)

top_label = int(
    gallery_labels[top_index]
)

top_cow = top_label + 1


# Find second DIFFERENT cow

second_cow = None
second_similarity = None

for rank in range(1, TOP_K):

    index = int(
        indices[0][rank]
    )

    label = int(
        gallery_labels[index]
    )

    cow_id = label + 1

    if cow_id != top_cow:

        second_cow = cow_id

        second_similarity = float(
            similarities[0][rank]
        )

        break


if second_cow is not None:

    margin = (
        top_similarity
        - second_similarity
    )

else:

    margin = 0.0


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("FINAL MOO-ID RESULT")
print("=" * 70)

print(
    f"\nYOLO confidence : {yolo_confidence:.4f}"
)

print(
    f"Top Cow        : Cow {top_cow}"
)

print(
    f"Top similarity : {top_similarity:.4f}"
)

if second_cow is not None:

    print(
        f"Second Cow     : Cow {second_cow}"
    )

    print(
        f"Second score   : {second_similarity:.4f}"
    )

else:

    print(
        "Second Cow     : No different cow in Top 10"
    )

    print(
        "Second score   : N/A"
    )


print(
    f"Margin         : {margin:.4f}"
)

print(
    f"Threshold      : {UNKNOWN_THRESHOLD:.4f}"
)


print("\n" + "-" * 70)


# ============================================================
# KNOWN / UNKNOWN DECISION
# ============================================================

if top_similarity >= UNKNOWN_THRESHOLD:

    print("✅ KNOWN COW")
    print(f"🐄 Cow ID: {top_cow}")

else:

    print("❌ UNKNOWN COW")
    print("No registered cow matches this image.")


print("-" * 70)


print("""
NOTE:
The current threshold is temporary.
It should be calibrated using genuine registered cows
and real unknown cows before final deployment.
""")

print("=" * 70)