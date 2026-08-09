import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from verifier.signature import verify_signature


MANIFEST_PATH = Path("assets/manifests/sample.json")
PUBLIC_KEY_PATH = Path("keys/public.pem")


def main():
    print("=" * 50)
    print("SIGNATURE VERIFICATION TEST")
    print("=" * 50)

    if not MANIFEST_PATH.exists():
        print(f"❌ Manifest not found: {MANIFEST_PATH}")
        return

    if not PUBLIC_KEY_PATH.exists():
        print(f"❌ Public key not found: {PUBLIC_KEY_PATH}")
        return

    try:
        status = verify_signature(
            str(MANIFEST_PATH),
            str(PUBLIC_KEY_PATH)
        )

        print(f"Manifest : {MANIFEST_PATH}")
        print(f"Public Key : {PUBLIC_KEY_PATH}")
        print(f"Signature Valid : {'PASS' if status else 'FAIL'}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()