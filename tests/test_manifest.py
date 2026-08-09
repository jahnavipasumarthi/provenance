import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from verifier.manifest import find_manifest


ASSETS_DIR = Path("datasets/ps_i4_provenance/public/assets")


def main():
    print("=" * 70)
    print("DATASET MANIFEST TEST")
    print("=" * 70)

    if not ASSETS_DIR.exists():
        print(f"❌ Assets folder not found: {ASSETS_DIR}")
        return

    images = sorted(ASSETS_DIR.glob("*.jpg"))

    if not images:
        print("❌ No JPG images found.")
        return

    signed = 0
    unsigned = 0

    for image in images:
        try:
            manifest = find_manifest(image.name)

            if manifest:
                print(f"{image.name:35} --> SIGNED")
                signed += 1
            else:
                print(f"{image.name:35} --> UNSIGNED")
                unsigned += 1

        except Exception as e:
            print(f"{image.name:35} --> ERROR ({e})")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Images : {len(images)}")
    print(f"Signed       : {signed}")
    print(f"Unsigned     : {unsigned}")


if __name__ == "__main__":
    main()