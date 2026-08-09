
import json
from pathlib import Path

# Dataset root
DATASET = Path("datasets/ps_i4_provenance/public")


def load_manifest(manifest_path):
    """
    Load a provenance manifest.
    """
    manifest_path = Path(manifest_path)

    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_manifest(image_name):
    """
    Find manifest for an uploaded image.
    """

    image_name = Path(image_name).name

    asset_id = image_name.split("__")[0]

    manifest = DATASET / "manifests" / f"{asset_id}.manifest.json"

    if manifest.exists():
        return manifest

    return None


def has_provenance(image_name):
    return find_manifest(image_name) is not None


# -------------------------
# Claim Information
# -------------------------

def get_claim(manifest):
    return manifest.get("claim", {})


def get_asset_id(manifest):
    return get_claim(manifest).get("asset_id", "Unknown")


def get_capture_device(manifest):
    return get_claim(manifest).get("capture_device", "Unknown")


def get_capture_time(manifest):
    return get_claim(manifest).get("captured_at", "Unknown")


def get_hard_hash(manifest):
    return get_claim(manifest).get("hard_binding_sha256")


def get_soft_hash(manifest):
    return get_claim(manifest).get("soft_binding_phash")


# -------------------------
# Signature Information
# -------------------------

def get_signature(manifest):
    return manifest.get("signature_b64")


def get_public_key(manifest):
    return manifest.get("public_key_b64")


def get_algorithm(manifest):
    return manifest.get("algorithm", "Unknown")


def get_issuer(manifest):
    return manifest.get("issuer", "Unknown")


# -------------------------
# Full Manifest Summary
# -------------------------

def get_manifest_info(manifest):
    return {

        "asset_id": get_asset_id(manifest),

        "capture_device": get_capture_device(manifest),

        "captured_at": get_capture_time(manifest),

        "issuer": get_issuer(manifest),

        "algorithm": get_algorithm(manifest),

        "hard_binding_sha256": get_hard_hash(manifest),

        "soft_binding_phash": get_soft_hash(manifest),

        "signature_b64": get_signature(manifest),

        "public_key_b64": get_public_key(manifest)

    }