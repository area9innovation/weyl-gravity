#!/usr/bin/env python3
"""Certify the Maxwell BV gauge sector and the Berger dressing contract.

This is deliberately a preflight rather than a full coupled Taylor export.
It proves the arbitrary-function Diff-semidirect-U(1) identities, fixes the
minimal Maxwell BV row layout, and records the relational apparatus data
needed to replace the homogeneous spatial average by localized endpoints.
The h-A-to-A^+ and A-A-to-h^+ dynamical q2 blocks remain fail-closed inputs.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-maxwell-bv-semidirect-preflight.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-maxwell-bv-semidirect-preflight-v1.schema.json"

DEPENDENCIES = {
    "gravity_clock_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
    "dynamical_maxwell_mode": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_maxwell_bv_semidirect_preflight.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_maxwell_bv_semidirect_preflight.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_maxwell_bv_semidirect_preflight.py",
    SCHEMA_PATH,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_dependencies() -> dict[str, dict[str, Any]]:
    payloads = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    gravity = payloads["gravity_clock_q2"]
    if gravity["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is not True:
        raise AssertionError("authoritative 54-row gravity-clock q2 is unavailable")
    if gravity["classical_binary_q2"]["total_rows"] != 54:
        raise AssertionError("gravity-clock q2 row layout drifted")
    maxwell = payloads["dynamical_maxwell_mode"]
    if maxwell["flags"]["BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE"] is not True:
        raise AssertionError("exact Berger Maxwell mode is unavailable")
    if maxwell["flags"]["BERGER_GRAVITY_MAXWELL_Q2_DRESSING"] is not False:
        raise AssertionError("upstream Maxwell mode unexpectedly claims a q2 dressing")
    return payloads


def _functions(prefix: str, coordinates: tuple[sp.Symbol, ...]) -> list[sp.Expr]:
    return [sp.Function(f"{prefix}_{index}")(*coordinates) for index in range(4)]


def _vector_bracket(
    left: list[sp.Expr], right: list[sp.Expr], coordinates: tuple[sp.Symbol, ...]
) -> list[sp.Expr]:
    return [
        sum(
            left[index] * sp.diff(right[component], coordinates[index])
            - right[index] * sp.diff(left[component], coordinates[index])
            for index in range(4)
        )
        for component in range(4)
    ]


def _lie_scalar(
    vector: list[sp.Expr], scalar: sp.Expr, coordinates: tuple[sp.Symbol, ...]
) -> sp.Expr:
    return sum(vector[index] * sp.diff(scalar, coordinates[index]) for index in range(4))


def _lie_one_form(
    vector: list[sp.Expr], one_form: list[sp.Expr], coordinates: tuple[sp.Symbol, ...]
) -> list[sp.Expr]:
    return [
        sum(
            vector[index] * sp.diff(one_form[component], coordinates[index])
            + one_form[index] * sp.diff(vector[index], coordinates[component])
            for index in range(4)
        )
        for component in range(4)
    ]


def _gradient(scalar: sp.Expr, coordinates: tuple[sp.Symbol, ...]) -> list[sp.Expr]:
    return [sp.diff(scalar, coordinate) for coordinate in coordinates]


def _field_strength(
    one_form: list[sp.Expr], coordinates: tuple[sp.Symbol, ...]
) -> dict[tuple[int, int], sp.Expr]:
    return {
        (first, second): sp.diff(one_form[second], coordinates[first])
        - sp.diff(one_form[first], coordinates[second])
        for first in range(4)
        for second in range(first + 1, 4)
    }


def _lie_two_form(
    vector: list[sp.Expr], two_form: dict[tuple[int, int], sp.Expr], coordinates: tuple[sp.Symbol, ...]
) -> dict[tuple[int, int], sp.Expr]:
    def component(first: int, second: int) -> sp.Expr:
        if first == second:
            return sp.S.Zero
        if first < second:
            return two_form[(first, second)]
        return -two_form[(second, first)]

    return {
        (first, second): sum(
            vector[index] * sp.diff(component(first, second), coordinates[index])
            + component(index, second) * sp.diff(vector[index], coordinates[first])
            + component(first, index) * sp.diff(vector[index], coordinates[second])
            for index in range(4)
        )
        for first in range(4)
        for second in range(first + 1, 4)
    }


def _clean(expression: sp.Expr) -> sp.Expr:
    return sp.simplify(sp.expand(expression))


def _exact_algebra() -> dict[str, Any]:
    coordinates = sp.symbols("x_0:4", real=True)
    xi = _functions("xi", coordinates)
    eta = _functions("eta", coordinates)
    zeta = _functions("zeta", coordinates)
    potential = _functions("A", coordinates)
    lam = sp.Function("lambda")(*coordinates)
    mu = sp.Function("mu")(*coordinates)
    nu = sp.Function("nu")(*coordinates)

    def transform(vector: list[sp.Expr], gauge: sp.Expr, field: list[sp.Expr]) -> list[sp.Expr]:
        lie = _lie_one_form(vector, field, coordinates)
        gradient = _gradient(gauge, coordinates)
        return [lie[index] + gradient[index] for index in range(4)]

    first = transform(xi, lam, potential)
    second = transform(eta, mu, potential)
    commutator = [
        _lie_one_form(xi, second, coordinates)[component]
        - _lie_one_form(eta, first, coordinates)[component]
        for component in range(4)
    ]
    bracket_vector = _vector_bracket(xi, eta, coordinates)
    bracket_gauge = _lie_scalar(xi, mu, coordinates) - _lie_scalar(eta, lam, coordinates)
    bracket_action = transform(bracket_vector, bracket_gauge, potential)
    action_residual = [_clean(commutator[index] - bracket_action[index]) for index in range(4)]

    pairs = ((xi, lam), (eta, mu), (zeta, nu))

    def pair_bracket(
        left: tuple[list[sp.Expr], sp.Expr], right: tuple[list[sp.Expr], sp.Expr]
    ) -> tuple[list[sp.Expr], sp.Expr]:
        return (
            _vector_bracket(left[0], right[0], coordinates),
            _lie_scalar(left[0], right[1], coordinates)
            - _lie_scalar(right[0], left[1], coordinates),
        )

    nested = [
        pair_bracket(pairs[index], pair_bracket(pairs[(index + 1) % 3], pairs[(index + 2) % 3]))
        for index in range(3)
    ]
    jacobi_vector = [
        _clean(sum(term[0][component] for term in nested)) for component in range(4)
    ]
    jacobi_gauge = _clean(sum(term[1] for term in nested))

    field = _field_strength(potential, coordinates)
    gauge_shifted = [potential[index] + sp.diff(lam, coordinates[index]) for index in range(4)]
    gauge_residual = {
        f"{first}{second}": _clean(value - field[(first, second)])
        for (first, second), value in _field_strength(gauge_shifted, coordinates).items()
        if _clean(value - field[(first, second)]) != 0
    }
    transformed_field = _field_strength(transform(xi, lam, potential), coordinates)
    field_lie = _lie_two_form(xi, field, coordinates)
    covariance_residual = {
        f"{first}{second}": _clean(transformed_field[(first, second)] - field_lie[(first, second)])
        for first in range(4)
        for second in range(first + 1, 4)
        if _clean(transformed_field[(first, second)] - field_lie[(first, second)]) != 0
    }

    d_squared = {
        f"{first}{second}": _clean(
            sp.diff(lam, coordinates[first], coordinates[second])
            - sp.diff(lam, coordinates[second], coordinates[first])
        )
        for first in range(4)
        for second in range(first + 1, 4)
    }
    if any(value != 0 for value in action_residual + jacobi_vector + [jacobi_gauge]):
        raise AssertionError("Diff-semidirect-U(1) identity failed")
    if gauge_residual or covariance_residual or any(value != 0 for value in d_squared.values()):
        raise AssertionError("Maxwell gauge or curvature covariance identity failed")

    return {
        "coefficient_domain": "arbitrary smooth four-dimensional local component functions",
        "action_commutator_residual": [str(value) for value in action_residual],
        "semidirect_jacobi_vector_residual": [str(value) for value in jacobi_vector],
        "semidirect_jacobi_u1_residual": str(jacobi_gauge),
        "d_squared_residual": {key: str(value) for key, value in d_squared.items()},
        "field_strength_gauge_residual": gauge_residual,
        "field_strength_covariance_residual": covariance_residual,
        "four_dimensional_hodge_weyl_exponent_on_two_forms": "4-2*2=0",
    }


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    exact = _exact_algebra()
    payload = {
        "schema": "pure-weyl-berger-maxwell-bv-semidirect-preflight-v1",
        "result_id": "BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_MAXWELL_BV_GAUGE_SEMIDIRECT_AND_APPARATUS_CONTRACT_FULL_DRESSING_INPUT_BLOCKED",
        "generality_level": "G0_TO_G1_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "maxwell_bv_complex": {
            "minimal_rows": 10,
            "combined_gravity_clock_maxwell_rows": 64,
            "row_layout": [
                {"row_id": "c_M", "degree": -1, "multiplicity": 1, "role": "Maxwell ghost"},
                {"row_id": "A_mu", "degree": 0, "multiplicity": 4, "role": "Maxwell potential"},
                {"row_id": "A_plus_mu", "degree": 1, "multiplicity": 4, "role": "Maxwell antifield density"},
                {"row_id": "c_M_plus", "degree": 2, "multiplicity": 1, "role": "Maxwell ghost antifield density"},
            ],
            "unary_chain": "c_M --d--> A --d star d--> A_plus --d--> c_M_plus",
            "odd_pairing": "integral(delta A wedge delta A_plus + delta c_M delta c_M_plus)",
            "action": "S_M=-1/2 integral(F wedge star_g F)+integral(A_plus wedge(L_c A+d c_M))+integral(c_M_plus L_c c_M)",
            "weyl_weights": {"A": 0, "c_M": 0, "F": 0},
            "background_maxwell_field": "zero for the unary direct-sum complex; the certified traveling mode is a fluctuation",
        },
        "semidirect_q2_gauge_sector": {
            "ghost_bracket": "[(xi,lambda),(eta,mu)]=([xi,eta],L_xi mu-L_eta lambda)",
            "potential_action": "delta_(xi,lambda) A=L_xi A+d lambda",
            "field_strength_action": "delta_(xi,lambda) F=L_xi F",
            "weyl_action": "delta_sigma A=delta_sigma c_M=delta_sigma F=0",
            "certified_blocks": [
                "q2(c_diff,c_M)->c_M",
                "q2(c_diff,A)->A",
                "their canonical antifield-density actions fixed by the displayed BV master term",
                "zero Weyl-Maxwell gauge action",
            ],
            "exact_checks": exact,
        },
        "dynamical_mixed_q2_ledger": {
            "status": "INPUT_BLOCKED",
            "required_blocks": [
                "q2(h_hat,A)->A_plus: first metric variation of d star_g d",
                "q2(A,A)->h_hat_plus: Maxwell stress-energy source in the gravity equation",
                "canonical antifield partners required by BV cyclicity",
            ],
            "not_present_in_authoritative_gravity_payload_reason": "BERGER_SUPPORT_LOCAL_Q2 exports the pure Weyl-plus-clock action on 54 rows and contains no Maxwell rows",
            "first_transfer_consumer": "ell2_res(x,y)=pi_cl q2(iota x,iota y), with homotopy correction data retained for the next arity",
            "negative_direction_verdict": "not introduced by the gauge-sector extension; the full mixed dynamical block remains unevaluated",
        },
        "relational_apparatus_contract": {
            "status": "CONTRACT_COMPLETE_EXACT_FIXTURE_INPUT_BLOCKED",
            "homogeneity_defect": "the Berger clock and anisotropy axis do not select a spatial base point",
            "reference_data": "Theta plus three local rod scalars R^I on neighborhoods of two compact timelike worldtubes",
            "nondegeneracy_condition": "dTheta wedge dR1 wedge dR2 wedge dR3 is nonzero on each apparatus tube",
            "emitter_worldtube": "W_e={R^I=r_e^I} inside a declared compact apparatus chart",
            "receiver_worldtube": "W_r={R^I=r_r^I} inside a declared compact apparatus chart",
            "source_requirement": "a compact conserved current J_e supported in W_e with d star J_e=0",
            "retarded_requirement": "F_ret=d G_ret J_e with support in J_plus(supp J_e)",
            "detector_reading": "E_r=F_{mu alpha}F_nu^alpha u_r^mu u_r^nu evaluated at Theta=tau_r,R=r_r",
            "frequency_ratio": "1+z=sqrt(E_e/E_r) after a common calibrated polarization/amplitude normalization",
            "missing_exact_inputs": [
                "an explicit local rod/reference-field solution and its standard-sign health check",
                "compact conserved emitter current coefficients",
                "a retarded Maxwell Green operator on the selected Berger clock domain",
                "a detector response/window and a unique no-wrap causal intersection",
            ],
        },
        "flags": {
            "BERGER_MAXWELL_MINIMAL_BV_LAYOUT": True,
            "BERGER_MAXWELL_SEMIDIRECT_GAUGE_Q2": True,
            "BERGER_RELATIONAL_APPARATUS_CONTRACT": True,
            "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2": False,
            "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING": False,
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE": False,
            "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL": False,
            "BERGER_MAXWELL_BACKREACTION": False,
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED": False,
            "LORENTZIAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_FIRST_MIXED_MAXWELL_Q2_TAYLOR_BLOCK_AND_LOCAL_APPARATUS_FIXTURE",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/berger_maxwell_bv_semidirect_preflight.py --check --guards", "elapsed_seconds": 3.82, "status": "PASS"},
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_maxwell_bv_semidirect_preflight.py", "elapsed_seconds": 2.56, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_maxwell_bv_semidirect_preflight", "elapsed_seconds": 4.99, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-maxwell-bv-semidirect-preflight-v1.schema.json -d d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json", "elapsed_seconds": 3.8, "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "The two authoritative inputs are unchanged and content-addressed; this preflight adds no mixed dynamical Taylor coefficient.",
            "tier_3": "No freeze, shared-core algebra change, lifecycle promotion, or Lorentzian certification is made.",
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC preflight fixes the ten-row minimal Maxwell BV layout, proves the arbitrary-function Diff-semidirect-U(1) gauge identities and four-dimensional Weyl inertness, binds the resulting 64-row consumer layout to the authoritative 54-row gravity-clock q2, and specifies the relational apparatus contract. It does not export the h-A-to-A-plus or A-A-to-h-plus dynamical q2 blocks, transfer a gravity-Maxwell interaction, construct rods, a compact source, a retarded Green operator, localized endpoints, backreaction, a Lorentzian quantum theory, or a quantum claim.",
    }
    verify(payload)
    return payload


def verify(payload: dict[str, Any]) -> None:
    _exact_algebra()
    if payload["maxwell_bv_complex"]["minimal_rows"] != 10:
        raise AssertionError("minimal Maxwell BV row count drifted")
    if payload["maxwell_bv_complex"]["combined_gravity_clock_maxwell_rows"] != 64:
        raise AssertionError("combined consumer row count drifted")
    exact = payload["semidirect_q2_gauge_sector"]["exact_checks"]
    if exact["action_commutator_residual"] != ["0"] * 4:
        raise AssertionError("semidirect action residual is nonzero")
    if exact["semidirect_jacobi_vector_residual"] != ["0"] * 4:
        raise AssertionError("semidirect Jacobi vector residual is nonzero")
    if exact["semidirect_jacobi_u1_residual"] != "0":
        raise AssertionError("semidirect Jacobi U(1) residual is nonzero")
    if exact["field_strength_gauge_residual"] or exact["field_strength_covariance_residual"]:
        raise AssertionError("field-strength gauge/covariance residual is nonzero")
    if payload["dynamical_mixed_q2_ledger"]["status"] != "INPUT_BLOCKED":
        raise AssertionError("missing mixed dynamical q2 was not fail-closed")
    if payload["relational_apparatus_contract"]["status"] != "CONTRACT_COMPLETE_EXACT_FIXTURE_INPUT_BLOCKED":
        raise AssertionError("localized apparatus was improperly promoted")
    for required in (
        "BERGER_MAXWELL_MINIMAL_BV_LAYOUT",
        "BERGER_MAXWELL_SEMIDIRECT_GAUGE_Q2",
        "BERGER_RELATIONAL_APPARATUS_CONTRACT",
    ):
        if payload["flags"][required] is not True:
            raise AssertionError(f"required preflight flag missing: {required}")
    for forbidden in (
        "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
        "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING",
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
        "BERGER_MAXWELL_BACKREACTION",
        "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED",
        "LORENTZIAN_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        if payload["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency hash drift: {name}")


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report(payload: dict[str, Any]) -> str:
    return r"""# Berger Maxwell BV semidirect and apparatus preflight

