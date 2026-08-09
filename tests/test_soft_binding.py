import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from verifier.soft_binding import verify_soft_binding


IMAGE_PATH = Path("assets/images/sample.jpg")
REFERENCE_IMAGE_PATH = Path("assets/images/sample.jpg")


def main():
    print("=" * 50)
    print("SOFT BINDING TEST")
    print("=" * 50)

    # Check source image
    if not IMAGE_PATH.exists():
        print(f"❌ Image not found: {IMAGE_PATH}")
        return

    # Check reference image
    if not REFERENCE_IMAGE_PATH.exists():
        print(f"❌ Reference image not found: {REFERENCE_IMAGE_PATH}")
        return

    try:
        matched, distance = verify_soft_binding(
            str(IMAGE_PATH),
            str(REFERENCE_IMAGE_PATH)
        )

        print(f"Image     : {IMAGE_PATH}")
        print(f"Reference : {REFERENCE_IMAGE_PATH}")
        print(f"Distance  : {distance}")

        if matched:
            print("✅ Soft Binding Passed")
        else:
            print("❌ Soft Binding Failed")

    except Exception as e:
        print(f"❌ Soft Binding Error: {e}")


if __name__ == "__main__":
    main()