from pathlib import Path
import uuid

import cv2
import numpy as np

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from auth_service import (
    get_user_from_token
)

from mongodb_service import (
    register_cow,
    get_registered_cow,
    get_user_registered_cows,
)

from biometric_service import (
    detect_muzzle,
    extract_embedding,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/cows",
    tags=["Registered Cows"]
)


# ============================================================
# AUTH
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# IMAGE DIRECTORY
# ============================================================

CURRENT_DIR = Path(
    __file__
).resolve().parent

REGISTERED_COW_IMAGES = (
    CURRENT_DIR /
    "registered_cow_images"
)

REGISTERED_COW_IMAGES.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# REGISTER COW
# ============================================================

@router.post("/register")
async def register_new_cow(

    cow_id: str = Form(...),

    cow_name: str = Form(...),

    owner_name: str = Form(...),

    owner_phone: str = Form(...),

    owner_address: str = Form(...),

    file: UploadFile = File(...),

    token: str = Depends(
        oauth2_scheme
    ),
):

    # ========================================================
    # CURRENT USER
    # ========================================================

    user = get_user_from_token(
        token
    )

    user_id = user[
        "user_id"
    ]

    # ========================================================
    # CLEAN INPUT
    # ========================================================

    cow_id = cow_id.strip()

    cow_name = cow_name.strip()

    owner_name = owner_name.strip()

    owner_phone = owner_phone.strip()

    owner_address = (
        owner_address.strip()
    )

    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    if not cow_id:
        raise HTTPException(
            status_code=400,
            detail="Cow ID is required."
        )

    if not cow_name:
        raise HTTPException(
            status_code=400,
            detail="Cow name is required."
        )

    if not owner_name:
        raise HTTPException(
            status_code=400,
            detail="Owner name is required."
        )

    if not owner_phone:
        raise HTTPException(
            status_code=400,
            detail="Owner phone is required."
        )

    if not owner_address:
        raise HTTPException(
            status_code=400,
            detail="Owner address is required."
        )

    # ========================================================
    # IMAGE VALIDATION
    # ========================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Cow image is required."
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    extension = (
        Path(
            file.filename
        ).suffix.lower()
    )

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image format. "
                "Use JPG, JPEG, PNG or WEBP."
            )
        )

    # ========================================================
    # DUPLICATE COW ID
    # ========================================================

    existing_cow = get_registered_cow(
        cow_id
    )

    if existing_cow:

        raise HTTPException(
            status_code=409,
            detail=(
                f"Cow ID '{cow_id}' "
                "is already registered."
            )
        )

    # ========================================================
    # READ IMAGE
    # ========================================================

    image_bytes = await file.read()

    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    # ========================================================
    # IMAGE SIZE LIMIT
    # ========================================================

    max_size = (
        10 * 1024 * 1024
    )

    if len(image_bytes) > max_size:

        raise HTTPException(
            status_code=400,
            detail=(
                "Image size must be less than 10 MB."
            )
        )

    # ========================================================
    # DECODE IMAGE
    # ========================================================

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:

        raise HTTPException(
            status_code=400,
            detail="Could not read uploaded image."
        )

    # ========================================================
    # YOLO MUZZLE DETECTION
    # ========================================================

    try:

        (
            muzzle_crop,
            yolo_confidence,
            bbox,
        ) = detect_muzzle(
            image
        )

    except Exception as error:

        raise HTTPException(
            status_code=422,
            detail=(
                "Muzzle detection failed: "
                f"{str(error)}"
            )
        )

    # ========================================================
    # RESNET50 EMBEDDING
    # ========================================================

    try:

        embedding = extract_embedding(
            muzzle_crop
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "ResNet50 feature extraction failed: "
                f"{str(error)}"
            )
        )

    # ========================================================
    # SAVE ORIGINAL IMAGE
    # ========================================================

    unique_filename = (
        f"{cow_id}_"
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    image_path = (
        REGISTERED_COW_IMAGES /
        unique_filename
    )

    try:

        with open(
            image_path,
            "wb"
        ) as image_file:

            image_file.write(
                image_bytes
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save image: "
                f"{str(error)}"
            )
        )

    # ========================================================
    # SAVE REGISTERED COW
    # ========================================================

    try:

        inserted_id = register_cow(

            cow_id=cow_id,

            cow_name=cow_name,

            owner_name=owner_name,

            owner_phone=owner_phone,

            owner_address=owner_address,

            user_id=user_id,

            image_path=str(
                image_path
            ),

            embedding=embedding,
        )

    except ValueError as error:

        if image_path.exists():
            image_path.unlink()

        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    except Exception as error:

        if image_path.exists():
            image_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save cow: "
                f"{str(error)}"
            )
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "success": True,

        "message": (
            "Cow registered successfully "
            "with biometric embedding."
        ),

        "cow": {

            "cow_id": cow_id,

            "cow_name": cow_name,

            "user_id": user_id,

            "yolo_confidence":
                round(
                    float(
                        yolo_confidence
                    ),
                    4
                ),

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

            "embedding_dimension":
                int(
                    embedding.shape[-1]
                ),
        },

        "registered_id": str(
            inserted_id
        ),
    }


# ============================================================
# GET MY COWS
# ============================================================

@router.get("/my-cows")
def get_my_cows(token: str = Depends(oauth2_scheme)):

    # --------------------------------------------------------
    # CURRENT USER
    # --------------------------------------------------------

    user = get_user_from_token(token)

    user_id = user["user_id"]

    # --------------------------------------------------------
    # GET USER'S REGISTERED COWS
    # --------------------------------------------------------

    cows = get_user_registered_cows(user_id)

    # --------------------------------------------------------
    # PREPARE FRONTEND RESPONSE
    # --------------------------------------------------------

    for cow in cows:

        # Never send biometric embedding to frontend
        cow.pop(
            "embedding",
            None
        )

        # Convert MongoDB datetime to JSON-safe string
        if "created_at" in cow and cow["created_at"]:

            cow["created_at"] = (
                cow["created_at"].isoformat()
            )

        if "updated_at" in cow and cow["updated_at"]:

            cow["updated_at"] = (
                cow["updated_at"].isoformat()
            )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "success": True,
        "count": len(cows),
        "cows": cows
    }