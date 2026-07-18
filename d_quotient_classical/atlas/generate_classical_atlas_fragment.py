#!/usr/bin/env python3
"""Generate the fail-closed classical causal/gauge/carrier atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "classical-causal-atlas-fragment.json"
VACUUM_EVIDENCE = HERE / "CLASSICAL_VACUUM_CYLINDER_ATLAS_EVIDENCE_V1.json"
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]

LEGACY_VACUUM = {
    "four_flags": ROOT / "covariant_completion/certificates/four_flag_closure_status.json",
    "gram_transport": ROOT / "covariant_completion/certificates/covariant_gram_transport.json",
    "one_particle": ROOT / "analytic_completion/certificates/one_particle_krein.json",
    "positive_frequency": ROOT / "covariant_completion/certificates/positive_frequency_transform.json",
}
CERTS = {
    "vacuum": VACUUM_EVIDENCE,
    "Berger_green": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "Berger_Cartan": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
    "Berger_charge": ROOT / "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
    "Berger_redshift": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "Berger_projector": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
    "Nariai_conformal": ROOT / "d_quotient_classical/certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json",
    "Nariai_single": ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json",
    "Nariai_transverse": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json",
    "Nariai_incidence": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json",
    "Nariai_PBW_gate": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1.json",
    "Nariai_jet_aware_parent": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json",
    "Nariai_first_order_schur": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1.json",
    "Nariai_Phi_only_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json",
    "Nariai_incidence_L1_rigidity": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1.json",
    "Nariai_normalized_L0_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1.json",
    "Nariai_K_admissibility": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1.json",
    "Nariai_Phi2_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1.json",
    "Nariai_PBW_associativity": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1.json",
    "Nariai_coefficient_jets": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1.json",
    "Nariai_splitting_jets": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json",
    "Bach_parent": ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json",
    "cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _legacy_id(path: Path) -> str:
    payload = json.loads(path.read_text())
    return str(payload.get("result_id", payload.get("schema", "UNIDENTIFIED")))


def vacuum_evidence() -> dict[str, Any]:
    records = {name: json.loads(path.read_text()) for name, path in LEGACY_VACUUM.items()}
    if not records["four_flags"]["flags"]["final_covariant_H4"]:
        raise AssertionError("vacuum covariant closure changed")
    if not records["gram_transport"]["status"]:
        raise AssertionError("vacuum Gram transport changed")
    if records["one_particle"]["classification"] != "infinite-index Krein space":
        raise AssertionError("vacuum one-particle carrier changed")
    if not (
        records["positive_frequency"]["harmonic_transform_isometry_on_algebraic_core"]
        and records["positive_frequency"]["normalized_metric_modes_map_to_unit_coefficients"]
        and records["positive_frequency"]["krein_signs"] == {"E": 1, "A": -1, "L": -1}
    ):
        raise AssertionError("vacuum positive-frequency transform changed")
    return {
        "schema": "classical-vacuum-cylinder-atlas-evidence-v1",
        "result_id": "CLASSICAL_VACUUM_CYLINDER_ATLAS_EVIDENCE_V1",
        "result_state": "VACUUM_CYLINDER_CAUSAL_SYMPLECTIC_AND_RESIDUAL_CARRIER_EVIDENCE_WRAPPED",
        "dependencies": {
            name: {"path": str(path.relative_to(ROOT)), "artifact_id": _legacy_id(path), "sha256": _sha(path)}
            for name, path in LEGACY_VACUUM.items()
        },
        "flags": {
            "causal_quasi_isomorphism": True,
            "EAL_Krein_carrier": True,
            "pairing_transport": True,
            "residual_H4_two_deformation_classes": True,
            "one_particle_residual_cohomology_zero": True,
            "Hadamard_or_interacting_quantum_theorem": False,
        },
        "claim_boundary": "This is a content-addressed adapter for legacy certificates that use schema identifiers instead of result_id. It adds no theorem and does not turn E/A/L modes or W-square deformation classes into quantum particles.",
    }


def _evidence(*names: str) -> list[dict[str, str]]:
    rows = []
    for name in names:
        path = CERTS[name]
        payload = json.loads(path.read_text())
        rows.append({"path": str(path.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha(path)})
    return rows


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second(bounded: tuple[str, str], secular: tuple[str, str], causal: tuple[str, str]) -> dict[str, Any]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(*bounded),
        "smooth_secular": _claim(*secular),
        "causal_retarded": _claim(*causal),
    }


def _entry(identifier: str, scope: dict[str, Any], descriptions: dict[str, str], dispersion: tuple[str, str], lee_wald: tuple[str, str], taub: tuple[str, str], resonance: tuple[str, str], second: dict[str, Any], evidence: list[dict[str, str]], boundary: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "scope": scope,
        "descriptions": descriptions,
        "mode_data": {
            "dispersion": _claim(*dispersion),
            "lee_wald": _claim(*lee_wald),
            "taub_maps": _claim(*taub),
            "resonance": _claim(*resonance),
            "second_order": second,
        },
        "evidence": evidence,
        "claim_boundary": boundary,
    }


VACUUM = {
    "theory": "free pure-Weyl gravity",
    "background": "unit conformal cylinder R_t x S3",
    "boundaries": "closed compact Cauchy surface S3; no spatial boundary",
    "charge_sector": "selected closed-universe absolute residual SO(4,2) quotient including D",
}
BERGER = {
    "theory": "pure-Weyl gravity plus two standard-sign rotating conformal scalars and retained Maxwell sector",
    "background": "fixed rational positive Berger clock",
    "boundaries": "R_t x compact Berger S3; no spatial boundary",
    "charge_sector": "fixed-coupling Taub/moment-map-zero clock sector; K_Berger=D-omega R is the stationary unary generator",
}
NARIAI = {
    "theory": "free pure-Weyl metric BV complex and normal-adjoint-tractor parent",
    "background": "unit Nariai dS2 x S2 and declared bounded smooth conformal orbit",
    "boundaries": "global compact Cauchy surface S1 x S2; no timelike boundary",
    "charge_sector": "unquotiented linear gauge complex; no residual state quotient imported",
}


def _scope(base: dict[str, Any], **updates: Any) -> dict[str, Any]:
    value = dict(base)
    value.update(updates)
    return value


def entries() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    family_data = {
        "E": ("+1", "Einstein/lower-TT family, both chiralities"),
        "A": ("-1", "vector-descendant family, both chiralities"),
        "L": ("-1", "upper-TT/logarithmic family, both chiralities"),
    }
    for family, (sign, carrier) in family_data.items():
        values.append(_entry(
            f"classical.vacuum_cylinder.one_particle.{family.lower()}",
            _scope(VACUUM, carrier=carrier, degree=1, parity="both chiralities", ell="all allowed SO(4) levels", m="all", k="not a separate cylinder label", omega="positive and negative cylinder-energy shells"),
            {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
            ("CERTIFIED", f"The {family} all-level cylinder mode family is part of the exact E/A/L causal Cauchy carrier."),
            ("CERTIFIED", f"The normalized one-particle Krein sign is {sign} on {family}."),
            ("CERTIFIED", "The selected absolute residual CE complex has zero one-particle cohomology; this does not erase the causal solution family."),
            ("NOT_APPLICABLE", "No second-order resonance claim is needed for this linear carrier entry."),
            _second(("OPEN", "No all-mode bounded second-order classification."), ("OPEN", "No all-mode smooth-secular second-order classification."), ("OPEN", "No nonlinear retarded second-order classification.")),
            _evidence("vacuum", "cone"),
            "This is a classical causal one-particle mode family with an indefinite Krein sign, not a positive residual particle and not either W-square degree-four class.",
        ))
    for chirality in ("plus", "minus"):
        symbol = "+" if chirality == "plus" else "-"
        values.append(_entry(
            f"classical.vacuum_cylinder.deformation.w_{chirality}_squared",
            _scope(VACUUM, carrier=f"ghost-dressed degree-four deformation/vertex class [W_{symbol}^2], not a one-particle mode", degree=4, parity=f"chirality {symbol}", ell="NOT_APPLICABLE", m="NOT_APPLICABLE", k="NOT_APPLICABLE", omega="centered total residual weight zero"),
            {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
            ("NOT_APPLICABLE", "A composite deformation class has no one-particle dispersion relation."),
            ("CERTIFIED", "The complementary-degree residual pairing is positive definite and normalized to I2 on the two chiral classes."),
            ("CERTIFIED", "The covariant and residual H4 transports identify exactly these two classes."),
            ("NOT_APPLICABLE", "No propagation resonance is assigned to a deformation class."),
            _second(("NOT_APPLICABLE", "Not a first-order tangent mode."), ("NOT_APPLICABLE", "Not a first-order tangent mode."), ("NOT_APPLICABLE", "Not a first-order tangent mode.")),
            _evidence("vacuum"),
            "This is a vertex/deformation class. It must never be relabelled as a positive-norm graviton or one-particle state.",
        ))
    values.append(_entry(
        "classical.berger.retained_gravity_clock_maxwell",
        _scope(BERGER, carrier="complete 54-row gauge-fixed gravity-clock complex with typed retained 36-row gravity-clock-Maxwell carrier", degree="all BV degrees; physical local fields at degree 0", parity="all local tensor and Maxwell parities", ell="arbitrary four-dimensional jets; no harmonic truncation", m="all", k="all local covectors", omega="K_Berger weight; raw D action is affine"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "CERTIFIED", "quantum": "OPEN"},
        ("OPEN", "No complete Berger harmonic dispersion catalogue is asserted."),
        ("CERTIFIED", "The full and retained odd cyclic pairings and advanced/retarded adjoint reversal are exact."),
        ("CERTIFIED", "The clock momentum is nonzero but its variation vanishes on the declared fixed-coupling tangent; K_Berger, not raw affine D, is the stationary unary generator."),
        ("OPEN", "No complete Berger second-order resonance catalogue exists."),
        _second(("OPEN", "No finite-harmonic bounded Berger tangent cone."), ("OPEN", "No smooth-secular Berger tangent cone."), ("OPEN", "The unary retarded complex is certified, but the nonlinear causal second-order tangent cone is open.")),
        _evidence("Berger_green", "Berger_Cartan", "Berger_charge", "Berger_redshift", "cone"),
        "Causality is unary and the cyclic Cartan theorem stops at arity three. Raw affine D, arity four, Hadamard/QME, and a branch-resolved physical projector remain false.",
    ))
    values.append(_entry(
        "classical.berger.crosswalk.retained36_to_einstein_extra",
        _scope(BERGER, carrier="support-local Einstein-like/extra-Weyl dynamical branch projector on the retained 36-row carrier", degree="crosswalk", parity="all", ell="all", m="all", k="all", omega="all"),
        {axis: "NO_CERTIFIED_MAP" for axis in AXES},
        ("NO_CERTIFIED_MAP", "No support-local branch-resolved dispersion map exists on this carrier."),
        ("NO_CERTIFIED_MAP", "No branch-resolved pairing pullback exists."),
        ("NO_CERTIFIED_MAP", "No branch-resolved Taub map exists."),
        ("OBSTRUCTED", "The canonical support-local same-bundle projector is obstructed by the certified subprincipal witness."),
        _second(("NO_CERTIFIED_MAP", "No branch projector."), ("NO_CERTIFIED_MAP", "No branch projector."), ("NO_CERTIFIED_MAP", "No branch projector.")),
        _evidence("Berger_projector"),
        "Bridge 1 is not activated on Berger: the unsplit cyclic causal carrier remains valid, but no admissible branch crosswalk has been selected. The certified obstruction leaves four scoped possibilities—a relative cofiber, a larger noncontractible mixed-bundle carrier, a declared nonlocal REDUCED-MODE map, or a port to a background with a certified split.",
    ))
    values.append(_entry(
        "classical.nariai.conformal_orbit.rank310_metric",
        _scope(NARIAI, background="bounded smooth global conformal orbit g_phi=exp(2phi)g_N with sup|exp(phi)-1|<1/9", carrier="metric four-row Bach complex and repaired rank-310 parent-detour graph", degree="all BV degrees", parity="all", ell="all smooth modes", m="all", k="all", omega="all"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The exact metric biwave endpoint and rank-310 graph carry advanced/retarded propagation on the declared class."),
        ("CERTIFIED", "The support-local SDR is cyclic and the causal homotopies satisfy adjoint reversal."),
        ("OPEN", "No nonlinear Taub/tangent-cone classification on the conformal orbit."),
        ("OPEN", "No nonlinear resonance classification."),
        _second(("OPEN", "No bounded nonlinear cone."), ("OPEN", "No smooth-secular nonlinear cone."), ("OPEN", "Unary causal homotopy is certified; nonlinear causal correction is open.")),
        _evidence("Nariai_conformal", "Nariai_single", "cone"),
        "This is the metric theorem on the conformal Nariai orbit only; transverse Bach-flat directions and Hadamard/nonlinear/quantum claims remain open.",
    ))
    values.append(_entry(
        "classical.bach_flat.open_parent_detour",
        _scope(NARIAI, background="every globally hyperbolic Bach-flat four-manifold; explicit relative ADM radius-1/4 ball around Nariai", carrier="normal-adjoint-tractor Yang-Mills detour parent", degree="parent complex degrees", parity="all", ell="NOT_APPLICABLE without additional symmetry", m="NOT_APPLICABLE", k="all local covectors", omega="all"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The parent detour is degreewise Green hyperbolic on every declared globally hyperbolic Bach-flat background."),
        ("CERTIFIED", "The parent is cyclic under its tractor fibre pairing and advanced/retarded adjoint reversal."),
        ("OPEN", "No class-wide nonlinear tangent cone."),
        ("NOT_APPLICABLE", "No finite harmonic resonance decomposition is assumed on the open parent class."),
        _second(("OPEN", "No bounded harmonic class is declared."), ("OPEN", "No smooth-secular class-wide theorem."), ("OPEN", "Unary parent Green homotopy does not by itself solve nonlinear sourced second order.")),
        _evidence("Bach_parent", "cone"),
        "This certifies the parent, not a support-local metric/parent SDR or metric Bach Green homotopy throughout the whole relative-open class.",
    ))
    values.append(_entry(
        "classical.nariai.transverse_kantowski_sachs_tangent",
        _scope(NARIAI, background="unit Nariai with transverse Kantowski-Sachs linearized Einstein tangent", carrier="metric tangent plus first rank-310 curvature-incidence and formal-adjoint rows", degree=1, parity="homogeneous scalar anisotropy", ell=0, m=0, k=0, omega="nonstationary sinh(t), sinh(2t) profile"),
        {"causal": "OPEN", "symplectic": "OPEN", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The displayed tangent solves the complete linearized fixed-Lambda Einstein equations and is linearized Bach-flat."),
        ("OPEN", "No physical Lee-Wald norm or reduced pairing is assigned to this tangent."),
        ("OPEN", "No second-order Taub classification or exact nonlinear family is certified."),
        ("OPEN", "The frozen-parallel shortcut is obstructed. The associative coefficient-jet PBW backend and all four L0 plus fourteen L1 corrected-splitting jets are now exact, and the strict first square closes through every required ordered jet. The parent middle, shifted-chain and compressed-Schur replay remains open; the earlier Phi/L0/K rank screens remain backend regression data, not operator no-go theorems."),
        _second(("OPEN", "No bounded correction theorem."), ("OPEN", "No smooth-secular correction theorem."), ("OPEN", "No transverse retarded SDR theorem.")),
        _evidence("Nariai_transverse", "Nariai_incidence", "Nariai_PBW_gate", "Nariai_jet_aware_parent", "Nariai_first_order_schur", "Nariai_Phi_only_obstruction", "Nariai_incidence_L1_rigidity", "Nariai_normalized_L0_obstruction", "Nariai_K_admissibility", "Nariai_Phi2_obstruction", "Nariai_PBW_associativity", "Nariai_coefficient_jets", "Nariai_splitting_jets", "cone"),
        "The old typed M_parent/L1_corrected/Kp0 associator has 209 first-variation coefficients, so its 207-coefficient shifted-chain defect is not an authoritative operator obstruction. The replacement coefficient-jet algebra agrees with direct symbolic composition. The full corrected L0/L1 jet families are now derived from covariant HPL plus the unique normalized strict-square correction, recover the point values, and close d_aut L0=L1 K through all required jets. The earlier Phi/L0/K rank screens remain exact linear algebra relative to that superseded target only; the associative middle/shifted-chain/Schur replay, complete SDR and causal transfer remain open.",
    ))
    values.append(_entry(
        "classical.crosswalk.bach_flat_parent_to_metric",
        _scope(NARIAI, background="open Bach-flat parent class <-> metric Bach complexes away from the certified conformal Nariai orbit", carrier="support-local parent/metric SDR", degree="crosswalk", parity="all", ell="all", m="all", k="all", omega="all"),
        {axis: "NO_CERTIFIED_MAP" for axis in AXES},
        ("NO_CERTIFIED_MAP", "No class-wide metric endpoint crosswalk."),
        ("NO_CERTIFIED_MAP", "No class-wide metric current pullback."),
        ("NO_CERTIFIED_MAP", "No class-wide charge-sector crosswalk."),
        ("NO_CERTIFIED_MAP", "No class-wide mode/resonance crosswalk."),
        _second(("NO_CERTIFIED_MAP", "No metric crosswalk."), ("NO_CERTIFIED_MAP", "No metric crosswalk."), ("NO_CERTIFIED_MAP", "No metric crosswalk.")),
        _evidence("Bach_parent"),
        "The universal parent theorem must not be promoted to a metric theorem outside the certified conformal Nariai orbit.",
    ))
    return values


def build() -> dict[str, Any]:
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "d_quotient_classical",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(),
        "verification_commands": [
            "python3 -m d_quotient_classical.atlas.generate_classical_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py d_quotient_classical/atlas/classical-causal-atlas-fragment.json",
            "python3 d_quotient_classical/atlas/verify_classical_atlas_fragment.py",
            "python3 -m unittest d_quotient_classical.atlas.tests.test_classical_atlas_fragment",
        ],
    }
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    wrapper = vacuum_evidence()
    if args.write:
        VACUUM_EVIDENCE.write_text(json.dumps(wrapper, indent=2, sort_keys=True) + "\n")
        OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    else:
        if json.loads(VACUUM_EVIDENCE.read_text()) != wrapper:
            raise AssertionError("vacuum evidence wrapper is stale")
        if json.loads(OUTPUT.read_text()) != build():
            raise AssertionError("classical atlas fragment is stale")
    print("CLASSICAL_CAUSAL_RESIDUAL_ATLAS_FRAGMENT_V1: PASS")


if __name__ == "__main__":
    main()
