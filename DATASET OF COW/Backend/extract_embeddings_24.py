import sys
from pathlib import Path

import numpy as np
import torch
import faiss
from torch.utils.data import DataLoader

# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
ROOT_DIR = PROJECT_DIR.parent

MODEL_DIR = PROJECT_DIR / "models"

sys.path.insert(0, str(CURRENT_DIR))

from dataset import get_datasets
from model import ResNet50Embedding


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

MODEL_PATH = (
    MODEL_DIR /
    "best_resnet50_arcface_24c_yolo_texture.pth"
)

FAISS_PATH = (
    MODEL_DIR /
    "cow_24_yolo_texture_train.faiss"
)

LABELS_PATH = (
    MODEL_DIR /
    "cow_24_yolo_texture_train_labels.npy"
)

PATHS_PATH = (
    MODEL_DIR /
    "cow_24_yolo_texture_train_paths.npy"
)

EMBEDDING_SIZE = 512
BATCH_SIZE = 8

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)


# ------------------------------------------------------------
# Start
# ------------------------------------------------------------

print("=" * 70)
print("24-COW RESNET50 EMBEDDING EXTRACTION")
print("=" * 70)

print(f"\nDevice: {DEVICE}")

if torch.cuda.is_available():
    print(
        f"GPU: {torch.cuda.get_device_name(0)}"
    )


# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

(
    train_dataset,
    val_dataset,
    test_dataset
) = get_datasets()

print(
    f"\nTraining images: {len(train_dataset)}"
)

print(
    f"Validation images: {len(val_dataset)}"
)

print(
    f"Test images: {len(test_dataset)}"
)


# ------------------------------------------------------------
# Training loader
# ------------------------------------------------------------

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)


# ------------------------------------------------------------
# Load ResNet50
# ------------------------------------------------------------

print("\nLoading ResNet50...")

model = ResNet50Embedding(
    embedding_size=EMBEDDING_SIZE
).to(DEVICE)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

print("Model loaded successfully.")


# ------------------------------------------------------------
# Extract embeddings
# ------------------------------------------------------------

all_embeddings = []
all_labels = []
all_paths = []

print("\nExtracting embeddings...")

with torch.no_grad():

    for batch_index, (images, labels) in enumerate(
        train_loader
    ):

        images = images.to(
            DEVICE,
            non_blocking=True
        )

        embeddings = model(images)

        embeddings = embeddings.cpu().numpy()

        all_embeddings.append(
            embeddings
        )

        all_labels.extend(
            labels.numpy().tolist()
        )

        start_index = (
            batch_index * BATCH_SIZE
        )

        end_index = min(
            start_index + len(labels),
            len(train_dataset.samples)
        )

        for i in range(
            start_index,
            end_index
        ):

            image_path, _ = (
                train_dataset.samples[i]
            )

            all_paths.append(
                str(image_path)
            )

        print(
            f"Processed "
            f"{end_index}/{len(train_dataset)}"
        )


# ------------------------------------------------------------
# Combine
# ------------------------------------------------------------

embeddings = np.vstack(
    all_embeddings
).astype("float32")

labels = np.array(
    all_labels,
    dtype=np.int64
)

paths = np.array(
    all_paths,
    dtype=str
)


# ------------------------------------------------------------
# Normalize
# ------------------------------------------------------------

faiss.normalize_L2(
    embeddings
)


# ------------------------------------------------------------
# Build FAISS
# ------------------------------------------------------------

print("\nBuilding FAISS index...")

index = faiss.IndexFlatIP(
    EMBEDDING_SIZE
)

index.add(
    embeddings
)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

faiss.write_index(
    index,
    str(FAISS_PATH)
)

np.save(
    LABELS_PATH,
    labels
)

np.save(
    PATHS_PATH,
    paths
)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("FAISS DATABASE CREATED")
print("=" * 70)

print(
    f"Embeddings : {len(embeddings)}"
)

print(
    f"Dimension  : {embeddings.shape[1]}"
)

print(
    f"FAISS size : {index.ntotal}"
)

print(
    f"\nIndex:\n{FAISS_PATH}"
)

print(
    f"\nLabels:\n{LABELS_PATH}"
)

print(
    f"\nPaths:\n{PATHS_PATH}"
)

print("=" * 70)