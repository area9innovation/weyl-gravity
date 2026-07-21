"""Fail-closed Einstein-source crosswalk for the counterflow Berger fixture.

The selected two-phase action is exactly equivalent, on its gravity/relative-
clock block, to the positive Berger clock action.  The latter is a certified
Weyl--matter solution but not an Einstein--matter solution with the same
stress for any constants kappa and Lambda.  Hence the requested relative
Einstein--Weyl triangle fails at the background-incidence map, before a
linear tangent map, cofiber, pulled-back pairing, or quadratic Einstein-clock
source can be defined.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/TWO_PHASE_COUNTERFLOW_EINSTEIN_SOURCE_CONDITION_OBSTRUCTION_V1.json"
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-einstein-source-condition-obstruction-fragment-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/two-phase-counterflow-einstein-source-condition-obstruction-v1.schema.json"

IMPORTS = {
    "counterflow_parent": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "counterflow_parent_payload": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1",
        "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "trace_charge_preflight": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json",
        "TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1",
        "2b578967ece7a2e6a8079c8fd84665ac40cf2b7e0aeef41d96882553c35115ea",
        "d6d54a6efaa30ffe48dd7b9718c1954fa4ea514b",
    ),
    "fixed_charge_reduction": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json",
        "TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1",
        "812f6a3c2308eaeef09bee25ec8c79c8f7c86de7a51383141f8cae46c2f9cae5",
        "a1ec93fe5d73d0c93341019c4e93a00d23ab95d6",
    ),
    "charge_clock_complementarity": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json",
        "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1",
        "cd1fe1bf22604d17c65b941032c6b31c404bfd5cc01bd7f8399642840da01ed4",
        "59764067a16a55d695fbe583724d7fb27c808b2e",
    ),
    "charge_clock_complementarity_payload": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1.json",
        "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1",
        "2e25c28e06ab54256c8a4af4b6793f241801bdfa84eab3eb218a1ab53eb873c0",
        "59764067a16a55d695fbe583724d7fb27c808b2e",
    ),
    "residual_bfv_receiver": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1.json",
        "TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1",
        "461474f7b9e35b75d862566f075d2cf3c6dc09c5333a5afada707304d15cbaea",
        "51207639e7dc6c47ecc33bdf8ce8e121cff2219f",
    ),
    "residual_bfv_receiver_payload": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_PAYLOAD_V1.json",
        "TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_PAYLOAD_V1",
        "e6835e1ebb199c9e7753fc19666fd7dba3fc997e5ac0115da124a4a6c14560c7",
        "51207639e7dc6c47ecc33bdf8ce8e121cff2219f",
    ),
    "berger_incidence": (
        ROOT / "bridge/certificates/berger_einstein_incidence.json",
        "BERGER_EINSTEIN_INCIDENCE",
        "6ab941dbf3312bcc991dc0de59be30853f876e4599414196a3ae21c967c863b4",
        "7e87281c416f4c4f98edfe61ae05829f4b48593a",
    ),
    "compact_product_chain_map": (
        ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json",
        "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1",
        "50958aaae3339a1aa5a78d7be3d17d71a3754c06633783e9957e2df0a02eeec0",
        "8a91c1260144e5d56dc0c033fc060988e320d33d",
    ),
}


class CounterflowEinsteinSourceError(RuntimeError):
    """Raised when an exact input or the first-map obstruction changes."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CounterflowEinsteinSourceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _imports() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, Any]]]:
    records: dict[str, dict[str, str]] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, (path, result_id, expected_sha, source_commit) in IMPORTS.items():
        actual_sha = _sha256(path)
        _require(actual_sha == expected_sha, f"stale imported hash: {name}")
        payload = _load(path)
        _require(payload.get("result_id") == result_id, f"stale result id: {name}")
        records[name] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": result_id,
            "sha256": actual_sha,
            "source_commit": source_commit,
        }
        payloads[name] = payload
    return records, payloads


