import torch
import torch.nn as nn
import torch.nn.functional as F

from torchvision.models import (
    resnet50,
    ResNet50_Weights
)


class ResNet50Embedding(nn.Module):

    def __init__(self, embedding_size=512):

        super().__init__()

        # Load ImageNet pretrained ResNet50
        self.backbone = resnet50(weights=None)
        # ResNet50 originally produces 2048 features
        num_features = self.backbone.fc.in_features

        print(
            f"ResNet50 feature size: {num_features}"
        )

        # Remove original ImageNet classifier
        self.backbone.fc = nn.Identity()

        # Convert 2048 features → 512 embedding
        self.embedding = nn.Linear(
            num_features,
            embedding_size
        )

    def forward(self, x):

        # ResNet50 features
        features = self.backbone(x)

        # 2048 → 512
        embeddings = self.embedding(
            features
        )

        # L2 normalize
        embeddings = F.normalize(
            embeddings,
            p=2,
            dim=1
        )

        return embeddings


# ============================================================
# TEST MODEL
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("RESNET50 MODEL TEST")
    print("=" * 50)

    # Select GPU
    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"Device: {device}"
    )

    if torch.cuda.is_available():

        print(
            f"GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

    # Create model
    model = ResNet50Embedding(
        embedding_size=512
    )

    model = model.to(device)

    # Create fake batch
    batch_size = 4

    dummy_input = torch.randn(
        batch_size,
        3,
        224,
        224
    ).to(device)

    print(
        f"Input shape: "
        f"{dummy_input.shape}"
    )

    # Forward pass
    with torch.no_grad():

        embeddings = model(
            dummy_input
        )

    print(
        f"Embedding shape: "
        f"{embeddings.shape}"
    )

    # Check embedding norm
    norms = torch.norm(
        embeddings,
        p=2,
        dim=1
    )

    print(
        f"Embedding norms: "
        f"{norms}"
    )

    print("=" * 50)
    print("MODEL TEST SUCCESSFUL")
    print("=" * 50)