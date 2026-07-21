"""Assemble the cylinder's intrinsic derived BFV/Koszul carrier.

The selected D-finite residual model already contains the fifteen conformal
ghost momenta and the exact cubic BFV charge.  This module identifies those
momenta with the Koszul generators of the derived moment-map zero fibre and
audits every map needed to receive local anomaly representatives.  The
intrinsic carrier closes; the support-local full-BV bulk-to-slice map does not.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/CYLINDER_DERIVED_BFV_KOSZUL_TIME_SLICE_CARRIER_V1.json"
ATLAS_OUTPUT = ROOT / "residual_atlas/cylinder-derived-bfv-koszul-time-slice-carrier-fragment-v1.json"
SCHEMA_PATH = ROOT / "bridge/anomaly_restriction/schema/cylinder-derived-bfv-koszul-time-slice-carrier-v1.schema.json"
PRODUCER_PATH = ROOT / "bridge/anomaly_restriction/cylinder_derived_bfv_koszul_time_slice_carrier.py"

INPUTS = {
    "predecessor_obstruction": (
        "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json",
        "4863e00186e719e933e20fe58f2bc0429b1cb0a13db8481b6f8152680b3255fb",
        "STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1",
    ),
    "residual_bfv": (
        "bridge/certificates/residual_bfv.json",
        "f7c73355ec9712283e30693ca6f4b53a67ed0638ae366bee76c0c10e632a81ac",
        None,
    ),
    "closed_universe_bfv": (
        "bridge/certificates/closed_universe_bfv.json",
        "37eda8319d7fbe69e6b0838677b3d7fd4aecddd8b6274c281fefc2cf3f612ceb",
        None,
    ),
    "full_hpl_transfer": (
        "bridge/certificates/full_hpl_transfer.json",
        "18acc197a45ba9256e0979e7b04c0cd5e7ca36de94b7540aa2038fc1f9e3511a",
        None,
    ),
    "metric_to_residual": (
        "bridge/certificates/metric_to_residual.json",
        "25bd2b6c3ac31139bda9bcee6ad18f2df69a73cea3ec102b66ff310b1644f8c3",
        None,
    ),
    "taub_moment_map": (
        "bridge/certificates/taub_moment_map.json",
        "84fb8d94043f89fcd70e8fdd2940b266ea6f9006c3ff94cb55884b1b4ceb46e1",
        None,
    ),
    "endpoint_taub_map": (
        "field_bv_identification/zero_modes/certificates/taub_obstruction_map.json",
        "72ac747c0b15c85c75f7a86d983960f305e486c96ab594c056f9b3377cfbf540",
        None,
    ),
    "zero_mode_transgression": (
        "field_bv_identification/polarized_state/certificates/zero_mode_transgression.json",
        "dfe70f8bf6ad6820178e67247a06b1c27fefba3c5b7396ba42fd14e96db82b53",
        None,
    ),
    "residual_cubic_bfv": (
        "quantum-weyl/transfer/certificates/HT1_RESIDUAL_CUBIC_BLOCK.json",
        "802ea86e1bb807476c7e1bbbe25f33435fa1a79ba433c1b0943b19c4986eefc4",
        "HT1_RESIDUAL_CUBIC_BLOCK",
    ),
    "local_bach_seed_lift": (
        "quantum-weyl/transfer/certificates/HT1B_LOCAL_BACH_SEED_LIFT.json",
        "f08976200d4e07dc4fb349fa785c960ab4aa8a0d685fc82fe1a2cb30c5ff26c5",
        "HT1B_LOCAL_BACH_SEED_LIFT",
    ),
    "euler_transgression": (
        "quantum-weyl/local_bv/certificates/EULER_TRANSGRESSION_CERTIFICATE.json",
        "2c03b184f27d6f0054ed12029b052834ef08aa8bf4f2c42663f84617f0e63063",
        "EULER_TRANSGRESSION_CERTIFICATE",
    ),
    "local_anomaly_cohomology": (
        "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json",
        "a7730a34b21d2068cc73e46c563ce929195a3d9a7c7626d3843788b54e0592b3",
        "H14_GAUGE_FIXED_BV_RESULT",
    ),
    "raw_d_charge_audit": (
        "d_quotient_classical/certificates/compact_cylinder_d_charge_audit.json",
        "6e609dd850049fb7b85867033dbdce0b2b214f2d5196665015f8e2b552d493e4",
        None,
    ),
}


class CylinderDerivedCarrierError(RuntimeError):
    """Raised when an imported or assembled carrier identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CylinderDerivedCarrierError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _import_inputs() -> tuple[list[dict[str, str]], dict[str, dict[str, Any]]]:
    ledger: list[dict[str, str]] = []
    payloads: dict[str, dict[str, Any]] = {}
    for name, (relative, expected_hash, expected_id) in INPUTS.items():
        path = ROOT / relative
        _require(path.exists(), f"missing input: {relative}")
        actual_hash = _sha256(path)
        _require(actual_hash == expected_hash, f"input hash drift: {name}")
        payload = _load(path)
        if expected_id is not None:
            _require(payload.get("result_id") == expected_id, f"input result id drift: {name}")
        payloads[name] = payload
        ledger.append(
            {
                "name": name,
                "path": relative,
                "sha256": actual_hash,
                "result_id": payload.get("result_id", payload.get("schema", "NO_RESULT_ID")),
            }
        )
    return ledger, payloads