def _exact_fixture() -> dict[str, Any]:
    q = sp.Rational(9, 40)
    alpha_b = sp.Integer(5)
    eta = sp.diag(-1, 1, 1, 1)
    ricci = sp.diag(0, (2 - q) / 2, (2 - q) / 2, q / 2)
    scalar = sp.simplify(sp.trace(eta * ricci))
    bach = sp.diag(
        (1 - q) ** 2 / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (5 * q - 1) / 6,
    )
    stress = alpha_b * bach
    trace_fixed_lambda = scalar / 4
    tracefree = ricci - trace_fixed_lambda * eta
    minor_b = sp.factor(tracefree[0, 0] * bach[1, 1] - tracefree[1, 1] * bach[0, 0])
    minor_t = sp.factor(tracefree[0, 0] * stress[1, 1] - tracefree[1, 1] * stress[0, 0])
    kappa_00 = sp.factor(tracefree[0, 0] / stress[0, 0])
    kappa_11 = sp.factor(tracefree[1, 1] / stress[1, 1])

    _require(scalar == sp.Rational(151, 80), "Berger scalar changed")
    _require(minor_b == -sp.Rational(279, 12800), "Bach incidence separator changed")
    _require(minor_t == -sp.Rational(279, 2560), "stress incidence separator changed")
    _require(kappa_00 == sp.Rational(906, 961), "00 coupling changed")
    _require(kappa_11 == sp.Rational(798, 403), "11 coupling changed")
    _require(stress[0, 0] == sp.Rational(961, 1920), "positive clock energy changed")
    _require(sp.trace(eta * stress) == 0, "counterflow stress trace changed")

    matrix = lambda m: [[str(sp.factor(m[i, j])) for j in range(m.cols)] for i in range(m.rows)]
    return {
        "q": str(q),
        "alpha_B": str(alpha_b),
        "ricci": matrix(ricci),
        "scalar": str(scalar),
        "bach": matrix(bach),
        "stress": matrix(stress),
        "tracefree": matrix(tracefree),
        "trace_fixed_lambda": str(trace_fixed_lambda),
        "minor_b": str(minor_b),
        "minor_t": str(minor_t),
        "kappa_00": str(kappa_00),
        "kappa_11": str(kappa_11),
        "residual_11_after_kappa_00": str(sp.factor(tracefree[1, 1] - kappa_00 * stress[1, 1])),
        "residual_00_after_kappa_11": str(sp.factor(tracefree[0, 0] - kappa_11 * stress[0, 0])),
    }


