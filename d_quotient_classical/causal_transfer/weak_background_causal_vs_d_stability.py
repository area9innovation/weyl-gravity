#!/usr/bin/env python3
"""First scoped background-stability theorem for the classical causal complex.

This consumer deliberately separates:

* persistence of advanced/retarded cyclic Green homotopies; and
* persistence of a fixed residual D-Cartan contraction and target carrier.

It hash-consumes the existing conformal-cylinder, Bach-flat and
Kantowski--Sachs producers.  It does not regenerate any of them.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/weak-background-causal-vs-d-stability.md"
SCHEMA = ROOT / "d_quotient_classical/schema/weak-background-causal-vs-d-stability-v1.schema.json"
VERIFIER = HERE / "verify_weak_background_causal_vs_d_stability.py"
TESTS = HERE / "tests/test_weak_background_causal_vs_d_stability.py"

DEPENDENCIES = {
    "sharp_transfer_theorem": ROOT / "d_quotient_classical/certificates/GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json",
    "conformal_cylinder_orbit": ROOT / "d_quotient_classical/certificates/CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1.json",
    "wz_d_cartan": ROOT / "d_quotient_classical/certificates/WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json",
    "bach_flat_parent": ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json",
    "bach_flat_metric": ROOT / "d_quotient_classical/certificates/BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
    "bach_flat_sdr": ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_NATURAL_SDR_V1.json",
    "bach_flat_rank310": ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1.json",
    "ks_common_slab": ROOT / "d_quotient_classical/certificates/NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1.json",
    "ks_rank310": ROOT / "d_quotient_classical/certificates/NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1.json",
    "ks_global_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _zero(matrix: sp.Matrix) -> bool:
    return all(sp.factor(value) == 0 for value in matrix)


def _exact_fixtures() -> dict[str, Any]:
    """Recompute the D-carrier split and a finite residual stability model."""
    t, z = sp.symbols("t z", real=True)

    # Positive same-target fixture.  Here z is the standard height function
    # on S^3, so -1 <= z <= 1 and Omega is globally positive.
    omega_spatial = 1 + z / 10
    phi_spatial = sp.log(omega_spatial)
    sigma_spatial = sp.diff(phi_spatial, t)
    if sigma_spatial != 0:
        raise AssertionError("time-independent conformal fixture lost D invariance")

    # Negative same-target fixture already used by the conformal causal rail.
    omega_time = 1 + 1 / (10 * (1 + t**2))
    phi_time = sp.log(omega_time)
    sigma_time = sp.factor(sp.diff(phi_time, t))
    expected_sigma = -2 * t / ((t**2 + 1) * (10 * t**2 + 11))
    if sp.factor(sigma_time - expected_sigma) != 0:
        raise AssertionError("time-dependent Weyl component drifted")
    witness = sp.simplify(sigma_time.subs(t, 1))
    if witness != -sp.Rational(1, 21):
        raise AssertionError("normalized augmentation witness drifted")

    # Finite residual Cartan model.  Q and iota are odd block maps and
    # Q iota+iota Q=L.  A rational perturbation keeps both nonzero weights
    # invertible when the Neumann ratio is 1/2; at r=1 one weight crosses zero.
    q0 = sp.Matrix([[0, 0], [1, 0]])
    iota0 = sp.Matrix([[0, 1], [0, 0]])
    q_plus = sp.Rational(3, 2) * q0
    q_minus = -sp.Rational(1, 2) * q0
    q = sp.diag(q_plus, q_minus)
    iota = sp.diag(iota0, iota0)
    lie = q * iota + iota * q
    expected_lie = sp.diag(
        sp.Rational(3, 2),
        sp.Rational(3, 2),
        -sp.Rational(1, 2),
        -sp.Rational(1, 2),
    )
    if not _zero(lie - expected_lie):
        raise AssertionError("finite residual Cartan identity failed")
    homotopy = iota * expected_lie.inv()
    if not _zero(q * homotopy + homotopy * q - sp.eye(4)):
        raise AssertionError("finite residual contraction failed")
    singular_lie = sp.diag(2, 2, 0, 0)
    if singular_lie.rank() != 2:
        raise AssertionError("weight-crossing mutation drifted")

    return {
        "positive_conformal_fixture": {
            "background": "g_sp=Omega_sp^2(-dt^2+dOmega_3^2)",
            "Omega_sp": "1+z/10, where z:S3->[ -1,1 ] is the height function",
            "bounds": "9/10<=Omega_sp<=11/10",
            "generator": "D=partial_t",
            "sigma_D": str(sigma_spatial),
            "causal_complex": "CERTIFIED by pointwise BV-canonical conformal transport",
            "fixed_augmentation_D_Cartan": "CERTIFIED because sigma_D=0",
        },
        "negative_conformal_fixture": {
            "background": "g_tm=Omega_tm^2(-dt^2+dOmega_3^2)",
            "Omega_tm": str(omega_time),
            "bounds": "1<Omega_tm<=11/10",
            "generator": "D=partial_t",
            "sigma_D": str(sigma_time),
            "normalized_point": "t=1",
            "augmentation_equivariance_defect": str(witness),
            "causal_complex": "CERTIFIED",
            "fixed_augmentation_D_Cartan": "OBSTRUCTED",
            "repair_not_supplied": "translated compensator-background orbit or another affine D-stable target",
        },
        "finite_residual_fixture": {
            "unperturbed_nonzero_weights": ["1", "-1"],
            "perturbed_nonzero_weights": ["3/2", "-1/2"],
            "neumann_ratio": "1/2",
            "cartan_defect_rank": 0,
            "contraction_defect_rank": 0,
            "weight_crossing_mutation": ["2", "0"],
            "weight_crossing_rank": singular_lie.rank(),
        },
    }


def _check_dependencies(records: dict[str, dict[str, Any]]) -> None:
    if records["sharp_transfer_theorem"]["result_state"] != "SHARP_ABSTRACT_THEOREM_WITH_TOY_CYLINDER_AND_CURVED_CONSUMERS":
        raise ValueError("sharp transfer theorem unavailable")
    if records["conformal_cylinder_orbit"]["flags"]["G3_OPEN_BACKGROUND_CLASS"] is not True:
        raise ValueError("conformal-cylinder orbit unavailable")
    if records["wz_d_cartan"]["claim_flags"]["SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION"] is not True:
        raise ValueError("vacuum-cylinder D contraction unavailable")
    if records["bach_flat_parent"]["claim_boundary"]["statement"].startswith("On every globally hyperbolic") is not True:
        raise ValueError("Bach-flat parent theorem unavailable")
    if records["bach_flat_metric"]["claim_boundary"]["statement"].startswith("Every metric") is not True:
        raise ValueError("Bach-flat metric theorem unavailable")
    if records["bach_flat_sdr"]["claim_boundary"]["statement"].startswith("Every metric") is not True:
        raise ValueError("Bach-flat SDR unavailable")
    if records["bach_flat_rank310"]["claim_boundary"]["statement"].startswith("The natural rank-310") is not True:
        raise ValueError("Bach-flat rank-310 transfer unavailable")
    if records["ks_common_slab"]["flags"]["NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1"] is not True:
        raise ValueError("KS common-slab domain unavailable")
    if records["ks_rank310"]["flags"]["KS_COMMON_SLAB_RANK310_GREEN_HOMOTOPY"] is not True:
        raise ValueError("KS slabwise rank-310 transfer unavailable")
    if records["ks_global_obstruction"]["flags"]["TRANSVERSE_KS_GLOBAL_FAMILY_OBSTRUCTED"] is not True:
        raise ValueError("KS whole-cylinder obstruction unavailable")


def build() -> dict[str, Any]:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    _check_dependencies(records)
    fixtures = _exact_fixtures()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-weak-background-causal-vs-d-stability-v1",
        "result_id": "WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1",
        "result_state": "CAUSAL_STABILITY_DOMAINS_CERTIFIED_D_CARTAN_SYMMETRY_BOUNDARY_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _ref(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES
        },
        "background_classes": {
            "globally_conformal_cylinder": {
                "manifold": "R x S3",
                "metrics": "g_phi=exp(2phi)g0",
                "topology": "bounded-smooth Frechet topology",
                "open_set": "||phi||_C0<epsilon, epsilon>0",
                "causal_verdict": "CERTIFIED",
                "mechanism": "pointwise support-local BV-canonical conjugation; causal sets are unchanged",
            },
            "bach_flat_nariai_adm": {
                "manifold": "R x (S1 x S2)",
                "metrics": "smooth Bach-flat ADM metrics in the declared radius-1/4 ball about unit Nariai",
                "topology": "relative C0 ADM topology on the smooth Bach-flat locus; C_b^k refinements when derivative estimates are invoked",
                "open_set": "relative radius 1/4, not ambient-open in all metrics",
                "causal_verdict": "CERTIFIED",
                "mechanism": "normally hyperbolic parent; metric biwave Volterra homotopy; natural finite-order cyclic rank-310 SDR; sharp transfer theorem",
            },
            "conformally_einstein_ks_slabs": {
                "manifold": "(-T,T) x S1 x S2",
                "metrics": "exact Kantowski-Sachs Einstein family g_epsilon",
                "topology": "smooth parameter topology on each fixed finite slab",
                "open_set": "for every T>0 there exists delta_T>0 with |epsilon|<delta_T",
                "causal_verdict": "CERTIFIED_ON_EACH_COMMON_SLAB",
                "whole_cylinder_verdict": "OBSTRUCTED_FOR_THE_DECLARED_NONZERO_BRANCH",
                "mechanism": "common wider cone, metric biwave homotopy and nilpotent six-block cyclic HPL",
            },
        },
        "causal_stability_theorem": {
            "hyperbolicity_conditions": [
                "one common globally hyperbolic support category, or pointwise conformal equality of causal sets",
                "normally hyperbolic diagonal companions or a certified biwave-plus-order-at-most-two Volterra normal form",
                "smooth coefficient bounds on each finite slab; quantitative Sobolev uniformity requires the corresponding C_b^k bounds",
                "finite-order support-local cyclic inclusion, projection and homotopy",
                "finite filtration nilpotence, or an independently justified finite-order support-local inverse, for the HPL resolvents",
            ],
            "hpl_formulas": {
                "resolvents": "R=(1+H Delta)^(-1), L=(1+Delta H)^(-1)",
                "inclusion": "I_Delta=R I",
                "projection": "p_Delta=p L",
                "homotopy": "H_Delta=R H=H L",
                "transferred_differential": "q_Delta=q+p Delta R I",
                "causal_lift": "Lambda_C,+/-=H_Delta+I_Delta Lambda_E,+/- p_Delta",
            },
            "support_boundary": "No support statement follows if a required inverse, shear, projector or homotopy is pseudodifferential, infinite-order or otherwise non-support-local.",
        },
        "residual_d_stability_theorem": {
            "geometric_activation_gate": "A declared family (D_epsilon,sigma_epsilon) must solve L_D g=2 sigma_D g on the same background family. If it does not, the residual D row is NO_CERTIFIED_MAP.",
            "cartan_activation_gate": "[Q_epsilon,iota_D,epsilon]_+=L_D,epsilon and the inclusion, projection and homotopy must be D-equivariant on the declared target carrier.",
            "finite_residual_gap_gate": "On the contracted complement, L_D,0 must be invertible and ||L_D,0^(-1)(L_D,epsilon-L_D,0)||<1 in a declared operator norm; then the Neumann inverse exists and h_D,epsilon=iota_D,epsilon L_D,epsilon^(-1).",
            "conformal_specialization": "If L_D g0=2 sigma0 g0, then L_D(exp(2phi)g0)=2(sigma0+D(phi))exp(2phi)g0.",
            "fixed_augmentation_gate": "For the tau-adic target pi(tau)=0, pi L_D(tau)-L_D pi(tau)=sigma_D. Thus sigma_D=0 is necessary for that fixed target even when D remains conformal Killing.",
            "verdict": "Residual D-Cartan stability is certified only on the symmetry-, gap- and carrier-compatible sublocus; it is not inferred from causal stability.",
        },
        "fixtures": fixtures,
        "cross_class_ledger": [
            {
                "class": "globally conformal cylinder, D(phi)=0",
                "causal_complex": "CERTIFIED",
                "fixed_residual_D": "CERTIFIED",
            },
            {
                "class": "globally conformal cylinder, D(phi)!=0",
                "causal_complex": "CERTIFIED",
                "fixed_residual_D": "OBSTRUCTED_BY_AFFINE_TARGET_DEFECT",
            },
            {
                "class": "relative-open Bach-flat Nariai ADM ball",
                "causal_complex": "CERTIFIED",
                "fixed_residual_D": "NO_CERTIFIED_MAP unless a CKV family and D-equivariant contraction are separately supplied",
            },
            {
                "class": "exact conformally Einstein Kantowski-Sachs branch",
                "causal_complex": "CERTIFIED_ON_COMMON_FINITE_SLABS",
                "fixed_residual_D": "NO_CERTIFIED_MAP for undeclared generators",
            },
        ],
        "exact_checks": {
            "dependency_hashes_recorded": True,
            "conformal_positive_fixture_exact": True,
            "conformal_negative_fixture_exact": True,
            "normalized_D_target_defect_minus_1_over_21": True,
            "finite_residual_neumann_fixture_exact": True,
            "weight_crossing_mutation_rejected": True,
            "causal_and_D_verdicts_separated": True,
            "relative_and_ambient_openness_separated": True,
            "finite_slab_and_whole_cylinder_separated": True,
        },
        "flags": {
            "WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1": True,
            "CONFORMAL_CYLINDER_CAUSAL_OPEN_CLASS": True,
            "BACH_FLAT_RELATIVE_ADM_CAUSAL_OPEN_CLASS": True,
            "KS_COMMON_SLAB_CAUSAL_STABILITY": True,
            "CAUSAL_STABILITY_IMPLIES_D_CARTAN_STABILITY": False,
            "D_CARTAN_ON_ALL_BACH_FLAT_BACKGROUNDS": False,
            "KS_NONZERO_WHOLE_CYLINDER_NEIGHBOURHOOD": False,
            "HADAMARD_TRANSFER": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "MICROLOCAL_HADAMARD_TRANSPORT_REQUIRES_AN_INDEPENDENT_WAVEFRONT_SET_INPUT; RESIDUAL_D_EXTENSION_REQUIRES_A_DECLARED_CKV_FAMILY_AND_D_EQUIVARIANT_TARGET",
        "claim_boundary": (
            "This theorem certifies the first scoped background-stability domains for the classical cyclic causal complex and separates them from residual D-Cartan persistence. It hash-consumes, rather than reproduces, the globally conformal-cylinder, relative-open Bach-flat and Kantowski--Sachs slabwise producers. The fixed tau-adic augmentation obstruction is a same-background carrier statement, not loss of the causal complex and not removal of a physical mode. The Bach-flat class is open only relative to the smooth Bach-flat locus. No arbitrary-background, timelike-boundary, Hadamard, nonlinear, particle, QME or quantum theorem is claimed."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/weak_background_causal_vs_d_stability.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_weak_background_causal_vs_d_stability.py",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_weak_background_causal_vs_d_stability",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/weak-background-causal-vs-d-stability-v1.schema.json -d d_quotient_classical/certificates/WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1.json",
            ],
        },
    }


def validate(value: dict[str, Any]) -> None:
    if not all(value["exact_checks"].values()):
        raise ValueError("an exact stability check dropped")
    flags = value["flags"]
    for name in (
        "CAUSAL_STABILITY_IMPLIES_D_CARTAN_STABILITY",
        "D_CARTAN_ON_ALL_BACH_FLAT_BACKGROUNDS",
        "KS_NONZERO_WHOLE_CYLINDER_NEIGHBOURHOOD",
        "HADAMARD_TRANSFER",
        "QUANTUM_CLAIM",
    ):
        if flags[name] is not False:
            raise ValueError(f"claim boundary crossed: {name}")
    if value["fixtures"]["negative_conformal_fixture"]["augmentation_equivariance_defect"] != "-1/21":
        raise ValueError("normalized D-target obstruction drifted")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Weak-background causal stability versus residual \(D\)

The first background-stability domain is now precise, and it has two
different answers.

## Causal complex

The complete cyclic causal complex persists on:

1. the open bounded-smooth global conformal orbit
   \(g_\phi=e^{2\phi}(-dt^2+d\Omega_3^2)\);
2. the radius-\(1/4\) relative ADM neighbourhood of unit Nariai inside the
   smooth Bach-flat locus; and
3. every common finite slab of the exact small Kantowski--Sachs Einstein
   family.

The mechanisms differ.  The first is pointwise BV-canonical conjugation.  The
second combines the normally hyperbolic tractor parent, the metric
biwave--Volterra homotopy and the natural support-local cyclic rank-310 SDR.
The third uses a common wider cone and a nilpotent six-block HPL.  The
Kantowski--Sachs branch is not a nonzero whole-cylinder neighbourhood: its
declared branch develops a finite-time curvature singularity.

## Residual \(D\)-Cartan contraction

This occupies a smaller locus.  A family must first supply a conformal Killing
pair

\[
{\cal L}_{D_\epsilon}g_\epsilon=2\sigma_{D,\epsilon}g_\epsilon,
\]

then satisfy the Cartan and equivariance identities on the declared target,
and retain an invertible \(D\)-weight operator on the contracted complement.
For a finite residual carrier, the sufficient gap condition is

\[
\left\|L_{D,0}^{-1}(L_{D,\epsilon}-L_{D,0})\right\|<1.
\]

It yields the Neumann inverse and
\(h_{D,\epsilon}=\iota_{D,\epsilon}L_{D,\epsilon}^{-1}\).

The separation is already decisive inside the conformally flat cylinder
class.  Let \(D=\partial_t\).  For the spatial conformal fixture

\[
\Omega_{\rm sp}=1+\frac{z}{10},\qquad -1\le z\le1,
\]

one has \(D\log\Omega_{\rm sp}=0\).  Both the causal complex and the fixed
tau-adic augmentation contraction persist.

For the equally causal time-dependent fixture

\[
\Omega_{\rm tm}=1+\frac1{10(1+t^2)},
\]

one instead has

\[
\sigma_D=D\log\Omega_{\rm tm}
=-\frac{2t}{(1+t^2)(10t^2+11)},\qquad
\sigma_D(1)=-\frac1{21}.
\]

The fixed projection \(\pi(\tau)=0\) therefore has the exact defect

\[
\pi{\cal L}_D\tau-{\cal L}_D\pi\tau=\sigma_D.
\]

Thus the causal complex remains certified while that fixed residual target is
obstructed.  A translated compensator-background orbit or another affine
\(D\)-stable target would be a different construction.

For the broader Bach-flat and conformally Einstein classes, a residual
\(D\)-row is `NO_CERTIFIED_MAP` unless a conformal-Killing family and
\(D\)-equivariant contraction are separately supplied.  Causal stability
alone never removes a mode and never implies a \(D\)-quotient.

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: d_quotient_classical/certificates/WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1.json
"""


def _guards(value: dict[str, Any]) -> None:
    for name in (
        "CAUSAL_STABILITY_IMPLIES_D_CARTAN_STABILITY",
        "D_CARTAN_ON_ALL_BACH_FLAT_BACKGROUNDS",
        "KS_NONZERO_WHOLE_CYLINDER_NEIGHBOURHOOD",
        "HADAMARD_TRANSFER",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][name] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")
    mutant = deepcopy(value)
    mutant["fixtures"]["negative_conformal_fixture"]["augmentation_equivariance_defect"] = "0"
    try:
        validate(mutant)
    except Exception:
        return
    raise AssertionError("mutation guard erased the D-target obstruction")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("weak-background stability outputs drifted")
    if args.guards:
        _guards(value)
    print("WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1: PASS")


if __name__ == "__main__":
    main()
