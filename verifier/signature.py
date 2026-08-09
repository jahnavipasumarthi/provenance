
import json
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature


def verify_signature(manifest_path):
    """
    Verify the digital signature stored in the provenance manifest.

    Returns
    -------
    bool
    """

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    try:
        # Signature stored in manifest
        signature = base64.b64decode(manifest["signature_b64"])

        # Public key stored in manifest
        public_key_bytes = base64.b64decode(manifest["public_key_b64"])

        public_key = Ed25519PublicKey.from_public_bytes(
            public_key_bytes
        )

        # Data that was signed
        signed_data = json.dumps(
            manifest["claim"],
            sort_keys=True,
            separators=(",", ":")
        ).encode()

        # Verify signature
        public_key.verify(signature, signed_data)

        return True

    except (InvalidSignature, KeyError, ValueError, Exception):
        return False