def build_certificate() -> dict[str, Any]:
    imports, payloads = _imports()
    parent = payloads["counterflow_parent"]
    parent_payload = payloads["counterflow_parent_payload"]
    preflight = payloads["trace_charge_preflight"]
    fixed = payloads["fixed_charge_reduction"]
    complementarity = payloads["charge_clock_complementarity"]
    complementarity_payload = payloads["charge_clock_complementarity_payload"]
    residual_receiver = payloads["residual_bfv_receiver"]
    residual_receiver_payload = payloads["residual_bfv_receiver_payload"]
    incidence = payloads["berger_incidence"]
    product_map = payloads["compact_product_chain_map"]

    _require(parent["result_state"] == "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT", "counterflow parent not terminal")
    _require(parent_payload["action_equivalence"]["conclusion"].startswith("the physical gravity-relative-clock block is exactly"), "action equivalence changed")
    _require(preflight["selected_fixture"]["background"] == "stationary Berger R x S3, a=1, c_squared=9/40", "selected background changed")
    _require(fixed["claim_flags"]["POSITIVE_RELATIVE_CLOCK_SURVIVES"] is False, "fixed-charge clock disposition changed")
    _require(complementarity["result_state"] == "UNRESTRICTED_CHARGED_CLOCK_HAS_EXACT_SECULAR_ZERO_JORDAN_OBSTRUCTION", "unrestricted charge-clock theorem changed")
    _require(complementarity_payload["branch_dichotomy"]["unrestricted_Q_rel"]["pairing_rank"] == 2, "unrestricted charge pairing changed")
    _require(residual_receiver["result_state"] == "OBSTRUCTED_MISSING_SPATIAL_STABILIZER_LIFT_AND_MOMENT_MAPS", "residual receiver disposition changed")
    _require(residual_receiver_payload["available_receiver_data"]["K_Rrel_D_U1_Cartan_ledger"] == "CERTIFIED", "K Cartan ledger changed")
    _require(incidence["classification"]["same_base_point_linearized_einstein_clock_complex_exists"] is False, "Berger incidence gate changed")
    _require(product_map["scope"]["background"].startswith("compact magnetic Plebanski-Hacyan"), "comparison-map background changed")

    fixture = _exact_fixture()
    return {
        "schema": "two-phase-counterflow-einstein-source-condition-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "TWO_PHASE_COUNTERFLOW_EINSTEIN_SOURCE_CONDITION_OBSTRUCTION_V1",
        "result_state": "OBSTRUCTED_BEFORE_LINEAR_MAP_BY_EXACT_BACKGROUND_NONINCIDENCE",
        "lifecycle_state": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "scope": {
            "theory": "selected two-phase counterflow Weyl--matter action tested against conventional same-source Einstein--matter gravity",
            "background": "stationary Berger R x S3, a=1, c_squared=q=9/40",
            "boundaries": "closed S3 Cauchy slices; no asymptotic boundary",
            "charge_sectors": ["unrestricted Q_rel", "derived fixed-Q_rel leaf followed by R_rel quotient"],
            "carrier": "certified 70-component causal Weyl--matter BV parent; proposed Einstein source object fails at background degree",
        },
        "action_transport": {
            "status": "CERTIFIED",
            "identity": parent_payload["action_equivalence"]["identity"],
            "conclusion": parent_payload["action_equivalence"]["conclusion"],
            "stress_transport": "the gravity/relative-clock stress is exactly the certified positive Berger clock stress; the diagonal U1 quartet is algebraically contractible",
            "background_weyl_equation": "alpha_B B_ab=T_ab with alpha_B=5",
        },
        "exact_background_test": {
            "weyl_matter_equation": "5 B_ab=T_ab: PASS",
            "einstein_matter_equation": "G_ab+Lambda g_ab=kappa T_ab: no constants (Lambda,kappa) solve all components",
            "trace_fixed_lambda": fixture["trace_fixed_lambda"],
            "tracefree_ricci": fixture["tracefree"],
            "stress": fixture["stress"],
            "kappa_from_00": fixture["kappa_00"],
            "kappa_from_11": fixture["kappa_11"],
            "stress_proportionality_minor_00_11": fixture["minor_t"],
            "bach_proportionality_minor_00_11": fixture["minor_b"],
            "residual_11_after_kappa_00": fixture["residual_11_after_kappa_00"],
            "residual_00_after_kappa_11": fixture["residual_00_after_kappa_11"],
            "first_failed_map": "background incidence Sol_Einstein-matter -> Sol_Weyl-matter",
            "linearization_consequence": "linearizing the Einstein equation at this non-solution yields an affine residual problem, not a same-base-point Jacobi complex",
        },
        "source_condition_disposition": {
            "diagonal_gauge_charge": "Q_diag=0 by the local Gauss equation",
            "relative_charge_density": "mu_squared*Omega=3/4 on the selected stationary fixture, hence the unrestricted relative charge is nonzero",
            "positive_stress_witness": "T_00=961/1920>0",
            "logical_separator": "Q_diag=0 does not imply vanishing stress, Einstein incidence, or Q(T)=0",
            "flat_compensated_Q_operator": "Q(T)_mn=(1/2)Box T_mn-(1/6)(eta_mn Box-partial_m partial_n)tr(T)",
            "Q_T_status": "NOT_APPLICABLE",
            "Q_T_reason": "the certified Q chain map is a flat constant-compensator same-source theorem; no curved-Berger source-complex crosswalk exists, and the Berger fixture already fails the prerequisite common-background incidence",
            "forbidden_inference": "neither diagonal U1 neutrality nor formal homogeneity is used to set Q(T)=0",
        },
        "charge_sector_split": {
            "unrestricted_Q_rel": {
                "clock": "one rank-two relative-clock Darboux pair survives in the unreduced Weyl--matter parent",
                "D": "charged global generator with H_D=(3/4)Q_rel",
                "K_Berger": "K=D-(3/4)R_rel is the null Hamiltonian background stabilizer",
                "linear_health": "OBSTRUCTED for bounded or finite-quasiperiodic stability by an exact size-two zero Jordan block; no real exponential growing root is present",
                "secular_solution": complementarity_payload["unrestricted_global_clock_health"]["solution"],
                "background_Q_rel": complementarity_payload["unrestricted_global_clock_health"]["background_Q_rel"],
                "Einstein_clock_sector": "NOT_APPLICABLE: background incidence already fails",
            },
            "fixed_Q_rel": {
                "clock": "OBSTRUCTED: the derived level set and R_rel quotient remove the complete relative-clock cohomology and pairing",
                "D": "presymplectic-null only after the explicit fixed-charge restriction",
                "K_Berger": "null stabilizer independently",
                "Einstein_clock_sector": "NOT_APPLICABLE: no clock remains and background incidence independently fails",
            },
        },
        "relative_triangle": {
            "candidate_sequence": "T_Einstein-clock --i--> T_Weyl-clock --pi--> T_extra",
            "background_object_map": "OBSTRUCTED",
            "Einstein_linear_source_equations": "NOT_APPLICABLE_AS_A_JACOBI_COMPLEX_AT_THIS_BASE_POINT",
            "inclusion_i": "NO_CERTIFIED_MAP",
            "projection_or_cofiber_pi": "NO_CERTIFIED_MAP",
            "additional_Weyl_quotient": "NO_CERTIFIED_MAP",
            "comparison_map_disposition": {
                "imported_map": "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1",
                "status": "NOT_APPLICABLE",
                "reason": "it is a compact magnetic Plebanski--Hacyan Einstein--Maxwell/Weyl--Maxwell map, not a Berger counterflow map; no cross-background or cross-carrier identification is authorized",
            },
        },
        "pairing_and_residual_action": {
            "direct_target_pairing": "CERTIFIED on the 70-component Weyl--matter parent",
            "Einstein_pairing": "NO_CERTIFIED_MAP at this background",
            "pulled_back_Weyl_pairing": "NO_CERTIFIED_MAP because inclusion_i does not exist",
            "relative_pairing": "NO_CERTIFIED_MAP because the cofiber is undefined",
            "abstract_stabilizer_CE": "CERTIFIED for su(2)_L direct_sum u(1)_R3 direct_sum R_K",
            "K_Berger_target_action": "CERTIFIED in the K/R_rel/D/U1 Cartan ledger on the Weyl--matter parent",
            "K_Berger_Einstein_restriction": "NO_CERTIFIED_MAP",
            "full_five_generator_residual_receiver": "OBSTRUCTED: the four spatial row actions, Hamiltonian moment maps, causal contractions and bulk-to-time-slice map are missing on the ordered 70-row carrier",
            "descended_residual_pairing": "NO_CERTIFIED_MAP",
        },
        "second_order_disposition": {
            "equation": "L v=-(1/2)D^2E(u,u)",
            "Einstein_clock_Taub_source_test": "NOT_APPLICABLE: there is no same-base-point Einstein-clock linear tangent u",
            "fixed_charge": "NOT_APPLICABLE: the relative clock is removed before q2",
            "unrestricted_charge": "OPEN as a Weyl--matter q2 problem only; it is not an Einstein-sector closure test",
            "causal_retarded": "NO_CERTIFIED_MAP",
            "does_not_refute": "the separate nonlinear-two-phase-counterflow-q2-stability work item on the Weyl--matter parent",
        },
        "claim_flags": {
            "counterflow_action_transport_certified": True,
            "same_background_einstein_incidence": False,
            "same_background_linear_inclusion": False,
            "relative_cofiber_constructed": False,
            "pulled_back_pairing_constructed": False,
            "fixed_and_unrestricted_charge_sectors_separated": True,
            "diagonal_neutrality_used_as_stress_vanishing": False,
            "flat_Q_operator_transplanted_to_Berger": False,
            "einstein_clock_second_order_test_defined": False,
            "lorentzian_scattering_particle_or_quantum_claim": False,
        },
        "claim_boundary": {
            "establishes": [
                "exact transport of the selected two-phase action to the certified positive Berger clock stress",
                "a nonzero rational Einstein-incidence separator at the selected fixture",
                "the first failed map before any same-background tangent inclusion or relative cofiber",
                "separate unrestricted and fixed-relative-charge dispositions",
            ],
            "does_not_establish": [
                "a universal no-go for Einstein sectors on other common backgrounds",
                "a value of the flat compensated Q(T) operator on the curved Berger fixture",
                "a Weyl target q2 obstruction or extension",
                "a residual BFV quotient, causal scattering, observer, particle, positivity, unitarity or quantum theorem",
            ],
        },
        "verification_commands": [
            "python3 bridge/einstein_sector/two_phase_counterflow_einstein_source_condition.py --check",
            "python3 bridge/einstein_sector/verify_two_phase_counterflow_einstein_source_condition.py",
            "python3 -m unittest -v bridge.einstein_sector.tests.test_two_phase_counterflow_einstein_source_condition",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-einstein-source-condition-obstruction-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    evidence = [{
        "path": str(OUTPUT.relative_to(ROOT)),
        "result_id": certificate["result_id"],
        "sha256": _sha256(OUTPUT) if OUTPUT.exists() else "PENDING_GENERATION",
    }]
    base_scope = {
        "theory": "selected two-phase counterflow Weyl--matter action versus conventional same-source Einstein--matter gravity",
        "background": "stationary Berger R x S3, a=1, c_squared=9/40",
        "boundaries": "none; closed S3 Cauchy slices",
        "carrier": "proposed same-background Einstein/Weyl relative triangle over the certified 70-component Weyl--matter parent",
        "degree": "all BV degrees",
        "parity": "mixed",
        "ell": "all",
        "m": "all",
        "k": "NOT_APPLICABLE",
        "omega": "all supported frequencies; background Omega=3/4",
    }
    entries = []
    for sector, symplectic, clock in (
        ("unrestricted Q_rel", "NO_CERTIFIED_MAP", "rank-two relative-clock Darboux pair retained only in the Weyl--matter parent, with a certified size-two secular zero Jordan block"),
        ("derived fixed-Q_rel leaf followed by R_rel quotient", "OBSTRUCTED", "complete relative-clock cohomology and pairing removed"),
    ):
        scope = dict(base_scope)
        scope["charge_sector"] = sector
        entries.append({
            "id": "bridge.two_phase_counterflow.einstein_source_condition." + ("unrestricted" if sector.startswith("unrestricted") else "fixed_q_rel"),
            "scope": scope,
            "descriptions": {
                "causal": "CERTIFIED",
                "symplectic": symplectic,
                "nonlinear": "NOT_APPLICABLE",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": {"status": "NO_CERTIFIED_MAP", "statement": "No Einstein-clock Jacobi carrier exists at this non-Einstein base point."},
                "lee_wald": {"status": symplectic, "statement": clock + "; no cross-theory pullback exists."},
                "taub_maps": {"status": "NOT_APPLICABLE", "statement": "No same-base-point Einstein-clock tangent exists on which to evaluate a Taub map."},
                "resonance": {"status": "NOT_APPLICABLE", "statement": "The bridge fails at background incidence before a relative resonance problem is typed."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "NOT_APPLICABLE", "statement": "No Einstein-clock tangent u exists at this base point."},
                    "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "No Einstein-clock tangent u exists at this base point."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "The Weyl--matter causal parent is certified, but no Einstein-clock source map exists."},
                },
            },
            "evidence": evidence,
            "claim_boundary": "Exact same-background incidence obstruction only; no cross-background identification, Weyl-target q2 verdict, observer, particle or quantum promotion.",
        })
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "bridge",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": entries,
        "verification_commands": certificate["verification_commands"],
    }


def verify_certificate(path: Path = OUTPUT) -> dict[str, Any]:
    expected = build_certificate()
    actual = _load(path)
    _require(actual == expected, "stale or mutated counterflow Einstein-source certificate")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.check:
        _require(_load(OUTPUT) == certificate, "canonical certificate is stale")
        expected_atlas = build_atlas(certificate)
        _require(_load(ATLAS) == expected_atlas, "canonical atlas fragment is stale")
        print("TWO_PHASE_COUNTERFLOW_EINSTEIN_SOURCE_CONDITION_OBSTRUCTION_V1: PASS")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    atlas = build_atlas(certificate)
    atlas["entries"][0]["evidence"][0]["sha256"] = _sha256(OUTPUT)
    atlas["entries"][1]["evidence"][0]["sha256"] = _sha256(OUTPUT)
    ATLAS.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {ATLAS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
