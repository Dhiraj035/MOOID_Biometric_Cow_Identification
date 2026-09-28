import os
import socket
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = CURRENT_DIR.parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv(
    "MONGODB_URI"
)

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "moo_id"
)

if not MONGODB_URI:

    raise RuntimeError(
        "MONGODB_URI is missing from .env"
    )


# ============================================================
# FORCE IPv4
# ============================================================

_original_getaddrinfo = socket.getaddrinfo


def _ipv4_only(
    host,
    port,
    family=0,
    type=0,
    proto=0,
    flags=0
):

    if family == 0:
        family = socket.AF_INET

    return _original_getaddrinfo(
        host,
        port,
        family,
        type,
        proto,
        flags
    )


socket.getaddrinfo = _ipv4_only


# ============================================================
# MONGODB CONNECTION
# ============================================================

client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1"),
    connectTimeoutMS=20000,
    serverSelectionTimeoutMS=30000,
    tls=True,
)


# ============================================================
# DATABASE
# ============================================================

db = client[DATABASE_NAME]


# ============================================================
# COLLECTIONS
# ============================================================

cows_collection = db["cows"]

registered_cows_collection = (
    db["registered_cows"]
)

user_logs_collection = (
    db["user_logs"]
)


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection():

    client.admin.command(
        "ping"
    )

    return True


# ============================================================
# REGISTER COW
# ============================================================

def register_cow(
    cow_id,
    cow_name,
    owner_name,
    owner_phone,
    owner_address,
    user_id,
    image_path=None,
    embedding=None,
):

    cow_id = str(
        cow_id
    ).strip()

    cow_name = str(
        cow_name
    ).strip()

    user_id = str(
        user_id
    ).strip()

    # ========================================================
    # DUPLICATE CHECK
    # ========================================================

    existing_cow = (
        registered_cows_collection.find_one(
            {
                "cow_id": cow_id
            }
        )
    )

    if existing_cow:

        raise ValueError(
            f"Cow ID '{cow_id}' "
            "is already registered."
        )

    # ========================================================
    # CURRENT TIME
    # ========================================================

    now = datetime.now(
        timezone.utc
    )

    # ========================================================
    # EMBEDDING
    # ========================================================

    embedding_data = None

    embedding_created = False

    embedding_dimension = None

    if embedding is not None:

        embedding_array = np.asarray(
            embedding,
            dtype=np.float32
        )

        embedding_array = (
            embedding_array.reshape(-1)
        )

        embedding_data = (
            embedding_array.tolist()
        )

        embedding_created = True

        embedding_dimension = (
            len(embedding_data)
        )

    # ========================================================
    # COW DOCUMENT
    # ========================================================

    cow_document = {

        "cow_id": cow_id,

        "cow_name": cow_name,

        "user_id": user_id,

        "owner": {

            "name": str(
                owner_name
            ).strip(),

            "phone": str(
                owner_phone
            ).strip(),

            "address": str(
                owner_address
            ).strip(),
        },

        "image_path": image_path,

        "embedding": embedding_data,

        "embedding_created":
            embedding_created,

        "embedding_dimension":
            embedding_dimension,

        "status": "active",

        "created_at": now,

        "updated_at": now,
    }

    # ========================================================
    # INSERT
    # ========================================================

    result = (
        registered_cows_collection.insert_one(
            cow_document
        )
    )

    # ========================================================
    # REGISTRATION LOG
    # ========================================================

    log_registration(
        user_id=user_id,
        cow_id=cow_id,
        cow_name=cow_name,
    )

    return result.inserted_id


# ============================================================
# GET REGISTERED COW
# ============================================================

def get_registered_cow(
    cow_id
):

    return (
        registered_cows_collection.find_one(
            {
                "cow_id": str(
                    cow_id
                )
            }
        )
    )

# ============================================================
# GET USER'S REGISTERED COWS
# ============================================================

def get_user_registered_cows(user_id):
    cows = (
        registered_cows_collection.find(
            {
                "user_id": str(user_id),
                "status": "active",
            },
            {
                "_id": 0
            }
        )
        .sort(
            "created_at",
            -1
        )
    )

    return list(cows)

# ============================================================
# GET ALL REGISTERED COWS
# ============================================================

def get_all_registered_cows():

    cows = (
        registered_cows_collection.find(
            {}
        )
        .sort(
            "created_at",
            -1
        )
    )

    return list(cows)


# ============================================================
# OLD COW COLLECTION
# ============================================================

def get_cow(
    cow_id
):

    return cows_collection.find_one(
        {
            "cow_id": str(
                cow_id
            )
        }
    )


def get_all_cows():

    cows = (
        cows_collection.find({})
        .sort(
            "created_at",
            -1
        )
    )

    return list(cows)


# ============================================================
# REGISTRATION LOG
# ============================================================

def log_registration(
    user_id,
    cow_id,
    cow_name
):

    log = {

        "action": "REGISTRATION",

        "user_id": str(
            user_id
        ),

        "cow_id": str(
            cow_id
        ),

        "timestamp":
            datetime.now(
                timezone.utc
            ),

        "source": "web",

        "result": "REGISTERED",

        "details": {

            "cow_name": str(
                cow_name
            )
        }
    }

    return (
        user_logs_collection.insert_one(
            log
        )
    )


# ============================================================
# IDENTIFICATION LOG
# ============================================================

def log_identification(
    user_id,
    cow_id,
    result,
    similarity,
    yolo_confidence,
    source="web"
):

    log = {

        "action": "IDENTIFICATION",

        "user_id": str(
            user_id
        ),

        "cow_id": (
            str(cow_id)
            if cow_id is not None
            else None
        ),

        "timestamp":
            datetime.now(
                timezone.utc
            ),

        "source": str(
            source
        ),

        "result": str(
            result
        ),

        "similarity": float(
            similarity
        ),

        "yolo_confidence": float(
            yolo_confidence
        ),
    }

    return (
        user_logs_collection.insert_one(
            log
        )
    )


# ============================================================
# GET COW HISTORY
# ============================================================

def get_cow_history(
    cow_id
):

    logs = (
        user_logs_collection.find(
            {
                "cow_id": str(
                    cow_id
                )
            }
        )
        .sort(
            "timestamp",
            -1
        )
    )

    return list(logs)


# ============================================================
# GET USER HISTORY
# ============================================================

def get_user_history(
    user_id
):

    logs = (
        user_logs_collection.find(
            {
                "user_id": str(
                    user_id
                )
            }
        )
        .sort(
            "timestamp",
            -1
        )
    )

    return list(logs)


# ============================================================
# GET ALL HISTORY
# ============================================================

def get_all_history():

    logs = (
        user_logs_collection.find({})
        .sort(
            "timestamp",
            -1
        )
    )

    return list(logs)


# ============================================================
# CLOSE CONNECTION
# ============================================================

def close_connection():

    client.close()