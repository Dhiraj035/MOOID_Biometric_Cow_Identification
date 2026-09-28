from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from auth_service import get_user_from_token
from mongodb_service import cows_collection, user_logs_collection


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

@router.get("/stats")
def get_dashboard_stats(
    token: str = Depends(oauth2_scheme)
):

    # Verify logged-in user
    user = get_user_from_token(token)

    user_id = user["user_id"]

    # --------------------------------------------------------
    # TOTAL REGISTERED COWS
    # --------------------------------------------------------

    total_cows = cows_collection.count_documents({
        "status": "active"
    })

    # --------------------------------------------------------
    # USER IDENTIFICATION LOGS
    # --------------------------------------------------------

    total_identifications = user_logs_collection.count_documents({
        "user_id": user_id,
        "action": "IDENTIFICATION"
    })

    # --------------------------------------------------------
    # KNOWN COWS
    # --------------------------------------------------------

    known_identifications = user_logs_collection.count_documents({
        "user_id": user_id,
        "action": "IDENTIFICATION",
        "result": "KNOWN"
    })

    # --------------------------------------------------------
    # UNKNOWN COWS
    # --------------------------------------------------------

    unknown_identifications = user_logs_collection.count_documents({
        "user_id": user_id,
        "action": "IDENTIFICATION",
        "result": "UNKNOWN"
    })

    # --------------------------------------------------------
    # RECENT ACTIVITY
    # --------------------------------------------------------

    recent_logs = list(
        user_logs_collection
        .find(
            {
                "user_id": user_id
            },
            {
                "_id": 0
            }
        )
        .sort(
            "timestamp",
            -1
        )
        .limit(10)
    )

    # Convert MongoDB datetime objects
    for log in recent_logs:

        if "timestamp" in log:

            log["timestamp"] = (
                log["timestamp"].isoformat()
            )

    return {
        "success": True,

        "stats": {
            "total_cows": total_cows,
            "total_identifications": total_identifications,
            "known_identifications": known_identifications,
            "unknown_identifications": unknown_identifications
        },

        "recent_activity": recent_logs
    }