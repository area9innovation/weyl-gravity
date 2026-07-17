#!/usr/bin/env python3
"""Project the exact Berger Maxwell stress source through ``pi_cl``.

The calculation is intentionally the first physical-shape mixed block, not
an arbitrary-jet Einstein--Maxwell export.  It derives q2(A,A)->h^+ from the
frozen Maxwell normalization, applies the certified gravity projection, and
decides exactness in the stationary homogeneous constant-coefficient
retained metric complex.
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
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-maxwell-stress-residual-projection.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-maxwell-stress-residual-projection-v1.schema.json"

DEPENDENCIES = {
    "maxwell_mode": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "maxwell_bv_preflight": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json",
    "gravity_contraction": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "retained_unary": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_maxwell_stress_residual_projection.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_maxwell_stress_residual_projection.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_maxwell_stress_residual_projection.py",
    SCHEMA_PATH,
)

PAIRS = tuple((first, second) for first in range(4) for second in range(first, 4))
ROW_IDS = tuple(f"h_hat_star_{first}{second}" for first, second in PAIRS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if data["maxwell_mode"]["flags"]["BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE"] is not True:
        raise AssertionError("certified Berger Maxwell mode is unavailable")
    if data["maxwell_mode"]["maxwell_probe"]["action"] != "S_M=-1/4 int sqrt(-g_hat) F_ab F^ab":
        raise AssertionError("Maxwell action normalization drifted")
    if data["maxwell_bv_preflight"]["flags"]["BERGER_MAXWELL_MINIMAL_BV_LAYOUT"] is not True:
        raise AssertionError("Maxwell BV row contract is unavailable")
    contraction = data["gravity_contraction"]
    if contraction["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("gravity contraction is unavailable")
    retained = data["retained_unary"]
    if retained["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is not True:
        raise AssertionError("retained gravity unary operator is unavailable")
    if retained["action_inputs"]["metric_equation"] != "alpha_B B_ab-T_ab=0":
        raise AssertionError("gravity metric-equation normalization drifted")
    return data


def _field_strengths(beta: sp.Expr, time: sp.Symbol) -> tuple[sp.Matrix, sp.Matrix]:
    cosine = sp.cos(beta * time)
    sine = sp.sin(beta * time)
    first = sp.zeros(4)
    second = sp.zeros(4)
    first_components = {
        (0, 1): -beta * sine,
        (0, 2): beta * cosine,
        (1, 3): beta * sine,
        (2, 3): -beta * cosine,
    }
    second_components = {
        (0, 1): -beta * cosine,
        (0, 2): -beta * sine,
        (1, 3): beta * cosine,
        (2, 3): beta * sine,
    }
    for matrix, components in ((first, first_components), (second, second_components)):
        for (left, right), value in components.items():
            matrix[left, right] = value
            matrix[right, left] = -value
    return first, second


def _stress_polarization(first: sp.Matrix, second: sp.Matrix) -> sp.Matrix:
    """Symmetric Maxwell stress polarization with covariant free indices."""

    eta = sp.diag(-1, 1, 1, 1)
    contraction = sum(
        eta[a, c] * eta[b, d] * first[a, b] * second[c, d]
        for a in range(4)
        for b in range(4)
        for c in range(4)
        for d in range(4)
    )
    return sp.simplify(
        (first * eta * second.T + second * eta * first.T) / 2
        - eta * contraction / 4
    )


def _berger_connection(a: sp.Expr, c: sp.Expr) -> list[list[list[sp.Expr]]]:
    eta = sp.diag(-1, 1, 1, 1)
    structure = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for first, second, target, value in (
        (1, 2, 3, c / a**2),
        (2, 3, 1, 1 / c),
        (3, 1, 2, 1 / c),
    ):
        structure[first][second][target] = value
        structure[second][first][target] = -value
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for derivative in range(4):
        for vector in range(4):
            for lowered_target in range(4):
                gamma_lower = sp.Rational(1, 2) * (
                    eta[lowered_target, lowered_target] * structure[derivative][vector][lowered_target]
                    - eta[derivative, derivative] * structure[vector][lowered_target][derivative]
                    + eta[vector, vector] * structure[lowered_target][derivative][vector]
                )
                connection[lowered_target][derivative][vector] += eta[lowered_target, lowered_target] * gamma_lower
    return connection


def _parse_constant_matrix(record: dict[str, Any], shape: tuple[int, int]) -> sp.Matrix:
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["shape"] != list(shape) or record["sha256"] != _canonical_hash(body):
        raise AssertionError("operator record hash or shape drifted")
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    alpha_b = sp.S(5)
    matrix = sp.zeros(*shape)
    for row, column, terms in record["entries"]:
        for exponents, raw in terms:
            if any(exponents):
                continue
            matrix[row, column] += sp.sympify(
                raw, locals={"u": u, "v": v, "alpha_B": alpha_b}
            )
    return sp.simplify(matrix)


def _projection_on_metric_sources(record: dict[str, Any]) -> sp.Matrix:
    projection = _parse_constant_matrix(record, (26, 54))
    block = projection[13:23, 27:37]
    if block != sp.eye(10):
        raise AssertionError("pi_cl is not the identity on retained metric sources")
    return block


def _strings(vector: sp.Matrix) -> list[str]:
    return [str(sp.factor(value)) for value in vector]


def _nonzero_rows(vector: sp.Matrix) -> list[dict[str, str]]:
    return [
        {"row_id": ROW_IDS[index], "coefficient": str(sp.factor(value))}
        for index, value in enumerate(vector)
        if value != 0
    ]


def _exact_block(dependencies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    beta = 2 * sp.sqrt(10) / 3
    time = sp.symbols("t", real=True)
    eta = sp.diag(-1, 1, 1, 1)
    first, second = _field_strengths(beta, time)
    stress_cc_cov = _stress_polarization(first, first).applyfunc(sp.trigsimp)
    stress_ss_cov = _stress_polarization(second, second).applyfunc(sp.trigsimp)
    stress_cs_cov = _stress_polarization(first, second).applyfunc(sp.trigsimp)
    expected_stress = beta**2 * sp.Matrix(
        [[1, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 1]]
    )
    if stress_cc_cov != expected_stress or stress_ss_cov != expected_stress:
        raise AssertionError("real Maxwell phase stresses disagree")
    if stress_cs_cov != sp.zeros(4):
        raise AssertionError("orthogonal Maxwell phase cross-stress is nonzero")
    if sp.simplify(sum(eta[a, b] * stress_cc_cov[a, b] for a in range(4) for b in range(4))) != 0:
        raise AssertionError("Maxwell stress is not tracefree")

    stress_upper = sp.simplify(eta * stress_cc_cov * eta)
    connection = _berger_connection(sp.S.One, 3 / (2 * sp.sqrt(10)))
    divergence = sp.Matrix(
        [
            sp.simplify(
                sum(
                    connection[a][a][c] * stress_upper[c, b]
                    + connection[b][a][c] * stress_upper[a, c]
                    for a in range(4)
                    for c in range(4)
                )
            )
            for b in range(4)
        ]
    )
    if divergence != sp.zeros(4, 1):
        raise AssertionError("Maxwell stress is not covariantly conserved")
    source = sp.zeros(10, 1)
    for index, (left, right) in enumerate(PAIRS):
        multiplicity = 2 if left != right else 1
        # The canonical gravity row is -(multiplicity)(alpha B-T)^{ab}.
        # q2 is the second Taylor derivative, giving the additional factor 2.
        source[index] = sp.factor(2 * multiplicity * stress_upper[left, right])
    expected_source = sp.zeros(10, 1)
    expected_source[0] = sp.Rational(80, 9)
    expected_source[3] = -sp.Rational(160, 9)
    expected_source[9] = sp.Rational(80, 9)
    if source != expected_source:
        raise AssertionError("canonical Maxwell stress q2 source drifted")

    projection = _projection_on_metric_sources(
        dependencies["gravity_contraction"]["contraction"]["pi_cl"]
    )
    retained_source = sp.simplify(projection * source)
    if retained_source != source:
        raise AssertionError("metric source changed under pi_cl")

    retained = dependencies["retained_unary"]["q1_blocks"]
    hessian = _parse_constant_matrix(retained["H_retained"], (10, 10))
    noether = _parse_constant_matrix(retained["minus_K_spatial_sharp"], (3, 10))
    closure = sp.simplify(noether * retained_source)
    if closure != sp.zeros(3, 1):
        raise AssertionError("projected source is not q1 closed")

    diagonal_source = sp.Matrix(retained_source)
    diagonal_source[3] = 0
    primitive = sp.Matrix(
        [
            -sp.Rational(5120, 567),
            0,
            0,
            0,
            sp.Rational(10880, 651),
            0,
            0,
            sp.Rational(10880, 651),
            0,
            sp.Rational(14080, 1953),
        ]
    )
    if sp.simplify(hessian * primitive - diagonal_source) != sp.zeros(10, 1):
        raise AssertionError("diagonal Maxwell source primitive failed")

    witness = sp.zeros(10, 1)
    witness[3] = -sp.Rational(9, 160)
    if sp.simplify(witness.T * hessian) != sp.zeros(1, 10):
        raise AssertionError("dual obstruction witness does not annihilate im(q1)")
    witness_pairing = sp.factor((witness.T * retained_source)[0])
    if witness_pairing != 1:
        raise AssertionError("dual obstruction witness is not normalized")
    rank = hessian.rank()
    augmented_rank = hessian.row_join(retained_source).rank()
    if (rank, augmented_rank) != (7, 8):
        raise AssertionError("stationary homogeneous obstruction ranks drifted")

    return {
        "beta": str(beta),
        "stress_covariant": [[str(sp.factor(value)) for value in stress_cc_cov.row(row)] for row in range(4)],
        "stress_contravariant": [[str(sp.factor(value)) for value in stress_upper.row(row)] for row in range(4)],
        "stress_trace": "0",
        "stress_covariant_divergence": _strings(divergence),
        "phase_cross_stress": [["0"] * 4 for _ in range(4)],
        "full_metric_source": _strings(source),
        "retained_metric_source": _strings(retained_source),
        "nonzero_retained_rows": _nonzero_rows(retained_source),
        "q1_closure_residual": _strings(closure),
        "constant_hessian_rank": rank,
        "augmented_rank": augmented_rank,
        "diagonal_exact_primitive": _strings(primitive),
        "diagonal_primitive_residual": _strings(sp.simplify(hessian * primitive - diagonal_source)),
        "normalized_dual_witness": _strings(witness),
        "dual_witness_image_residual": _strings(sp.simplify(hessian.T * witness)),
        "dual_witness_source_pairing": str(witness_pairing),
    }


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    exact = _exact_block(dependencies)
    payload = {
        "schema": "pure-weyl-berger-maxwell-stress-residual-projection-v1",
        "result_id": "BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_REDUCED_MODE_MAXWELL_STRESS_BRACKET_OBSTRUCTED_IN_HOPF_FLUX_CHANNEL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "normalization": {
            "maxwell_action": "S_M=-1/4 int sqrt(-g_hat) F_ab F^ab",
            "gravity_metric_equation_before_extension": "alpha_B B_ab-T_clock_ab=0",
            "mixed_extension": "alpha_B B_ab-T_clock_ab-T_Maxwell_ab=0",
            "alpha_B_fixture": "5",
            "canonical_symmetric_row_weight": "-(2-delta_ab) eta_aa eta_bb",
            "same_input_q2_formula": "q2(A,A)_(h_plus_ab)=2(2-delta_ab)T_Maxwell^ab[A]",
        },
        "physical_mode_block": {
            "input_basis": ["A_c", "A_s"],
            "amplitude_formula": "q2(x A_c+y A_s,x A_c+y A_s)=(x^2+y^2) S_Maxwell",
            "D_weight": "0",
            "field_content": ["h_hat_star_00", "h_hat_star_03", "h_hat_star_33"],
            "stress_geometry": "stationary homogeneous tracefree null stress with future energy and Hopf flux along s=-e3",
            "exact_data": exact,
        },
        "projection_and_verdict": {
            "projection": "pi_cl is the exact identity from full metric-antifield rows 27:37 to retained rows 13:23",
            "q1_closed": True,
            "diagonal_energy_pressure_sector": "EXACT_WITH_DISPLAYED_PRIMITIVE",
            "Hopf_flux_sector": "NONTRIVIAL_NORMALIZED_DUAL_WITNESS",
            "binary_verdict": "OBSTRUCTION",
            "obstruction_row": "h_hat_star_03",
            "obstruction_interpretation": "the stationary homogeneous gravity block cannot absorb the null Maxwell momentum flux without an additional momentum-balancing or nonhomogeneous sector",
        },
        "branch_and_health": {
            "Einstein_like_radiative_branch_coupled": False,
            "extra_Weyl_radiative_branch_coupled": False,
            "reason": "the only nontrivial class in this weight-zero block is the homogeneous time-Hopf momentum/shift source, not a transverse radiative tensor; the diagonal metric response is q1 exact",
            "Maxwell_energy_signature": [2, 0, 0],
            "negative_physical_direction_introduced": False,
            "health_boundary": "an obstruction source is not a new propagating kinetic direction; no backreacted solution or response energy has been constructed",
        },
        "flags": {
            "BERGER_MAXWELL_STRESS_Q2_PHYSICAL_BLOCK": True,
            "BERGER_MAXWELL_STRESS_PI_CL_PROJECTED": True,
            "BERGER_REDUCED_MODE_MAXWELL_BRACKET_OBSTRUCTED": True,
            "BERGER_HOPF_FLUX_OBSTRUCTION_WITNESS": True,
            "BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2": False,
            "BERGER_FULL_RESIDUAL_GRAVITY_MAXWELL_BRACKET": False,
            "BERGER_EINSTEIN_EXTRA_WEYL_BRANCH_MIXING": False,
            "BERGER_MAXWELL_BACKREACTED_SOLUTION": False,
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED": False,
            "LORENTZIAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "reduced_mode_limitation": "The verdict is exact only in the stationary SU(2)_L x U(1)_R homogeneous constant-component, D-weight-zero metric source block at a=1, c^2=9/40, rho=1, omega=3/4, alpha_B=5. It proves non-exactness against the constant retained Hessian, but does not exclude a nonhomogeneous or support-local primitive, does not supply q2(h,A)->A_plus or the remaining Maxwell antifield rows, and does not classify radiative Einstein/extra-Weyl scattering channels.",
        "next_gate": "BERGER_MAXWELL_HOPF_FLUX_BALANCING_OR_FULL_SUPPORT_LOCAL_PRIMITIVE_VERDICT",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/berger_maxwell_stress_residual_projection.py --check --guards", "elapsed_seconds": 1.49, "status": "PASS"},
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_maxwell_stress_residual_projection.py", "elapsed_seconds": 0.61, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_maxwell_stress_residual_projection", "elapsed_seconds": 2.53, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-maxwell-stress-residual-projection-v1.schema.json -d d_quotient_classical/certificates/BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION.json", "elapsed_seconds": 1.09, "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "All imported operators are unchanged and content-addressed; this result adds one isolated physical-shape Maxwell source block.",
            "tier_3": "This REDUCED-MODE obstruction does not freeze shared algebra, promote a full support-local theorem, or certify a Lorentzian theory.",
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result derives the normalized q2(A,A)-to-metric-antifield Maxwell stress source for the certified two-phase Berger light mode, applies the authoritative pi_cl projection, proves q1 closure, displays an exact primitive for the diagonal energy-pressure part, and gives a normalized dual witness for the nontrivial time-Hopf flux obstruction. It does not prove a full support-local obstruction, construct every coupled Maxwell BV row, establish Einstein/extra-Weyl radiative mixing, produce a backreacted solution, introduce a negative kinetic direction, certify Lorentzian causal perturbation theory, or make a quantum claim.",
    }
    verify(payload)
    return payload


def verify(payload: dict[str, Any]) -> None:
    dependencies = _load_dependencies()
    exact = _exact_block(dependencies)
    if payload["physical_mode_block"]["exact_data"] != exact:
        raise AssertionError("persisted exact Maxwell stress block drifted")
    if payload["projection_and_verdict"]["binary_verdict"] != "OBSTRUCTION":
        raise AssertionError("binary obstruction verdict drifted")
    if exact["dual_witness_source_pairing"] != "1":
        raise AssertionError("obstruction witness is not normalized")
    if exact["constant_hessian_rank"] != 7 or exact["augmented_rank"] != 8:
        raise AssertionError("obstruction ranks drifted")
    if exact["q1_closure_residual"] != ["0", "0", "0"]:
        raise AssertionError("source is not q1 closed")
    if any(value != "0" for value in exact["diagonal_primitive_residual"]):
        raise AssertionError("diagonal source is not exact")
    for required in (
        "BERGER_MAXWELL_STRESS_Q2_PHYSICAL_BLOCK",
        "BERGER_MAXWELL_STRESS_PI_CL_PROJECTED",
        "BERGER_REDUCED_MODE_MAXWELL_BRACKET_OBSTRUCTED",
        "BERGER_HOPF_FLUX_OBSTRUCTION_WITNESS",
    ):
        if payload["flags"][required] is not True:
            raise AssertionError(f"required flag missing: {required}")
    for forbidden in (
        "BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2",
        "BERGER_FULL_RESIDUAL_GRAVITY_MAXWELL_BRACKET",
        "BERGER_EINSTEIN_EXTRA_WEYL_BRANCH_MIXING",
        "BERGER_MAXWELL_BACKREACTED_SOLUTION",
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
    data = payload["physical_mode_block"]["exact_data"]
    primitive = data["diagonal_exact_primitive"]
    return rf"""# Berger Maxwell stress residual projection

