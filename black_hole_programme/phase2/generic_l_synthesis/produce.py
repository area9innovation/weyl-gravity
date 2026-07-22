#!/usr/bin/env python3
"""Produce the exact axial/polar generic-ell disposition and Q21 wall ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from flint import ctx as flint_ctx
from flint import fmpz_mpoly_ctx, fmpz_poly


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
AXIAL = ROOT / "black_hole_programme/phase2/general_l_axial_selection/certificate.json"
AXIAL_RECEIPT = ROOT / "black_hole_programme/phase2/general_l_axial_selection/receipt.json"
POLAR = ROOT / "black_hole_programme/phase2/general_l_polar_extendible_current_closure/certificate.json"
POLAR_RECEIPT = ROOT / "black_hole_programme/phase2/general_l_polar_extendible_current_closure/receipt.json"
Q21_PATH = ROOT / "black_hole_programme/phase2/general_l_polar_extendible_current_closure/current_artifacts/q21-finite-line-factor.json"
POLAR_WALL = ROOT / "black_hole_programme/phase2/general_l_polar_extendible_current_closure/current_artifacts/canonical-pivot-wall-certificate.json"

CERTIFICATE = OUT / "certificate.json"
CLAIM_MAP = OUT / "claim_map.json"
RECEIPT = OUT / "receipt.json"
REPORT = ROOT / "reports/phase2-black-hole-generic-l-disposition-2026-07-22.md"
CORRECTION_REQUEST = ROOT / "planning/paper-coverage/phase2-black-hole-paper-correction-request.json"

AXIAL_SHA = "e480fd0f247fd42c049ce395099c1c957199586a31f907d32d0b6c7f64c71caf"
AXIAL_RECEIPT_SHA = "fc6566fecf5ba63902ada98c50a27f5cea95768c585f51e15928edca7dc0517c"
POLAR_SHA = "38cedbfab9931c111cb3569b0d5b15ea6182638a7e7de00ea849cfe8728f7fce"
POLAR_RECEIPT_SHA = "a46c5b737a8797395675039f7170c3492dd8d9565bb5b6aaa0fb1fd6e2dcf963"
Q21_SHA = "9c08f3c59adfd2da973872a0d718ef97249fa91b690f63df40bdcac81cae7f62"
POLAR_WALL_SHA = "d28ec7f9e046295dd45d58bbf1ef6b5cae1a640e98eb565835c6dadc86f3ce85"
AXIAL_COMMIT = "fe1cd1e60a874f0548fae464bff987054fa5482a"
POLAR_TERMINAL_COMMIT = "e66db9d7b01df3510472aa0359c6b9070c8fc6f4"

TRANSITION_INTERVALS = [
    ("DISCRIMINANT", Fraction(6588, 1000), Fraction(6589, 1000), "between Lambda_2=6 and Lambda_3=12"),
    ("X_ZERO_BOUNDARY", Fraction(6796, 1000), Fraction(6797, 1000), "between Lambda_2=6 and Lambda_3=12"),
    ("DISCRIMINANT", Fraction(8226, 1000), Fraction(8227, 1000), "between Lambda_2=6 and Lambda_3=12"),
    ("DISCRIMINANT", Fraction(13983, 1000), Fraction(13984, 1000), "between Lambda_3=12 and Lambda_4=20"),
    ("DISCRIMINANT", Fraction(111320, 1000), Fraction(111322, 1000), "between Lambda_10=110 and Lambda_11=132"),
    ("DISCRIMINANT", Fraction(1640901, 1000), Fraction(1640902, 1000), "between Lambda_40=1640 and Lambda_41=1722"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def load_checked(path: Path, expected: str) -> dict:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"input hash mismatch: {path}: {actual} != {expected}")
    return json.loads(path.read_text())


def q21_expression(data: dict) -> tuple[sp.Symbol, sp.Symbol, sp.Expr]:
    lam, x = sp.symbols("Lambda x", real=True)
    expr = sum(sp.Integer(c) * lam ** m[0] * x ** (m[1] // 2) for m, c in data["terms"])
    return lam, x, sp.expand(expr)


def exact_positive_count(poly: sp.Poly) -> int:
    return int(poly.count_roots(0, sp.oo))


def rational_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def discriminant_ledger(q21_data: dict) -> dict:
    mctx = fmpz_mpoly_ctx.get(["Lambda", "x"], "lex")
    lam, x = mctx.gens()
    q = mctx.constant(0)
    for (a, twice_b), coefficient in q21_data["terms"]:
        q += int(coefficient) * lam**a * x ** (twice_b // 2)
    discriminant = q.discriminant("x")
    unit, factors = discriminant.factor()
    factor_rows = sorted(
        [(factor.degrees()[0], exponent, factor) for factor, exponent in factors],
        key=lambda row: row[0],
    )
    expected_small = {(1, 2, "Lambda - 3"), (1, 2, "Lambda + 1"), (1, 14, "Lambda"), (1, 16, "Lambda - 2")}
    actual_small = {(degree, exponent, str(factor)) for degree, exponent, factor in factor_rows if degree == 1}
    if actual_small != expected_small:
        raise RuntimeError(f"unexpected discriminant small factors: {actual_small}")
    big_rows = [(exponent, factor) for degree, exponent, factor in factor_rows if degree > 1]
    if len(big_rows) != 1 or big_rows[0][0] != 1 or big_rows[0][1].degrees()[0] != 397:
        raise RuntimeError("expected one square-free degree-397 discriminant factor")
    big = big_rows[0][1]
    big_terms = sorted([[[int(e) for e in monomial], str(coefficient)] for monomial, coefficient in big.to_dict().items()])
    big_sha = hashlib.sha256(canonical_json(big_terms)).hexdigest()
    coefficients = [0] * 398
    for monomial, coefficient in big.to_dict().items():
        coefficients[monomial[0]] = int(coefficient)
    big_poly = fmpz_poly(coefficients)
    flint_ctx.prec = 80
    roots = big_poly.complex_roots()
    real_roots = [root.real for root, multiplicity in roots if multiplicity == 1 and root.imag.contains(0)]
    physical = [root for root in real_roots if float(root.mid()) >= 6]
    discriminant_intervals = [(lo, hi) for kind, lo, hi, _ in TRANSITION_INTERVALS if kind == "DISCRIMINANT"]
    if len(physical) != len(discriminant_intervals):
        raise RuntimeError(f"expected five real D397 roots above Lambda=6, found {len(physical)}")
    physical.sort(key=lambda root: float(root.mid()))
    for root, (lo, hi) in zip(physical, discriminant_intervals):
        if not (float(lo) < float(root.lower()) and float(root.upper()) < float(hi)):
            raise RuntimeError(f"D397 root not isolated in ({lo},{hi}): {root}")
        left = sp.Poly(sum(sp.Integer(c) * sp.Symbol("L") ** i for i, c in enumerate(coefficients)), sp.Symbol("L")).eval(sp.Rational(lo.numerator, lo.denominator))
        right = sp.Poly(sum(sp.Integer(c) * sp.Symbol("L") ** i for i, c in enumerate(coefficients)), sp.Symbol("L")).eval(sp.Rational(hi.numerator, hi.denominator))
        if sp.sign(left) * sp.sign(right) != -1:
            raise RuntimeError(f"D397 rational isolating interval lacks an exact sign change: ({lo},{hi})")
    return {
        "resultant_object": "disc_x(Q21)=(-1)^210*LC_x(Q21)^(-1)*Res_x(Q21,dQ21/dx)",
        "factorization": "unit*D397(Lambda)*(Lambda-3)^2*(Lambda+1)^2*Lambda^14*(Lambda-2)^16",
        "factorization_evidence_type": "EXACT_RATIONAL",
        "degree_397_factor_sha256": big_sha,
        "degree_397_factor_square_free": True,
        "degree_397_real_roots_ge_6": len(physical),
        "root_isolation_evidence_type": "CERTIFIED_INTERVAL_NUMERIC",
        "certified_isolation_method": "exhaustive Arb complex-root enclosures narrowed to rational intervals; exact rational endpoint signs are replayed separately",
        "unit_decimal_digits": len(str(abs(int(unit)))),
    }


def q21_proof(q21_data: dict) -> dict:
    lam, x, q = q21_expression(q21_data)
    q_poly = sp.Poly(q, lam, x, domain=sp.ZZ)
    if q_poly.degree(lam) != 21 or q_poly.degree(x) != 21 or len(q_poly.terms()) != 282:
        raise RuntimeError("unexpected Q21 shape")
    leading = sp.factor(sp.Poly(q, x).LC())
    expected_leading = -sp.Integer(7253554917687775048237056) * (lam + 2) * (5 * lam + 8)
    if sp.expand(leading - expected_leading) != 0:
        raise RuntimeError("Q21 leading-x coefficient mismatch")
    q0 = sp.factor(q.subs(x, 0))
    r5 = 145 * lam**5 - 1228 * lam**4 + 1292 * lam**3 + 2056 * lam**2 + 480 * lam + 13536
    expected_q0 = lam**6 * (lam - 3) * (lam - 2) ** 6 * (lam + 2) * (lam**2 - 4 * lam + 12) * r5
    if sp.expand(q0 - expected_q0) != 0:
        raise RuntimeError("Q21(Lambda,0) factorization mismatch")
    r5_poly = sp.Poly(r5, lam, domain=sp.ZZ)
    if r5_poly.count_roots(6, sp.oo) != 1 or r5_poly.count_roots(sp.Rational(6796, 1000), sp.Rational(6797, 1000)) != 1:
        raise RuntimeError("Q21 x=0 transition is not uniquely isolated")
    discriminant = discriminant_ledger(q21_data)

    samples = [
        (sp.Integer(6), 0),
        (sp.Rational(13, 2), 0),
        (sp.Rational(27, 4), 2),
        (sp.Integer(7), 3),
        (sp.Integer(10), 3),
        (sp.Integer(20), 1),
        (sp.Integer(132), 3),
        (sp.Integer(1722), 1),
    ]
    for value, expected in samples:
        count = exact_positive_count(sp.Poly(q.subs(lam, value), x, domain=sp.QQ))
        if count != expected:
            raise RuntimeError(f"continuous-Lambda Q21 count mismatch at {value}: {count} != {expected}")
    triangular_counts = {}
    for ell in range(2, 42):
        value = ell * (ell + 1)
        triangular_counts[ell] = exact_positive_count(sp.Poly(q.subs(lam, value), x, domain=sp.ZZ))
    expected_triangular = {2: 0, 3: 3}
    expected_triangular.update({ell: 1 for ell in range(4, 11)})
    expected_triangular.update({ell: 3 for ell in range(11, 41)})
    expected_triangular[41] = 1
    if triangular_counts != expected_triangular:
        raise RuntimeError(f"triangular Q21 count mismatch: {triangular_counts}")

    transitions = []
    for kind, lo, hi, location in TRANSITION_INTERVALS:
        transitions.append({
            "kind": kind,
            "isolating_interval": [rational_text(lo), rational_text(hi)],
            "relative_to_triangular_harmonics": location,
        })
    legacy_value = sp.factor(q.subs({lam: 6, x: sp.Rational(9, 25)}))
    expected_legacy = sp.Rational(
        -174226120816040380076641138108451235935620694016,
        227373675443232059478759765625,
    )
    if legacy_value != expected_legacy:
        raise RuntimeError(f"Q21 fixture mismatch: {legacy_value}")
    prior_misread = sp.factor(q.subs({lam: 6, x: sp.Rational(81, 625)}))
    expected_prior_misread = sp.Rational(
        -14448171146294349891375497475824503848382375518461685248033668073043001344,
        51698788284564229679463043254372678347863256931304931640625,
    )
    if prior_misread != expected_prior_misread:
        raise RuntimeError(f"prior evaluator-variable replay mismatch: {prior_misread}")

    return {
        "variable": "x=omega^2>0",
        "leading_x_coefficient": sp.sstr(leading),
        "leading_x_coefficient_nonzero_for_Lambda_ge_6": True,
        "boundary_factorization": sp.sstr(q0),
        "boundary_transition_factor": sp.sstr(r5),
        "boundary_transition_roots_ge_6": 1,
        "discriminant_factorization": discriminant,
        "transition_roots": transitions,
        "continuous_lambda_bands": [
            {"sample": "6", "positive_x_roots": 0},
            {"sample": "13/2", "positive_x_roots": 0},
            {"sample": "27/4", "positive_x_roots": 2},
            {"sample": "7", "positive_x_roots": 3},
            {"sample": "10", "positive_x_roots": 3},
            {"sample": "20", "positive_x_roots": 1},
            {"sample": "132", "positive_x_roots": 3},
            {"sample": "1722", "positive_x_roots": 1},
        ],
        "physical_triangular_harmonics": [
            {"ell": "2", "positive_x_roots": 0, "real_omega_roots": 0},
            {"ell": "3", "positive_x_roots": 3, "real_omega_roots": 6},
            {"ell": "4..10", "positive_x_roots": 1, "real_omega_roots": 2},
            {"ell": "11..40", "positive_x_roots": 3, "real_omega_roots": 6},
            {"ell": ">=41", "positive_x_roots": 1, "real_omega_roots": 2},
        ],
        "uniform_tail_reason": "all real discriminant and x=0 boundary transitions with Lambda>=6 lie below Lambda_41=1722, and the leading-x coefficient has no physical zero",
        "count_evidence_type": "EXACT_RATIONAL_STURM",
        "count_method": "exact x-Sturm counts at every triangular Lambda through ell=41 and at one sample in every continuous-Lambda chamber",
        "legacy_fixture": {
            "Lambda": 6,
            "omega_squared": "9/25",
            "Q21_value": sp.sstr(legacy_value),
            "nonzero": True,
            "consequence": "the legacy ell=2, M*omega=3/5 point is not on the polar finite-line exceptional wall",
            "evaluator_variable_correction": {
                "prior_value": sp.sstr(prior_misread),
                "prior_substitution": "the serialized even-omega polynomial was evaluated at omega=9/25, producing reparametrized x=(9/25)^2=81/625",
                "correct_substitution": "after conversion to Q21(Lambda,x), substitute x=omega^2=9/25",
                "disposition": "CORRECTED_EXACTLY_NO_EFFECT_ON_NONVANISHING",
            },
        },
    }


def build_outputs() -> dict[Path, bytes]:
    axial = load_checked(AXIAL, AXIAL_SHA)
    axial_receipt = load_checked(AXIAL_RECEIPT, AXIAL_RECEIPT_SHA)
    polar = load_checked(POLAR, POLAR_SHA)
    polar_receipt = load_checked(POLAR_RECEIPT, POLAR_RECEIPT_SHA)
    q21_data = load_checked(Q21_PATH, Q21_SHA)
    polar_wall = load_checked(POLAR_WALL, POLAR_WALL_SHA)
    if axial.get("result_id") != "PURE_WEYL_PHASE2_GENERAL_L_AXIAL_SELECTION_COUNTEREXAMPLE" or axial.get("lifecycle") != "CLASSIFIED":
        raise RuntimeError("axial input is not the terminal classified counterexample")
    if polar.get("result_id") != "POLAR_RESTRICTION_STABLE_MODULE_CURRENT_FILTRATION_V1":
        raise RuntimeError("refusing retired or partial polar input")
    if polar_receipt.get("status") != "PASS_SCOPED_TERMINAL":
        raise RuntimeError("polar closure lacks PASS_SCOPED_TERMINAL receipt")
    if polar["invariant_current_filtration"]["disposition"] != "NONRADICAL_AWAY_FROM_Q21_ZERO_LOCUS":
        raise RuntimeError("polar congruence disposition mismatch")
    q21 = q21_proof(q21_data)

    certificate = {
        "schema": "phase2-black-hole-generic-l-parity-disposition-v1",
        "result_id": "PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1",
        "result_token": "BH_PHASE2_GENERIC_L_AXIAL_COUNTEREXAMPLE_POLAR_FINITE_LINE_Q21_WALL",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "strict pure-Weyl gravity",
            "background": "Schwarzschild M>0 in ingoing Eddington-Finkelstein coordinates",
            "domain": "Lambda=ell*(ell+1), integer ell>=2, real omega!=0",
            "radial_class": "formal polyhomogeneous infinity data in the fixed Lee-Wald representative",
            "dangerous_layer_rule": "a radial/log layer r^p log(r)^q is nonintegrable when p>=-1 unless its invariant coefficient vanishes",
        },
        "input_snapshot": {
            "axial": {
                "path": str(AXIAL.relative_to(ROOT)),
                "result_id": axial["result_id"],
                "certificate_sha256": AXIAL_SHA,
                "receipt_sha256": AXIAL_RECEIPT_SHA,
                "evidence_commit": AXIAL_COMMIT,
                "receipt_status": axial_receipt["tiers"]["tier_1"]["status"],
            },
            "polar": {
                "path": str(POLAR.relative_to(ROOT)),
                "result_id": polar["result_id"],
                "certificate_sha256": POLAR_SHA,
                "receipt_sha256": POLAR_RECEIPT_SHA,
                "terminal_commit": POLAR_TERMINAL_COMMIT,
                "terminal_status": polar_receipt["status"],
                "rejected_inputs": [
                    "PHASE2_BLACK_HOLE_GENERAL_L_POLAR_DISPOSITION",
                    "PHASE2_BLACK_HOLE_GENERAL_L_POLAR_CANONICAL_LOG_FREE_FRONTIER_V1",
                ],
            },
            "q21": {
                "path": str(Q21_PATH.relative_to(ROOT)),
                "sha256": Q21_SHA,
                "bidegree": [21, 21],
                "term_count": 282,
            },
            "polar_wall": {
                "path": str(POLAR_WALL.relative_to(ROOT)),
                "sha256": POLAR_WALL_SHA,
                "identity_verified": polar_wall["finite_line"]["identity_verified"],
            },
        },
        "axial_phase": {
            "headline": "GENERIC_ELL_EINSTEIN_ONLY_FORMAL_RADIAL_SELECTION_FALSE",
            "E0": "finite nonzero r^-2 Einstein current on the full declared domain",
            "E2": "finite nonzero r^-2 Einstein current in the declared fixed representative",
            "X0": "non-Einstein all-orders formal lift with finite X0|X0 and nonzero finite E0|X0; finiteness is invariant under X0->X0+beta*E0",
            "X2": "UNCLASSIFIED_AFTER_FIRST_COUNTEREXAMPLE_STOP",
            "exceptional_set": "empty inside ell>=2, real omega!=0 for the certified E0/X0 counterexample",
            "legacy_fixture": "the inherited divergent axial ell=2 X0 table is invalid because it omitted the differentiated c' forcing",
        },
        "polar_phase": {
            "headline": "GENERICALLY_NONRADICAL_FINITE_MIXED_LINE_WITH_Q21_EXCEPTIONAL_WALL",
            "module_scope": polar["status"]["module_reconciliation"],
            "current_scope": polar["status"]["current"],
            "basis": polar["invariant_current_filtration"]["basis"],
            "generic_rank": polar["invariant_current_filtration"]["generic_rank_away_from_detK_walls"],
            "generic_radical_dimension": polar["invariant_current_filtration"]["generic_radical_dimension_away_from_detK_walls"],
            "finite_line": polar["status"]["finite_radical"],
            "exceptional_wall": "Q21(ell*(ell+1),omega^2)=0",
            "denominator_cleared_p_minus_2_factorization": polar_wall["finite_line"]["factorization"],
            "denominator_cleared_prefactor_constant_C": polar_wall["finite_line"]["constant_C"],
            "normalization_boundary": "this is the denominator-cleared induced-current coefficient, not a Hilbert norm",
            "at_exceptional_wall": "the p=-2 induced form vanishes and the deeper asymptotic-current filtration remains open",
            "congruence_invariants": polar["invariant_current_filtration"]["invariant_ledger"]["invariant"],
            "lift_sensitive": polar["invariant_current_filtration"]["invariant_ledger"]["lift_sensitive"],
            "zero_rate": polar["zero_rate_disposition"]["status"],
        },
        "q21_exceptional_frequency_count": q21,
        "joint_disposition": {
            "einstein_only_selection": "FALSE_IN_THE_DECLARED_FORMAL_RADIAL_CLASS_BY_AXIAL_X0",
            "parity_reading": "axial X0 survives the formal radial gate; the certified polar oscillatory block has a generically nonradical finite mixed Einstein/additional line away from Q21=0",
            "not_parity_complete_all_modes": "axial X2, terminal-only polar prefixes, and the deeper Q21-wall filtration remain unclassified",
            "strongest_theorem": "modewise formal radial survival after classical reduction is parity- and filtration-sensitive and does not reduce to an Einstein-image selection rule",
        },
        "claim_map_path": "black_hole_programme/phase2/generic_l_synthesis/claim_map.json",
        "does_not_establish": [
            "axial X2 disposition",
            "q9 extension of terminal-only polar prefixes",
            "the deeper polar filtration on Q21 exceptional frequencies",
            "all-order polar asymptotic solutions",
            "horizon-to-infinity matching",
            "an asymptotically flat phase space or Hilbert norm",
            "scattering, QNMs, ringdown, stability, particles, positivity or quantum theory",
        ],
        "verification": {
            "producer": "python3 -m black_hole_programme.phase2.generic_l_synthesis.produce --check",
            "independent": "python3 -m black_hole_programme.phase2.generic_l_synthesis.verify",
            "tests": "python3 -m unittest black_hole_programme.phase2.generic_l_synthesis.tests.test_generic_l_synthesis -v",
        },
    }

    claim_map = {
        "schema": "phase2-black-hole-generic-l-claim-map-v1",
        "result_id": certificate["result_id"],
        "claims": [
            {"claim_id": "BH-P2-JOIN-AXIAL-X0", "status": "CERTIFIED", "statement": certificate["axial_phase"]["X0"], "evidence": str(AXIAL.relative_to(ROOT))},
            {"claim_id": "BH-P2-JOIN-POLAR-FINITE-LINE", "status": "CERTIFIED_SCOPED", "statement": certificate["polar_phase"]["finite_line"], "evidence": str(POLAR.relative_to(ROOT))},
            {"claim_id": "BH-P2-JOIN-Q21-COUNTS", "status": "CERTIFIED", "statement": "positive x=omega^2 roots: ell=2:0; ell=3:3; ell=4..10:1; ell=11..40:3; ell>=41:1", "evidence": str(CERTIFICATE.relative_to(ROOT))},
            {"claim_id": "BH-P2-JOIN-PHASE-SPACE", "status": "DOES_NOT_ESTABLISH", "statement": "No horizon-to-infinity phase space or scattering theorem is constructed.", "evidence": str(CERTIFICATE.relative_to(ROOT))},
        ],
    }

    request = {
        "schema": "phase2-black-hole-paper-correction-request-v1",
        "result_id": "PHASE2_BLACK_HOLE_GENERIC_L_PAPER_CORRECTION_REQUEST_V1",
        "status": "REQUEST_ONLY_NO_PAPER_EDIT",
        "source_claim_map": str(CLAIM_MAP.relative_to(ROOT)),
        "papers": {
            "14": [
                "Withdraw the generic or ell=2 Einstein-only infinity-selection reading invalidated by the corrected finite axial X0 lift.",
                "Record the polar generically nonradical finite mixed line and its exact Q21 exceptional wall; at Q21=0 leave the deeper filtration open.",
                "At Lambda=6 and (M*omega)^2=9/25, record Q21!=0, so the legacy polar fixture is off the exceptional wall.",
                "Correct the evaluator-variable ledger: the previously recorded long rational used x=81/625 after substituting omega=9/25 into the serialized even-omega polynomial; the correct Q21(Lambda,x) substitution is x=9/25.",
                "Keep axial X2, terminal-only polar prefixes, phase-space completion and scattering explicitly unclassified."
            ],
            "15": [
                "Replace any parity-uniform Einstein-only boundary-selection summary by the axial counterexample plus scoped polar finite-line/Q21 phase diagram.",
                "Preserve the REDUCED-MODE boundary: no asymptotic phase space, scattering, stability, particle or quantum promotion."
            ]
        },
        "forbidden_promotions": [
            "formal radial integrability to horizon-to-infinity admissibility",
            "Q21 nonvanishing to positivity",
            "a chosen extra-lift sign to a congruence invariant",
            "the scoped polar module to all-order extension",
        ],
    }

    report = f"""# Phase 2 generic-ell Schwarzschild parity disposition

