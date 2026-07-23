#!/usr/bin/env python3
"""Independent logical verifier for the activated channel classification.

The expensive affine algebra and action-current replay belong to the typed
channel handoff and are independently checked by its verifier.  This rail
checks the *distinct* claim-transfer problem: the activated certificate must
be a faithful, scope-preserving interpretation of that validated handoff.
It deliberately does not import the activation producer or classifier.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HANDOFF = ROOT / (
    "black_hole_programme/phase3/axial_global_connection_matrix_v5/"
    "chunks/channel-handoff-v6.json"
)
HANDOFF_VERIFIER = ROOT / (
    "black_hole_programme/phase3/axial_global_connection_matrix_v5/"
    "chunks/verify_channel_handoff_schema.py"
)
CERTIFICATE = HERE / "activated-certificate.json"
SCHEMA = HERE / "activated-schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def verify_documents(
    handoff: dict,
    certificate: dict,
    *,
    handoff_sha256: str,
) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(certificate),
        key=lambda error: list(error.path),
    )
    if errors:
        path = ".".join(str(part) for part in errors[0].path) or "root"
        fail(f"schema at {path}: {errors[0].message}")

    if certificate["input"]["handoff_sha256"] != handoff_sha256:
        fail("activated certificate does not pin the imported handoff")
    if certificate["input"]["handoff_schema"] != handoff["schema"]:
        fail("activated certificate changed the handoff schema")
    if certificate["scope"] != {
        "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
        "background": "Schwarzschild exterior with M=1",
        "sector": "axial ell=2",
        "pilot_frequency_interval": ["1/2", "129/256"],
        "positive_frequency_core": "C_c^infinity((1/2,129/256);C^3)",
        "completion": "L2([1/2,129/256];C^3)",
        "relation": "Iminus to Hplus direct_sum Iplus",
        "missing_boundary_block": "Hminus incoming data",
    }:
        fail("activated scope widened or changed")

    source_cells = handoff["cells"]
    cells = certificate["cells"]
    if len(cells) != len(source_cells):
        fail("activated cell count differs from handoff")
    cursor = Fraction(1, 2)
    unresolved: list[str] = []
    for index, (source, cell) in enumerate(zip(source_cells, cells)):
        expected_id = f"q{index}"
        if source["cell_id"] != expected_id or cell["cell_id"] != expected_id:
            fail("cell IDs are not ordered q0,q1,...")
        if cell["omega_interval"] != source["omega_interval"]:
            fail(f"{expected_id}: frequency interval changed")
        lo, hi = map(Fraction, cell["omega_interval"])
        if lo != cursor or hi <= lo:
            fail(f"{expected_id}: gap, overlap, or reversed interval")
        cursor = hi

        if source["disposition"] != "CERTIFIED":
            unresolved.append(expected_id)
            if cell["disposition"] != "UNRESOLVED":
                fail(f"{expected_id}: unresolved source was promoted")
            if cell["shortfall"] != source["shortfall"]:
                fail(f"{expected_id}: shortfall was altered")
            continue

        if cell["disposition"] != "CERTIFIED":
            fail(f"{expected_id}: certified source was silently dropped")
        payload = source["validated_payload"]
        inertia = payload["classification_witnesses"]["inertia"]
        if (
            cell["future_horizon_regular_domain_dimension"] != 3
            or cell["additional_origin_dimension"] != 2
            or cell["einstein_origin_dimension"] != 1
        ):
            fail(f"{expected_id}: horizon-origin dimensions changed")
        for endpoint, source_name in (
            ("Iminus", "gminus"),
            ("Iplus", "gplus"),
        ):
            expected_inertia = [
                inertia[source_name]["positive"],
                inertia[source_name]["negative"],
                inertia[source_name]["zero"],
            ]
            data = cell[endpoint]
            if data["populated_dimension"] != 3:
                fail(f"{expected_id}: populated dimension changed")
            if data["inertia"] != expected_inertia:
                fail(f"{expected_id}: {endpoint} inertia changed")
            if data["physical_quotient_dimension"] != sum(
                expected_inertia[:2]
            ):
                fail(f"{expected_id}: quotient dimension disagrees with inertia")
            origins = data["origins"]
            for name, dimension in (("additional", 2), ("einstein", 1)):
                restricted = origins[name]
                if restricted["status"] == "CERTIFIED" and sum(
                    restricted["inertia"]
                ) != dimension:
                    fail(
                        f"{expected_id}: {endpoint} {name} origin dimension changed"
                    )
            mixed_status = origins["einstein_additional_mixed_status"]
            mixed_rank = origins["einstein_additional_mixed_rank"]
            if (
                (mixed_status == "EXACT_ZERO" and mixed_rank != 0)
                or (mixed_status == "CERTIFIED_NONZERO" and mixed_rank != 1)
                or (mixed_status == "UNRESOLVED" and mixed_rank is not None)
            ):
                fail(f"{expected_id}: {endpoint} mixing witness is inconsistent")
        expected_horizon = [
            inertia["GHplus"]["positive"],
            inertia["GHplus"]["negative"],
            inertia["GHplus"]["zero"],
        ]
        if cell["Hplus_outward_inertia"] != expected_horizon:
            fail(f"{expected_id}: horizon inertia changed")
        if not cell["additional_global_direction_survives"]:
            fail(f"{expected_id}: injective additional origin was deleted")

        conservation = cell["current_conservation"]
        source_conservation = payload["endpoint_forms"]["conservation"]
        if conservation["identity"] != "GHplus+gplus-gminus=0":
            fail(f"{expected_id}: orientation identity changed")
        if conservation["structural_identity_witness"] != (
            source_conservation["structural_identity_witness"]
        ):
            fail(f"{expected_id}: structural-current witness changed")
        if not conservation["affine_enclosure_independently_checked"]:
            fail(f"{expected_id}: affine conservation check was dropped")

        relation = cell["one_sided_relation"]
        if relation["input"] != "Iminus" or relation["output"] != (
            "Hplus_direct_sum_Iplus"
        ):
            fail(f"{expected_id}: one-sided boundary relation changed")
        if relation["full_two_ended_scattering_matrix"]:
            fail(f"{expected_id}: partial relation called full scattering")
        if not relation["Cminus_inverse_whole_cell_certified"]:
            fail(f"{expected_id}: uncertified inverse used")
        if cell["wavepacket_multiplier_bounds"] != payload[
            "classification_witnesses"
        ]["multiplier_bounds"]:
            fail(f"{expected_id}: multiplier bounds changed")

    if cursor != Fraction(129, 256):
        fail("activated cells do not exactly cover the pilot interval")

    all_resolved = not unresolved
    parent = certificate["parent"]
    if parent["all_cells_resolved"] != all_resolved:
        fail("parent resolved flag disagrees with cells")
    if parent["unresolved_cells"] != unresolved:
        fail("parent unresolved-cell ledger disagrees with cells")
    for promoted in (
        "additional_global_channel_classified",
        "wavepacket_extension_certified",
        "current_conservation_certified",
        "one_sided_J_isometry_constructed",
    ):
        if parent[promoted] != all_resolved:
            fail(f"parent {promoted} crosses an unresolved cell")
    if parent["full_scattering_matrix_constructed"]:
        fail("one-sided relation called a full scattering matrix")
    expected_lifecycle = "CERTIFIED" if all_resolved else "SCOPED_SHORTFALL"
    if certificate["lifecycle"] != expected_lifecycle:
        fail("lifecycle disagrees with cell dispositions")


def main() -> int:
    if not HANDOFF.is_file() or not CERTIFICATE.is_file():
        print("NOT_ACTIVATED: handoff or activated certificate is absent")
        return 4
    checked = subprocess.run(
        [sys.executable, str(HANDOFF_VERIFIER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=300,
        check=False,
    )
    if checked.returncode:
        fail(
            "upstream handoff replay failed: "
            + checked.stdout[-500:]
            + checked.stderr[-500:]
        )
    handoff = json.loads(HANDOFF.read_text())
    certificate = json.loads(CERTIFICATE.read_text())
    verify_documents(handoff, certificate, handoff_sha256=sha256(HANDOFF))
    print("PASS: activated axial channel classification independently verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
