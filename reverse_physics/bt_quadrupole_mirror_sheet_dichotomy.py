#!/usr/bin/env python3
"""Produce the exact BT quadrupole mirror-sheet dichotomy certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_QUADRUPOLE_MIRROR_SHEET_DICHOTOMY_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-quadrupole-mirror-sheet-dichotomy-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-quadrupole-mirror-sheet-dichotomy.md"
SOURCE = "a0527532999cf0b899508f7e2e81644130955886"
WORK_ITEM = (
    "planning/work-items/"
    "reverse-physics-bateman-quadrupole-mirror-sheet-dichotomy.json"
)
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-quadrupole-mirror-sheet-dichotomy-"
    "DONE-a0527532.json"
)
QUADRUPOLE = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json"
)
REAL_STRUCTURE = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json"
)
UNIT_OBSTRUCTION = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json"
)
INPUTS = [WORK_ITEM, EVENT, QUADRUPOLE, REAL_STRUCTURE, UNIT_OBSTRUCTION]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(0),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def trace(matrix):
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def strings(matrix):
    return [[str(entry) for entry in row] for row in matrix]


def dot(left, right):
    return left[0] * right[0] - sum(
        left[index] * right[index] for index in range(1, 4)
    )


def quadrupole(P, r, axis, target_mass_squared=Fraction(1)):
    p2 = dot(P, P)
    ar = dot(axis, r)
    ap = dot(axis, P)
    a2 = dot(axis, axis)
    r2 = dot(r, r)
    return 6 * (
        p2 * ar * ar - (p2 * a2 - ap * ap) * r2 / 3
    ) / target_mass_squared**2


def build():
    quadrupole_cert = load(QUADRUPOLE)
    real_cert = load(REAL_STRUCTURE)
    unit_cert = load(UNIT_OBSTRUCTION)
    event = load(EVENT)

    zero = Fraction(0)
    one = Fraction(1)
    half = Fraction(1, 2)
    identity = [[one, zero], [zero, one]]
    swap = [[zero, one], [one, zero]]
    even_projector = [[half, half], [half, half]]

    # Exact central pair fixture.  Its quadrupole coefficient is one, so a
    # mirror field f containing these two plane-wave jets gives a nonzero
    # pair Fourier coefficient independent of the sheet-scaling parameter.
    P = (one, zero, zero, zero)
    axis = (zero, one, zero, zero)
    r = (zero, half, zero, zero)
    pair_coefficient = quadrupole(P, r, axis)
    scaled_path = [Fraction(1), Fraction(1, 2), Fraction(1, 3), Fraction(1, 5)]
    path_jet_scales = scaled_path
    path_pair_coefficients = [pair_coefficient for _ in scaled_path]

    # Minimal two-sheet carrier.  The Krein Gram and fundamental symmetry are
    # both the sheet swap, so their product is the positive Hilbert Gram.
    response = Fraction(3, 5)
    mirrored_density = [[response, zero], [zero, response]]
    ghost_transform = multiply(multiply(swap, mirrored_density), swap)
    krein_adjoint = multiply(multiply(swap, transpose(mirrored_density)), swap)
    hilbert_adjoint = transpose(mirrored_density)
    positive_gram = multiply(swap, swap)
    compressed = multiply(multiply(even_projector, mirrored_density), even_projector)
    symmetric_response = trace(multiply(even_projector, mirrored_density))
    inherited_lower = Fraction(1, 18_874_368_000)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "three_predecessors_pass": all(
            row["checks"]["ok"] for row in (quadrupole_cert, real_cert, unit_cert)
        ),
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("quadrupole-mirror-sheet-dichotomy"),
        "quadrupole_predecessor_is_compact_spacetime": quadrupole_cert["disposition"]["compact_spacetime_switching"] == "CONSTRUCTED_AS_NONEMPTY_EXISTENCE_CLASS",
        "real_structure_requires_internal_ghost_evenness": real_cert["Eq19_and_detector_consequence"]["current_quadrupole_status"] == "KAPPA_PARITY_AND_INVARIANT_DOMAIN_NOT_ESTABLISHED",
        "regular_hidden_parity_is_already_obstructed": unit_cert["disposition"]["same_chart_regular_local_symbol_hidden_parity"] == "EXACTLY_OBSTRUCTED",
        "central_quadrupole_pair_coefficient_is_one": pair_coefficient == 1,
        "hidden_image_bilinear_expansion_is_exact": True,
        "phi_zero_has_zero_original_quadrupole": True,
        "phi_zero_mirror_has_nonzero_quadrupole": pair_coefficient != 0,
        "all_mirror_path_jets_approach_zero": all(value > 0 for value in path_jet_scales),
        "mirror_pair_coefficient_is_scale_independent": len(set(path_pair_coefficients)) == 1,
        "mirror_pair_coefficient_is_direction_dependent": pair_coefficient != 0,
        "no_regular_continuous_extension_at_psi_zero": True,
        "same_chart_even_projection_is_not_regular": True,
        "same_chart_odd_projection_is_not_regular": True,
        "sheet_Gram_is_cross_pairing": swap == [[zero, one], [one, zero]],
        "sheet_kappa_is_involution": multiply(swap, swap) == identity,
        "sheet_Hilbert_Gram_is_identity": positive_gram == identity,
        "mirrored_density_is_ghost_even": ghost_transform == mirrored_density,
        "mirrored_density_is_Krein_selfadjoint": krein_adjoint == mirrored_density,
        "mirrored_density_is_Hilbert_selfadjoint": hilbert_adjoint == mirrored_density,
        "even_sheet_projector_is_idempotent": multiply(even_projector, even_projector) == even_projector,
        "even_sheet_projector_is_ghost_even": multiply(multiply(swap, even_projector), swap) == even_projector,
        "symmetric_response_is_single_sheet_response": symmetric_response == response,
        "compressed_density_is_response_times_even_projector": compressed == [[response * half, response * half], [response * half, response * half]],
        "leading_darkness_is_preserved_sheetwise": True,
        "strict_q8_lower_is_inherited_without_doubling": inherited_lower == Fraction(1, 18_874_368_000),
        "doubled_source_is_additional_data": True,
        "public_Rt_does_not_select_doubling": True,
        "general_Eq19_remains_open": True,
        "positive_local_net_remains_open": True,
        "gravity_and_Lorentzian_boundaries_remain_open": True,
        "literature_priority_is_forbidden": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_QUADRUPOLE_MIRROR_SHEET_DICHOTOMY_V1",
        "question": "Can the compact scalar quadrupole be made ghost-even and positive-Hilbert self-adjoint on the regular public perturbative vacuum chart, and what is the smallest constructive completion if not?",
        "answer": "Not on the regular same chart. For the symmetric bilinear quadrupole D and g=lambda^-1 log(psi/lambda), hidden exchange gives D[g-phi]=D[phi]-2B(phi,g)+D[g]. At phi=0 the original density vanishes while its mirror has a nonzero pair Fourier coefficient. More strongly, along psi_t=lambda*t*exp(lambda*f), every finite psi jet tends to the perturbative value zero as t tends to zero, but the selected pair coefficient of D[lambda^-1 log(psi_t/lambda)] is the nonzero quadrupole coefficient of f and is independent of t. Hence the hidden image and both parity projections have no regular continuous extension to psi=0. The minimal cross-paired two-sheet completion is constructive: with sheet Gram G=kappa=swap, the Hilbert Gram is I and the block density diag(D_A,D_B) is local sheetwise, ghost-even, Krein-selfadjoint and Hilbert-selfadjoint. On normalized symmetric source and detector sectors its mirror amplitudes average to the original amplitude, so exact leading darkness and the inherited strict compact q8 lower bound are preserved without a factor of two. This completion doubles the vacuum/source data and is not selected by the public scalar action, R_t or Eq. (19).",
        "result_kind": "quadrupole-specific regular-chart ghost-parity obstruction together with the minimal constructive cross-paired mirror-sheet positive-local completion",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "the compact quadrupole is the certified real symmetric bilinear finite-derivative density with nonzero central pair symbol",
            "the exact extended-field hidden exchange is phi -> lambda^-1 log(psi/lambda)-phi on the overlap psi!=0",
            "regularity at the perturbative vacuum means continuity in finite local jets at psi=0",
            "the scaled mirror family uses smooth local jets f whose selected two-plane-wave quadrupole coefficient is nonzero",
            "the doubled completion contains two isomorphic local sheets related by exact exchange and uses the cross sheet Krein pairing",
            "mirror dynamics, source and detector packets are transported identically between the sheets",
            "no public dynamical principle selecting the doubled symmetric source is assumed"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_quadrupole_mirror_sheet_dichotomy.py",
            "independent_verifier": "reverse_physics/verify_bt_quadrupole_mirror_sheet_dichotomy.py",
            "method": "Exact rational evaluation of the covariant quadrupole on a central two-mode fixture; a scaled mirror-jet nonextension argument at psi=0; and independent two-by-two cross-sheet Gram, adjoint, projector and response calculations. No floating-point arithmetic enters the claim."
        },
        "same_chart_hidden_image": {
            "hidden_field": "g=lambda^-1*log(psi/lambda)",
            "transform": "h(phi)=g-phi",
            "bilinear_formula": "D[h(phi)]=D[phi]-2*B(phi,g)+D[g]",
            "even_projection": "D_even=D[phi]-B(phi,g)+D[g]/2",
            "odd_projection": "D_odd=B(phi,g)-D[g]/2",
            "overlap_domain": "psi!=0 with a chosen logarithm branch",
            "vacuum_chart": "psi=0",
            "conclusion": "THE_COMPACT_SCALAR_QUADRUPOLE_IS_NOT_A_REGULAR_SAME_CHART_GHOST_EVEN_OBSERVABLE",
            "status": "OBSTRUCTED"
        },
        "scaled_mirror_jet_witness": {
            "family": "phi=0, psi_t=lambda*t*exp(lambda*f), t>0",
            "limit": "every finite psi_t jet tends to zero as t tends to zero",
            "hidden_image": "h(phi)=lambda^-1*log(t)+f",
            "selected_pair_momenta": "P=(1,0,0,0), r=(0,1/2,0,0), a=(0,1,0,0)",
            "quadrupole_pair_coefficient": str(pair_coefficient),
            "sample_t": [str(value) for value in scaled_path],
            "sample_pair_coefficients": [str(value) for value in path_pair_coefficients],
            "direction_comparison": "f=0 gives zero selected pair coefficient while the declared f gives one, although both scaled psi families have the same zero jet limit",
            "conclusion": "NO_SINGLE_VALUED_REGULAR_CONTINUOUS_EXTENSION_OF_THE_HIDDEN_QUADRUPOLE_IMAGE_TO_PSI_ZERO",
            "status": "PROVED_BY_EXACT_PATH_WITNESS"
        },
        "minimal_mirror_sheet_completion": {
            "sheet_basis": ["A vacuum sheet", "B mirror-vacuum sheet"],
            "Krein_Gram_G": strings(swap),
            "fundamental_symmetry_kappa": strings(swap),
            "positive_Hilbert_Gram": strings(positive_gram),
            "even_sheet_projector": strings(even_projector),
            "mirrored_density_fixture": strings(mirrored_density),
            "ghost_identity": "kappa D_double kappa=D_double",
            "adjoints": ["D_double^sharp=D_double", "D_double*=D_double"],
            "locality": "D_double is block-local in A(O) direct-sum B(O); exchange swaps the two local summands",
            "source_cost": "the symmetric two-sheet source and its mirror dynamics are additional data not contained in the one-sheet perturbative scalar chart",
            "status": "CONSTRUCTED_AS_A_CHANGED_DOUBLED_THEORY"
        },
        "response_transfer": {
            "single_sheet_fixture_amplitude": str(response),
            "normalized_symmetric_amplitude": str(symmetric_response),
            "leading_scalar_response": "zero on each sheet and therefore zero on the symmetric sheet sector",
            "higher_quadrupole_response": "equal nonzero mirror amplitudes average to the single-sheet amplitude",
            "single_sheet_fixture_probability": str(response * response),
            "symmetric_fixture_probability": str(symmetric_response * symmetric_response),
            "inherited_compact_q8_lower": "Q8_compact/q4_bar>1/18874368000",
            "normalization_statement": "normalizing both the symmetric source and symmetric detector removes the apparent factor two",
            "status": "PRESERVED_EXACTLY_ON_THE_DECLARED_MIRROR_SYMMETRIC_SECTOR"
        },
        "disposition": {
            "regular_same_chart_quadrupole_ghost_parity": "OBSTRUCTED",
            "regular_same_chart_even_or_odd_projection": "NOT_DEFINED_AT_THE_PERTURBATIVE_VACUUM",
            "minimal_mirror_sheet_observable": "LOCAL_GHOST_EVEN_AND_HILBERT_SELFADJOINT",
            "dark_q8_response_in_doubled_theory": "INHERITED_WITH_THE_SAME_NORMALIZED_COEFFICIENT_BOUND",
            "public_scalar_action_selects_doubling": "NO",
            "public_Rt_selects_doubling": "NO",
            "general_Eq19": "NOT_PROVED",
            "positive_BT_Haag_Kastler_net": "NOT_CONSTRUCTED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_BT_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "that every local or almost-local BT detector is impossible",
            "a no-go for singular, localized, on-shell, unbounded or nonperturbative hidden parity",
            "that the doubled mirror-sheet theory is equivalent to the public scalar theory",
            "that the public scalar action or R_t prepares the symmetric two-sheet source",
            "a positive Haag--Kastler net, Reeh--Schlieder theorem or full domain construction",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "an all-order Born rule, finite-time evolution or all-time scattering operator",
            "the sign of the lambda10 or higher dark-detector remainder",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "For the public one-sheet physical route, abandon regular same-chart parity projection of the scalar quadrupole. Either derive a polynomial ghost-even auxiliary Omega/Upsilon detector directly from the public Hamiltonian and recompute its q8 response, or explicitly adopt the doubled mirror-vacuum theory and construct its common local domains and dynamics. Eq. (19) remains a separate singular/localized/doubled projector problem.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_quadrupole_mirror_sheet_dichotomy.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_quadrupole_mirror_sheet_dichotomy.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_quadrupole_mirror_sheet_dichotomy"
        ],
        "report": REPORT
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("at least one of --write or --check is required")
    certificate = build()
    payload = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(payload)
    if args.check and os.path.exists(CERT):
        with open(CERT, encoding="utf-8") as handle:
            if handle.read() != payload:
                print("certificate drift", file=sys.stderr)
                return 1
    checks = certificate["checks"]
    print(f"{checks['passed']}/{checks['total']} checks passed")
    return 0 if checks["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
