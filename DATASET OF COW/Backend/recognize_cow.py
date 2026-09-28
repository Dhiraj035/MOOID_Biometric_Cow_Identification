import sys
from pathlib import Path

import faiss
import numpy as np
import torch
from PIL import Image

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
MODEL_DIR = PROJECT_DIR / "models"

# ============================================================
# FILE PATHS
# ============================================================

MODEL_PATH = MODEL_DIR / "best_resnet50_arcface.pth"

FAISS_INDEX_PATH = (
    MODEL_DIR / "cow_train_embeddings.faiss"
)

LABELS_PATH = (
    MODEL_DIR / "cow_train_labels.npy"
)

IMAGE_PATHS_PATH = (
    MODEL_DIR / "cow_train_image_paths.npy"
)

# ============================================================
# TEMPORARY THRESHOLD
# ============================================================

THRESHOLD = 0.5813


# ============================================================
# IMPORT MODEL
# ============================================================

if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from model import ResNet50Embedding
from dataset import val_transform


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("MOO-ID COW RECOGNITION")
print("=" * 60)

print(f"Device: {device}")

if torch.cuda.is_available():
    print(
        f"GPU: {torch.cuda.get_device_name(0)}"
    )


# ============================================================
# ASK FOR IMAGE
# ============================================================

image_input = input(
    "\nEnter the path of the muzzle image: "
).strip().strip('"')


image_path = Path(image_input)


if not image_path.exists():

    print("\nERROR: Image not found!")

    print(
        f"Path entered: {image_path}"
    )

    sys.exit(1)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading ResNet50 model...")

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=False
)

embedding_size = checkpoint[
    "embedding_size"
]

model = ResNet50Embedding(
    embedding_size=embedding_size
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()

print(
    f"Embedding size: {embedding_size}"
)


# ============================================================
# LOAD FAISS
# ============================================================

print("\nLoading FAISS index...")

index = faiss.read_index(
    str(FAISS_INDEX_PATH)
)

labels = np.load(
    LABELS_PATH
)

image_paths = np.load(
    IMAGE_PATHS_PATH,
    allow_pickle=True
)

print(
    f"FAISS vectors: {index.ntotal}"
)


# ============================================================
# LOAD IMAGE
# ============================================================

print("\nLoading image...")

image = Image.open(
    image_path
).convert("RGB")


# ============================================================
# PREPROCESS IMAGE
# ============================================================

image_tensor = val_transform(
    image
)

image_tensor = image_tensor.unsqueeze(
    0
).to(device)


# ============================================================
# GENERATE EMBEDDING
# ============================================================

print("Generating embedding...")

with torch.no_grad():

    embedding = model(
        image_tensor
    )

    embedding = embedding.cpu().numpy().astype(
        np.float32
    )


# ============================================================
# NORMALIZE
# ============================================================

faiss.normalize_L2(
    embedding
)


# ============================================================
# SEARCH
# ============================================================

print("Searching FAISS...")

distances, indices = index.search(
    embedding,
    5
)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("RECOGNITION RESULTS")
print("=" * 60)

print(
    f"Input image: {image_path}"
)

print(
    f"Threshold: {THRESHOLD:.4f}"
)

print("\nTop matches:")

for rank in range(5):

    idx = indices[0][rank]

    similarity = distances[0][rank]

    cow_label = int(labels[idx]) + 1

    matched_image = image_paths[idx]

    print(
        f"{rank + 1}. "
        f"Cow {cow_label} | "
        f"Similarity: {similarity:.4f}"
    )

    print(
        f"   Match: {matched_image}"
    )


# ============================================================
# BEST MATCH
# ============================================================

best_index = indices[0][0]

best_similarity = float(
    distances[0][0]
)

best_cow = int(labels[best_index]) + 1
# ============================================================
# THRESHOLD DECISION
# ============================================================

print("\n")
print("=" * 60)
print("FINAL DECISION")
print("=" * 60)

if best_similarity >= THRESHOLD:

    print(
        f"✓ COW RECOGNIZED"
    )

    print(
        f"Cow ID: {best_cow}"
    )

    print(
        f"Similarity: {best_similarity:.4f}"
    )

else:

    print(
        "✗ UNKNOWN COW"
    )

    print(
        f"Best similarity: "
        f"{best_similarity:.4f}"
    )

print("=" * 60)