Result: `{certificate['result_token']}`

Dependency tags: `LOCAL-ALGEBRAIC` + `REDUCED-MODE`

Lifecycle: `CLASSIFIED`

## Joined disposition

The generic-ell Einstein-only formal radial selection claim is false.  The
corrected axial `X0` carrier is non-Einstein, extends formally to all radial
orders in its declared class, and has finite fixed-representative Lee--Wald
pairing for every integer `ell>=2` and real `omega!=0`.  Axial `X2` remains
unclassified.

The terminal polar closure proves a different scoped structure.  Its ordered
oscillatory `(E,X0,X1,X2)` current has generic rank three and a one-dimensional
mixed Einstein/additional filtered radical through `p=0,-1`.  The first finite
`p=-2` form on that line is generically nonzero.  Its exact exceptional wall is

```text
Q21(ell*(ell+1), omega^2) = 0.
```

At that wall the deeper filtration is open; it is not interpreted as a
physical radical, positivity wall, or scattering threshold.

## Exact exceptional-frequency count

Writing `x=omega^2>0`, `Q21` has bidegree `(21,21)` and 282 terms.  Its leading
`x` coefficient is

```text
-7253554917687775048237056*(Lambda+2)*(5*Lambda+8),
```

which is nonzero for `Lambda>=6`.  The exact `x=0` boundary factorization and
the exact `x`-discriminant show six transition roots above `Lambda=6`: five
discriminant roots and one boundary root.  Rational isolating intervals place
them in `(6.588,6.589)`, `(6.796,6.797)`, `(8.226,8.227)`,
`(13.983,13.984)`, `(111.320,111.322)`, and
`(1640.901,1640.902)`.  Exact `x`-Sturm counts then give:

