#!/usr/bin/env python3

"""
PS-I4 Provenance Dataset Generator

Creates:
- synthetic images
- signed manifests
- Ed25519 signatures
- C2PA-like provenance records
- platform transformations
- evaluation CSV files
"""

import os
import io
import csv
import json
import base64
import random
import hashlib

import numpy as np

from PIL import Image, ImageDraw, ImageFilter

from scipy.fftpack import dct

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey
)

from cryptography.hazmat.primitives import serialization


# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------

SEED = 20260806

random.seed(SEED)
np.random.seed(SEED)


OUT = os.path.dirname(
    os.path.abspath(__file__)
)


PUBLIC_DIR = os.path.join(
    OUT,
    "public"
)


ANSWER_DIR = os.path.join(
    OUT,
    "answer_key"
)


ASSETS_DIR = os.path.join(
    PUBLIC_DIR,
    "assets"
)


MANIFEST_DIR = os.path.join(
    PUBLIC_DIR,
    "manifests"
)


for folder in [
    PUBLIC_DIR,
    ANSWER_DIR,
    ASSETS_DIR,
    MANIFEST_DIR
]:
    os.makedirs(
        folder,
        exist_ok=True
    )


SIZE = 320

N_BASE = 84



# -------------------------------------------------
# DATASET CLASSES
# -------------------------------------------------


CATEGORIES = [

    (
        "signed_authentic",
        0.22,
        True,
        "northcam",
        False,
        False
    ),


    (
        "signed_edit_declared",
        0.13,
        True,
        "northcam",
        False,
        False
    ),


    (
        "signed_tampered_undeclared",
        0.12,
        True,
        "northcam",
        False,
        True
    ),


    (
        "signed_staged_scene",
        0.18,
        True,
        "northcam",
        True,
        False
    ),


    (
        "signed_untrusted_issuer",
        0.08,
        True,
        "ghostsign",
        False,
        False
    ),


    (
        "unsigned_authentic",
        0.22,
        False,
        None,
        False,
        False
    ),


    (
        "unsigned_generated",
        0.10,
        False,
        None,
        False,
        False
    )

]
# -------------------------------------------------
# CREATE ISSUERS
# -------------------------------------------------

issuers = {}


for name, trusted in [
    ("northcam", True),
    ("ghostsign", False)
]:

    private_key = Ed25519PrivateKey.generate()

    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    issuers[name] = {

        "private_key": private_key,

        "public_key_b64":
            base64.b64encode(
                public_key
            ).decode(),

        "trusted": trusted

    }



# -------------------------------------------------
# PERCEPTUAL HASH
# -------------------------------------------------

def phash(image):

    """
    Creates a 64 bit perceptual hash.
    """

    gray = np.asarray(

        image.convert("L")
        .resize((32, 32), Image.LANCZOS),

        dtype=float

    )


    transformed = dct(

        dct(
            gray,
            axis=0,
            norm="ortho"
        ),

        axis=1,
        norm="ortho"

    )


    low_frequency = transformed[:8, :8]


    values = low_frequency.flatten()[1:]


    median = np.median(values)


    bits = values > median


    return "".join(

        "1" if bit else "0"

        for bit in bits

    )




# -------------------------------------------------
# HAMMING DISTANCE
# -------------------------------------------------

def hamming(hash1, hash2):

    return sum(

        a != b

        for a, b in zip(
            hash1,
            hash2
        )

    )



# -------------------------------------------------
# IMAGE GENERATOR
# -------------------------------------------------

