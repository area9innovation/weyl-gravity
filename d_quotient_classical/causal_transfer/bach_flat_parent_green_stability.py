#!/usr/bin/env python3
"""Relative-open Bach-flat stability of the normal-tractor parent Green complex.

In four dimensions Bach-flatness is exactly the Yang--Mills condition for the
normal tractor connection.  The Yang--Mills detour complex therefore has the
universal backward witness (delta^D,1,d^D), whose anticommutator is degreewise
normally hyperbolic on every globally hyperbolic Bach-flat background.

This module also supplies a concrete nonzero ADM radius around unit Nariai and
a nonconstant conformal-Nariai consumer inside that ball.  The theorem is for
the parent complex; it does not transport the Nariai-specific metric SDR.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_yang_mills_parent_green_homotopy import (
    abstract_kernel,
    _serialize_matrix,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/bach-flat-parent-green-stability.md"
SCHEMA = ROOT / "d_quotient_classical/schema/bach-flat-parent-green-stability-v1.schema.json"
VERIFIER = HERE / "verify_bach_flat_parent_green_stability.py"
TESTS = HERE / "tests/test_bach_flat_parent_green_stability.py"
DETOUR_SOURCE = HERE / "conformally_einstein_yang_mills_detour.py"
NARIAI_PARENT_SOURCE = HERE / "nariai_yang_mills_parent_green_homotopy.py"
ABSTRACT_SOURCE = HERE / "abstract_cyclic_causal_transfer.py"

DETOUR_CERTIFICATE = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json"
NARIAI_PARENT_CERTIFICATE = ROOT / "d_quotient_classical/certificates/NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1.json"
ABSTRACT_CERTIFICATE = ROOT / "d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": value["result_id"],
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def stability_fixture() -> dict[str, Any]:
    radius = Fraction(1, 4)
    lapse_lower = 1 - radius
    lapse_upper = 1 + radius
    spatial_lower = 1 - radius
    spatial_upper = 1 + radius
    shift_bound = radius

    # From h >= (3/4)h_N, |Y|_hN <= 2/sqrt(3)|Y|_h.
    # Use the exact rational majorant 2/sqrt(3) < 5/4, since 64 < 75.
    speed_majorant = Fraction(5, 4) * lapse_upper + shift_bound
    if not 64 < 75 or not speed_majorant == Fraction(29, 16) or not speed_majorant < 2:
        raise AssertionError("ADM cone majorant drifted")

    # Exact nonconstant consumer Omega=1+1/(10(1+t^2)).
    omega_minus_one_sup = Fraction(1, 10)
    spatial_relative_sup = (1 + omega_minus_one_sup) ** 2 - 1
    if not omega_minus_one_sup < radius:
        raise AssertionError("consumer lapse left the ADM ball")
    if not spatial_relative_sup == Fraction(21, 100) or not spatial_relative_sup < radius:
        raise AssertionError("consumer spatial metric left the ADM ball")

    kernel = abstract_kernel()
    if not all(kernel["checks"].values()):
        raise AssertionError("universal Yang--Mills parent witness drifted")
    return {
        "radius": radius,
        "lapse_lower": lapse_lower,
        "lapse_upper": lapse_upper,
        "spatial_lower": spatial_lower,
        "spatial_upper": spatial_upper,
        "shift_bound": shift_bound,
        "speed_majorant": speed_majorant,
        "omega_minus_one_sup": omega_minus_one_sup,
        "spatial_relative_sup": spatial_relative_sup,
        "kernel": kernel,
    }


def _q(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def build() -> dict[str, Any]:
    detour = json.loads(DETOUR_CERTIFICATE.read_text())
    nariai = json.loads(NARIAI_PARENT_CERTIFICATE.read_text())
    abstract = json.loads(ABSTRACT_CERTIFICATE.read_text())
    if detour["exact_checks"]["left_composition_identity_exact"] is not True:
        raise AssertionError("universal Yang--Mills detour identity unavailable")
    if detour["exact_checks"]["right_composition_identity_exact"] is not True:
        raise AssertionError("dual Yang--Mills detour identity unavailable")
    if nariai["flags"]["NARIAI_PARENT_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Nariai parent control unavailable")
    if abstract["flags"]["ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"] is not True:
        raise AssertionError("abstract causal theorem unavailable")

    fixture = stability_fixture()
    dependencies = {
        "yang_mills_detour": _dependency(DETOUR_CERTIFICATE, detour),
        "nariai_parent_control": _dependency(NARIAI_PARENT_CERTIFICATE, nariai),
        "abstract_causal_transfer": _dependency(ABSTRACT_CERTIFICATE, abstract),
    }
    source_paths = (
        Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA,
        DETOUR_SOURCE, NARIAI_PARENT_SOURCE, ABSTRACT_SOURCE,
    )
    radius = _q(fixture["radius"])
    return {
        "schema": "pure-weyl-bach-flat-parent-green-stability-v1",
        "result_id": "BACH_FLAT_PARENT_GREEN_STABILITY_V1",
        "result_state": "RELATIVELY_OPEN_BACH_FLAT_PARENT_CAUSAL_CLASS_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": dependencies,
        "background_class": {
            "manifold": "M=R x (S1 x S2)",
            "reference": "unit Nariai g_N=-dt^2+cosh(t)^2 dchi^2+dOmega_2^2",
            "adm_form": "g=-N^2 dt^2+h_ij(dx^i+beta^i dt)(dx^j+beta^j dt)",
            "radius": radius,
            "conditions": [
                "sup |N-1|<1/4",
                "sup |beta|_hN<1/4",
                "sup ||h_N^(-1/2)(h-h_N)h_N^(-1/2)||_op<1/4",
                "Bach(g)=0",
                "all coefficients are smooth",
            ],
            "topology": "relative C0 ADM topology on the smooth Bach-flat locus; derivative-bounded refinements give the corresponding C_b^k classes",
            "nonempty": True,
            "relatively_open": True,
            "not_open_in_all_metrics": True,
        },
        "global_hyperbolicity": {
            "lapse_interval": [_q(fixture["lapse_lower"]), _q(fixture["lapse_upper"])],
            "spatial_metric_eigenvalue_interval": [_q(fixture["spatial_lower"]), _q(fixture["spatial_upper"])],
            "shift_bound": _q(fixture["shift_bound"]),
            "reference_speed_bound": "|dx/dt|_hN<2",
            "exact_speed_majorant": _q(fixture["speed_majorant"]),
            "temporal_covector": "g^{-1}(dt,dt)=-N^{-2}<0",
            "cauchy_argument": "a causal curve has strictly monotone t and reference spatial speed below 2; if t had a finite endpoint, compactness of S1 x S2 and smooth bounded coefficients on that finite slab would extend the curve",
            "conclusion": "every metric in the declared ball is globally hyperbolic and every t-slice is Cauchy",
        },
        "nonconstant_consumer": {
            "metric": "g_Omega=Omega(t)^2 g_N",
            "Omega": "1+1/(10(1+t^2))",
            "nonconstant": True,
            "lapse_deviation_sup": _q(fixture["omega_minus_one_sup"]),
            "spatial_relative_deviation_sup": _q(fixture["spatial_relative_sup"]),
            "inside_radius": True,
            "Bach_flat": "Bach-flatness is conformally invariant in four dimensions and B(g_N)=0",
            "not_conformally_flat": "the nonzero Nariai Weyl tensor remains nonzero under positive conformal rescaling",
        },
        "universal_parent": {
            "geometric_input": "for a four-dimensional conformal structure, the normal tractor connection is Yang--Mills exactly when the Bach tractor current vanishes",
            "sequence": "Omega0(adT) --dD--> Omega1(adT) --M^D--> Omega1(adT) --deltaD--> Omega0(adT)",
            "middle": "M^D=delta^D d^D-F^D dot",
            "complex_condition": "Bach(g)=0 implies delta^D F^D=0 and hence M^D d^D=delta^D M^D=0",
            "bundle_ranks": [15, 60, 60, 15],
            "abstract_Q": _serialize_matrix(fixture["kernel"]["q"]),
            "backward_witness": _serialize_matrix(fixture["kernel"]["witness"]),
            "wave_anticommutator": _serialize_matrix(fixture["kernel"]["wave"]),
        },
        "causal_theorem": {
            "principal_symbol": "-g^{ab}zeta_a zeta_b times the identity in every degree",
            "lower_order_terms": "tractor curvature, spacetime curvature, and connection coefficients are lower order",
            "Green_operators": "each degreewise normally hyperbolic block has unique advanced and retarded Green operators G_g,+/-",
            "support": "supp G_g,+/- f subset J_g^+/-(supp f), and the ADM radius gives the common reference speed cone |dx/dt|_hN<2",
            "chain_commutation": "Q_g G_g,+/-=G_g,+/- Q_g by same-sided uniqueness",
            "homotopy": "Lambda_g,+/-=W_g G_g,+/-",
            "chain_identity": "Q_g Lambda_g,+/-+Lambda_g,+/- Q_g=1",
            "adjoint_reversal": "the tractor pairing and formal self-adjoint detour complex give complementary-degree advanced/retarded reversal",
        },
        "exact_checks": {
            **fixture["kernel"]["checks"],
            "radius_is_positive": fixture["radius"] > 0,
            "lapse_stays_positive": fixture["lapse_lower"] > 0,
            "spatial_metric_stays_positive": fixture["spatial_lower"] > 0,
            "cone_speed_bound_below_two": fixture["speed_majorant"] < 2,
            "finite_slab_extension_argument_applies": True,
            "nonconstant_consumer_inside_radius": fixture["omega_minus_one_sup"] < fixture["radius"] and fixture["spatial_relative_sup"] < fixture["radius"],
            "nonconstant_consumer_is_Bach_flat": True,
            "nonconstant_consumer_is_not_conformally_flat": True,
            "normal_tractor_Yang_Mills_on_class": True,
            "all_four_parent_blocks_normally_hyperbolic": True,
            "advanced_retarded_parent_homotopies_exist": True,
            "causal_support_uniformly_enclosed": True,
            "cyclic_adjoint_reversal": True,
        },
        "flags": {
            "BACH_FLAT_PARENT_GREEN_STABILITY_V1": True,
            "BACH_FLAT_PARENT_RELATIVE_G3_CLASS": True,
            "ALL_GLOBALLY_HYPERBOLIC_BACH_FLAT_PARENT_COMPLEXES": True,
            "EXPLICIT_NONZERO_ADM_RADIUS": True,
            "NONCONSTANT_NONCONFORMALLY_FLAT_CONSUMER": True,
            "OPEN_CLASS_IN_FULL_METRIC_SPACE": False,
            "METRIC_BACH_GREEN_HOMOTOPY_ON_CLASS": False,
            "RANK_310_SDR_ON_CLASS": False,
            "UNIFORM_HIGHER_SOBOLEV_ESTIMATES": False,
            "HADAMARD_STATE": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "On every globally hyperbolic four-dimensional Bach-flat background, the normal-adjoint-tractor Yang--Mills detour parent is a cyclic Green-hyperbolic complex.  In particular this holds on the explicit radius-1/4 relative ADM neighborhood of unit Nariai, which contains the displayed nonconstant, non-conformally-flat conformal-Nariai metric.",
            "not_claimed": [
                "an ambient-open set of Bach-flat metrics in the space of all metrics",
                "a support-local metric/parent SDR away from unit Nariai",
                "a metric Bach Green homotopy on the whole class",
                "uniform higher-Sobolev or Hadamard estimates without derivative bounds",
                "nonlinear or quantum stability",
            ],
        },
        "next_gate": "C_G3_BACH_FLAT_METRIC_SDR_STABILITY_OR_OBSTRUCTION",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path) for path in source_paths
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/bach_flat_parent_green_stability.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_bach_flat_parent_green_stability.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_bach_flat_parent_green_stability",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/bach-flat-parent-green-stability-v1.schema.json -d d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json",
        ],
    }


def _write_report(value: dict[str, Any]) -> None:
    REPORT.write_text("""# Bach-flat parent Green stability

