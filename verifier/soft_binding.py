from pathlib import Path

from PIL import Image
import imagehash


def phash(image_path):
    """
    Compute perceptual hash (pHash).
    """
    return imagehash.phash(Image.open(image_path))


def phash_distance(image1, image2):
    """
    Compute pHash Hamming distance.
    """
    return phash(image1) - phash(image2)


def similarity(distance):
    """
    Convert pHash distance to similarity percentage.
    """
    score = max(0, 100 - (distance / 64) * 100)
    return round(score, 2)


def transformation_name(filename):
    """
    Extract transformation from filename.

    Example:
        A000__crop.jpg
        -> crop
    """

    name = Path(filename).stem

    if "__" not in name:
        return "Original"

    return name.split("__")[1].replace("_", " ").title()


def verify_soft_binding(image1, image2, threshold=10):
    """
    Simple soft binding.
    """

    distance = phash_distance(image1, image2)

    return distance <= threshold, distance


def verify_soft_binding_extended(
    uploaded_image,
    original_image,
    dataset_folder,
    threshold=10,
):
    """
    Compare uploaded image with every dataset variant.
    """

    uploaded_image = Path(uploaded_image)
    dataset_folder = Path(dataset_folder)

    best_distance = 999
    best_file = None

    ranking = []

    for file in dataset_folder.glob("*.*"):

        if file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue

        try:

            distance = phash_distance(uploaded_image, file)

            ranking.append({

                "file": file.name,

                "distance": distance,

                "similarity": similarity(distance),

                "transformation": transformation_name(file.name),

            })

            if distance < best_distance:

                best_distance = distance

                best_file = file

        except Exception:
            pass

    ranking.sort(key=lambda x: x["distance"])

    matched = best_distance <= threshold

    if best_file is None:

        return {

            "matched": False,

            "distance": None,

            "similarity": 0,

            "matched_variant": None,

            "transformation": "Unknown",

            "ranking": []

        }

    return {

        "matched": matched,

        "distance": best_distance,

        "similarity": similarity(best_distance),

        "matched_variant": best_file.name,

        "transformation": transformation_name(best_file.name),

        "ranking": ranking,

    }