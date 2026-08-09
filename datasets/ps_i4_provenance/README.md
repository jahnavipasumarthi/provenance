# PS-I4 dataset — Signed media and the platform gauntlet

`python generate.py` regenerates everything deterministically (SEED = 20260806).

## Layout
```
public/assets/                 504 JPEGs — 84 base scenes × 6 variants
public/manifests/              C2PA-shaped signed manifests (Ed25519)
public/trust_list.json         two issuers: northcam (active), ghostsign (revoked)
public/assets_index.csv        file → manifest mapping, nothing else
public/user_study_stimuli.csv  32 items for the human interface test
answer_key/labels.csv          ORGANISERS ONLY — category and correct verdict
answer_key/user_study_expected.csv  ORGANISERS ONLY
```

## Categories (base scenes, n=84)
| Category | n | Correct verdict |
|---|---|---|
| unsigned_authentic | 24 | no credential — **no inference possible** |
| signed_authentic | 14 | origin confirmed |
| signed_edit_declared | 14 | valid, edits disclosed |
| signed_staged_scene | 11 | **valid signature, staged content** |
| signed_tampered_undeclared | 7 | credential broken, pixels altered |
| signed_untrusted_issuer | 7 | signature verifies, issuer revoked |
| unsigned_generated | 7 | no credential — no inference possible |

Note the two largest groups: unsigned-but-authentic media is the plurality, and
`unsigned_authentic` and `unsigned_generated` share the *same* correct verdict.
An interface that says anything stronger than "unknown" about either has failed.

The staged scenes are **not visually marked**. A staged photograph looks like a
candid one; that is why provenance cannot attest to truth.

## Gauntlet variants
`original`, `recompress_q40`, `crop_10pct`, `resize_640`, `screenshot_sim`,
`platform_strip`. Median pHash Hamming distance from the signed soft binding:

| Variant | Honest | Tampered |
|---|---|---|
| original / platform_strip / recompress_q40 / resize_640 | **0** | 15 |
| screenshot_sim | 12 | 14 |
| crop_10pct | **24** | 28 |

Read that table carefully. Hard binding (sha256) dies on *every* transform
including honest recompression. Soft binding survives recompression perfectly —
and then an **honest 10% crop (24) scores as more altered than actual tampering
(15)**. A single global pHash threshold cannot separate these classes. Beating
this needs crop-invariant matching — block-level hashing, keypoint
correspondence, or a registration step before comparison. This overlap is
deliberate and it is the technical core of the problem.

## Verifying a manifest
Signature is Ed25519 over `json.dumps(claim, sort_keys=True, separators=(',',':'))`.
Public keys are in `trust_list.json`. A valid signature from `ghostsign` proves
the bytes came from that issuer and tells you nothing about whether to believe it.
