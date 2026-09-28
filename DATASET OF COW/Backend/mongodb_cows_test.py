import os
import socket
from pathlib import Path

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
    raise RuntimeError("MONGODB_URI is missing from .env")


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
# CONNECT
# ============================================================

print("\nConnecting to MongoDB Atlas...")

client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1")
)


try:

    # --------------------------------------------------------
    # TEST CONNECTION
    # --------------------------------------------------------

    client.admin.command("ping")

    print("\nMongoDB connected successfully!")


    # --------------------------------------------------------
    # SELECT DATABASE
    # --------------------------------------------------------

    db = client[DATABASE_NAME]

    print(f"Database: {DATABASE_NAME}")


    # --------------------------------------------------------
    # SELECT COLLECTION
    # --------------------------------------------------------

    cows_collection = db["cows"]

    print("Collection: cows")


    # --------------------------------------------------------
    # TEST COW DATA
    # --------------------------------------------------------

    cow_data = {
        "cow_id": "COW001",
        "name": "Cow 1",

        "owner": {
            "name": "Test Owner",
            "phone": "9876543210",
            "address": "Karnataka"
        },

        "status": "active"
    }


    # --------------------------------------------------------
    # INSERT DATA
    # --------------------------------------------------------

    result = cows_collection.insert_one(cow_data)

    print("\n" + "=" * 60)
    print("COW INSERTED SUCCESSFULLY!")
    print("=" * 60)

    print("MongoDB ID:", result.inserted_id)
    print("Cow ID:", cow_data["cow_id"])
    print("Cow Name:", cow_data["name"])

    print("=" * 60)


    # --------------------------------------------------------
    # READ DATA BACK
    # --------------------------------------------------------

    saved_cow = cows_collection.find_one(
        {"cow_id": "COW001"}
    )

    print("\nRetrieved from MongoDB:")

    print(saved_cow)


except Exception as e:

    print("\n" + "=" * 60)
    print("MONGODB ERROR")
    print("=" * 60)

    print(e)

    print("=" * 60)


finally:

    client.close()

    print("\nMongoDB connection closed.")