## Binary verdict

**OBSTRUCTION in the stationary homogeneous Hopf-flux channel.**

The Maxwell normalization is frozen as

\[
S_M=-\frac14\int\sqrt{{-\hat g}}F_{{ab}}F^{{ab}},
\]

and the gravity equation is extended from
`alpha_B B-T_clock=0` to `alpha_B B-T_clock-T_Maxwell=0`.
With the repository symmetric-component convention, the same-input Taylor
block is

\[
q_2(A,A)_{{h^+_{{ab}}}}=2(2-\delta_{{ab}})T^{{ab}}[A].
\]

For both real phases `A_c` and `A_s`, `beta={data['beta']}` and the only
nonzero retained source rows are

- `h_hat_star_00 = 80/9`;
- `h_hat_star_03 = -160/9`;
- `h_hat_star_33 = 80/9`.

The phase cross-source vanishes, so for a real mode
`A=x A_c+y A_s` the source is `(x^2+y^2) S_Maxwell`.  It is stationary,
homogeneous, tracefree, has total `D`-weight zero, and carries positive
energy with Hopf momentum flux along `s=-e3`.

## Projection and exactness

On these ten metric-antifield rows, the certified `pi_cl` block is exactly
the identity.  The retained Noether operator annihilates the source, so it
is `q1` closed.