def render_scene(
        index,
        staged=False,
        generated=False
):

    rng = random.Random(
        SEED + index
    )


    image = Image.new(
        "RGB",
        (SIZE, SIZE)
    )


    draw = ImageDraw.Draw(
        image
    )


    top_color = (

        rng.randint(30,120),
        rng.randint(60,150),
        rng.randint(110,220)

    )


    bottom_color = (

        rng.randint(120,235),
        rng.randint(110,210),
        rng.randint(80,180)

    )



    for y in range(SIZE):

        factor = y / SIZE


        color = tuple(

            int(
                top_color[c]
                +
                (
                    bottom_color[c]
                    -
                    top_color[c]
                )
                *
                factor
            )

            for c in range(3)

        )


        draw.line(

            [
                (0,y),
                (SIZE,y)
            ],

            fill=color

        )



    for _ in range(
        rng.randint(4,9)
    ):

        x = rng.randint(
            0,
            SIZE-60
        )

        y = rng.randint(
            0,
            SIZE-60
        )


        width = rng.randint(
            30,
            110
        )


        height = rng.randint(
            30,
            110
        )


        colour = (

            rng.randint(20,240),
            rng.randint(20,240),
            rng.randint(20,240)

        )


        if rng.random() < 0.5:

            draw.ellipse(

                [
                    x,
                    y,
                    x+width,
                    y+height
                ],

                fill=colour

            )

        else:

            draw.rectangle(

                [
                    x,
                    y,
                    x+width,
                    y+height
                ],

                fill=colour

            )
                # bottom label area
    draw.rectangle(

        [
            8,
            SIZE - 30,
            SIZE - 8,
            SIZE - 8
        ],

        fill=(12,12,12)

    )


    draw.text(

        (
            14,
            SIZE - 25
        ),

        f"SCENE {index:03d}",

        fill=(240,240,240)

    )



    # add sensor noise

    array = np.asarray(
        image,
        dtype=float
    )


    noise_level = (
        1.8
        if generated
        else
        6.0
    )


    array += np.random.normal(

        0,
        noise_level,
        array.shape

    )



    if generated:

        image2 = Image.fromarray(

            np.clip(
                array,
                0,
                255
            )
            .astype("uint8")

        )


        image2 = image2.filter(

            ImageFilter.GaussianBlur(
                0.4
            )

        )


        array = np.asarray(

            image2,
            dtype=float

        )



    return Image.fromarray(

        np.clip(
            array,
            0,
            255
        )
        .astype("uint8")

    )




# -------------------------------------------------
# JPEG CONVERTER
# -------------------------------------------------

def jpeg_bytes(
        image,
        quality=88
):

    buffer = io.BytesIO()


    image.save(

        buffer,

        format="JPEG",

        quality=quality

    )


    return buffer.getvalue()




# -------------------------------------------------
# SIGN MANIFEST
# -------------------------------------------------

def sign_manifest(
        claim,
        issuer
):

    payload = json.dumps(

        claim,

        sort_keys=True,

        separators=(
            ",",
            ":"
        )

    ).encode()



    signature = issuers[issuer][
        "private_key"
    ].sign(

        payload

    )


    return {


        "claim":
            claim,


        "signature_b64":
            base64.b64encode(
                signature
            ).decode(),


        "issuer":
            issuer,


        "public_key_b64":
            issuers[issuer][
                "public_key_b64"
            ],


        "algorithm":
            "Ed25519"


    }




# -------------------------------------------------
# PLATFORM GAUNTLET
# -------------------------------------------------

def gauntlet(image):


    outputs = {}


    outputs["original"] = image



    outputs["recompress_q40"] = Image.open(

        io.BytesIO(

            jpeg_bytes(
                image,
                40
            )

        )

    )


    crop = int(
        SIZE * 0.10
    )


    outputs["crop_10pct"] = (

        image.crop(

            (
                crop,
                crop,
                SIZE-crop,
                SIZE-crop
            )

        )

        .resize(

            (
                SIZE,
                SIZE
            ),

            Image.LANCZOS

        )

    )


    outputs["resize_640"] = image.resize(

        (
            640,
            640
        ),

        Image.LANCZOS

    )
        # simulate screenshot

    small = image.resize(

        (
            int(SIZE * 0.92),
            int(SIZE * 0.92)

        ),

        Image.LANCZOS

    )


    small = small.filter(

        ImageFilter.GaussianBlur(
            0.3
        )

    )


    canvas = Image.new(

        "RGB",

        (
            SIZE,
            SIZE
        ),

        (18,18,20)

    )


    canvas.paste(

        small,

        (
            13,
            13
        )

    )


    outputs["screenshot_sim"] = Image.open(

        io.BytesIO(

            jpeg_bytes(
                canvas,
                72
            )

        )

    )



    # metadata stripped version

    outputs["platform_strip"] = Image.open(

        io.BytesIO(

            jpeg_bytes(
                image,
                62
            )

        )

    )


    return outputs




# -------------------------------------------------
# EXPECTED VERDICTS
# -------------------------------------------------

