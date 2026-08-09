from pathlib import Path

DATASET = Path("datasets/ps_i4_provenance")

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def main():
    print("=" * 60)
    print("DATASET SCAN")
    print("=" * 60)

    if not DATASET.exists():
        print(f"❌ Dataset folder not found: {DATASET}")
        return

    print(f"✅ Dataset Found: {DATASET}\n")

    # ---------------- Images ----------------

    images = []

    for ext in IMAGE_EXTENSIONS:
        images.extend(DATASET.rglob(f"*{ext}"))

    print("=" * 60)
    print("IMAGES")
    print("=" * 60)

    if images:
        for image in sorted(images):
            print(image)

        print(f"\nTotal Images: {len(images)}")
    else:
        print("❌ No images found.")

    # ---------------- Manifests ----------------

    manifests = sorted(DATASET.rglob("*.json"))

    print("\n" + "=" * 60)
    print("MANIFESTS")
    print("=" * 60)

    if manifests:
        for manifest in manifests:
            print(manifest)

        print(f"\nTotal Manifests: {len(manifests)}")
    else:
        print("❌ No manifest files found.")

    # ---------------- Trust Lists ----------------

    trustlists = sorted(DATASET.rglob("trustlist*.json"))

    print("\n" + "=" * 60)
    print("TRUST LIST")
    print("=" * 60)

    if trustlists:
        for trust in trustlists:
            print(trust)
    else:
        print("❌ Trust list not found.")

    print("\n" + "=" * 60)
    print("Dataset Scan Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()