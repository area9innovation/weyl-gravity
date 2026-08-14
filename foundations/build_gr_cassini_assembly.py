#!/usr/bin/env python3
"""Build the model-scoped standard-GR to Cassini prediction assembly.

The exact rail starts at the vacuum Einstein equations in a static spherical
sector and ends at the PPN prediction gamma=1 and its null-delay coefficient.
The empirical rail is deliberately separate: it transcribes the publisher's
reported Cassini estimate and checks interval containment, but does not claim
to reproduce the spacecraft reduction or likelihood.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
EINSTEIN_SOURCE = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1.json"
CONTROL_SOURCE = FOUNDATIONS / "standard-gr-observational-control-v1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json"
REPORT = FOUNDATIONS / "reports/gr-cassini-model-assembly-v1.md"

OBLIGATIONS = [
    "KINEMATICS_OBSERVABLES",
    "STATE_EXISTENCE",
    "STATE_REPRESENTATION",
    "PROBABILITY_RULE",
    "PHYSICAL_STATE_SELECTION",
    "GENERATOR_SPECTRAL_DYNAMICS",
    "EVOLUTION_WELLPOSEDNESS",
    "CAUSAL_PROPAGATION_GREEN",
    "GAUGE_BV_COHOMOLOGY",
    "INTERACTION_CONSTRUCTION",
    "COUNTERTERM_CLASSIFICATION",
    "ANOMALY_CLASSIFICATION",
    "RENORMALIZED_PRODUCTS",
    "QME_RESTORATION",
    "RESIDUAL_QUANTUM_TRANSFER",
    "RECONSTRUCTION_LIMITS",
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def rational(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def display(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def multiply(left: list[Fraction], right: list[Fraction], degree: int) -> list[Fraction]:
    result = [Fraction() for _ in range(degree + 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= degree:
                result[i + j] += a * b
    return result


def divide(numerator: list[Fraction], denominator: list[Fraction], degree: int) -> list[Fraction]:
    if not denominator or denominator[0] == 0:
        raise ValueError("series denominator must have a nonzero constant term")
    result = [Fraction() for _ in range(degree + 1)]
    for n in range(degree + 1):
        target = numerator[n] if n < len(numerator) else Fraction()
        target -= sum(denominator[k] * result[n - k] for k in range(1, min(n, len(denominator) - 1) + 1))
        result[n] = target / denominator[0]
    return result


def exact_rail() -> dict[str, Any]:
    # x=m/rho.  In isotropic radius, Schwarzschild has
    # A=((1-x/2)/(1+x/2))^2 and B=(1+x/2)^4.
    a = divide(
        [Fraction(1), Fraction(-1), Fraction(1, 4)],
        [Fraction(1), Fraction(1), Fraction(1, 4)],
        2,
    )
    one_plus_half_x = [Fraction(1), Fraction(1, 2)]
    square = multiply(one_plus_half_x, one_plus_half_x, 2)
    b = multiply(square, square, 2)
    gtt = [-item for item in a]
    beta = -gtt[2] / 2
    gamma = b[1] / 2

    # sqrt(B/A)=(1+x/2)^3/(1-x/2) in the exterior branch.  Its
    # first-order coefficient is the generic PPN factor 1+gamma.
    propagation = divide(
        [Fraction(1), Fraction(3, 2), Fraction(3, 4), Fraction(1, 8)],
        [Fraction(1), Fraction(-1, 2)],
        2,
    )
    assert a == [Fraction(1), Fraction(-2), Fraction(2)]
    assert b == [Fraction(1), Fraction(2), Fraction(3, 2)]
    assert gtt == [Fraction(-1), Fraction(2), Fraction(-2)]
    assert beta == gamma == 1
    assert propagation[:2] == [Fraction(1), Fraction(2)]
    assert propagation[1] == 1 + gamma

    return {
        "arithmetic": "EXACT_RATIONAL_AND_FORMAL_SERIES",
        "conventions": {
            "dimension": 4,
            "signature": "(-,+,+,+)",
            "units": "c=1",
            "mass_length": "m=G M_sun",
            "weak_field_variable": "x=m/rho",
        },
        "field_equation_derivation": {
            "starting_equations": "G_mu_nu=0 in the vacuum exterior; Lambda=0",
            "ansatz": "ds^2=-f(r)dt^2+f(r)^(-1)dr^2+r^2 dOmega^2",
            "independent_equations": [
                "G^t_t=G^r_r=(r f'(r)+f(r)-1)/r^2=0",
                "G^theta_theta=G^phi_phi=f'(r)/r+f''(r)/2=0",
            ],
            "integration": "(r f)'=1, hence f=1+C/r; Newtonian normalization fixes C=-2m",
            "solution": "f(r)=1-2m/r",
            "substitution_residuals": {
                "r_fprime_plus_f_minus_1": rational(Fraction()),
                "fprime_over_r_plus_half_fsecond": rational(Fraction()),
            },
            "scope": "Exact within the static, spherically symmetric, asymptotically flat vacuum ansatz.",
        },
        "isotropic_translation": {
            "coordinate_map": "r=rho(1+m/(2rho))^2=rho(1+x/2)^2",
            "lapse_factor": "A(x)=((1-x/2)/(1+x/2))^2",
            "spatial_factor": "B(x)=(1+x/2)^4",
            "coordinate_identity": "(dr/drho)^2/A=B and r^2=rho^2 B",
            "A_coefficients_through_x2": [rational(item) for item in a],
            "B_coefficients_through_x2": [rational(item) for item in b],
            "gtt_coefficients_through_x2": [rational(item) for item in gtt],
        },
        "ppn_identification": {
            "template": "g_tt=-1+2U-2 beta U^2+O(U^3); g_ij=(1+2 gamma U+O(U^2))delta_ij",
            "potential_identification": "U=x=m/rho",
            "beta": rational(beta),
            "gamma": rational(gamma),
            "gamma_minus_one": rational(gamma - 1),
        },
        "null_delay": {
            "null_condition": "dt/dl=sqrt(B/A)=1+(1+gamma)U+O(U^2)",
            "sqrt_B_over_A_coefficients_through_x2": [rational(item) for item in propagation],
            "first_order_delay_coefficient": rational(propagation[1]),
            "one_way_excess": "Delta t=(1+gamma)m[asinh(z_receiver/b)+asinh(z_emitter/b)]+O(m^2)",
            "observable_parameter": "gamma+1",
        },
    }


def applicability_mask() -> list[dict[str, str]]:
    required = {
        "KINEMATICS_OBSERVABLES": "The metric, null paths, PPN gamma, and radio time/frequency response are the declared configurations and observables.",
        "INTERACTION_CONSTRUCTION": "The nonlinear Einstein vacuum field equation and its exact Schwarzschild exterior solution define the gravitational model used by the prediction.",
        "RECONSTRUCTION_LIMITS": "The isotropic weak-field map identifies the formal metric coefficient with the operational PPN gamma fitted by Cassini.",
    }
    touched = {
        "CAUSAL_PROPAGATION_GREEN": "A null-geodesic propagation law is used, but no retarded/advanced Green operator or Cauchy-support theorem is required or established.",
        "GAUGE_BV_COHOMOLOGY": "Areal and isotropic coordinate gauges are related exactly, but no BV complex or gauge cohomology is required or established.",
    }
    result = []
    for obligation in OBLIGATIONS:
        if obligation in required:
            status, reason = "IN_SCOPE_REQUIRED", required[obligation]
        elif obligation in touched:
            status, reason = "TOUCHED_NOT_REQUIRED", touched[obligation]
        else:
            status = "OUT_OF_SCOPE"
            reason = "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        result.append({"obligation": obligation, "status": status, "reason": reason})
    return result


def build() -> dict[str, Any]:
    einstein = load(EINSTEIN_SOURCE)
    control = load(CONTROL_SOURCE)
    if einstein.get("certificate") != "REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1" or einstein.get("checks", {}).get("ok") is not True:
        raise ValueError("Einstein field-equation source identity or checks")
    cassini = next((item for item in control.get("records", []) if item.get("id") == "GR_CASSINI_SHAPIRO_2003"), None)
    if cassini is None or cassini.get("benchmark") != "SOLAR_SYSTEM":
        raise ValueError("Cassini control source identity")

    exact = exact_rail()
    central = Fraction(21, 1_000_000)
    uncertainty = Fraction(23, 1_000_000)
    predicted = Fraction()
    lower = central - uncertainty
    upper = central + uncertainty
    standardized_distance = abs(central - predicted) / uncertainty
    assert lower <= predicted <= upper

    mask = applicability_mask()
    required_count = sum(item["status"] == "IN_SCOPE_REQUIRED" for item in mask)
    stages = [
        {"id": "FIELD_EQUATIONS", "label": "Vacuum Einstein equations", "status": "CERTIFIED_EXACT", "establishes": "The declared model uses G_mu_nu=0 in the exterior sector."},
        {"id": "EXTERIOR_SOLUTION", "label": "Static spherical exterior", "status": "CERTIFIED_EXACT", "establishes": "The field equations integrate to f(r)=1-2m/r under the declared boundary normalization."},
        {"id": "PPN_REDUCTION", "label": "Isotropic weak-field reduction", "status": "CERTIFIED_EXACT", "establishes": "Exact coordinate translation and formal series give beta=gamma=1."},
        {"id": "NULL_OBSERVABLE", "label": "Null-delay observable", "status": "CERTIFIED_EXACT", "establishes": "The first-order delay coefficient is 1+gamma=2."},
        {"id": "CASSINI_PARAMETER_MAP", "label": "Cassini fitted parameter", "status": "LITERATURE_SCOPED", "establishes": "The publisher abstract identifies bending/delay and the measured frequency shift with gamma+1."},
        {"id": "EMPIRICAL_COMPARISON", "label": "Published Cassini comparison", "status": "SUPPORTED_REPORTED_BAND", "establishes": "The exact prediction gamma-1=0 lies inside the displayed reported plus-minus band."},
    ]
    interfaces = [
        {"id": "FIELD_EQUATION_TO_SOLUTION", "from": "FIELD_EQUATIONS", "to": "EXTERIOR_SOLUTION", "relation": "EXACT_DERIVATION", "status": "CERTIFIED", "basis": "The reduced Einstein equation is an exact first-order ODE and the angular residual vanishes after substitution."},
        {"id": "SOLUTION_TO_PPN", "from": "EXTERIOR_SOLUTION", "to": "PPN_REDUCTION", "relation": "EXACT_TRANSLATION", "status": "CERTIFIED", "basis": "The areal-to-isotropic coordinate map is exact and the series coefficients are rational."},
        {"id": "PPN_TO_NULL_DELAY", "from": "PPN_REDUCTION", "to": "NULL_OBSERVABLE", "relation": "EXACT_ASYMPTOTIC_DERIVATION", "status": "CERTIFIED", "basis": "The Lorentzian null condition fixes the first-order coefficient 1+gamma."},
        {"id": "NULL_DELAY_TO_CASSINI_PARAMETER", "from": "NULL_OBSERVABLE", "to": "CASSINI_PARAMETER_MAP", "relation": "CONDITIONAL_OPERATIONAL_BRIDGE", "status": "REGISTERED", "basis": "Assumes minimally coupled radio photons follow metric null geodesics and imports the experiment's identification of its fitted gamma parameter."},
        {"id": "PREDICTION_TO_REPORTED_ESTIMATE", "from": "CASSINI_PARAMETER_MAP", "to": "EMPIRICAL_COMPARISON", "relation": "LITERATURE_SCOPED_COMPARISON", "status": "REGISTERED", "basis": "Compares the exact theoretical value only with the publisher's displayed estimate; no raw-data or likelihood reconstruction is claimed."},
    ]
    value = {
        "schema_version": "foundational-gr-cassini-model-assembly-v1",
        "result_id": "FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1",
        "result_kind": "MODEL_SCOPED_END_TO_END_PREDICTION_ASSEMBLY",
        "lifecycle": "MODEL_SCOPED_EMPIRICAL_COMPARISON_REGISTERED",
        "created": "2026-08-14",
        "repository_base_commit": "be5b23b72ea73f6b5dd099e9a3bd3126e6778922",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "title": "Standard GR solar-system prediction assembly: field equations to Cassini",
        "model_identity": {
            "id": "STANDARD_GR_VACUUM_SOLAR_EXTERIOR",
            "theory": "Four-dimensional standard general relativity",
            "sector": "Static, spherically symmetric, asymptotically flat vacuum exterior of the Sun",
            "field_equations": "G_mu_nu=0 with Lambda=0 outside the source",
            "matter_coupling": "Radio photons are minimally coupled and follow null geodesics of the same metric",
            "approximation": "Exact exterior solution followed by a first post-Newtonian expansion for the observable map",
            "benchmark": "SOLAR_SYSTEM",
            "comparison_id": "GR_CASSINI_SHAPIRO_2003",
        },
        "applicability_mask": mask,
        "applicability_summary": {
            "total_atlas_obligations": len(mask),
            "required": required_count,
            "required_satisfied": required_count,
            "touched_not_required": sum(item["status"] == "TOUCHED_NOT_REQUIRED" for item in mask),
            "out_of_scope": sum(item["status"] == "OUT_OF_SCOPE" for item in mask),
        },
        "shared_object_ledger": [
            {"id": "MODEL", "object": "STANDARD_GR_VACUUM_SOLAR_EXTERIOR", "used_by": ["FIELD_EQUATIONS", "EXTERIOR_SOLUTION", "PPN_REDUCTION", "NULL_OBSERVABLE"], "identity_status": "IDENTICAL_MODEL"},
            {"id": "MASS_M", "object": "m=G M_sun in c=1 units", "used_by": ["EXTERIOR_SOLUTION", "PPN_REDUCTION", "NULL_OBSERVABLE"], "identity_status": "IDENTICAL_PARAMETER"},
            {"id": "PPN_GAMMA", "object": "the spatial-curvature parameter gamma", "used_by": ["PPN_REDUCTION", "NULL_OBSERVABLE", "CASSINI_PARAMETER_MAP", "EMPIRICAL_COMPARISON"], "identity_status": "EXACT_TO_OPERATIONAL_TRANSLATION"},
            {"id": "RADIO_NULL_SIGNAL", "object": "Cassini radio photons near solar conjunction", "used_by": ["NULL_OBSERVABLE", "CASSINI_PARAMETER_MAP"], "identity_status": "CONDITIONAL_OPERATIONAL_IDENTIFICATION"},
        ],
        "stages": stages,
        "interfaces": interfaces,
        "exact_prediction_rail": exact,
        "empirical_comparison_rail": {
            "type": "IMPORTED_REPORTED_ESTIMATE_WITH_EXACT_ARITHMETIC_COMPARISON",
            "source_record_id": cassini["id"],
            "citation": cassini["citation"],
            "stable_url": cassini["stable_url"],
            "publisher_reported_expression": "gamma=1+(2.1+/-2.3)e-5",
            "reported_gamma_minus_one": rational(central),
            "reported_plus_minus_uncertainty": rational(uncertainty),
            "reported_band": {"lower": rational(lower), "upper": rational(upper)},
            "exact_prediction_gamma_minus_one": rational(predicted),
            "prediction_inside_reported_band": True,
            "absolute_standardized_distance": rational(standardized_distance),
            "comparison_status": "SUPPORTED_WITHIN_REPORTED_PLUS_MINUS_BAND",
            "data_lifecycle": "LITERATURE_TRANSCRIPTION_NOT_RAW_DATA_REANALYSIS",
            "boundary": "The arithmetic comparison is exact after transcription. The spacecraft data reduction, plasma correction, covariance model, and likelihood are imported from the paper and are not reproduced.",
        },
        "maturity_rails": [
            {"id": "MODEL_IDENTITY", "status": "SATISFIED", "basis": "Every exact stage uses the same declared standard-GR solar-exterior model and mass parameter."},
            {"id": "APPLICABILITY", "status": "SATISFIED", "basis": f"All {required_count} obligations required by this bounded prediction are satisfied; other obligations are explicitly masked."},
            {"id": "CROSS_STAGE_COMPOSITION", "status": "SATISFIED_WITH_TYPED_BOUNDARY", "basis": "All 5 joins are registered: 3 exact and 2 literature-scoped operational/comparison joins."},
            {"id": "PREDICTION_DERIVATION", "status": "SATISFIED", "basis": "The exact field-equation, coordinate, PPN, and null-condition chain gives gamma=1 and gamma+1=2."},
            {"id": "OBSERVABLE_IDENTIFICATION", "status": "SATISFIED_WITH_TYPED_BOUNDARY", "basis": "The fitted Cassini gamma is connected to the null-delay coefficient under the declared photon-coupling and experimental-model assumptions."},
            {"id": "EMPIRICAL_COMPARISON", "status": "SUPPORTED_IN_DECLARED_SCOPE", "basis": "gamma-1=0 lies in the publisher's displayed (2.1+/-2.3)e-5 band."},
            {"id": "ROBUSTNESS_OUT_OF_SAMPLE", "status": "NOT_ASSESSED", "basis": "No second solar-system dataset or held-out comparison is included in this assembly."},
        ],
        "assembly_disposition": {
            "status": "BOUNDED_PREDICTION_ASSEMBLY_COMPLETE",
            "complete_within_declared_scope": True,
            "empirically_supported_within_declared_scope": True,
            "complete_theory": False,
        },
        "provenance": {
            "inputs": [
                {"path": str(EINSTEIN_SOURCE.relative_to(ROOT)), "sha256": sha(EINSTEIN_SOURCE), "role": "local exact D=4 Einstein field-equation classification and Schwarzschild vacuum control"},
                {"path": str(CONTROL_SOURCE.relative_to(ROOT)), "sha256": sha(CONTROL_SOURCE), "role": "typed Cassini primary-source comparison record"},
            ],
            "remote_source": {
                "locator": "https://doi.org/10.1038/nature01997",
                "artifact_status": "PUBLISHER_METADATA_LIVE_SOURCE",
                "retrieved": "2026-08-14",
                "reported_fact": "gamma=1+(2.1+/-2.3)e-5 and bending/delay proportional to gamma+1",
                "pinning_boundary": "The evolving publisher HTML is not treated as a stable byte artifact; the local typed control ledger is the content-addressed transcription authority.",
            },
        },
        "independent_checker": {
            "path": "foundations/check_gr_cassini_assembly.py",
            "method": "Direct rational coefficient identities, ODE residual checks, source-pin closure, applicability closure, and comparison-band arithmetic; it does not reuse the producer's series routines.",
        },
        "claim_flags": {
            "single_model_identity_declared": True,
            "applicability_mask_complete": True,
            "vacuum_field_equation_to_solution_derived": True,
            "isotropic_coordinate_translation_exact": True,
            "ppn_gamma_equals_one_derived_exactly": True,
            "null_delay_gamma_plus_one_coefficient_derived": True,
            "cassini_observable_map_registered": True,
            "prediction_inside_reported_band": True,
            "bounded_prediction_assembly_complete": True,
            "raw_cassini_data_reanalysed": False,
            "cassini_likelihood_reproduced": False,
            "robustness_out_of_sample_assessed": False,
            "all_solar_system_tests_covered": False,
            "complete_standard_gr_theory_established": False,
            "weyl_gravity_empirically_supported": False,
            "quantum_lifecycle_promoted": False,
        },
        "does_not_establish": [
            "the Einstein equations outside the declared four-dimensional local metric and vacuum exterior assumptions",
            "solar interior structure, multipoles, rotation, plasma physics, spacecraft dynamics, or the Cassini data-reduction pipeline",
            "a retarded or advanced Green operator, full Cauchy well-posedness theorem, or BV gauge construction",
            "reproduction of the Cassini likelihood, covariance analysis, or systematic-error budget",
            "robustness against a second or held-out solar-system dataset",
            "agreement of standard GR in the other five benchmark families",
            "a complete classical, quantum, cosmological, or ultraviolet theory",
            "any empirical support for Mannheim--Kazanas or another Weyl-gravity model",
        ],
        "human_report": "foundations/reports/gr-cassini-model-assembly-v1.md",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    exact = value["exact_prediction_rail"]
    empirical = value["empirical_comparison_rail"]
    lines = [
        "# Standard GR solar-system prediction assembly: field equations to Cassini",
        "",
        f"**Result:** `{value['result_id']}`",
        "",
        f"**Lifecycle:** `{value['lifecycle']}`",
        "",
        "**Dependency tags:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`",
        "",
        "## Outcome",
        "",
        "This is the first model-scoped end-to-end prediction assembly in the",
        "foundations atlas. It uses one declared model throughout: four-dimensional",
        "standard GR in the static, asymptotically flat vacuum exterior of the Sun,",
        "with minimally coupled radio photons. Within that bounded scope the assembly",
        "is complete and empirically supported. It is not a complete theory.",
        "",
        "## Exact prediction rail",
        "",
        "1. `G_mu_nu=0` reduces in the static spherical ansatz to",
        "   `(r f' + f - 1)/r^2=0`, so `(r f)'=1` and",
        "   `f(r)=1-2m/r` after Newtonian normalization.",
        "2. The exact isotropic map `r=rho(1+m/(2rho))^2` gives",
        "   `g_tt=-1+2U-2U^2+...` and `g_ij=(1+2U+...)delta_ij`.",
        "3. Comparison with the PPN template gives exact `beta=gamma=1`.",
        "4. The null condition gives `dt/dl=1+(1+gamma)U+...`, hence the",
        "   standard-GR delay coefficient `gamma+1=2`.",
        "",
        "All coefficients are generated with exact rational formal-series arithmetic.",
        "",
        "## Typed empirical rail",
        "",
        f"The publisher reports `{empirical['publisher_reported_expression']}`. The",
        "exact prediction `gamma-1=0` lies in the displayed reported plus-minus band",
        f"and has absolute standardized distance `{display(Fraction(**empirical['absolute_standardized_distance']))}`.",
        "This is a literature-scoped comparison: the Cassini reduction and likelihood",
        "are not reproduced.",
        "",
        "## Applicability mask",
        "",
        "| Atlas obligation | Applicability | Reason |",
        "|---|---|---|",
    ]
    lines.extend(f"| `{item['obligation']}` | `{item['status']}` | {item['reason']} |" for item in value["applicability_mask"])
    lines.extend([
        "",
        "## Composed stages",
        "",
        "| Stage | Status | Establishes |",
        "|---|---|---|",
    ])
    lines.extend(f"| {item['label']} | `{item['status']}` | {item['establishes']} |" for item in value["stages"])
    lines.extend([
        "",
        "## Boundaries",
        "",
        *[f"- This does not establish {item}." for item in value["does_not_establish"]],
        "",
        "## Verification",
        "",
        "```bash",
        "python3 foundations/build_gr_cassini_assembly.py --check",
        "python3 foundations/check_gr_cassini_assembly.py",
        "python3 foundations/verify_gr_cassini_assembly.py",
        "python3 -m unittest foundations.tests.test_gr_cassini_assembly",
        "```",
        "",
        f"Canonical digest: `{value['canonical_digest']}`",
        "",
    ])
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    if args.check:
        stale = []
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != result:
            stale.append(str(OUTPUT.relative_to(ROOT)))
        if not REPORT.is_file() or REPORT.read_bytes() != report:
            stale.append(str(REPORT.relative_to(ROOT)))
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1: generated artifacts current")
        return 0
    OUTPUT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
