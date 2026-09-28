import sys
from pathlib import Path

import cv2
import faiss
import numpy as np
import torch

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    Depends,
)

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer


# ============================================================
# PATH SETUP
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent

# F:\python_RENET50_TRAIN\DATASET OF COW
PROJECT_DIR = CURRENT_DIR.parent

# F:\python_RENET50_TRAIN
ROOT_DIR = PROJECT_DIR.parent


# ============================================================
# IMPORT BACKEND SERVICES
# ============================================================

if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))


# Shared biometric pipeline
from biometric_service import (
    load_biometric_models,
    detect_muzzle,
    extract_embedding_with_pipeline,
    device,
)


# Authentication
from auth_service import get_user_from_token


# MongoDB
from mongodb_service import (
    get_user_registered_cows,
    log_identification,
)


# API routers
from auth_routes import router as auth_router
from dashboard_routes import router as dashboard_router
from cow_routes import router as cow_router


# ============================================================
# SETTINGS
# ============================================================

# Temporary threshold.
#
# This threshold should later be calibrated using:
# - known cow images
# - unknown cow images
#
# For now we use the previously tested threshold.
UNKNOWN_THRESHOLD = 0.5813

TOP_K = 5


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Moo-ID API",
    description="AI-powered biometric cow identification API",
    version="2.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Vercel production
        "https://mooid-biometric-cow-identification.vercel.app",
    ],

    # Allow Vercel preview deployments
    allow_origin_regex=r"^https://mooid-biometric-cow-identification-[a-z0-9-]+\.vercel\.app$",

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# AUTHENTICATION
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# INCLUDE ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(cow_router)

# Mount static directory for registered cow images
from fastapi.staticfiles import StaticFiles
REGISTERED_COW_IMAGES = CURRENT_DIR / "registered_cow_images"
REGISTERED_COW_IMAGES.mkdir(parents=True, exist_ok=True)
app.mount(
    "/registered_cow_images",
    StaticFiles(directory=str(REGISTERED_COW_IMAGES)),
    name="registered_cow_images"
)


# ============================================================
# GLOBAL STATUS
# ============================================================

biometric_models_loaded = False


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    global biometric_models_loaded

    print()
    print("=" * 70)
    print("MOO-ID BACKEND")
    print("=" * 70)

    print(f"Device: {device}")

    if torch.cuda.is_available():
        print(
            f"GPU: {torch.cuda.get_device_name(0)}"
        )

    print()
    print("Loading biometric models...")

    try:

        load_biometric_models()

        biometric_models_loaded = True

        print()
        print("Biometric models loaded successfully.")

    except Exception as e:

        biometric_models_loaded = False

        print()
        print("=" * 70)
        print("MODEL LOADING ERROR")
        print("=" * 70)

        print(
            f"Error type: {type(e).__name__}"
        )

        print(
            f"Error message: {str(e)}"
        )

        print("=" * 70)

        raise

    print("=" * 70)
    print("MOO-ID BACKEND READY")
    print("=" * 70)
    print()


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "success": True,
        "message": "Moo-ID API is running",
        "service": "AI Cow Biometric Identification",
        "version": "2.0.0",
        "device": str(device),
        "biometric_pipeline": [
            "Upload Image",
            "YOLOv8 Muzzle Detection",
            "Muzzle Cropping",
            "Grayscale",
            "CLAHE",
            "Gaussian Blur",
            "Sharpening",
            "Min-Max Normalization",
            "RGB Conversion",
            "Resize 224x224",
            "ImageNet Normalization",
            "ResNet50 Feature Extraction",
            "512-D Embedding",
            "L2 Normalization",
            "FAISS Cosine Similarity Search",
            "Known / Unknown Decision",
            "MongoDB User-Registered Cows",
        ],
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "device": str(device),
        "biometric_models_loaded": biometric_models_loaded,
    }


# ============================================================
# BUILD FAISS INDEX FROM REGISTERED COWS
# ============================================================

