import sys
import time
from pathlib import Path

import cv2
import faiss
import numpy as np
import torch
from ultralytics import YOLO


# ============================================================
# PATH CONFIGURATION
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
ROOT_DIR = PROJECT_DIR.parent
MODEL_DIR = PROJECT_DIR / "models"


# ============================================================
# YOLOv8 MUZZLE DETECTOR
# ============================================================

YOLO_PATH = (
    ROOT_DIR
    / "runs"
    / "detect"
    / "train-2"
    / "weights"
    / "best.pt"
)


# ============================================================
# NEW 24-COW RESNET50 + ARCFACE MODEL
# ============================================================

RESNET_PATH = (
    MODEL_DIR
    / "best_resnet50_arcface_24c_yolo_texture.pth"
)


# ============================================================
# NEW 24-COW FAISS GALLERY
# ============================================================

FAISS_PATH = (
    MODEL_DIR
    / "cow_24_yolo_texture_train.faiss"
)


# ============================================================
# COW LABELS
# ============================================================

LABELS_PATH = (
    MODEL_DIR
    / "cow_24_yolo_texture_train_labels.npy"
)


# ============================================================
# TRAINING IMAGE PATHS
# ============================================================

IMAGE_PATHS_PATH = (
    MODEL_DIR
    / "cow_24_yolo_texture_train_paths.npy"
)


# ============================================================
# SETTINGS
# ============================================================

YOLO_CONFIDENCE = 0.25
YOLO_IMAGE_SIZE = 640

# Run recognition every N frames
#
# 1 = every frame
# 3 = every 3rd frame
# 5 = every 5th frame
#
RECOGNITION_INTERVAL = 3


# ============================================================
# UNKNOWN THRESHOLD
# ============================================================
#
# IMPORTANT:
# This is the threshold currently being used by the
# full-image recognition system.
#
# It should eventually be calibrated using real
# known and unknown cow images.
#
UNKNOWN_THRESHOLD = 0.50


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# IMPORT EXISTING RESNET50 MODEL
# ============================================================

if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from model import ResNet50Embedding


# ============================================================
# START
# ============================================================

print("=" * 70)
print("MOO-ID REAL-TIME COW RECOGNITION")
print("=" * 70)

print(
    f"Device: {device}"
)

if torch.cuda.is_available():

    print(
        f"GPU: {torch.cuda.get_device_name(0)}"
    )

    print(
        f"CUDA version: {torch.version.cuda}"
    )


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

print("\nChecking required model files...")

required_files = {

    "YOLOv8": YOLO_PATH,

    "ResNet50": RESNET_PATH,

    "FAISS": FAISS_PATH,

    "Labels": LABELS_PATH,

    "Image paths": IMAGE_PATHS_PATH,
}


for name, path in required_files.items():

    if not path.exists():

        print(
            f"\nERROR: {name} file not found:"
        )

        print(path)

        sys.exit(1)

    print(
        f"✓ {name}: {path}"
    )


# ============================================================
# LOAD YOLO
# ============================================================

print("\nLoading YOLOv8 muzzle detector...")

yolo_model = YOLO(
    str(YOLO_PATH)
)

print(
    f"YOLO classes: {yolo_model.names}"
)


# ============================================================
# LOAD RESNET50
# ============================================================

print("\nLoading ResNet50...")

checkpoint = torch.load(
    RESNET_PATH,
    map_location=device,
    weights_only=False
)


# ============================================================
# READ EMBEDDING SIZE
# ============================================================

if isinstance(checkpoint, dict):

    if "embedding_size" in checkpoint:

        embedding_size = checkpoint[
            "embedding_size"
        ]

    else:

        embedding_size = 512

else:

    embedding_size = 512


print(
    f"Embedding size: {embedding_size}"
)


# ============================================================
# CREATE RESNET50
# ============================================================

resnet_model = ResNet50Embedding(
    embedding_size=embedding_size
)


# ============================================================
# LOAD CHECKPOINT
# ============================================================

if (
    isinstance(checkpoint, dict)
    and "model_state_dict" in checkpoint
):

    resnet_model.load_state_dict(
        checkpoint["model_state_dict"]
    )

elif (
    isinstance(checkpoint, dict)
    and "state_dict" in checkpoint
):

    resnet_model.load_state_dict(
        checkpoint["state_dict"]
    )

