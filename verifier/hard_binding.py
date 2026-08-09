import hashlib
from pathlib import Path

from verifier.manifest import (
    load_manifest,
    find_manifest,
    get_manifest_info,
)


def sha256_file(file_path):
    """
    Calculate SHA-256 hash of a file.
    """

    sha = hashlib.sha256()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(4096)

            if not chunk:
                break

            sha.update(chunk)

    return sha.hexdigest()


def verify_hash(file_path, expected_hash):
    """
    Compare calculated SHA256 with expected SHA256.
    """

    calculated_hash = sha256_file(file_path)

    return calculated_hash.lower() == expected_hash.lower()


def verify_hard_binding(image_path):
    """
    Verify hard binding using the provenance manifest.

    Returns
    -------
    dict
    """

    image_path = Path(image_path)

    manifest_path = find_manifest(image_path.name)

    if manifest_path is None:

        return {
            "verified": False,
            "manifest": None,
            "stored_hash": None,
            "calculated_hash": None,
            "message": "Manifest not found"
        }

    # Load manifest
    manifest = load_manifest(manifest_path)

    manifest_info = get_manifest_info(manifest)

    stored_hash = manifest_info["hard_binding_sha256"]

    calculated_hash = sha256_file(image_path)

    verified = (
        stored_hash is not None
        and stored_hash.lower() == calculated_hash.lower()
    )

    return {

        "verified": verified,

        "manifest": str(manifest_path),

        "stored_hash": stored_hash,

        "calculated_hash": calculated_hash,

        "asset_id": manifest_info["asset_id"],

        "capture_device": manifest_info["capture_device"],

        "captured_at": manifest_info["captured_at"],

        "issuer": manifest_info["issuer"],

        "algorithm": manifest_info["algorithm"],

        "message": (
            "Hard Binding Verified"
            if verified
            else "Hard Binding Failed"
        )

    }