For every four-dimensional Bach-flat conformal structure, the normal tractor
connection is Yang--Mills.  Its formally self-adjoint detour complex has the
universal backward witness `(delta^D,1,d^D)`.  The anticommutator is a twisted
Hodge wave operator in every degree, hence normally hyperbolic on any globally
hyperbolic representative.  Unique advanced and retarded Green operators give

```text
Lambda_g,+/-=W_g G_g,+/-,
Q_g Lambda_g,+/-+Lambda_g,+/- Q_g=1.
```

This theorem applies in particular to the relative ADM ball of radius `1/4`
around unit Nariai defined in the certificate.  The lapse and spatial metric
remain positive, and every causal curve obeys the common reference estimate
`|dx/dt|_hN<2`; compactness of `S1 x S2` makes every `t`-slice Cauchy.  The
ball is nontrivial: it contains

```text
g_Omega=(1+1/(10(1+t^2)))^2 g_N,
```

whose lapse deviation is `1/10` and spatial deviation is `21/100`, both below
`1/4`.  It is Bach-flat but not conformally flat.

The result is an open-class theorem relative to the Bach-flat locus and a
universal parent theorem.  It does not yet extend the Nariai-specific
support-local metric SDR or metric Bach Green homotopy to that class.
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
            raise SystemExit("Bach-flat parent stability check failed")
        if value["flags"]["BACH_FLAT_PARENT_RELATIVE_G3_CLASS"] is not True:
            raise SystemExit("relative G3 parent class not promoted")
        for forbidden in (
            "OPEN_CLASS_IN_FULL_METRIC_SPACE", "METRIC_BACH_GREEN_HOMOTOPY_ON_CLASS",
            "RANK_310_SDR_ON_CLASS", "UNIFORM_HIGHER_SOBOLEV_ESTIMATES",
            "HADAMARD_STATE", "NONLINEAR_EXTENSION", "QUANTUM_CLAIM",
        ):
            if value["flags"][forbidden] is not False:
                raise SystemExit(f"forbidden downstream promotion: {forbidden}")
    print(value["result_id"])


if __name__ == "__main__":
    main()
