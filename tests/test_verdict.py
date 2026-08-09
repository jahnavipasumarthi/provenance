import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from verifier.verdict import generate_verdict


def main():
    print("=" * 50)
    print("FINAL VERDICT TEST")
    print("=" * 50)

    try:
        result = generate_verdict(
            signature_ok=True,
            hard_binding_ok=True,
            soft_binding_ok=True
        )

        print(result)

    except Exception as error:
        print(f"❌ Error: {error}")


if __name__ == "__main__":
    main()