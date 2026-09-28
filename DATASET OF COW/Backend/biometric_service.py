import sys
from pathlib import Path

import cv2
import faiss
import numpy as np
import torch

from PIL import Image
from torchvision import transforms
from ultralytics import YOLO


# ============================================================
# PATHS
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent

# F:\python_RENET50_TRAIN\DATASET OF COW
PROJECT_DIR = CURRENT_DIR.parent

# F:\python_RENET50_TRAIN
ROOT_DIR = PROJECT_DIR.parent

MODEL_DIR = PROJECT_DIR / "models"


# ============================================================
# MODEL PATHS
# ============================================================

# YOLOv8 muzzle detector
YOLO_PATH = (
    ROOT_DIR
    / "runs"
    / "detect"
    / "train-2"
    / "weights"
    / "best.pt"
)


# ResNet50 + ArcFace
RESNET_PATH = (
    MODEL_DIR
    / "best_resnet50_arcface_24c_yolo_texture.pth"
)


# ============================================================
# SETTINGS
# ============================================================

YOLO_CONFIDENCE = 0.25

YOLO_IMAGE_SIZE = 640

EMBEDDING_SIZE = 512


# ============================================================
# IMPORT RESNET MODEL
# ============================================================

if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from model import ResNet50Embedding


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# IMAGE TRANSFORMATION
# ============================================================

imagenet_transform = transforms.Compose(
    [
        transforms.Resize(
            (224, 224)
        ),

        transforms.ToTensor(),

        transforms.Normalize(
            mean=[
                0.485,
                0.456,
                0.406,
            ],

            std=[
                0.229,
                0.224,
                0.225,
            ],
        ),
    ]
)


# ============================================================
# GLOBAL MODELS
# ============================================================

yolo_model = None

resnet_model = None


# ============================================================
# CHECK MODEL FILES
# ============================================================

def check_model_files():

    required_files = {
        "YOLO model": YOLO_PATH,
        "ResNet50 model": RESNET_PATH,
    }

    for name, path in required_files.items():

        if not path.exists():

            raise FileNotFoundError(
                f"{name} not found:\n{path}"
            )


# ============================================================
# LOAD BIOMETRIC MODELS
# ============================================================