else:

    resnet_model.load_state_dict(
        checkpoint
    )


# ============================================================
# MOVE MODEL TO GPU / CPU
# ============================================================

resnet_model = resnet_model.to(
    device
)

resnet_model.eval()

print(
    "✓ ResNet50 loaded"
)


# ============================================================
# LOAD FAISS
# ============================================================

print("\nLoading FAISS gallery...")

index = faiss.read_index(
    str(FAISS_PATH)
)


# ============================================================
# LOAD LABELS
# ============================================================

labels = np.load(
    LABELS_PATH
)


# ============================================================
# LOAD IMAGE PATHS
# ============================================================

image_paths = np.load(
    IMAGE_PATHS_PATH,
    allow_pickle=True
)


print(
    f"✓ FAISS vectors: {index.ntotal}"
)

print(
    f"✓ Embedding dimension: {index.d}"
)


# ============================================================
# OPEN WEBCAM
# ============================================================

print("\nOpening webcam...")

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print(
        "ERROR: Could not open webcam."
    )

    sys.exit(1)


# ============================================================
# CAMERA SETTINGS
# ============================================================

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)


# ============================================================
# WINDOW
# ============================================================

window_name = (
    "Moo-ID Real-Time Cow Recognition"
)


cv2.namedWindow(
    window_name,
    cv2.WINDOW_NORMAL
)


# ============================================================
# VARIABLES
# ============================================================

frame_count = 0

last_cow_id = None

last_similarity = 0.0

last_yolo_confidence = 0.0

last_top_matches = []

status = "SEARCHING..."

last_recognition_time = 0

recognition_time_ms = 0

last_margin = 0.0

last_second_cow = None

last_second_similarity = 0.0


# ============================================================
# FPS VARIABLES
# ============================================================

fps = 0.0

fps_counter = 0

fps_start_time = time.time()


# ============================================================
# MAIN WEBCAM LOOP
# ============================================================

print("\n")
print("=" * 70)
print("WEBCAM STARTED")
print("=" * 70)

print(
    "Show a cow muzzle to the camera."
)

print(
    "YOLO will detect the muzzle."
)

print(
    "The muzzle will be converted to grayscale "
    "using OpenCV before ResNet50."
)

print(
    "Press Q or close the window to exit."
)

print("=" * 70)


while True:

    # ========================================================
    # READ FRAME
    # ========================================================

    ret, frame = cap.read()


    if not ret:

        print(
            "\nERROR: Could not read webcam frame."
        )

        break


    frame_count += 1

    fps_counter += 1


    # ========================================================
    # CALCULATE FPS
    # ========================================================

    elapsed = (
        time.time()
        - fps_start_time
    )


    if elapsed >= 1.0:

        fps = (
            fps_counter
            / elapsed
        )

        fps_counter = 0

        fps_start_time = (
            time.time()
        )


    # ========================================================
    # YOLO MUZZLE DETECTION
    # ========================================================

    results = yolo_model.predict(

        source=frame,

        conf=YOLO_CONFIDENCE,

        imgsz=YOLO_IMAGE_SIZE,

        device=(
            0
            if torch.cuda.is_available()
            else "cpu"
        ),

        verbose=False
    )


    result = results[0]


    detected_muzzle = False

    best_confidence = 0.0

    x1 = y1 = x2 = y2 = 0


    # ========================================================
    # CHECK YOLO DETECTIONS
    # ========================================================

    if (

        result.boxes is not None

        and len(result.boxes) > 0

    ):

        # ----------------------------------------------------
        # SELECT HIGHEST CONFIDENCE MUZZLE
        # ----------------------------------------------------

        best_box_index = int(

            torch.argmax(
                result.boxes.conf
            ).item()

        )


        best_confidence = float(

            result.boxes.conf[
                best_box_index
            ].item()

        )


        box = (

            result.boxes.xyxy[
                best_box_index
            ]

            .cpu()

            .numpy()

        )


        x1, y1, x2, y2 = map(
            int,
            box
        )


        # ----------------------------------------------------
        # IMAGE DIMENSIONS
        # ----------------------------------------------------

        image_height, image_width = (
            frame.shape[:2]
        )


        # ----------------------------------------------------
        # CLAMP BOX
        # ----------------------------------------------------

        x1 = max(
            0,
            min(
                x1,
                image_width - 1
            )
        )


        y1 = max(
            0,
            min(
                y1,
                image_height - 1
            )
        )


        x2 = max(
            x1 + 1,
            min(
                x2,
                image_width
            )
        )


        y2 = max(
            y1 + 1,
            min(
                y2,
                image_height
            )
        )


        detected_muzzle = True


        last_yolo_confidence = (
            best_confidence
        )


        # ====================================================
        # DRAW MUZZLE BOX
        # ====================================================

        cv2.rectangle(

            frame,

            (x1, y1),

            (x2, y2),

            (0, 255, 0),

            3
        )


        # ====================================================
        # YOLO LABEL
        # ====================================================

        yolo_label = (

            f"Muzzle "
            f"{best_confidence:.2f}"

        )


        cv2.putText(

            frame,

            yolo_label,

            (
                x1,
                max(
                    y1 - 10,
                    30
                )
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0, 255, 0),

            2,

            cv2.LINE_AA
        )


        # ====================================================
        # RUN RESNET + FAISS
        # ====================================================

        if (

            frame_count
            % RECOGNITION_INTERVAL
            == 0

        ):

            recognition_start = (
                time.time()
            )


            # ------------------------------------------------
            # CROP MUZZLE
            # ------------------------------------------------

            muzzle_crop_bgr = frame[
                y1:y2,
                x1:x2
            ]


            if (
                muzzle_crop_bgr.size
                > 0
            ):

                try:

                    # ========================================
                    # STEP 1
                    # BGR → GRAYSCALE
                    # ========================================

                    gray = cv2.cvtColor(

                        muzzle_crop_bgr,

                        cv2.COLOR_BGR2GRAY

                    )


                    # ========================================
                    # STEP 2
                    # CLAHE
                    # ========================================

                    clahe = cv2.createCLAHE(

                        clipLimit=2.0,

                        tileGridSize=(8, 8)

                    )


                    enhanced = clahe.apply(
                        gray
                    )


                    # ========================================
                    # STEP 3
                    # SHARPENING
                    # ========================================

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


                    # ========================================
                    # STEP 4
                    # NORMALIZATION
                    # ========================================

                    normalized = cv2.normalize(

                        sharpened,

                        None,

                        0,

                        255,

                        cv2.NORM_MINMAX

                    )


                    # ========================================
                    # STEP 5
                    # GRAYSCALE → RGB
                    #
                    # ResNet50 requires 3 channels.
                    # ========================================

                    muzzle_rgb = cv2.cvtColor(

                        normalized,

                        cv2.COLOR_GRAY2RGB

                    )


                    # ========================================
                    # STEP 6
                    # RESIZE 224 × 224
                    # ========================================

                    muzzle_rgb = cv2.resize(

                        muzzle_rgb,

                        (224, 224),

                        interpolation=cv2.INTER_AREA

                    )


                    # ========================================
                    # STEP 7
                    # NUMPY → PYTORCH
                    # ========================================

                    image_tensor = (
                        torch.from_numpy(
                            muzzle_rgb
                        )
                        .permute(
                            2,
                            0,
                            1
                        )
                        .float()
                        / 255.0
                    )


                    # ========================================
                    # STEP 8
                    # IMAGENET NORMALIZATION
                    # ========================================

                    mean = torch.tensor(

                        [
                            0.485,
                            0.456,
                            0.406
                        ]

                    ).view(
                        3,
                        1,
                        1
                    )


                    std = torch.tensor(

                        [
                            0.229,
                            0.224,
                            0.225
                        ]

                    ).view(
                        3,
                        1,
                        1
                    )


                    image_tensor = (

                        image_tensor
                        - mean

                    ) / std


                    # ========================================
                    # STEP 9
                    # ADD BATCH DIMENSION
                    # ========================================

                    image_tensor = (

                        image_tensor

                        .unsqueeze(0)

                        .to(device)

                    )


                    # ========================================
                    # STEP 10
                    # RESNET50 EMBEDDING
                    # ========================================

                    with torch.no_grad():

                        embedding = (
                            resnet_model(
                                image_tensor
                            )
                        )


                        embedding = (

                            embedding

                            .cpu()

                            .numpy()

                            .astype(
                                np.float32
                            )

                        )


                    # ========================================
                    # STEP 11
                    # NORMALIZE EMBEDDING
                    # ========================================

                    faiss.normalize_L2(
                        embedding
                    )


                    # ========================================
                    # STEP 12
                    # FAISS TOP 5 SEARCH
                    # ========================================

                    distances, indices = (

                        index.search(

                            embedding,

                            5

                        )

                    )


                    # ========================================
                    # TOP 1 MATCH
                    # ========================================

                    best_similarity = float(

                        distances[0][0]

                    )


                    best_index = int(

                        indices[0][0]

                    )


                    predicted_cow = (

                        int(

                            labels[
                                best_index
                            ]

                        )

                        + 1

                    )


                    # ========================================
                    # FIND SECOND DIFFERENT COW
                    # ========================================

                    second_cow = None

                    second_similarity = None


                    for rank in range(1, 5):

                        match_index = int(

                            indices[0][rank]

                        )


                        match_cow = (

                            int(

                                labels[
                                    match_index
                                ]

                            )

                            + 1

                        )


                        match_similarity = float(

                            distances[0][rank]

                        )


                        if (
                            match_cow
                            != predicted_cow
                        ):

                            second_cow = (
                                match_cow
                            )

                            second_similarity = (
                                match_similarity
                            )

                            break


                    # ========================================
                    # CALCULATE MARGIN
                    # ========================================

                    if (
                        second_similarity
                        is not None
                    ):

                        margin = (

                            best_similarity
                            - second_similarity

                        )

                    else:

                        margin = 0.0


                    # ========================================
                    # SAVE RESULT
                    # ========================================

                    last_cow_id = (
                        predicted_cow
                    )

                    last_similarity = (
                        best_similarity
                    )

                    last_second_cow = (
                        second_cow
                    )

                    last_second_similarity = (

                        second_similarity

                        if second_similarity
                        is not None

                        else 0.0

                    )

                    last_margin = (
                        margin
                    )


                    # ========================================
                    # SAVE TOP 5
                    # ========================================

                    last_top_matches = []


                    for rank in range(5):

                        match_index = int(

                            indices[0][rank]

                        )


                        match_similarity = float(

                            distances[0][rank]

                        )


                        match_cow = (

                            int(

                                labels[
                                    match_index
                                ]

                            )

                            + 1

                        )


                        last_top_matches.append(

                            (
                                match_cow,
                                match_similarity
                            )

                        )


                    # ========================================
                    # KNOWN / UNKNOWN DECISION
                    # ========================================

                    if (
                        best_similarity
                        >= UNKNOWN_THRESHOLD
                    ):

                        status = (
                            "KNOWN COW"
                        )

                    else:

                        status = (
                            "UNKNOWN COW"
                        )


                    # ========================================
                    # RECOGNITION TIME
                    # ========================================

                    recognition_time_ms = (

                        (
                            time.time()
                            - recognition_start
                        )

                        * 1000

                    )


                    # ========================================
                    # TERMINAL OUTPUT
                    # ========================================

                    print()

                    print(
                        "-" * 70
                    )

                    print(
                        "REAL-TIME RECOGNITION"
                    )

                    print(
                        f"YOLO Confidence: "
                        f"{best_confidence:.4f}"
                    )

                    print(
                        f"Top Cow: "
                        f"Cow {predicted_cow}"
                    )

                    print(
                        f"Top Similarity: "
                        f"{best_similarity:.4f}"
                    )


                    if second_cow is not None:

                        print(
                            f"Second Different Cow: "
                            f"Cow {second_cow}"
                        )

                        print(
                            f"Second Similarity: "
                            f"{second_similarity:.4f}"
                        )

                    else:

                        print(
                            "Second Different Cow: N/A"
                        )


                    print(
                        f"Margin: "
                        f"{margin:.4f}"
                    )

                    print(
                        f"Threshold: "
                        f"{UNKNOWN_THRESHOLD:.4f}"
                    )

                    print(
                        f"Final Result: "
                        f"{status}"
                    )

                    print(
                        f"Recognition Time: "
                        f"{recognition_time_ms:.1f} ms"
                    )


                    print(
                        "\nTop 5 Matches:"
                    )


                    for rank, (
                        cow,
                        similarity
                    ) in enumerate(

                        last_top_matches,

                        start=1

                    ):

                        print(

                            f"{rank}. "
                            f"Cow {cow} | "
                            f"Similarity: "
                            f"{similarity:.4f}"

                        )


                    print(
                        "-" * 70
                    )


                except Exception as e:

                    print(
                        f"\nRecognition error: {e}"
                    )

                    status = (
                        "RECOGNITION ERROR"
                    )


    else:

        # ====================================================
        # NO MUZZLE DETECTED
        # ====================================================

        last_yolo_confidence = 0.0

        status = (
            "MUZZLE NOT DETECTED"
        )


    # ========================================================
    # INFORMATION PANEL
    # ========================================================

    panel_x = 20

    panel_y = 35


    # --------------------------------------------------------
    # FPS
    # --------------------------------------------------------

    cv2.putText(

        frame,

        f"FPS: {fps:.1f}",

        (
            panel_x,
            panel_y
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (255, 255, 255),

        2,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # YOLO CONFIDENCE
    # --------------------------------------------------------

    cv2.putText(

        frame,

        (
            f"YOLO Confidence: "
            f"{last_yolo_confidence:.3f}"
        ),

        (
            panel_x,
            panel_y + 35
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (255, 255, 255),

        2,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # COW ID
    # --------------------------------------------------------

    if last_cow_id is not None:

        if status == "UNKNOWN COW":

            cow_text = (
                "Cow ID: UNKNOWN"
            )

        else:

            cow_text = (
                f"Cow ID: "
                f"{last_cow_id}"
            )

    else:

        cow_text = (
            "Cow ID: ---"
        )


    cv2.putText(

        frame,

        cow_text,

        (
            panel_x,
            panel_y + 75
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.0,

        (0, 255, 255),

        3,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # SIMILARITY
    # --------------------------------------------------------

    cv2.putText(

        frame,

        (
            f"Similarity: "
            f"{last_similarity:.4f}"
        ),

        (
            panel_x,
            panel_y + 115
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (255, 255, 255),

        2,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # MARGIN
    # --------------------------------------------------------

    cv2.putText(

        frame,

        (
            f"Margin: "
            f"{last_margin:.4f}"
        ),

        (
            panel_x,
            panel_y + 150
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (255, 255, 255),

        2,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    cv2.putText(

        frame,

        (
            f"Status: "
            f"{status}"
        ),

        (
            panel_x,
            panel_y + 190
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (255, 255, 255),

        2,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # RECOGNITION TIME
    # --------------------------------------------------------

    cv2.putText(

        frame,

        (
            f"Recognition: "
            f"{recognition_time_ms:.1f} ms"
        ),

        (
            panel_x,
            panel_y + 230
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (255, 255, 255),

        2,

        cv2.LINE_AA

    )


    # ========================================================
    # SHOW TOP MATCHES
    # ========================================================

    if len(last_top_matches) > 0:

        top_y = (
            frame.shape[0] - 160
        )


        cv2.putText(

            frame,

            "Top FAISS Matches:",

            (
                20,
                top_y
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2,

            cv2.LINE_AA

        )


        for i, (
            cow,
            similarity
        ) in enumerate(
            last_top_matches
        ):

            text = (

                f"{i + 1}. "
                f"Cow {cow}  "
                f"{similarity:.4f}"

            )


            cv2.putText(

                frame,

                text,

                (
                    20,
                    top_y
                    + 30
                    + i * 25
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 255, 255),

                2,

                cv2.LINE_AA

            )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(

        window_name,

        frame

    )


    # ========================================================
    # KEYBOARD EXIT
    # ========================================================

    key = (

        cv2.waitKey(1)
        & 0xFF

    )


    if (

        key == ord("q")

        or key == ord("Q")

    ):

        print(
            "\nQ pressed."
        )

        break


    # ========================================================
    # WINDOW X BUTTON EXIT
    # ========================================================

    if (

        cv2.getWindowProperty(

            window_name,

            cv2.WND_PROP_VISIBLE

        )

        < 1

    ):

        print(
            "\nWindow closed."
        )

        break


# ============================================================
# CLEANUP
# ============================================================

print(
    "\nStopping webcam..."
)


cap.release()


cv2.destroyAllWindows()


cv2.waitKey(1)


print(
    "Webcam released successfully."
)


print(
    "Moo-ID real-time recognition stopped."
)


print("=" * 70)