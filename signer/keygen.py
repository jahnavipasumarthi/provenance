from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


KEYS_DIR = Path("keys")
PRIVATE_KEY_FILE = KEYS_DIR / "private.pem"
PUBLIC_KEY_FILE = KEYS_DIR / "public.pem"


def generate_keys():
    """Generate an Ed25519 public/private key pair."""

    KEYS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate private key
    private_key = Ed25519PrivateKey.generate()

    # Generate public key
    public_key = private_key.public_key()

    # Save private key
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    # Save public key
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print("=" * 50)
    print("Ed25519 Key Pair Generated Successfully")
    print("=" * 50)
    print(f"Private Key : {PRIVATE_KEY_FILE}")
    print(f"Public Key  : {PUBLIC_KEY_FILE}")


def main():
    generate_keys()


if __name__ == "__main__":
    main()