def load_biometric_models():

    global yolo_model
    global resnet_model

    print()
    print("=" * 70)
    print("LOADING MOO-ID BIOMETRIC MODELS")
    print("=" * 70)

    print(
        f"Device: {device}"
    )

    if torch.cuda.is_available():

        print(
            "GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

    # --------------------------------------------------------
    # CHECK FILES
    # --------------------------------------------------------

    print()
    print("Checking model files...")

    check_model_files()

    print(
        "All model files found."
    )

    # ========================================================
    # LOAD YOLO
    # ========================================================

    print()
    print("-" * 70)
    print("Loading YOLOv8 muzzle detector...")
    print("-" * 70)

    yolo_model = YOLO(
        str(YOLO_PATH)
    )

    print(
        f"YOLO classes: {yolo_model.names}"
    )

    print(
        f"YOLO confidence threshold: "
        f"{YOLO_CONFIDENCE}"
    )

    print(
        f"YOLO image size: "
        f"{YOLO_IMAGE_SIZE}"
    )

    print(
        "YOLO loaded successfully."
    )

    # ========================================================
    # LOAD RESNET50
    # ========================================================

    print()
    print("-" * 70)
    print("Loading ResNet50 embedding model...")
    print("-" * 70)

    checkpoint = torch.load(
        RESNET_PATH,
        map_location=device,
        weights_only=False,
    )

    embedding_size = checkpoint.get(
        "embedding_size",
        EMBEDDING_SIZE,
    )

    print(
        f"Embedding size: {embedding_size}"
    )

    resnet_model = ResNet50Embedding(
        embedding_size=embedding_size
    )

    resnet_model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    resnet_model = resnet_model.to(
        device
    )

    resnet_model.eval()

    print(
        "ResNet50 loaded successfully."
    )

    print()
    print("=" * 70)
    print("BIOMETRIC MODELS READY")
    print("=" * 70)
    print()


# ============================================================
# MUZZLE PREPROCESSING
# ============================================================

def preprocess_muzzle(
    muzzle_bgr
):
    """
    Same preprocessing used during
    ResNet50 training.

    Pipeline:

        BGR
         ↓
        Grayscale
         ↓
        CLAHE
         ↓
        Gaussian Blur
         ↓
        Sharpening
         ↓
        Min-Max Normalization
         ↓
        RGB
    """

    # --------------------------------------------------------
    # BGR → GRAYSCALE
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        muzzle_bgr,
        cv2.COLOR_BGR2GRAY,
    )

    # --------------------------------------------------------
    # CLAHE
    # --------------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(
        gray
    )

    # --------------------------------------------------------
    # GAUSSIAN BLUR
    # --------------------------------------------------------

    blur = cv2.GaussianBlur(
        enhanced,
        (0, 0),
        1.0,
    )

    # --------------------------------------------------------
    # SHARPENING
    # --------------------------------------------------------

    sharpened = cv2.addWeighted(
        enhanced,
        1.5,
        blur,
        -0.5,
        0,
    )

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    normalized = cv2.normalize(
        sharpened,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    # --------------------------------------------------------
    # GRAYSCALE → RGB
    # --------------------------------------------------------

    rgb = cv2.cvtColor(
        normalized,
        cv2.COLOR_GRAY2RGB,
    )

    return rgb


# ============================================================
# EXTRACT RESNET50 EMBEDDING
# ============================================================

def extract_embedding(
    muzzle_bgr
):
    """
    Convert detected muzzle into
    a normalized 512-dimensional embedding.
    """

    if resnet_model is None:

        raise RuntimeError(
            "ResNet50 model is not loaded."
        )

    # --------------------------------------------------------
    # PREPROCESS MUZZLE
    # --------------------------------------------------------

    processed_rgb = preprocess_muzzle(
        muzzle_bgr
    )

    # --------------------------------------------------------
    # RGB → PIL
    # --------------------------------------------------------

    pil_image = Image.fromarray(
        processed_rgb
    )

    # --------------------------------------------------------
    # IMAGE → TENSOR
    # --------------------------------------------------------

    image_tensor = imagenet_transform(
        pil_image
    )

    # --------------------------------------------------------
    # ADD BATCH DIMENSION
    # --------------------------------------------------------

    image_tensor = (
        image_tensor
        .unsqueeze(0)
        .to(device)
    )

    # --------------------------------------------------------
    # RESNET50
    # --------------------------------------------------------

    with torch.no_grad():

        embedding = resnet_model(
            image_tensor
        )

    # --------------------------------------------------------
    # GPU → CPU → NUMPY
    # --------------------------------------------------------

    embedding = (
        embedding
        .cpu()
        .numpy()
        .astype(np.float32)
    )

    # --------------------------------------------------------
    # NORMALIZE FOR COSINE SIMILARITY
    # --------------------------------------------------------

    faiss.normalize_L2(
        embedding
    )

    return embedding


# ============================================================
# FULL RESNET PIPELINE WITH STAGE INFORMATION
# ============================================================

def extract_embedding_with_pipeline(muzzle_bgr):
    """Run preprocessing, ResNet50 feature extraction and L2 normalization."""
    if resnet_model is None:
        raise RuntimeError("ResNet50 model is not loaded.")
    if muzzle_bgr is None or muzzle_bgr.size == 0:
        raise ValueError("Muzzle crop is empty.")

    info = {
        "grayscale": True,
        "clahe": True,
        "sharpening": True,
        "min_max_normalization": True,
        "rgb_conversion": True,
        "resize_224x224": True,
        "imagenet_normalization": True,
        "resnet50": False,
        "embedding_dimension": 0,
        "l2_normalization": False,
    }

    processed_rgb = preprocess_muzzle(muzzle_bgr)
    pil_image = Image.fromarray(processed_rgb)
    image_tensor = imagenet_transform(pil_image)
    image_tensor = image_tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = resnet_model(image_tensor)

    info["resnet50"] = True
    embedding = embedding.cpu().numpy().astype(np.float32)
    info["embedding_dimension"] = int(embedding.shape[1])

    faiss.normalize_L2(embedding)
    info["l2_normalization"] = True

    return embedding, info


# ============================================================
# YOLO MUZZLE DETECTION
# ============================================================

def detect_muzzle(
    image
):
    """
    Detect the cow muzzle using YOLO.

    This function now prints detailed
    information about EVERY detection.

    Useful for debugging images where
    YOLO sometimes fails.
    """

    if yolo_model is None:

        raise RuntimeError(
            "YOLO model is not loaded."
        )

    # ========================================================
    # IMAGE INFORMATION
    # ========================================================

    if image is None:

        raise ValueError(
            "Input image is None."
        )

    if image.size == 0:

        raise ValueError(
            "Input image is empty."
        )

    height, width = image.shape[:2]

    print()
    print("=" * 70)
    print("YOLO MUZZLE DETECTION")
    print("=" * 70)

    print(
        f"Input image size: "
        f"{width} x {height}"
    )

    print(
        f"YOLO confidence threshold: "
        f"{YOLO_CONFIDENCE}"
    )

    print(
        f"YOLO inference size: "
        f"{YOLO_IMAGE_SIZE}"
    )

    # ========================================================
    # RUN YOLO
    # ========================================================

    results = yolo_model.predict(
        source=image,
        conf=YOLO_CONFIDENCE,
        imgsz=YOLO_IMAGE_SIZE,
        verbose=False,
    )

    # ========================================================
    # CHECK RESULTS
    # ========================================================

    if not results:

        print()
        print(
            "WARNING: YOLO returned no results."
        )

        print("=" * 70)

        raise ValueError(
            "YOLO returned no results."
        )

    result = results[0]

    boxes = result.boxes

    # ========================================================
    # NO DETECTIONS
    # ========================================================

    if boxes is None or len(boxes) == 0:

        print()
        print(
            "NO MUZZLE DETECTION"
        )

        print()
        print(
            "Possible causes:"
        )

        print(
            "1. Muzzle is too small."
        )

        print(
            "2. Muzzle angle is different."
        )

        print(
            "3. Image is blurry."
        )

        print(
            "4. Lighting is poor."
        )

        print(
            "5. Muzzle is partially hidden."
        )

        print(
            "6. Image differs from YOLO training data."
        )

        print()
        print("=" * 70)

        raise ValueError(
            "No muzzle detected in the image."
        )

    # ========================================================
    # DETECTION COUNT
    # ========================================================

    detection_count = len(boxes)

    print()
    print(
        f"YOLO detections found: "
        f"{detection_count}"
    )

    print()
    print("-" * 70)

    # ========================================================
    # PRINT ALL DETECTIONS
    # ========================================================

    all_detections = []

    for i in range(
        detection_count
    ):

        confidence = float(
            boxes.conf[i].item()
        )

        box = (
            boxes.xyxy[i]
            .cpu()
            .numpy()
            .astype(int)
        )

        x1 = int(box[0])
        y1 = int(box[1])
        x2 = int(box[2])
        y2 = int(box[3])

        # Class ID
        class_id = int(
            boxes.cls[i].item()
        )

        # Class name
        class_name = str(
            yolo_model.names.get(
                class_id,
                class_id,
            )
        )

        box_width = x2 - x1
        box_height = y2 - y1

        print(
            f"Detection #{i + 1}"
        )

        print(
            f"  Class      : {class_name}"
        )

        print(
            f"  Confidence : "
            f"{confidence:.4f} "
            f"({confidence * 100:.2f}%)"
        )

        print(
            f"  BoundingBox: "
            f"[{x1}, {y1}, {x2}, {y2}]"
        )

        print(
            f"  Box size   : "
            f"{box_width} x {box_height}"
        )

        all_detections.append(
            {
                "index": i,
                "confidence": confidence,
                "class_id": class_id,
                "class_name": class_name,
                "box": [
                    x1,
                    y1,
                    x2,
                    y2,
                ],
            }
        )

        print("-" * 70)

    # ========================================================
    # SELECT HIGHEST CONFIDENCE
    # ========================================================

    best_index = int(
        torch.argmax(
            boxes.conf
        ).item()
    )

    best_detection = (
        all_detections[best_index]
    )

    confidence = float(
        best_detection["confidence"]
    )

    print()
    print(
        "SELECTED DETECTION"
    )

    print(
        f"  Detection : "
        f"#{best_index + 1}"
    )

    print(
        f"  Class     : "
        f"{best_detection['class_name']}"
    )

    print(
        f"  Confidence: "
        f"{confidence:.4f} "
        f"({confidence * 100:.2f}%)"
    )

    # ========================================================
    # GET BOUNDING BOX
    # ========================================================

    x1, y1, x2, y2 = (
        best_detection["box"]
    )

    # ========================================================
    # CLAMP COORDINATES
    # ========================================================

    x1 = max(
        0,
        min(
            x1,
            width - 1,
        ),
    )

    y1 = max(
        0,
        min(
            y1,
            height - 1,
        ),
    )

    x2 = max(
        0,
        min(
            x2,
            width,
        ),
    )

    y2 = max(
        0,
        min(
            y2,
            height,
        ),
    )

    # ========================================================
    # CHECK BOUNDING BOX
    # ========================================================

    if x2 <= x1 or y2 <= y1:

        print()
        print(
            "ERROR: Invalid bounding box."
        )

        print(
            f"Box: [{x1}, {y1}, {x2}, {y2}]"
        )

        print("=" * 70)

        raise ValueError(
            "Invalid muzzle bounding box."
        )

    # ========================================================
    # CROP MUZZLE
    # ========================================================

    muzzle_crop = image[
        y1:y2,
        x1:x2,
    ]

    if muzzle_crop.size == 0:

        print()
        print(
            "ERROR: Muzzle crop is empty."
        )

        print("=" * 70)

        raise ValueError(
            "Muzzle crop is empty."
        )

    # ========================================================
    # CROP INFORMATION
    # ========================================================

    crop_height, crop_width = (
        muzzle_crop.shape[:2]
    )

    print()
    print(
        "MUZZLE CROP"
    )

    print(
        f"  Coordinates: "
        f"[{x1}, {y1}, {x2}, {y2}]"
    )

    print(
        f"  Crop size  : "
        f"{crop_width} x {crop_height}"
    )

    print(
        f"  Area       : "
        f"{crop_width * crop_height} pixels"
    )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    print()
    print(
        "YOLO MUZZLE DETECTION SUCCESS"
    )

    print("=" * 70)
    print()

    return (
        muzzle_crop,
        float(confidence),
        [
            int(x1),
            int(y1),
            int(x2),
            int(y2),
        ],
    )


# ============================================================
# OPTIONAL: SAVE DEBUG MUZZLE
# ============================================================

def save_debug_muzzle(
    muzzle_crop,
    output_path,
):
    """
    Optional helper for debugging.

    Example:

        save_debug_muzzle(
            muzzle_crop,
            "debug_muzzle.jpg"
        )
    """

    if muzzle_crop is None:

        return False

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    success = cv2.imwrite(
        str(output_path),
        muzzle_crop,
    )

    return bool(success)


# ============================================================
# MODEL STATUS
# ============================================================

def get_model_status():

    return {
        "device": str(device),

        "cuda_available": bool(
            torch.cuda.is_available()
        ),

        "yolo_loaded": (
            yolo_model is not None
        ),

        "resnet_loaded": (
            resnet_model is not None
        ),

        "yolo_confidence": float(
            YOLO_CONFIDENCE
        ),

        "yolo_image_size": int(
            YOLO_IMAGE_SIZE
        ),

        "embedding_size": int(
            EMBEDDING_SIZE
        ),
    }