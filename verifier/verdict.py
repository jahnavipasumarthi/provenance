def generate_verdict(
    signature_ok,
    hard_binding_ok,
    soft_binding_ok,
):
    """
    Generate the final provenance verdict.
    """

    if signature_ok and hard_binding_ok:

        result = {
            "status": "Verified",
            "message": "Verified provenance. This does NOT mean the content is true.",
            "color": "green",
        }

    elif soft_binding_ok:

        result = {
            "status": "Related",
            "message": "Original provenance is unavailable, but the uploaded media appears visually related.",
            "color": "orange",
        }

    else:

        result = {
            "status": "Unknown",
            "message": "No verifiable provenance found.",
            "color": "gray",
        }

    return result