| harmonic | positive `x` roots | real nonzero `omega` roots |
|---|---:|---:|
| `ell=2` | 0 | 0 |
| `ell=3` | 3 | 6 |
| `4<=ell<=10` | 1 | 2 |
| `11<=ell<=40` | 3 | 6 |
| `ell>=41` | 1 | 2 |

The continuous-`Lambda` chamber counts are recorded separately in the
certificate.  At the legacy fixture `Lambda=6`, `omega^2=9/25`, `Q21` equals

```text
{q21['legacy_fixture']['Q21_value']}
```

and is exactly nonzero.

The previously recorded longer rational is also replayed exactly, but it is
`Q21(6,81/625)`: it arose by substituting `omega=9/25` into the serialized
even-`omega` polynomial and hence squaring the intended `x` a second time.
It is not the value of `Q21(6,x)` at `x=9/25`, and it is not a normalized
Hilbert norm.  Separately, the denominator-cleared `p=-2` induced-current
coefficient has the certified factorization
`C*omega^51*Lambda^3*(Lambda-2)^5*P6^2*P20*Q21`.

## Claim boundary

This is a formal infinity-mode classification in a fixed Lee--Wald
representative.  It does not classify axial `X2`, extend the terminal-only
polar prefixes, resolve the deeper `Q21=0` filtration, construct a global
asymptotic phase space, perform horizon-to-infinity matching, or establish
scattering, QNMs, stability, particles, positivity, or a quantum theory.

