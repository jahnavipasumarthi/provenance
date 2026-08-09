from pathlib import Path

ASSETS_DIR = Path("datasets/ps_i4_provenance/public/assets")


def main():
    print("=" * 60)
    print("ASSET TEST")
    print("=" * 60)

    if not ASSETS_DIR.exists():
        print(f"❌ Assets folder not found: {ASSETS_DIR}")
        return

    images = sorted(ASSETS_DIR.glob("*.jpg"))

    if not images:
        print("❌ No JPG images found.")
        return

    print("✅ First image found:")
    print(images[0].name)


if __name__ == "__main__":
    main()