def build_registered_cow_faiss(
    registered_cows
):
    """
    Build a FAISS cosine-similarity index from
    embeddings stored in MongoDB.

    Each MongoDB document contains:

        cow_id
        cow_name
        user_id
        embedding
        embedding_dimension

    Returns:

        index
        metadata
    """

    valid_embeddings = []
    metadata = []

    for cow in registered_cows:

        embedding = cow.get("embedding")

        if embedding is None:
            continue

        try:

            vector = np.asarray(
                embedding,
                dtype=np.float32,
            )

        except Exception:

            continue

        if vector.size == 0:
            continue

        # Flatten to one-dimensional vector
        vector = vector.reshape(-1)

        # Make sure it has the expected dimension
        if vector.shape[0] != 512:
            print(
                f"Skipping {cow.get('cow_id')}: "
                f"embedding dimension is {vector.shape[0]}"
            )
            continue

        valid_embeddings.append(vector)

        metadata.append(cow)

    # No valid registered cows
    if not valid_embeddings:

        return None, []

    # Convert to matrix
    vectors = np.asarray(
        valid_embeddings,
        dtype=np.float32,
    )

    # Normalize for cosine similarity
    faiss.normalize_L2(vectors)

    # Inner Product on normalized vectors
    # = cosine similarity
    index = faiss.IndexFlatIP(
        vectors.shape[1]
    )

    index.add(vectors)

    return index, metadata


# ============================================================
# RECOGNIZE REGISTERED COW
# ============================================================

def recognize_registered_cow(
    embedding,
    user_id,
):
    """
    Compare the uploaded cow embedding against
    only the cows registered by the current user.

    Pipeline:

        MongoDB
           ↓
        registered_cows
           ↓
        embeddings
           ↓
        FAISS IndexFlatIP
           ↓
        cosine similarity
           ↓
        KNOWN / UNKNOWN
    """

    # --------------------------------------------------------
    # GET USER'S REGISTERED COWS
    # --------------------------------------------------------

    registered_cows = get_user_registered_cows(
        user_id
    )

    if registered_cows is None:
        registered_cows = []

    registered_cows = list(
        registered_cows
    )

    print()
    print(
        f"Registered cows for {user_id}: "
        f"{len(registered_cows)}"
    )

    # --------------------------------------------------------
    # NO REGISTERED COWS
    # --------------------------------------------------------

    if len(registered_cows) == 0:

        return {
            "result": "UNKNOWN",
            "cow_id": None,
            "cow_name": None,
            "similarity": 0.0,
            "matches": [],
        }

    # --------------------------------------------------------
    # BUILD FAISS
    # --------------------------------------------------------

    index, metadata = build_registered_cow_faiss(
        registered_cows
    )

    if index is None or index.ntotal == 0:

        return {
            "result": "UNKNOWN",
            "cow_id": None,
            "cow_name": None,
            "similarity": 0.0,
            "matches": [],
        }

    # --------------------------------------------------------
    # PREPARE QUERY EMBEDDING
    # --------------------------------------------------------

    query = np.asarray(
        embedding,
        dtype=np.float32,
    )

    query = query.reshape(1, -1)

    faiss.normalize_L2(query)

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search_k = min(
        TOP_K,
        index.ntotal,
    )

    distances, indices = index.search(
        query,
        search_k,
    )

    matches = []

    # --------------------------------------------------------
    # BUILD TOP MATCHES
    # --------------------------------------------------------

    for rank in range(search_k):

        index_position = int(
            indices[0][rank]
        )

        similarity = float(
            distances[0][rank]
        )

        if index_position < 0:
            continue

        if index_position >= len(metadata):
            continue

        cow = metadata[index_position]

        cow_id = cow.get(
            "cow_id"
        )

        cow_name = cow.get(
            "cow_name",
            "",
        )

        matches.append(
            {
                "rank": int(rank + 1),

                "cow_id": (
                    str(cow_id)
                    if cow_id is not None
                    else None
                ),

                "cow_name": (
                    str(cow_name)
                    if cow_name is not None
                    else ""
                ),

                "similarity": float(
                    round(
                        similarity,
                        4,
                    )
                ),

                "similarity_percentage": float(
                    round(
                        similarity * 100,
                        2,
                    )
                ),
            }
        )

    # --------------------------------------------------------
    # NO MATCH
    # --------------------------------------------------------

    if not matches:

        return {
            "result": "UNKNOWN",
            "cow_id": None,
            "cow_name": None,
            "similarity": 0.0,
            "matches": [],
        }

    # --------------------------------------------------------
    # BEST MATCH
    # --------------------------------------------------------

    best_match = matches[0]

    best_similarity = float(
        best_match["similarity"]
    )

    # --------------------------------------------------------
    # KNOWN / UNKNOWN
    # --------------------------------------------------------

    if best_similarity >= UNKNOWN_THRESHOLD:

        result = "KNOWN"

        cow_id = best_match[
            "cow_id"
        ]

        cow_name = best_match[
            "cow_name"
        ]

    else:

        result = "UNKNOWN"

        cow_id = None

        cow_name = None

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("REGISTERED COW RECOGNITION")
    print("-" * 70)

    print(
        f"User ID: {user_id}"
    )

    print(
        f"Result: {result}"
    )

    print(
        f"Best Cow: {cow_id}"
    )

    print(
        f"Best Similarity: {best_similarity:.4f}"
    )

    print(
        f"Threshold: {UNKNOWN_THRESHOLD:.4f}"
    )

    print("-" * 70)

    return {
        "result": result,
        "cow_id": cow_id,
        "cow_name": cow_name,
        "similarity": best_similarity,
        "matches": matches,
    }


