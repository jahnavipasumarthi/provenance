from pathlib import Path

from flask import Flask, render_template, request, send_from_directory

from werkzeug.utils import secure_filename

from verifier.manifest import (
    load_manifest,
    find_manifest,
    get_manifest_info,
)

from verifier.hard_binding import verify_hard_binding
from verifier.signature import verify_signature
from verifier.soft_binding import (
    verify_soft_binding,
    verify_soft_binding_extended,
)
from verifier.verdict import generate_verdict

app = Flask(__name__, template_folder="viewer/templates")

# Folder where uploaded images are temporarily stored
UPLOAD_FOLDER = Path("assets/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Dataset folder
DATASET_FOLDER = Path("datasets/ps_i4_provenance/public/assets")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/media/upload/<path:filename>")
def uploaded_media(filename):
    """Serve an uploaded image for the verification result page."""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/media/dataset/<path:filename>")
def dataset_media(filename):
    """Serve a provenance reference image from the public dataset."""
    return send_from_directory(DATASET_FOLDER, filename)


@app.route("/verify", methods=["POST"])
def verify():

    # -------------------------
    # Upload Validation
    # -------------------------

    if "image" not in request.files:
        return "No image uploaded.", 400

    uploaded_file = request.files["image"]

    if uploaded_file.filename == "":
        return "No image selected.", 400

    safe_filename = secure_filename(uploaded_file.filename)

    if not safe_filename:
        return "Invalid image filename.", 400

    image_path = UPLOAD_FOLDER / safe_filename
    uploaded_file.save(image_path)

    # -------------------------
    # Find Manifest
    # -------------------------

    manifest_path = find_manifest(safe_filename)

    if manifest_path is None:

        verdict = {
            "status": "Unknown",
            "message": "No provenance manifest found.",
            "color": "gray",
        }

        return render_template(
            "result.html",
            verdict=verdict,
            manifest={},
            hard_binding={},
            signature_ok=False,
            hard_ok=False,
            soft_ok=False,
            similarity=0,
            distance=0,
            transformation="Unknown",
            matched_variant="None",
            ranking=[],
            uploaded_image_url=f"/media/upload/{safe_filename}",
            reference_image_url=None,
            matched_image_url=None,
        )

    # -------------------------
    # Load Manifest
    # -------------------------

    manifest = load_manifest(manifest_path)

    manifest_info = get_manifest_info(manifest)

    # -------------------------
    # Signature Verification
    # -------------------------

    signature_ok = verify_signature(manifest_path)

    # -------------------------
    # Hard Binding
    # -------------------------

    hard_binding = verify_hard_binding(image_path)

    hard_ok = hard_binding["verified"]

    # -------------------------
    # Original Image
    # -------------------------

    asset_id = manifest_info["asset_id"]

    original_image = DATASET_FOLDER / f"{asset_id}__original.jpg"

    if not original_image.exists():
        original_image = image_path

    # -------------------------
    # Soft Binding
    # -------------------------

    soft_ok, distance = verify_soft_binding(
        image_path,
        original_image
    )

    analysis = verify_soft_binding_extended(
        uploaded_image=image_path,
        original_image=original_image,
        dataset_folder=DATASET_FOLDER,
    )

    # -------------------------
    # Final Verdict
    # -------------------------

    verdict = generate_verdict(
        signature_ok=signature_ok,
        hard_binding_ok=hard_ok,
        soft_binding_ok=soft_ok,
    )

    return render_template(
        "result.html",

        verdict=verdict,

        manifest=manifest_info,

        signature_ok=signature_ok,

        hard_binding=hard_binding,

        hard_ok=hard_ok,

        soft_ok=soft_ok,

        similarity=analysis["similarity"],

        distance=analysis["distance"],

        transformation=analysis["transformation"],

        matched_variant=analysis["matched_variant"],

        ranking=analysis["ranking"],

        uploaded_image_url=f"/media/upload/{safe_filename}",

        reference_image_url=(
            f"/media/dataset/{original_image.name}"
            if original_image.exists()
            else None
        ),

        matched_image_url=(
            f"/media/dataset/{analysis["matched_variant"]}"
            if analysis["matched_variant"]
            else None
        ),
    )


if __name__ == "__main__":
    app.run(debug=True)