def _audit_inputs(data: dict[str, dict[str, Any]]) -> None:
    predecessor = data["predecessor_obstruction"]
    _require(
        predecessor["claim_flags"]["CYLINDER_DERIVED_BFV_KOSZUL_CARRIER_CERTIFIED"] is False,
        "predecessor obstruction changed",
    )
    residual = data["residual_bfv"]
    _require(residual["dimension"] == 15 and residual["exterior_dimension"] == 32768, "residual BFV dimension changed")
    transgression = data["zero_mode_transgression"]
    _require(
        transgression["lambda_all_generators"] == "1"
        and transgression["conventions"]["ghost_free_vector_field"] == "Q_BFV b_a=mu_a",
        "zero-mode transgression normalization changed",
    )
    endpoint = data["endpoint_taub_map"]
    _require(endpoint["endpoint_dimension"] == 15 and endpoint["moment_map_components"] == 15, "endpoint count changed")
    ht1 = data["residual_cubic_bfv"]
    _require(
        ht1["checks"]["endpoint_to_moment_map_components"] == "VERIFIED_15_OF_15"
        and ht1["checks"]["matter_matter_endpoint_output"] == "VERIFIED_Q_BFV_b_EQUALS_MU"
        and ht1["checks"]["cubic_master_equation"]["status"] == "VERIFIED_EXACT_CUBIC_MASTER_EQUATION",
        "residual cubic BFV gate changed",
    )
    hpl = data["full_hpl_transfer"]
    _require("all fifteen residual chain maps included" in hpl["scope"]["proved"], "HPL map coverage changed")
    local = data["local_bach_seed_lift"]
    _require(
        local["checks"]["full_support_local_q2"] == "NOT_COMPUTED"
        and local["checks"]["local_q1_q2_chain_identity"].startswith("NOT_COMPUTED"),
        "support-local obstruction changed",
    )
    anomaly = data["local_anomaly_cohomology"]
    _require(
        {row["representative_id"] for row in anomaly["classes"]}
        == {"ANOM_OMEGA_C2", "ANOM_OMEGA_E4", "ANOM_OMEGA_C_DUAL_C"},
        "local anomaly basis changed",
    )