# ============================================================
# JSON SAFE CONVERTER
# ============================================================

def make_json_safe(value):

    # --------------------------------------------------------
    # NumPy scalar
    # --------------------------------------------------------

    if isinstance(
        value,
        np.generic,
    ):

        return value.item()

    # --------------------------------------------------------
    # NumPy array
    # --------------------------------------------------------

    if isinstance(
        value,
        np.ndarray,
    ):

        return value.tolist()

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(
        value,
        dict,
    ):

        return {
            str(key): make_json_safe(
                val
            )
            for key, val in value.items()
        }

    # --------------------------------------------------------
    # List
    # --------------------------------------------------------

    if isinstance(
        value,
        list,
    ):

        return [
            make_json_safe(item)
            for item in value
        ]

    # --------------------------------------------------------
    # Tuple
    # --------------------------------------------------------

    if isinstance(
        value,
        tuple,
    ):

        return [
            make_json_safe(item)
            for item in value
        ]

    # --------------------------------------------------------
    # Normal value
    # --------------------------------------------------------

    return value


# ============================================================
# IDENTIFY COW
# ============================================================

@app.post("/identify")
async def identify_cow(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
):

    # ========================================================
    # AUTHENTICATE USER
    # ========================================================

    user = get_user_from_token(
        token
    )

    user_id = user["user_id"]

    # ========================================================
    # VALIDATE FILE
    # ========================================================

    if not file.content_type:

        raise HTTPException(
            status_code=400,
            detail=(
                "File type could not be determined."
            ),
        )

    allowed_types = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image format. "
                "Use JPG, PNG, or WEBP."
            ),
        )

    # ========================================================
    # CHECK MODELS
    # ========================================================

    if not biometric_models_loaded:

        raise HTTPException(
            status_code=503,
            detail=(
                "Biometric models are not loaded."
            ),
        )

    try:

        # ====================================================
        # READ IMAGE
        # ====================================================

        image_bytes = await file.read()

        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Uploaded image is empty."
                ),
            )

        # ====================================================
        # BYTES → NUMPY
        # ====================================================

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        # ====================================================
        # NUMPY → OPENCV IMAGE
        # ====================================================

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )

        if image is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not read uploaded image."
                ),
            )

        # ====================================================
        # YOLO MUZZLE DETECTION
        # ====================================================

        (
            muzzle_crop,
            yolo_confidence,
            bbox,
        ) = detect_muzzle(
            image
        )

        # ====================================================
        # RESNET50 EMBEDDING
        # ====================================================

        (
            embedding,
            embedding_pipeline,
        ) = extract_embedding_with_pipeline(
            muzzle_crop
        )

        # ====================================================
        # REGISTERED COW FAISS SEARCH
        # ========================================================

        recognition = recognize_registered_cow(
            embedding,
            user_id,
        )

        # ====================================================
        # LOG IDENTIFICATION
        # ====================================================

        try:

            log_identification(
                user_id=user_id,
                cow_id=recognition["cow_id"],
                result=recognition["result"],
                similarity=recognition["similarity"],
                yolo_confidence=yolo_confidence,
                source="web",
            )

        except Exception as log_error:

            print(
                "Warning: Could not save "
                f"identification log: {log_error}"
            )
        # ====================================================
        # BUILD RESPONSE
        # ====================================================

        response_data = {

            "success": True,

            "filename": (
                str(file.filename)
                if file.filename
                else "uploaded_image"
            ),

            # Current logged-in user
            "user_id": str(
                user_id
            ),

            # KNOWN / UNKNOWN
            "result": str(
                recognition["result"]
            ),

            # Registered cow ID
            "cow_id": (
                str(
                    recognition["cow_id"]
                )
                if recognition["cow_id"]
                is not None
                else None
            ),

            # Registered cow name
            "cow_name": (
                str(
                    recognition["cow_name"]
                )
                if recognition["cow_name"]
                is not None
                else None
            ),

            # Best similarity
            "similarity": float(
                recognition["similarity"]
            ),

            "similarity_percentage": float(
                round(
                    float(
                        recognition["similarity"]
                    ) * 100,
                    2,
                )
            ),

            # Threshold used
            "unknown_threshold": float(
                UNKNOWN_THRESHOLD
            ),

            # YOLO confidence
            "yolo_confidence": float(
                yolo_confidence
            ),

            "yolo_confidence_percentage": float(
                round(
                    float(
                        yolo_confidence
                    ) * 100,
                    2,
                )
            ),

            # YOLO bounding box
            "muzzle_box": {
                "x1": int(
                    bbox[0]
                ),
                "y1": int(
                    bbox[1]
                ),
                "x2": int(
                    bbox[2]
                ),
                "y2": int(
                    bbox[3]
                ),
            },

            # Top matches
            "top_matches": (
                recognition["matches"]
            ),
            "pipeline": {
                "input_image": "completed",
                "yolo_muzzle_detection": "completed",
                "muzzle_crop": "completed",
                "preprocessing": {
                    "grayscale": "completed" if embedding_pipeline["grayscale"] else "failed",
                    "clahe": "completed" if embedding_pipeline["clahe"] else "failed",
                    "sharpening": "completed" if embedding_pipeline["sharpening"] else "failed",
                    "min_max_normalization": "completed" if embedding_pipeline["min_max_normalization"] else "failed",
                    "rgb_conversion": "completed" if embedding_pipeline["rgb_conversion"] else "failed",
                    "resize_224x224": "completed" if embedding_pipeline["resize_224x224"] else "failed",
                    "imagenet_normalization": "completed" if embedding_pipeline["imagenet_normalization"] else "failed"
                },
                "resnet50": {
                    "status": "completed" if embedding_pipeline["resnet50"] else "failed",
                    "embedding_dimension": int(embedding_pipeline["embedding_dimension"])
                },
                "l2_normalization": "completed" if embedding_pipeline["l2_normalization"] else "failed",
                "faiss_search": "completed",
                "final_decision": str(recognition["result"])
            }
        }

        # ====================================================
        # JSON SAFE
        # ====================================================

        safe_response = make_json_safe(
            response_data
        )

        # ====================================================
        # RETURN
        # ====================================================

        return JSONResponse(
            content=safe_response
        )

    # ========================================================
    # FASTAPI ERROR
    # ========================================================

    except HTTPException:
        raise

    # ========================================================
    # OTHER ERROR
    # ========================================================

    except Exception as e:

        print()
        print("=" * 70)
        print("IDENTIFICATION ERROR")
        print("=" * 70)

        print(
            f"User ID: {user_id}"
        )

        print(
            f"Error type: {type(e).__name__}"
        )

        print(
            f"Error message: {str(e)}"
        )

        print("=" * 70)
        print()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Identification failed: {str(e)}"
            ),
        )


# ============================================================
# DEVELOPMENT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )