import os
import json
import base64
import hashlib
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


IMAGE_PATH = Path("assets/images/sample.jpg")
MANIFEST_PATH = Path("assets/manifests/sample.json")
PRIVATE_KEY_PATH = Path("keys/private.pem")


def sha256_file(filename):
    """Calculate SHA-256 hash of a file."""
    sha = hashlib.sha256()

    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha.update(chunk)

    return sha.hexdigest()


def load_private_key():
    """Load the Ed25519 private key."""
    if not PRIVATE_KEY_PATH.exists():
        raise FileNotFoundError(f"Private key not found: {PRIVATE_KEY_PATH}")

    with open(PRIVATE_KEY_PATH, "rb") as file:
        return serialization.load_pem_private_key(
            file.read(),
            password=None
        )


def create_manifest():
    """Create a signed provenance manifest."""

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

    private_key = load_private_key()

    image_hash = sha256_file(IMAGE_PATH)

    manifest = {
        "file": IMAGE_PATH.name,
        "hash": image_hash,
        "issuer": "TeamABC",
        "device": "Laptop",
        "location": "Hidden"
    }

    signature = private_key.sign(
        json.dumps(
            manifest,
            sort_keys=True
        ).encode("utf-8")
    )

    manifest["signature"] = base64.b64encode(signature).decode("utf-8")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as file:
        json.dump(
            manifest,
            file,
            indent=4
        )

    print("=" * 50)
    print("Manifest Created Successfully")
    print("=" * 50)
    print(MANIFEST_PATH)


def main():
    create_manifest()


if __name__ == "__main__":
    main()