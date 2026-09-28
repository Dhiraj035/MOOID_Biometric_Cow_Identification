from mongodb_service import (
    test_connection,
    register_cow,
    get_cow,
    log_identification,
    get_cow_history,
    get_user_history,
    close_connection
)


print("=" * 60)
print("TESTING MONGODB SERVICE")
print("=" * 60)


# ============================================================
# 1. TEST CONNECTION
# ============================================================

print("\n1. Testing MongoDB connection...")

if test_connection():
    print("MongoDB connection: SUCCESS")


# ============================================================
# 2. REGISTER A NEW COW
# ============================================================

print("\n2. Registering Cow 22...")

try:

    result = register_cow(
        cow_id="COW022",
        cow_name="Cow 22",
        owner_name="Test Owner 2",
        owner_phone="9876543211",
        owner_address="Karnataka",
        user_id="USER001"
    )

    print("Cow registered successfully!")
    print("MongoDB ID:", result)

except Exception as e:

    print("Registration failed:")
    print(e)


# ============================================================
# 3. GET COW
# ============================================================

print("\n3. Searching for COW022...")

cow = get_cow("COW022")

if cow:

    print("Cow found!")

    print("Cow ID:", cow["cow_id"])
    print("Name:", cow["name"])
    print("Owner:", cow["owner"]["name"])
    print("Phone:", cow["owner"]["phone"])

else:

    print("Cow not found.")


# ============================================================
# 4. IDENTIFICATION LOG
# ============================================================

print("\n4. Recording identification...")

try:

    result = log_identification(

        user_id="USER001",

        cow_id="COW022",

        result="KNOWN",

        similarity=0.8732,

        yolo_confidence=0.9123,

        source="webcam"
    )

    print("Identification log saved!")

    print("Log ID:", result.inserted_id)

except Exception as e:

    print("Identification logging failed:")
    print(e)


# ============================================================
# 5. COW HISTORY
# ============================================================

print("\n5. Getting COW022 history...")

history = get_cow_history("COW022")

print("Number of records:", len(history))

for record in history:

    print(
        record.get("action"),
        "|",
        record.get("result"),
        "|",
        record.get("user_id")
    )


# ============================================================
# 6. USER HISTORY
# ============================================================

print("\n6. Getting USER001 history...")

user_history = get_user_history("USER001")

print("Number of records:", len(user_history))

for record in user_history:

    print(
        record.get("action"),
        "| Cow:",
        record.get("cow_id"),
        "| Result:",
        record.get("result")
    )


# ============================================================
# FINISH
# ============================================================

close_connection()

print("\n" + "=" * 60)
print("MONGODB SERVICE TEST COMPLETED!")
print("=" * 60)