VERDICTS = {


    "signed_authentic":
        "credential_valid_origin_confirmed",



    "signed_edit_declared":
        "credential_valid_edits_disclosed",



    "signed_tampered_undeclared":
        "credential_broken_content_altered",



    "signed_staged_scene":
        "credential_valid_but_scene_staged",



    "signed_untrusted_issuer":
        "signature_valid_issuer_not_trusted",



    "unsigned_authentic":
        "no_credential_no_inference_possible",



    "unsigned_generated":
        "no_credential_no_inference_possible"


}




# -------------------------------------------------
# MAIN GENERATOR
# -------------------------------------------------

def main():


    rows = []

    keyrows = []


    weights = [

        category[1]

        for category in CATEGORIES

    ]



    for index in range(N_BASE):


        category, _, signed, issuer, staged, tampered = random.choices(

            CATEGORIES,

            weights=weights

        )[0]



        generated = (

            category == "unsigned_generated"

        )


        image = render_scene(

            index,

            staged=staged,

            generated=generated

        )


        asset_id = f"A{index:03d}"



        manifest = None



        if signed:


            claim = {


                "asset_id":
                    asset_id,


                "capture_device":
                    (
                        "NorthCam ONE"

                        if issuer=="northcam"

                        else

                        "unknown-app"
                    ),


                "captured_at":
                    "2026-01-01T12:00:00Z",


                "assertions":
                    [
                        {
                            "action":
                                "c2pa.created",

                            "software":
                                "camera-firmware-4.1"
                        }
                    ],


                "hard_binding_sha256":
                    hashlib.sha256(

                        jpeg_bytes(
                            image
                        )

                    ).hexdigest(),


                "soft_binding_phash":
                    phash(image)

            }
                        # add declared editing history

            if category == "signed_edit_declared":

                claim["assertions"].extend(

                    [

                        {
                            "action":
                                "c2pa.color_adjustments",

                            "software":
                                "EditPro 3"

                        },

                        {

                            "action":
                                "c2pa.cropped",

                            "software":
                                "EditPro 3"

                        }

                    ]

                )



            manifest = sign_manifest(

                claim,

                issuer

            )



            # tamper after signing

            if tampered:


                draw = ImageDraw.Draw(

                    image

                )


                draw.rectangle(

                    [

                        50,

                        50,

                        180,

                        180

                    ],

                    fill=(200,30,40)

                )



            manifest_path = os.path.join(

                MANIFEST_DIR,

                f"{asset_id}.manifest.json"

            )



            with open(

                manifest_path,

                "w"

            ) as file:


                json.dump(

                    manifest,

                    file,

                    indent=2

                )





        # create all platform variants

        variants = gauntlet(

            image

        )



        for variant_name, variant_image in variants.items():


            filename = (

                f"{asset_id}__{variant_name}.jpg"

            )



            save_path = os.path.join(

                ASSETS_DIR,

                filename

            )



            variant_image.save(

                save_path,

                "JPEG",

                quality=85

            )



            if signed:


                soft_distance = hamming(

                    manifest["claim"]["soft_binding_phash"],

                    phash(variant_image)

                )


            else:


                soft_distance = ""



            hard_binding = (

                signed

                and

                not tampered

                and

                variant_name=="original"

            )



            rows.append(

                {


                    "asset_id":
                        asset_id,


                    "variant":
                        variant_name,


                    "file":
                        filename,


                    "has_manifest":
                        int(signed),


                    "manifest_file":
                        (
                            f"{asset_id}.manifest.json"

                            if signed

                            else

                            ""

                        )

                }

            )



            keyrows.append(

                {


                    "asset_id":
                        asset_id,


                    "variant":
                        variant_name,


                    "file":
                        filename,


                    "category":
                        category,


                    "issuer":
                        issuer or "",


                    "issuer_trusted":
                        int(

                            issuer is not None

                            and

                            issuers[issuer]["trusted"]

                        ),


                    "hard_binding_intact":
                        int(hard_binding),


                    "soft_binding_hamming":
                        soft_distance,


                    "pixels_tampered_after_signing":
                        int(tampered),


                    "depicts_staged_scene":
                        int(staged),


                    "is_generated":
                        int(generated),


                    "correct_verdict":
                        VERDICTS[category]

                }

            )
                # -------------------------------------------------
    # SAVE INDEX FILES
    # -------------------------------------------------

    with open(

        os.path.join(
            PUBLIC_DIR,
            "assets_index.csv"
        ),

        "w",

        newline=""

    ) as file:


        writer = csv.DictWriter(

            file,

            fieldnames=list(
                rows[0].keys()
            )

        )


        writer.writeheader()


        writer.writerows(

            rows

        )




    with open(

        os.path.join(
            ANSWER_DIR,
            "labels.csv"
        ),

        "w",

        newline=""

    ) as file:


        writer = csv.DictWriter(

            file,

            fieldnames=list(
                keyrows[0].keys()
            )

        )


        writer.writeheader()


        writer.writerows(

            keyrows

        )





    # -------------------------------------------------
    # TRUST LIST
    # -------------------------------------------------

    trust = {


        "trust_list":

        [

            {


                "issuer":
                    name,


                "public_key_b64":
                    data["public_key_b64"],


                "status":

                    (

                        "active"

                        if data["trusted"]

                        else

                        "revoked"

                    )

            }


            for name, data

            in issuers.items()

        ]

    }



    with open(

        os.path.join(

            PUBLIC_DIR,

            "trust_list.json"

        ),

        "w"

    ) as file:


        json.dump(

            trust,

            file,

            indent=2

        )




    # -------------------------------------------------
    # USER STUDY FILES
    # -------------------------------------------------

    pool = [

        item

        for item in keyrows

        if item["variant"]

        in

        [

            "original",

            "platform_strip",

            "screenshot_sim"

        ]

    ]



    staged = [

        item

        for item in pool

        if item["depicts_staged_scene"]

        and

        item["variant"]=="original"

    ]



    remaining = [

        item

        for item in pool

        if item not in staged

    ]



    sample_size = 32 - len(staged)



    if sample_size > len(remaining):

        sample_size = len(remaining)



    stimuli = staged + random.sample(

        remaining,

        sample_size

    )



    random.shuffle(

        stimuli

    )
        # -------------------------------------------------
    # WRITE USER STUDY STIMULI
    # -------------------------------------------------

    with open(

        os.path.join(

            PUBLIC_DIR,

            "user_study_stimuli.csv"

        ),

        "w",

        newline=""

    ) as file:


        writer = csv.writer(

            file

        )


        writer.writerow(

            [

                "stimulus_id",

                "file",

                "prompt_to_participant"

            ]

        )



        for number, item in enumerate(stimuli):


            writer.writerow(

                [

                    f"S{number:02d}",


                    item["file"],


                    (
                        "You are scrolling and see "
                        "this image. What, if anything, "
                        "does the interface let you conclude?"
                    )

                ]

            )





    # -------------------------------------------------
    # EXPECTED USER STUDY ANSWERS
    # -------------------------------------------------

    with open(

        os.path.join(

            ANSWER_DIR,

            "user_study_expected.csv"

        ),

        "w",

        newline=""

    ) as file:


        writer = csv.writer(

            file

        )


        writer.writerow(

            [

                "stimulus_id",

                "file",

                "category",

                "correct_interpretation"

            ]

        )



        for number, item in enumerate(stimuli):


            writer.writerow(

                [

                    f"S{number:02d}",


                    item["file"],


                    item["category"],


                    VERDICTS[

                        item["category"]

                    ]

                ]

            )





    # -------------------------------------------------
    # SUMMARY OUTPUT
    # -------------------------------------------------

    from collections import Counter



    print()

    print(
        "================================"
    )

    print(
        " PS-I4 GENERATION COMPLETE "
    )

    print(
        "================================"
    )


    print(

        "Base assets:",

        N_BASE

    )


    print(

        "Generated files:",

        len(rows)

    )


    print()


    print(

        "Categories:"

    )


    print(

        Counter(

            item["category"]

            for item in keyrows

            if item["variant"]=="original"

        )

    )





    distances = [

        item["soft_binding_hamming"]

        for item in keyrows

        if item["soft_binding_hamming"] != ""

    ]



    if distances:


        print()


        print(

            "pHash distance:",

            "min=",

            min(distances),

            "max=",

            max(distances)

        )
# -------------------------------------------------
# PROGRAM ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":

    main()