def _carrier(data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    residual = data["residual_bfv"]
    ht1 = data["residual_cubic_bfv"]
    real_basis = residual["basis"]
    magnetic_basis = [row["name"] for row in ht1["transfer_payload"]["basis"]]
    _require(len(real_basis) == len(magnetic_basis) == 15, "carrier basis count changed")
    return {
        "category": "selected finite algebraic closed-cylinder derived BFV model",
        "derived_zero_fibre": "[P_lin x^R_{so(4,2)^*} {0} /^R SO(4,2)]",
        "constraint_count": 15,
        "real_generator_basis": real_basis,
        "magnetic_generator_basis": magnetic_basis,
        "basis_crosswalk_status": ht1["checks"]["common_magnetic_basis"],
        "generators": {
            "c_A": {
                "role": "odd residual CE ghosts",
                "count": 15,
                "differential": "Q c^A=-(1/2) f^A_BC c^B c^C",
            },
            "eta_A_equals_b_A": {
                "role": "odd Koszul generators / BFV ghost momenta",
                "count": 15,
                "koszul_degree": -1,
                "ghost_free_differential": "d_K eta_A=mu_A",
                "full_differential": "Q_BFV b_A=mu_A plus the coadjoint ghost-b term fixed by f^A_BC",
            },
            "matter": {
                "role": "selected E/A/L residual phase-space coordinates",
                "dimension": ht1["transfer_payload"]["matter_phase_space"]["dimension"],
                "differential": "Q Phi=c^A K_A Phi",
            },
        },
        "bfv_charge": "Omega_res=c^A mu_A-(1/2) f^A_BC c^B c^C b_A",
        "moment_map_formula": ht1["cubic_charge"]["moment_map_formula"],
        "nilpotency": {
            "koszul_slice": "d_K^2=0 because d_K acts trivially on the commuting moment-map coefficients",
            "full_bfv": ht1["checks"]["cubic_master_equation"]["status"],
            "jacobi_defects": ht1["checks"]["cubic_master_equation"]["ghost_jacobi_defects"],
            "representation_defects": ht1["checks"]["cubic_master_equation"]["ghost_matter_representation_defects"],
            "moment_map_equivariance_defects": ht1["checks"]["cubic_master_equation"]["matter_moment_map_equivariance_defects"],
        },
        "relations_needed_for_nilpotency": [
            "Jacobi: f^E_[AB f^D_C]E=0",
            "representation: [K_A,K_B]=f^C_AB K_C",
            "equivariance: rho_A(mu_B)=f^C_AB mu_C",
            "Hamiltonian normalization: M_A=-(1/2) J K_A",
        ],
        "syzygy_boundary": "No claim that the fifteen quadrics form a regular sequence or that their complete higher syzygy module has been resolved; those properties are not needed for the displayed BFV master equation.",
    }


def _chain_map_ledger(data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    minimal = data["predecessor_obstruction"]["input_pins"]["cylinder_minimal_bv_chain"]
    zero = data["zero_mode_transgression"]
    ht1 = data["residual_cubic_bfv"]
    local = data["local_bach_seed_lift"]
    return {
        "bulk_minimal_BV_to_raw_polynomial": {
            "status": "CERTIFIED_UNARY_D_FINITE",
            "source": minimal,
            "scope": "exact finite energy-buffer chain isomorphism; nonlinear master-action terms excluded from q1",
        },
        "raw_polynomial_to_residual_CE": {
            "status": "CERTIFIED_CENTERED_FINITE_WINDOW",
            "identity": data["full_hpl_transfer"]["conclusion"],
            "all_fifteen_maps": True,
        },
        "quadratic_endpoint_to_moment_map": {
            "status": "CERTIFIED_SELECTED_RESIDUAL_MODEL",
            "identity": "Theta([B^(2)(h,h)])(z)=T_z(h)=mu_z(h)",
            "representative_independence": "CERTIFIED_MODULO_K_SHARP_EXACT_ENDPOINT_SOURCES",
        },
        "endpoint_to_BFV_ghost_momentum": {
            "status": "CERTIFIED_SELECTED_ALGEBRAIC_TIME_SLICE",
            "map": zero["suspension"],
            "normalization": zero["lambda_all_generators"],
            "orientation": zero["cotangent_orientation"],
        },
        "boundary_BFV_differential": {
            "status": "CERTIFIED_SELECTED_FINITE_MODEL",
            "identity": ht1["checks"]["matter_matter_endpoint_output"],
            "master_equation": ht1["checks"]["cubic_master_equation"]["status"],
        },
        "raw_D_action": {
            "status": "CERTIFIED_ON_INTRINSIC_DERIVED_CARRIER",
            "generator": "D",
            "preservation": data["raw_d_charge_audit"]["phase_spaces"]["P_der"]["D_action_preserves_phase_space"],
            "verdict": data["raw_d_charge_audit"]["phase_spaces"]["P_der"]["verdict"],
            "cartan_on_local_anomalies": "NO_CERTIFIED_MAP",
        },
        "support_local_full_BV_bulk_to_slice": {
            "status": "OBSTRUCTED",
            "witnesses": {
                "full_support_local_q2": local["checks"]["full_support_local_q2"],
                "local_q1_q2_chain_identity": local["checks"]["local_q1_q2_chain_identity"],
                "ghost_completion": local["checks"]["ghost_completion"],
                "antifield_completion": local["checks"]["antifield_completion"],
            },
            "missing": local["next_required_exports"],
            "consequence": "The intrinsic residual carrier cannot yet receive arbitrary-support local BV anomaly cocycles as a chain map.",
        },
    }


def _anomaly_orders() -> list[dict[str, Any]]:
    return [
        {
            "class_id": "ANOM_OMEGA_C2",
            "background_value": "0 because the cylinder is conformally flat",
            "first_metric_order": 2,
            "reason": "C(gbar)=0, so sqrt(g) C^2 has no constant or linear metric term",
            "derived_receiver_map": "NO_CERTIFIED_MAP",
            "cohomology_verdict_on_receiver": "NOT_ASSIGNED",
        },
        {
            "class_id": "ANOM_OMEGA_E4",
            "background_value": "0 on R x S3",
            "first_metric_order": 1,
            "reason": "delta E4=d Theta_E is a nonzero local transgression; omega delta E4 leaves the certified d omega wedge Theta_E residual after the naive integration-by-parts step",
            "derived_receiver_map": "NO_CERTIFIED_MAP",
            "cohomology_verdict_on_receiver": "NOT_ASSIGNED",
        },
        {
            "class_id": "ANOM_OMEGA_C_DUAL_C",
            "background_value": "0 because the cylinder Weyl tensor vanishes",
            "first_metric_order": 2,
            "reason": "both Weyl factors vanish at the background",
            "derived_receiver_map": "NO_CERTIFIED_MAP",
            "cohomology_verdict_on_receiver": "NOT_ASSIGNED",
        },
    ]


def build_certificate() -> dict[str, Any]:
    imported, data = _import_inputs()
    _audit_inputs(data)
    return {
        "schema": "cylinder-derived-bfv-koszul-time-slice-carrier-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "CYLINDER_DERIVED_BFV_KOSZUL_TIME_SLICE_CARRIER_V1",
        "result_state": "INTRINSIC_DERIVED_CARRIER_CERTIFIED_SUPPORT_LOCAL_ANOMALY_MAP_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_commit": "a9be01eab",
            "producer": str(PRODUCER_PATH.relative_to(ROOT)),
            "producer_sha256": _sha256(PRODUCER_PATH),
            "imported_artifacts": imported,
        },
        "scope": {
            "theory": "pure Weyl gravity minimal/local BV and selected residual BFV",
            "background": "conformally flat vacuum Einstein cylinder R x S3",
            "boundaries": "closed Cauchy S3; selected algebraic time-slice polarization; no spatial boundary",
            "charge_sector": "derived common zero fibre of all fifteen SO(4,2) moment maps",
            "carrier": "D-finite E/A/L residual matter plus 15 CE ghosts and 15 Koszul/BFV ghost momenta",
            "degree": "unary residual action plus quadratic moment-map/BFV block; local anomaly metric orders recorded separately",
            "parity": "both residual chiralities; even and odd local anomaly representatives kept distinct",
            "ell": "D-finite cylinder harmonics in the imported selected finite regression window",
            "m": "complete imported magnetic basis in that window",
            "k": "NOT_APPLICABLE on S3",
            "omega": "integer cylinder D weights in the imported E/A/L window",
        },
        "derived_carrier": _carrier(data),
        "chain_map_ledger": _chain_map_ledger(data),
        "anomaly_perturbative_orders": _anomaly_orders(),
        "receiver_contract_for_quantum": {
            "may_import": [
                "the 15-generator intrinsic BFV charge and ghost-momentum Koszul identification",
                "the normalized algebraic endpoint suspension tau=suspension o Theta",
                "the selected finite-window nilpotency and raw-D preservation identities",
                "the kinematic first metric orders of the three local representatives",
            ],
            "must_not_import": [
                "a support-local full-BV local-to-time-slice chain map",
                "any image, zero, exactness or nontriviality verdict for the three anomaly classes in the derived carrier",
                "a raw-D Cartan defect on local anomaly representatives",
                "QME, Hadamard, causal, particle, positivity or unitarity conclusions",
            ],
            "activation_gate": "Supply arbitrary-input support-local q2 with Diff/Weyl ghost and antifield completion, portable local q1 and contraction maps, and verify the arity-two chain square before restricting anomaly descent classes.",
        },
        "classification": {
            "fifteen_generator_intrinsic_derived_carrier_certified": True,
            "eta_A_identified_with_BFV_ghost_momenta": True,
            "selected_algebraic_time_slice_transgression_certified": True,
            "selected_finite_BFV_nilpotency_certified": True,
            "raw_D_preserves_intrinsic_derived_carrier": True,
            "support_local_full_BV_time_slice_chain_map_certified": False,
            "local_anomaly_representatives_mapped_to_carrier": False,
            "local_anomaly_receiver_cohomology_verdict_assigned": False,
            "full_higher_syzygy_resolution_certified": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "claim_boundary": (
            "This certificate assembles the already certified intrinsic fifteen-generator residual BFV/Koszul carrier and normalized algebraic endpoint suspension on the selected D-finite Einstein-cylinder model. It identifies the precise remaining obstruction: arbitrary-support local q2, ghost/antifield completion, and portable local contraction data are absent, so no full local-BV-to-time-slice chain map or anomaly image exists. It makes no anomaly cohomology, Cartan-defect, QME, causal, state, particle, positivity or unitarity claim."
        ),
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.anomaly_restriction.cylinder_derived_bfv_koszul_time_slice_carrier --check",
            "PYTHONPATH=. python3 -m bridge.anomaly_restriction.verify_cylinder_derived_bfv_koszul_time_slice_carrier",
            "PYTHONPATH=. python3 -m unittest bridge.anomaly_restriction.tests.test_cylinder_derived_bfv_koszul_time_slice_carrier",
            "python3 residual_atlas/validate_fragment.py residual_atlas/cylinder-derived-bfv-koszul-time-slice-carrier-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any], certificate_path: Path) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(PRODUCER_PATH.relative_to(ROOT)),
        "generated_by_sha256": _sha256(PRODUCER_PATH),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "pure_weyl.cylinder.derived_bfv_koszul.time_slice_carrier",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "OBSTRUCTED",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "CERTIFIED", "statement": "The imported D-finite E/A/L residual window is unchanged."},
                    "lee_wald": {"status": "CERTIFIED", "statement": "The action-scaled residual symplectic matrix and ghost cotangent orientation are imported exactly."},
                    "taub_maps": {"status": "CERTIFIED", "statement": "All fifteen mu_A are the ghost-free Q_BFV images of eta_A=b_A."},
                    "resonance": {"status": "NOT_APPLICABLE", "statement": "This entry concerns the derived moment-map fibre, not the compact-product resonance ledger."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "NOT_APPLICABLE", "statement": "Cylinder residual derived carrier; no compact-product correction class is imported."},
                        "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "No source inversion theorem is asserted."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded local-to-time-slice complex is constructed."},
                    },
                },
                "evidence": [{"path": str(certificate_path.relative_to(ROOT)), "result_id": certificate["result_id"], "sha256": _sha256(certificate_path)}],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--atlas", type=Path, default=ATLAS_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.check:
        _require(args.output.exists(), "certificate missing")
        _require(_load(args.output) == certificate, "certificate drift")
        expected_atlas = build_atlas(certificate, args.output)
        _require(args.atlas.exists(), "atlas missing")
        _require(_load(args.atlas) == expected_atlas, "atlas drift")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    atlas = build_atlas(certificate, args.output)
    args.atlas.parent.mkdir(parents=True, exist_ok=True)
    args.atlas.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