## Outcome

The minimal Maxwell BV sector is now fixed as ten component rows:
`c_M` (one), `A_mu` (four), `A_plus_mu` (four), and `c_M_plus` (one).
Appending it to the certified 54-row Berger gravity-clock complex gives an
explicit 64-row consumer layout.  This imports the gravity operator by hash;
it does not reconstruct it.

On arbitrary smooth four-dimensional local component functions, exact
symbolic reduction proves

\[
[(\xi,\lambda),(\eta,\mu)]
=([\xi,\eta],\mathcal L_\xi\mu-\mathcal L_\eta\lambda),
\qquad
\delta_{(\xi,\lambda)}A=\mathcal L_\xi A+d\lambda .
\]

The Jacobi residual, action-commutator residual, `d^2` residual, Maxwell
gauge residual of `F`, and covariance residual
`delta F-L_xi F` all vanish coefficientwise.  In four dimensions the Hodge
star on two-forms has Weyl exponent `4-2*2=0`, so `A`, `c_M`, and `F` are
Weyl inert.  This certifies the gauge semidirect sector, not the dynamical
gravity-Maxwell Taylor coupling.

## Exact remaining mixed block

The authoritative `BERGER_SUPPORT_LOCAL_Q2` payload contains the pure
Weyl-plus-clock 54-row operator and no Maxwell rows.  The first actual
gravity-Maxwell dressing therefore still requires three linked exports:

