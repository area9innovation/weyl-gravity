"""Certify the three axial q-minus x q-minus L=4 cross-|n| obstructions."""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator,
)
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe import (
    canonical,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.schema.json"
INPUTS = {
    "candidate_ledger": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "parity_workload": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json",
    "candidate4": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "q2_slice": ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_qminus_pair_L4_q2_slice.json",
}
Q_PRIMARY_ANNIHILATOR = [
    2401,
    13649577984,
    -3277767710343168,
    -271550576338082463744,
    480328793324440503975936,
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


@lru_cache(maxsize=1)
def symbolic_slice() -> tuple[tuple[sp.Symbol, ...], sp.Matrix]:
    """Parse the content-addressed source slice once per certificate build."""

    value = json.loads(INPUTS["q2_slice"].read_text())
    variables = sp.symbols("k_1 omega_1 k_2 omega_2", real=True)
    local = dict(zip(value["variables"], variables, strict=True))
    local["sqrt"] = sp.sqrt
    source = sp.Matrix([
        sp.sympify(row, locals=local) for row in value["source_action_rows"]
    ])
    return variables, source


def specialized_source(
    k_1: sp.Expr,
    omega_1: sp.Expr,
    k_2: sp.Expr,
    omega_2: sp.Expr,
) -> sp.Matrix:
    variables, source = symbolic_slice()
    return source.subs(dict(zip(
        variables, (k_1, omega_1, k_2, omega_2), strict=True
    )))


@lru_cache(maxsize=1)
def q_primary_symbolic_adjoint_certificate() -> dict[str, object]:
    """Prove the q-primary left-kernel identity before radical specialization."""

    momentum, frequency, target_mass = sp.symbols(
        "K Omega mu", real=True
    )
    adjoint = sp.Matrix([
        -2 * (20 * momentum**2 - target_mass * momentum**2 - 20),
        2 * momentum * frequency * (20 - target_mass),
        -2 * (
            20 * momentum**2
            - target_mass * momentum**2
            + 400
            - 20 * target_mass
            - 20
        ),
        20,
    ])
    action, (eigenvalue, target_momentum, target_frequency) = _action_operator()
    defect = action.subs({
        eigenvalue: 20,
        target_momentum: momentum,
        target_frequency: frequency,
    }).T * adjoint
    shell = frequency**2 - momentum**2 - target_mass
    mass_polynomial = target_mass**2 - 40 * target_mass + 360
    shell_remainders = [
        sp.factor(sp.rem(sp.Poly(sp.expand(entry), frequency), sp.Poly(shell, frequency)).as_expr())
        for entry in defect
    ]
    final_remainders = [
        sp.factor(sp.rem(remainder, mass_polynomial, target_mass))
        for remainder in shell_remainders
    ]
    if final_remainders != [0, 0, 0, 0]:
        raise AssertionError(f"q-primary symbolic adjoint failed: {final_remainders}")
    return {
        "variables": ["K", "Omega", "mu"],
        "shell_relation": str(shell),
        "q_mass_polynomial": str(mass_polynomial),
        "shell_remainders_before_q_mass_reduction": [
            str(value) for value in shell_remainders
        ],
        "final_remainders": ["0", "0", "0", "0"],
    }


def q_candidate(index: int, target_sign: int, row: dict[str, object]) -> dict[str, object]:
    rho = parse(str(row["rho"]))
    k_1, k_2 = sp.sqrt(rho), -2 * sp.sqrt(rho)
    offset = 6 - 2 * sp.sqrt(3)
    omega_1 = sp.sqrt(rho + offset)
    omega_2 = sp.sqrt(4 * rho + offset)
    momentum = k_1 + k_2
    frequency = omega_1 + omega_2
    target_mass = 20 + target_sign * 2 * sp.sqrt(10)
    shell_defect = canonical(frequency**2 - momentum**2 - target_mass)
    if shell_defect != 0:
        raise AssertionError(f"candidate {index} left its q shell: {shell_defect}")

    source = specialized_source(k_1, omega_1, k_2, omega_2)
    adjoint = sp.Matrix([
        -2 * (20 * momentum**2 - target_mass * momentum**2 - 20),
        2 * momentum * frequency * (20 - target_mass),
        -2 * (
            20 * momentum**2
            - target_mass * momentum**2
            + 400
            - 20 * target_mass
            - 20
        ),
        20,
    ])
    pairing = canonical((adjoint.T * source)[0])
    witness_variable = sp.symbols("pairing")
    polynomial = sp.Poly.from_list(
        Q_PRIMARY_ANNIHILATOR, witness_variable
    )
    annihilator_defect = canonical(polynomial.as_expr().subs(witness_variable, pairing))
    if annihilator_defect != 0 or polynomial.eval(0) == 0:
        raise AssertionError(
            f"candidate {index} pairing lost its exact nonzero witness: "
            f"{annihilator_defect}"
        )
    return {
        "candidate_index": index,
        "target_branch": row["target_branch"],
        "rho": str(rho),
        "K": str(momentum),
        "Omega": str(frequency),
        "target_mass_squared_minus_K_squared": str(target_mass),
        "shell_defect": str(shell_defect),
        "source_action_rows": [str(value) for value in source],
        "adjoint_column": [str(value) for value in adjoint],
        "kernel_defect": ["0", "0", "0", "0"],
        "target_block_rank": 3,
        "cokernel_dimension": 1,
        "pairing": str(pairing),
        "pairing_annihilating_polynomial_coefficients": [
            int(value) for value in polynomial.all_coeffs()
        ],
        "annihilator_defect": str(annihilator_defect),
        "nonzero_constant_term": int(polynomial.eval(0)),
        "bounded_status": "OBSTRUCTED",
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    rows = records["candidate_ledger"]["candidate_ledger"]["rows"]
    expected_targets = {3: "q_minus", 4: "p_extra", 5: "q_plus"}
    for index, target in expected_targets.items():
        row = rows[index - 1]
        if not (
            row["first_branch"] == row["second_branch"] == "q_minus"
            and row["target_branch"] == target
            and row["output_ell"] == 4
            and row["canonical_signed_momenta"] == [1, -2]
            and row["admissible_temporal_channel"] == "SUM"
        ):
            raise AssertionError(f"candidate {index} triplet row changed: {row}")

    minus = q_candidate(3, -1, rows[2])
    plus = q_candidate(5, 1, rows[4])
    if (
        minus["pairing_annihilating_polynomial_coefficients"]
        != plus["pairing_annihilating_polynomial_coefficients"]
    ):
        raise AssertionError("candidate 3/5 common annihilator changed")
    common_polynomial = minus["pairing_annihilating_polynomial_coefficients"]
    if common_polynomial != Q_PRIMARY_ANNIHILATOR:
        raise AssertionError(f"candidate 3/5 annihilator changed: {common_polynomial}")

    primary = records["polar_operator"]["characteristic_and_module"]
    if primary["primary_decomposition"] != "(K[omega]/(p))^2 direct-sum K[omega]/(q)":
        raise AssertionError("certified polar primary decomposition changed")

    candidate4 = records["candidate4"]
    if not candidate4["classification"]["bounded_candidate_4_obstructed"]:
        raise AssertionError("candidate 4 obstruction input changed")
    candidate4_summary = {
        "candidate_index": 4,
        "target_branch": "p_extra",
        "rho": candidate4["candidate"]["rho"],
        "K": candidate4["candidate"]["K"],
        "Omega": candidate4["candidate"]["Omega"],
        "shell_defect": candidate4["candidate"]["p_shell_defect"],
        "target_block_rank": candidate4["polar_p_cokernel"]["target_block_rank"],
        "cokernel_dimension": candidate4["polar_p_cokernel"]["cokernel_dimension"],
        "pairings": candidate4["polar_p_cokernel"]["pairings"],
        "nonzero_norm_witness": candidate4["polar_p_cokernel"]["quadratic_field_norm_witness"],
        "bounded_status": "OBSTRUCTED",
    }
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-axial-qminus-L4-triplet-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_QMINUS_L4_TRIPLET_OBSTRUCTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_EXPLICIT_THREE_ROW_ELL2_TWO_ABS_MOMENTUM_FAMILY",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 at three separately tuned algebraic circumferences",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "axial q-minus ell=2,m=0 on n=+1 crossed with axial q-minus ell=2,m=0 on n=-2",
            "degree": 2,
            "parity": "axial times axial input; polar L=4 output",
            "ell": "2 times 2 -> 4",
            "m": "0+0 -> 0",
            "k": "signed compact-momentum integers (+1,-2)",
            "omega": "positive-frequency SUM channel",
        },
        "triplet": [minus, candidate4_summary, plus],
        "q_primary_symbolic_adjoint": q_primary_symbolic_adjoint_certificate(),
        "q_primary_common_nonzero_witness": {
            "annihilating_polynomial_coefficients": common_polynomial,
            "constant_term": common_polynomial[-1],
            "zero_is_not_a_root": True,
            "certified_polar_primary_decomposition": primary["primary_decomposition"],
        },
        "second_order_verdict": {
            "correction_class": "BOUNDED_OR_FINITE_QUASIPERIODIC",
            "candidate_3": "OBSTRUCTED",
            "candidate_4": "OBSTRUCTED",
            "candidate_5": "OBSTRUCTED",
            "smooth_secular_status": "OPEN",
            "causal_retarded_status": "NO_CERTIFIED_MAP",
        },
        "workload_progress": {
            "axisymmetric_L4_coefficients_total": 108,
            "resolved_axisymmetric_L4_coefficients": 4,
            "remaining_axisymmetric_L4_coefficients": 104,
            "remaining_nonaxisymmetric_L1_L3_coefficients": 56,
            "complete_two_fibre_tangent_cone_classified": False,
        },
        "classification": {
            "complete_axial_qminus_qminus_L4_candidate_triplet_classified": True,
            "qminus_target_pairing_nonzero": True,
            "p_extra_target_pairing_nonzero": True,
            "qplus_target_pairing_nonzero": True,
            "all_three_declared_tangents_bounded_obstructed": True,
            "all_axisymmetric_L4_coefficients_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "For axial q-minus inputs on the first two absolute momentum fibres, changing the resonant L=4 target from q-minus to p-extra to q-plus does not remove the bounded obstruction. The q-minus and q-plus pairings obey one exact quartic whose nonzero constant term excludes a vanishing pairing.",
        "next_gate": "extend the content-addressed source slices to the remaining axial/polar branch and parity representatives, leaving 104 axisymmetric L4 coefficients",
        "claim_boundary": "This classifies only candidates 3,4,5 in the axial-axial q-minus/q-minus L4 channel at three separate circumferences. It does not identify those fibres, classify the other 160 workload coefficients, smooth-secular or causal corrections, the complete tangent cone, residual observables or quantum states.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_qminus_L4_triplet --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("stale axial q-minus L4 obstruction-triplet certificate")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_QMINUS_L4_TRIPLET_OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
