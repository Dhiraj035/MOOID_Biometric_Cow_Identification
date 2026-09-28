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
    raise RuntimeError(
        "MONGODB_URI is missing from .env"
    )


# ============================================================
# FORCE IPv4 FOR MONGODB CONNECTION
# ============================================================

original_getaddrinfo = socket.getaddrinfo


def ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    """
    Force DNS resolution to use IPv4.
    This avoids the IPv6/NAT64 TLS problem encountered
    with the current network.
    """
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
# CONNECT TO MONGODB ATLAS
# ============================================================

print("\nConnecting to MongoDB Atlas...")

client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1"),
    connectTimeoutMS=20000,
    serverSelectionTimeoutMS=30000,
    tls=True,
)


# ============================================================
# TEST CONNECTION
# ============================================================

try:

    client.admin.command("ping")

    print("\n" + "=" * 60)
    print("MONGODB CONNECTED SUCCESSFULLY!")
    print("=" * 60)

    print(f"Database: {DATABASE_NAME}")
    print("Cluster connection: SUCCESS")
    print("Network family: IPv4")

    print("=" * 60)


except Exception as e:

    print("\n" + "=" * 60)
    print("MONGODB CONNECTION FAILED")
    print("=" * 60)

    print("Error:", e)

    print("=" * 60)


finally:

    client.close()