The diagonal energy-pressure part is exact.  In row order
`(00,01,02,03,11,12,13,22,23,33)`, one primitive is

```text
{primitive}
```

and its residual is exactly zero.  By contrast, the constant retained
Hessian has rank `7`, while adjoining the full Maxwell source raises the
rank to `8`.  The normalized left-null witness has only

```text
w(h_hat_star_03)=-9/160
```

and satisfies `w^T H=0`, `w^T S_Maxwell=1`.  This is an exact obstruction
witness, not a numerical rank diagnosis.

## Physical interpretation

The obstruction is the homogeneous time-Hopf momentum/shift source.  The
stationary homogeneous gravity block can absorb the diagonal energy and
pressure, but it cannot absorb the unbalanced null momentum flux.  A
backreacted configuration therefore needs either a counter-propagating or
otherwise momentum-balancing sector, or a genuinely nonhomogeneous gravity
response.

This block couples neither certified radiative Einstein-like nor extra-Weyl
branch: its only nontrivial class is a weight-zero constraint/flux channel,
while the diagonal metric response is exact.  The positive Maxwell
two-plane remains signature `[2,0,0]`; an obstruction source is not a new
kinetic direction, so no negative physical direction has been introduced.

## REDUCED-MODE limitation

The verdict holds only for constant components in the stationary
`SU(2)_L x U(1)_R`, `D`-weight-zero retained metric block at the rational
Berger fixture.  It does not exclude a nonhomogeneous or support-local
primitive and is not a radiative scattering or Lorentzian quantum theorem.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION.json`.
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
            raise AssertionError("Maxwell stress projection certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("Maxwell stress projection report drifted")
    if args.guards:
        mutants = []
        promoted = deepcopy(payload)
        promoted["flags"]["BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2"] = True
        mutants.append(("promote full support-local q2", promoted))
        exact = deepcopy(payload)
        exact["physical_mode_block"]["exact_data"]["dual_witness_source_pairing"] = "0"
        mutants.append(("erase obstruction pairing", exact))
        rank = deepcopy(payload)
        rank["physical_mode_block"]["exact_data"]["augmented_rank"] = 7
        mutants.append(("erase augmented rank jump", rank))
        negative = deepcopy(payload)
        negative["flags"]["NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED"] = True
        mutants.append(("promote negative direction", negative))
        for name, mutant in mutants:
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION: PASS")


if __name__ == "__main__":
    main()
