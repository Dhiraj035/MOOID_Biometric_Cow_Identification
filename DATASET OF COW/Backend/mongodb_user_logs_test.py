import os
import socket
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# ============================================================
# FIND .ENV
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

print("Looking for .env at:")
print(ENV_FILE)


# ============================================================
# LOAD .ENV
# ============================================================

if not ENV_FILE.exists():
    raise FileNotFoundError(
        f".env file not found at:\n{ENV_FILE}"
    )

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "moo_id")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing from .env"
    )


# ============================================================
# FORCE IPv4
# ============================================================

original_getaddrinfo = socket.getaddrinfo


def ipv4_only(host, port, family=0, type=0, proto=0, flags=0):

    if family == 0:
        family = socket.AF_INET

    return original_getaddrinfo(
        host,
        port,
        family,
        type,
        proto,
        flags
    )


socket.getaddrinfo = ipv4_only


# ============================================================
# CONNECT TO MONGODB
# ============================================================

print("\nConnecting to MongoDB Atlas...")

client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1")
)


try:

    # ========================================================
    # TEST CONNECTION
    # ========================================================

    client.admin.command("ping")

    print("\nMongoDB connected successfully!")


    # ========================================================
    # SELECT DATABASE
    # ========================================================

    db = client[DATABASE_NAME]

    print(f"Database: {DATABASE_NAME}")


    # ========================================================
    # SELECT USER LOGS COLLECTION
    # ========================================================

    user_logs = db["user_logs"]

    print("Collection: user_logs")


    # ========================================================
    # TEST 1 — REGISTRATION LOG
    # ========================================================

    registration_log = {
        "action": "REGISTRATION",

        "user_id": "USER001",

        "cow_id": "COW021",

        "timestamp": datetime.now(timezone.utc),

        "source": "web",

        "result": "REGISTERED",

        "details": {
            "cow_name": "Cow 21"
        }
    }

    registration_result = user_logs.insert_one(
        registration_log
    )


    print("\n" + "=" * 60)
    print("REGISTRATION LOG INSERTED")
    print("=" * 60)

    print("Log ID:", registration_result.inserted_id)
    print("User ID:", registration_log["user_id"])
    print("Cow ID:", registration_log["cow_id"])
    print("Action:", registration_log["action"])


    # ========================================================
    # TEST 2 — IDENTIFICATION LOG
    # ========================================================

    identification_log = {
        "action": "IDENTIFICATION",

        "user_id": "USER001",

        "cow_id": "COW021",

        "timestamp": datetime.now(timezone.utc),

        "source": "webcam",

        "result": "KNOWN",

        "similarity": 0.8732,

        "yolo_confidence": 0.9123
    }

    identification_result = user_logs.insert_one(
        identification_log
    )


    print("\n" + "=" * 60)
    print("IDENTIFICATION LOG INSERTED")
    print("=" * 60)

    print("Log ID:", identification_result.inserted_id)
    print("User ID:", identification_log["user_id"])
    print("Cow ID:", identification_log["cow_id"])
    print("Action:", identification_log["action"])
    print("Result:", identification_log["result"])
    print("Similarity:", identification_log["similarity"])
    print("YOLO Confidence:", identification_log["yolo_confidence"])


    # ========================================================
    # TEST 3 — UNKNOWN COW LOG
    # ========================================================

    unknown_log = {
        "action": "IDENTIFICATION",

        "user_id": "USER001",

        "cow_id": None,

        "timestamp": datetime.now(timezone.utc),

        "source": "webcam",

        "result": "UNKNOWN",

        "similarity": 0.4215,

        "yolo_confidence": 0.8342
    }

    unknown_result = user_logs.insert_one(
        unknown_log
    )


    print("\n" + "=" * 60)
    print("UNKNOWN IDENTIFICATION LOG INSERTED")
    print("=" * 60)

    print("Log ID:", unknown_result.inserted_id)
    print("User ID:", unknown_log["user_id"])
    print("Cow ID:", unknown_log["cow_id"])
    print("Result:", unknown_log["result"])
    print("Similarity:", unknown_log["similarity"])


    # ========================================================
    # READ LOGS BACK
    # ========================================================

    print("\n" + "=" * 60)
    print("RECENT USER LOGS")
    print("=" * 60)

    logs = user_logs.find().sort(
        "timestamp",
        -1
    ).limit(10)


    for log in logs:

        print("\n------------------------------")

        print("Action     :", log.get("action"))
        print("User ID    :", log.get("user_id"))
        print("Cow ID     :", log.get("cow_id"))
        print("Result     :", log.get("result"))
        print("Source     :", log.get("source"))

        if "similarity" in log:
            print(
                "Similarity :",
                log.get("similarity")
            )


    print("\n" + "=" * 60)
    print("USER LOG TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)


except Exception as e:

    print("\n" + "=" * 60)
    print("MONGODB ERROR")
    print("=" * 60)

    print("Error:", e)

    print("=" * 60)


finally:

    client.close()

    print("\nMongoDB connection closed.")