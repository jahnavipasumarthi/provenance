import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from verifier.hard_binding import verify_hard_binding


ASSETS_DIR = Path("datasets/ps_i4_provenance/public/assets")


def main():
    print("=" * 50)
    print("HARD BINDING TEST")
    print("=" * 50)

    if not ASSETS_DIR.exists():
        print(f"❌ Assets folder not found: {ASSETS_DIR}")
        return

    # Look for an original image
    images = sorted(ASSETS_DIR.glob("*original.jpg"))

    if not images:
        print("❌ No '*original.jpg' image found.")
        return

    image = images[0]

    try:
        status, manifest = verify_hard_binding(image)

        print(f"Image    : {image.name}")
        print(f"Status   : {'PASS' if status else 'FAIL'}")
        print(f"Manifest : {manifest}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()