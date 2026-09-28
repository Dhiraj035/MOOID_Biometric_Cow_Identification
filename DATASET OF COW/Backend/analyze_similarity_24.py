import sys
from pathlib import Path

import numpy as np
import torch
import faiss
from torch.utils.data import DataLoader


# ============================================================
# PATHS
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent

MODEL_DIR = PROJECT_DIR / "models"

sys.path.insert(0, str(CURRENT_DIR))

from dataset import get_datasets
from model import ResNet50Embedding


# ============================================================
# CONFIG
# ============================================================

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

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

BATCH_SIZE = 8


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("SIMILARITY ANALYSIS")
print("=" * 70)

(
    train_dataset,
    val_dataset,
    test_dataset
) = get_datasets()


test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


# ============================================================
# MODEL
# ============================================================

model = ResNet50Embedding(
    embedding_size=512
).to(DEVICE)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ============================================================
# FAISS
# ============================================================

index = faiss.read_index(
    str(FAISS_PATH)
)

gallery_labels = np.load(
    LABELS_PATH
)

gallery_paths = np.load(
    PATHS_PATH
)


# ============================================================
# SEARCH
# ============================================================

results = []


with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(
            DEVICE,
            non_blocking=True
        )

        embeddings = model(images)

        embeddings = embeddings.cpu().numpy().astype(
            "float32"
        )

        faiss.normalize_L2(
            embeddings
        )

        similarities, indices = index.search(
            embeddings,
            5
        )

        for i in range(len(labels)):

            true_label = int(
                labels[i].item()
            )

            top_label = int(
                gallery_labels[
                    indices[i][0]
                ]
            )

            top_similarity = float(
                similarities[i][0]
            )

            correct = (
                top_label == true_label
            )

            image_path = (
                test_dataset.samples[
                    len(results)
                ][0]
            )

            results.append(
                {
                    "path": str(image_path),
                    "true_label": true_label,
                    "predicted_label": top_label,
                    "similarity": top_similarity,
                    "correct": correct
                }
            )


# ============================================================
# SORT BY SIMILARITY
# ============================================================

results_sorted = sorted(
    results,
    key=lambda x: x["similarity"]
)


# ============================================================
# LOWEST SIMILARITY
# ============================================================

print("\n")
print("=" * 70)
print("LOWEST SIMILARITY TEST CASES")
print("=" * 70)

for item in results_sorted[:15]:

    print(
        f"\nTrue Cow       : "
        f"{item['true_label'] + 1}"
    )

    print(
        f"Predicted Cow : "
        f"{item['predicted_label'] + 1}"
    )

    print(
        f"Similarity    : "
        f"{item['similarity']:.4f}"
    )

    print(
        f"Correct       : "
        f"{item['correct']}"
    )

    print(
        f"Image         : "
        f"{item['path']}"
    )


# ============================================================
# STATISTICS
# ============================================================

similarities = np.array(
    [
        item["similarity"]
        for item in results
    ]
)

correct_similarities = np.array(
    [
        item["similarity"]
        for item in results
        if item["correct"]
    ]
)

incorrect_similarities = np.array(
    [
        item["similarity"]
        for item in results
        if not item["correct"]
    ]
)


print("\n")
print("=" * 70)
print("SIMILARITY STATISTICS")
print("=" * 70)

print(
    f"Minimum similarity : "
    f"{similarities.min():.4f}"
)

print(
    f"Mean similarity    : "
    f"{similarities.mean():.4f}"
)

print(
    f"Median similarity  : "
    f"{np.median(similarities):.4f}"
)

print(
    f"Maximum similarity : "
    f"{similarities.max():.4f}"
)


if len(correct_similarities) > 0:

    print("\nCorrect matches:")

    print(
        f"Minimum: "
        f"{correct_similarities.min():.4f}"
    )

    print(
        f"Mean: "
        f"{correct_similarities.mean():.4f}"
    )


if len(incorrect_similarities) > 0:

    print("\nIncorrect matches:")

    print(
        f"Minimum: "
        f"{incorrect_similarities.min():.4f}"
    )

    print(
        f"Maximum: "
        f"{incorrect_similarities.max():.4f}"
    )

    print(
        f"Mean: "
        f"{incorrect_similarities.mean():.4f}"
    )


print("\n")
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)