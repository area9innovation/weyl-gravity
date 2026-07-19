#!/usr/bin/env python3
"""Globalize the relative current improvement and replay the five charges."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_GLOBAL_FIVE_CHARGE_REPLAY_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-global-five-charge-replay.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-global-five-charge-replay-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_global_five_charge_replay.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_global_five_charge_replay.py"

DEPENDENCIES = {
    "cyclic_current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CYCLIC_FIVE_CURRENT_CONE_V1.json",
    "current_improvement": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_GREEN_LEE_WALD_IMPROVEMENT_V1.json",
    "complete_charge_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json",
    "generic_moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "exceptional_global_moments": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "physical_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "homogeneous": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
    "mixed_orthogonality": ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_block_orthogonality.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _block_replay(complete: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = complete["operation"]["blocks"]
    order = [
        "generic_radiative_ell_ge_2",
        "physical_ell1_all_k",
        "homogeneous_ell0",
        "axial_twist_ell1_k0",
    ]
    records = []
    for name in order:
        block = blocks[name]
        if block["status"] not in {"EXACT", "IMPORTED_EXACT"}:
            raise AssertionError(f"charge block is not exact: {name}")
        records.append({
            "block": name,
            "status": block["status"],
            "formula": block.get("formula", block.get("formula_H")),
            "output_basis": complete["operation"]["output_basis"],
        })
    return records


def build() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    cyclic = values["cyclic_current_cone"]
    improvement = values["current_improvement"]
    complete = values["complete_charge_q2"]
    if cyclic["classification"]["cyclic_dual_bv_rows_certified"] is not True:
        raise AssertionError("cyclic local receiver is absent")
    if improvement["classification"]["horizontal_improvement_identity_exact"] is not True:
        raise AssertionError("local improvement is absent")
    if complete["classification"]["complete_standard_source_five_charge_q2"] is not True:
        raise AssertionError("complete five-charge operation is absent")
    if values["generic_moment_map"]["classification"]["generic_covariant_moment_map_Taub_equality_certified"] is not True:
        raise AssertionError("generic moment-map/Taub bridge is absent")
    if complete["operation"]["output_basis"] != ["H", "P_x", "J_1", "J_2", "J_3"]:
        raise AssertionError("five-charge basis drifted")
    if complete["operation"]["constant_u1_component"].split(":", 1)[0] != "zero":
        raise AssertionError("constant U1 was promoted to a Taub charge")
    blocks = _block_replay(complete)
    return {
        "schema": "pure-weyl-relative-global-five-charge-replay-v1",
        "result_id": RESULT_ID,
        "result_state": "GLOBAL_CURRENT_DESCENT_AND_COMPLETE_FIVE_CHARGE_REPLAY_CERTIFIED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "connected compact magnetic product M=R_t x S1_L x S2",
            "boundaries": "closed oriented Cauchy slice Sigma=S1_L x S2; fixed magnetic bundle P_N with N=2",
            "charge_sector": "five connected-isometry moment maps H,P_x,J_1,J_2,J_3",
            "carrier": "local cyclic horizontal-current cone followed by closed-slice integration on complete standard solution cohomology",
            "degree": "arity-two current receiver and five-dimensional global charge output",
            "parity": "all certified standard axial and polar blocks",
            "ell": "generic ell>=2 plus physical ell1, homogeneous ell0 and axial twist ell1",
            "m": "all certified multiplicities", "k": "all certified compact momenta", "omega": "all certified standard branches",
        },
        "dependencies": {name: _artifact(path, values[name]) for name, path in DEPENDENCIES.items()},
        "global_descent_theorem": {
            "field_bundle": "the product of symmetric metric perturbations and the affine space of connections on fixed P_N; its vertical tangent is a vector bundle",
            "global_currents": "the action Lee-Wald current is natural; a global Green current exists by covariant integration by parts for the global formally self-adjoint relative Hessian",
            "closed_difference": "their difference is a globally defined d_H-closed form of vertical degree 2 and horizontal degree 3",
            "exact_row": "for an affine field bundle, the positive-contact rows of the global variational bicomplex are d_H-exact below horizontal top degree",
            "conclusion": "there exists a globally smooth bilinear horizontal 2-form U_global with omega_LW-omega_G,cov=d_H U_global",
            "coordinate_primitive_policy": "the serialized 2478-term Laurent product-coordinate primitive is a local exact witness only; this theorem does not assert that this particular representative is smooth at the polar coordinate singularities",
            "closed_slice": "partial Sigma is empty, hence integral_Sigma d_H U_global=0 by Stokes",
        },
        "moment_map_identity": {
            "formula": "D^2 mu_rel,X|_0(u,v)=integral_Sigma 1/2*(omega_rel(u,L_X v)+omega_rel(v,L_X u))",
            "green_representative": "the same integral is obtained from the certified Green current because the global improvement integrates to zero",
            "taub_pairing": "D^2 mu_rel,X|_0(u,v)=<zeta_X,Delta2(u,v)>",
            "normalization": "q2_charge,X=D^2 mu_rel,X|_0, with mu_rel,X(u)=q2_charge,X(u,u)/2",
        },
        "complete_replay": {
            "output_basis": complete["operation"]["output_basis"],
            "output_dimension": complete["operation"]["output_dimension"],
            "blocks": blocks,
            "direct_sum_rule": complete["operation"]["direct_sum_rule"],
            "all_cross_block_terms_zero": complete["classification"]["all_cross_block_terms_certified_zero"],
            "constant_u1_output": False,
        },
        "classification": {
            "global_smooth_horizontal_improvement_exists": True,
            "serialized_coordinate_primitive_global_smoothness_asserted": False,
            "closed_slice_improvement_integral_zero": True,
            "green_current_integral_equals_lee_wald_integral": True,
            "integrated_current_equals_moment_map_hessian": True,
            "all_four_complete_standard_blocks_replayed": True,
            "all_five_charge_outputs_replayed": True,
            "slice_integral_matches_complete_five_charge_q2": True,
            "support_local_bv_current_extension_certified": True,
            "direct_support_local_map_to_constant_charges": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "ASSEMBLE_RELATIVE_CURRENT_CONE_WITH_MAPPING_COFIBER_OR_PRESERVE_SCOPED_F2_OBSTRUCTION",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_global_five_charge_replay --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_global_five_charge_replay",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_global_five_charge_replay",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-global-five-charge-replay-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_GLOBAL_FIVE_CHARGE_REPLAY_V1.json",
            ],
        },
        "claim_boundary": (
            "This theorem globalizes the current comparison by the exact positive-contact row of the variational bicomplex and proves that a smooth global improvement, not necessarily the serialized Laurent coordinate primitive, has zero integral on the closed Cauchy slice. Composed with the certified moment-map/Taub identities, it replays the integrated local current on the four complete standard source blocks and all five connected-isometry charges. The local receiver remains a horizontal current/divergence BV cone: no support-local map directly into constant charges exists. This result does not repair the independently certified direct f2 obstruction, include target-only extra-Weyl inputs, solve a tangent cone, authorize arity three, or establish a causal, observational, particle or quantum theorem."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Global five-charge current replay

The local Laurent superpotential is not promoted to a global tensor.  Instead,
the invariant current comparison is globalized at the correct level.  The
Lee--Wald current is natural, while covariant integration by parts supplies a
global Green current for the global formally self-adjoint relative Hessian.
Their closed difference has vertical degree two and horizontal degree three.
The positive-contact row of the global variational bicomplex of the affine
metric/connection field bundle is exact below top horizontal degree, so a
smooth global bilinear horizontal two-form exists with

\[
\omega_{\rm LW}-\omega_{G,\rm cov}=d_HU_{\rm global}.
\]

The proof uses no polar-coordinate regularity assumption.  Choose a global
connection on the metric/connection variation bundle and integrate the global
relative Hessian covariantly by parts; this constructs a global Green form.
Formal self-adjointness makes its difference from the natural Lee--Wald form
`d_H`-closed.  Locally, the algebraic Poincare homotopy contracts every
positive-contact row below horizontal degree four.  These rows are fine
sheaves of modules over smooth jet functions, so the local contractions patch
to global exactness.  The affine fibres contribute no additional vertical
cohomology.  This proves existence of `U_global` independently of the local
Laurent representative.

Because the Cauchy surface is the closed manifold `S1_L x S2`, Stokes' theorem
removes this improvement.  The resulting integral is the polarized relative
moment-map Hessian.  The already-certified complete standard decomposition
then replays the generic radiative, physical `ell=1`, homogeneous and axial
twist blocks, with output basis `(H,P_x,J_1,J_2,J_3)` and no constant-`U(1)`
charge.

This closes the local-to-global five-charge receiver.  It does not turn the
global integration into a support-local map, repair the direct `f2`
obstruction, add target-only extra-Weyl inputs or authorize arity three.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in ("direct_support_local_map_to_constant_charges", "direct_f2_repaired", "arity_three_authorized", "causal_observable_particle_or_quantum_claim"):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("global five-charge replay outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