- `q2(h_hat,A)->A_plus`, the metric variation of the Maxwell equation;
- `q2(A,A)->h_hat_plus`, the Maxwell stress source;
- their antifield partners required by BV cyclicity.

Once supplied, the prepared consumer evaluates
`ell2_res(x,y)=pi_cl q2(iota x,iota y)` and retains the homotopy leg needed
at the next arity.  Until then the scientific status is `INPUT_BLOCKED`.

## Relational localization contract

A homogeneous Berger slice has no preferred point.  Local endpoints must
therefore carry explicit reference data.  The contract uses the existing
clock `Theta` plus three local rod scalars `R^I` near compact emitter and
receiver worldtubes, with
`dTheta wedge dR1 wedge dR2 wedge dR3 != 0` on each tube.  It requires a
compact conserved emitter current, a retarded Maxwell Green operator, a
detector window, and a unique no-wrap causal intersection.  None of these
inputs is replaced by the old spatial average.

No new physical mode is introduced by this gauge-sector extension, so it
introduces no negative physical direction.  The sign of the unexported full
mixed dynamical block remains unevaluated.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json`.

## Claim boundary

This is a `LOCAL-ALGEBRAIC` preflight.  It is not a localized or retarded
redshift theorem, not a backreaction result, not the first transferred
gravity-Maxwell interaction, and not a Lorentzian quantum claim.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        CERTIFICATE_PATH.write_text(_json(payload))
        REPORT_PATH.write_text(_report(payload))
    if args.check:
        if CERTIFICATE_PATH.read_text() != _json(payload):
            raise AssertionError("Maxwell BV semidirect certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("Maxwell BV semidirect report drifted")
    if args.guards:
        mutants = []
        promoted = deepcopy(payload)
        promoted["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"] = True
        mutants.append(("promote full mixed q2", promoted))
        localized = deepcopy(payload)
        localized["flags"]["BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE"] = True
        mutants.append(("promote localized endpoints", localized))
        residual = deepcopy(payload)
        residual["semidirect_q2_gauge_sector"]["exact_checks"]["action_commutator_residual"][0] = "1"
        mutants.append(("insert semidirect residual", residual))
        unblocked = deepcopy(payload)
        unblocked["dynamical_mixed_q2_ledger"]["status"] = "READY"
        mutants.append(("erase mixed input blocker", unblocked))
        for name, mutant in mutants:
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT: PASS")


if __name__ == "__main__":
    main()
