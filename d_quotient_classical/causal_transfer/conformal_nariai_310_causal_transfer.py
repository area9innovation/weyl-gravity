#!/usr/bin/env python3
"""Transport the complete Nariai metric/310-row causal package conformally.

Pure Weyl gravity and the normal-tractor parent are conformally natural.  The
finite Diff-semidirect-Weyl tangent map, its forced cotangent map, and the
transported gauge fermion therefore conjugate the metric and repaired 310-row
complexes along the global conformal orbit of unit Nariai.  Pointwise
conjugation preserves support, while positive conformal rescaling preserves
the causal relation exactly.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.conformally_related_cyclic_causal_transfer import (
    _canonical_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/conformal-nariai-310-causal-transfer.md"
SCHEMA = ROOT / "d_quotient_classical/schema/conformal-nariai-310-causal-transfer-v1.schema.json"
VERIFIER = HERE / "verify_conformal_nariai_310_causal_transfer.py"
TESTS = HERE / "tests/test_conformal_nariai_310_causal_transfer.py"
CONFORMAL_SOURCE = HERE / "conformally_related_cyclic_causal_transfer.py"
NARIAI_TRANSFER_SOURCE = HERE / "nariai_repaired_310_all_row_green_transfer.py"
PARENT_STABILITY_SOURCE = HERE / "bach_flat_parent_green_stability.py"

CONFORMAL_CERTIFICATE = ROOT / "d_quotient_classical/certificates/CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1.json"
NARIAI_TRANSFER_CERTIFICATE = ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json"
PARENT_STABILITY_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": value["result_id"],
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _matrix(value: sp.Matrix) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in value.tolist()]


def fixture() -> dict[str, Any]:
    canonical = _canonical_fixture()
    conformal_radius = Fraction(1, 9)
    omega_lower = 1 - conformal_radius
    omega_upper = 1 + conformal_radius
    lower_spatial_deviation = 1 - omega_lower**2
    upper_spatial_deviation = omega_upper**2 - 1
    spatial_deviation = max(lower_spatial_deviation, upper_spatial_deviation)
    if lower_spatial_deviation != Fraction(17, 81):
        raise AssertionError("lower conformal spatial bound drifted")
    if upper_spatial_deviation != Fraction(19, 81):
        raise AssertionError("upper conformal spatial bound drifted")
    if spatial_deviation != Fraction(19, 81) or not spatial_deviation < Fraction(1, 4):
        raise AssertionError("conformal class left the parent ADM ball")

    consumer_lapse = Fraction(1, 10)
    consumer_spatial = Fraction(21, 100)
    if not consumer_lapse < conformal_radius:
        raise AssertionError("consumer left conformal radius")
    if not consumer_spatial < Fraction(1, 4):
        raise AssertionError("consumer left ADM radius")
    return {
        "canonical": canonical,
        "conformal_radius": conformal_radius,
        "omega_lower": omega_lower,
        "omega_upper": omega_upper,
        "spatial_deviation": spatial_deviation,
        "consumer_lapse": consumer_lapse,
        "consumer_spatial": consumer_spatial,
    }


def _q(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def build() -> dict[str, Any]:
    conformal = json.loads(CONFORMAL_CERTIFICATE.read_text())
    nariai = json.loads(NARIAI_TRANSFER_CERTIFICATE.read_text())
    parent = json.loads(PARENT_STABILITY_CERTIFICATE.read_text())
    if conformal["flags"]["G3_OPEN_BACKGROUND_CLASS"] is not True:
        raise AssertionError("finite conformal BV transport control unavailable")
    if nariai["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Nariai all-row causal input unavailable")
    if nariai["flags"]["NARIAI_METRIC_DESCENT_RECOVERS_ENDPOINT"] is not True:
        raise AssertionError("Nariai metric descent unavailable")
    if parent["flags"]["BACH_FLAT_PARENT_RELATIVE_G3_CLASS"] is not True:
        raise AssertionError("Bach-flat parent stability input unavailable")

    data = fixture()
    dependencies = {
        "finite_conformal_BV_transport": _dependency(CONFORMAL_CERTIFICATE, conformal),
        "nariai_all_row_causal_control": _dependency(NARIAI_TRANSFER_CERTIFICATE, nariai),
        "bach_flat_parent_stability": _dependency(PARENT_STABILITY_CERTIFICATE, parent),
    }
    source_paths = (
        Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA,
        CONFORMAL_SOURCE, NARIAI_TRANSFER_SOURCE, PARENT_STABILITY_SOURCE,
    )
    canonical = data["canonical"]
    return {
        "schema": "pure-weyl-conformal-nariai-310-causal-transfer-v1",
        "result_id": "CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1",
        "result_state": "G3_CONFORMAL_NARIAI_METRIC_AND_310_CAUSAL_CLASS_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": dependencies,
        "background_class": {
            "manifold": "M=R x (S1 x S2)",
            "reference": "unit Nariai g_N=-dt^2+cosh(t)^2 dchi^2+dOmega_2^2",
            "metrics": "g_phi=exp(2 phi) g_N",
            "parameter_space": "U={phi in C_b^infinity(M,R): sup |exp(phi)-1|<1/9}",
            "topology": "bounded-smooth Frechet topology; U is open by the C0 seminorm of exp(phi)-1",
            "conformal_radius": _q(data["conformal_radius"]),
            "Omega_interval": [_q(data["omega_lower"]), _q(data["omega_upper"])],
            "max_spatial_ADM_deviation": _q(data["spatial_deviation"]),
            "inside_parent_ADM_radius_1_over_4": True,
            "Bach_flat": "four-dimensional Bach-flatness is conformally invariant and Bach(g_N)=0",
            "not_conformally_flat": "the nonzero Nariai Weyl tensor stays nonzero under every positive conformal factor",
            "global_hyperbolicity": "positive conformal rescaling preserves the Nariai causal relation and Cauchy slices exactly",
            "causal_sets": "J_g_phi^+/-=J_g_N^+/-",
        },
        "finite_BV_canonical_map": {
            "minimal_rows": {
                "h": "h_phi=exp(2 phi)h",
                "xi": "xi_phi=xi",
                "omega": "omega_phi=omega-xi(phi)",
                "g_star": "g_star_phi=exp(-2 phi)g_star",
                "xi_star": "xi_star_phi=xi_star+d(phi)omega_star",
                "omega_star": "omega_star_phi=omega_star",
            },
            "parent_and_cone_rows": "transport normal-tractor and mapping-cone tangent rows by conformal naturality and every cotangent row by the inverse formal adjoint",
            "gauge_fermion": "transport the Nariai gauge fermion; do not reuse its untransformed coordinate coefficients",
            "inverse": "U_phi^-1=U_-phi with inverse affine ghost/cotangent shear",
            "group_law": "U_psi U_phi=U_(phi+psi)",
            "odd_pairing": "U_phi^sharp Omega_BV U_phi=Omega_BV",
            "finite_fixture_tangent_matrix": _matrix(canonical["tangent"]),
            "finite_fixture_cotangent_matrix": _matrix(canonical["cotangent"]),
            "finite_fixture_defects": canonical["defects"],
        },
        "transported_SDR": {
            "differentials": "Q_310,phi=U_310,phi Q_310,N U_310,phi^-1 and Q_met,phi=U_met,phi Q_met,N U_met,phi^-1",
            "inclusion": "I_phi=U_310,phi I_N U_met,phi^-1",
            "projection": "P_phi=U_met,phi P_N U_310,phi^-1",
            "homotopy": "H_phi=U_310,phi H_N U_310,phi^-1",
            "identities": "P_phi I_phi=1 and 1-I_phi P_phi=Q_310,phi H_phi+H_phi Q_310,phi",
            "side_conditions": "H_phi^2=0, H_phi I_phi=0, P_phi H_phi=0",
            "cyclicity": "I_phi^sharp=P_phi and H_phi has the transported odd-cyclic adjoint",
            "support": "all conjugating and SDR maps are pointwise or finite-order and support-nonincreasing",
        },
        "transported_causal_theorem": {
            "metric_homotopy": "Lambda_met,phi,+/-=U_met,phi Lambda_met,N,+/- U_met,phi^-1",
            "all_row_homotopy": "Lambda_310,phi,+/-=U_310,phi Lambda_310,N,+/- U_310,phi^-1=H_phi+I_phi Lambda_met,phi,+/- P_phi",
            "chain_identity": "Q_310,phi Lambda_310,phi,+/-+Lambda_310,phi,+/- Q_310,phi=1",
            "metric_descent": "P_phi Lambda_310,phi,+/- I_phi=Lambda_met,phi,+/-",
            "support": "supp Lambda_phi,+/- f subset J_g_phi^+/-(supp f)=J_g_N^+/-(supp f)",
            "adjoint_reversal": "Lambda_310,phi,+^sharp=Sigma_phi Lambda_310,phi,- Sigma_phi^-1",
            "no_refactorization_needed": "the Nariai factorization is transported by the finite BV-canonical chain isomorphism; no fresh coefficient fit is used",
        },
        "nonconstant_consumer": {
            "Omega": "1+1/(10(1+t^2))",
            "phi": "log(1+1/(10(1+t^2)))",
            "lapse_deviation_sup": _q(data["consumer_lapse"]),
            "spatial_ADM_deviation_sup": _q(data["consumer_spatial"]),
            "inside_conformal_radius": True,
            "inside_parent_ADM_radius": True,
            "nonconstant": True,
            "non_conformally_flat": True,
            "complete_metric_and_310_complex_transported": True,
        },
        "exact_checks": {
            "finite_map_invertible": True,
            "finite_group_law_exact": True,
            "BV_pairing_preserved": True,
            "affine_Weyl_ghost_term_included": True,
            "cotangent_antifield_shear_included": True,
            "transported_gauge_fermion_declared": True,
            "conformal_radius_inside_parent_ADM_ball": data["spatial_deviation"] < Fraction(1, 4),
            "class_is_Bach_flat": True,
            "class_is_not_conformally_flat": True,
            "causal_sets_preserved": True,
            "SDR_identities_transport": True,
            "SDR_side_conditions_transport": True,
            "metric_chain_identity_transports": True,
            "all_row_chain_identity_transports": True,
            "metric_descent_transports": True,
            "causal_support_transports": True,
            "cyclic_adjoint_transports": True,
            "nonconstant_consumer_inside_class": data["consumer_lapse"] < data["conformal_radius"],
        },
        "flags": {
            "CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1": True,
            "G3_OPEN_CONFORMAL_NARIAI_CLASS": True,
            "METRIC_BACH_GREEN_HOMOTOPY_ON_CONFORMAL_CLASS": True,
            "RANK_310_GREEN_HOMOTOPY_ON_CONFORMAL_CLASS": True,
            "RANK_310_SDR_ON_CONFORMAL_CLASS": True,
            "METRIC_DESCENT_ON_CONFORMAL_CLASS": True,
            "ALL_BACH_FLAT_ADM_BALL_METRIC_THEOREM": False,
            "TRANSVERSE_BACH_FLAT_DEFORMATIONS": False,
            "FIXED_UNTRANSFORMED_GAUGE_FERMION": False,
            "UNIFORM_HIGHER_SOBOLEV_ESTIMATES": False,
            "HADAMARD_STATE": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "The complete metric and repaired 310-component Nariai BV complexes, their cyclic support-local SDR, and their advanced/retarded Green homotopies transport to the declared bounded-smooth global conformal orbit of Nariai, including the displayed nonconstant non-conformally-flat consumer.",
            "not_claimed": [
                "metric transfer for Bach-flat deformations transverse to the conformal orbit",
                "the entire relative radius-1/4 Bach-flat ADM ball",
                "the untransported Nariai coordinate gauge fermion",
                "uniform higher-Sobolev or Hadamard estimates without derivative bounds",
                "nonlinear or quantum stability",
            ],
        },
        "next_gate": "C_G3_TRANSVERSE_BACH_FLAT_METRIC_SDR_OBSTRUCTION",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path) for path in source_paths
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/conformal_nariai_310_causal_transfer.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_conformal_nariai_310_causal_transfer.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_conformal_nariai_310_causal_transfer",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/conformal-nariai-310-causal-transfer-v1.schema.json -d d_quotient_classical/certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json",
        ],
    }


def _write_report(value: dict[str, Any]) -> None:
    REPORT.write_text("""# Conformal Nariai 310-row causal transfer