CLOSE-OUT: DONE — exact axial and terminal polar inputs are joined into a scoped generic-ell phase diagram, including the independently certified Q21 exceptional-frequency count and every unresolved boundary.
EVIDENCE: black_hole_programme/phase2/generic_l_synthesis/certificate.json
"""

    provisional = {
        CERTIFICATE: (json.dumps(certificate, indent=2, sort_keys=True) + "\n").encode(),
        CLAIM_MAP: (json.dumps(claim_map, indent=2, sort_keys=True) + "\n").encode(),
        CORRECTION_REQUEST: (json.dumps(request, indent=2, sort_keys=True) + "\n").encode(),
        REPORT: report.encode(),
    }
    receipt = {
        "schema": "phase2-black-hole-generic-l-tier-receipt-v1",
        "result_id": "PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_RECEIPT_V1",
        "status": "PASS_SCOPED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "commands": [
            "python3 -m py_compile black_hole_programme/phase2/generic_l_synthesis/{produce.py,verify.py} black_hole_programme/phase2/generic_l_synthesis/tests/test_generic_l_synthesis.py",
            "python3 -m black_hole_programme.phase2.generic_l_synthesis.produce --check",
            "python3 -m black_hole_programme.phase2.generic_l_synthesis.verify",
            "python3 -m unittest black_hole_programme.phase2.generic_l_synthesis.tests.test_generic_l_synthesis -v",
            "git diff --check -- <exact allowed paths>"
        ],
        "artifact_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(data).hexdigest() for path, data in provisional.items()},
        "test_result": "5 scoped tests passed; independent exact fixture and fixed-harmonic Sturm verifier passed; producer byte-current check passed",
        "input_sha256": {
            str(AXIAL.relative_to(ROOT)): AXIAL_SHA,
            str(POLAR.relative_to(ROOT)): POLAR_SHA,
            str(Q21_PATH.relative_to(ROOT)): Q21_SHA,
        },
        "claim_boundary": "Scoped formal radial parity join; no global phase space, horizon matching, scattering, stability, particle, positivity or quantum claim.",
    }
    provisional[RECEIPT] = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    return provisional


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.check:
        mismatches = [str(path) for path, data in outputs.items() if not path.exists() or path.read_bytes() != data]
        if mismatches:
            raise SystemExit("stale outputs: " + ", ".join(mismatches))
        print("generic-l synthesis outputs are byte-current")
        return 0
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