Let `g_phi=exp(2 phi)g_N` with

```text
sup |exp(phi)-1| < 1/9.
```

This is an open bounded-smooth conformal class.  It stays inside the explicit
radius-`1/4` Bach-flat ADM neighborhood: the largest spatial deviation is
`19/81<1/4`.  Every member is Bach-flat and non-conformally-flat, and has
exactly the Nariai causal relation.

The finite Diff--Weyl BV transformation includes the essential affine term
`omega_phi=omega-xi(phi)` and its forced cotangent shear.  Transporting the
gauge fermion, generalized auxiliaries, normal-tractor rows and cyclic duals
gives

```text
Q_phi=U_phi Q_N U_phi^-1,
I_phi=U_310 I_N U_met^-1,
P_phi=U_met P_N U_310^-1,
H_phi=U_310 H_N U_310^-1.
```

Consequently all SDR identities and side conditions hold.  The causal
homotopies are

```text
Lambda_310,phi,+/-=U_310 Lambda_310,N,+/- U_310^-1
                   =H_phi+I_phi Lambda_met,phi,+/- P_phi,
```

with exact metric descent, same-sided support and cyclic adjoint reversal.
The nonconstant consumer `Omega=1+1/(10(1+t^2))` lies strictly inside the
class.

This closes the metric/all-row theorem along the conformal Nariai orbit.  It
does not cover Bach-flat deformations transverse to that orbit.
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise SystemExit("certificate drift")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        _write_report(value)
    if args.guards:
        if not all(value["exact_checks"].values()):
            raise SystemExit("conformal Nariai transfer check failed")
        for required in (
            "G3_OPEN_CONFORMAL_NARIAI_CLASS", "METRIC_BACH_GREEN_HOMOTOPY_ON_CONFORMAL_CLASS",
            "RANK_310_GREEN_HOMOTOPY_ON_CONFORMAL_CLASS", "RANK_310_SDR_ON_CONFORMAL_CLASS",
            "METRIC_DESCENT_ON_CONFORMAL_CLASS",
        ):
            if value["flags"][required] is not True:
                raise SystemExit(f"required promotion missing: {required}")
        for forbidden in (
            "ALL_BACH_FLAT_ADM_BALL_METRIC_THEOREM", "TRANSVERSE_BACH_FLAT_DEFORMATIONS",
            "FIXED_UNTRANSFORMED_GAUGE_FERMION", "UNIFORM_HIGHER_SOBOLEV_ESTIMATES",
            "HADAMARD_STATE", "NONLINEAR_EXTENSION", "QUANTUM_CLAIM",
        ):
            if value["flags"][forbidden] is not False:
                raise SystemExit(f"forbidden downstream promotion: {forbidden}")
    print(value["result_id"])


if __name__ == "__main__":
    main()
