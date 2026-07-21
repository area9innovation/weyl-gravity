"""Obstruct the finite-window arbitrary-support cylinder BV time-slice SDR.

The strict cylinder causal complex is an all-energy complex.  The currently
certified derived BFV receiver contains physical matter only at compact
energies 2, 3 and 4.  An SO(4,2)-equivariant SDR from the former to the latter
would induce an equivariant isomorphism on unary cohomology.  The nonzero E
branch at energy five is therefore a decisive counterexample before any
quadratic anomaly restriction can be defined.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/CYLINDER_ARBITRARY_SUPPORT_FULL_BV_Q2_TIME_SLICE_CHAIN_MAP_OBSTRUCTION_V1.json"
ATLAS = ROOT / "residual_atlas/cylinder-arbitrary-support-full-bv-q2-time-slice-obstruction-fragment-v1.json"
SCHEMA = ROOT / "bridge/anomaly_restriction/schema/cylinder-arbitrary-support-full-bv-q2-time-slice-obstruction-v1.schema.json"
PRODUCER = ROOT / "bridge/anomaly_restriction/cylinder_arbitrary_support_full_bv_q2_time_slice_obstruction.py"

INPUTS = {
    "intrinsic_derived_receiver": (
        "bridge/certificates/CYLINDER_DERIVED_BFV_KOSZUL_TIME_SLICE_CARRIER_V1.json",
        "31d47b21a63e03261c109568e1f852155412169fc7260500baba8a972da6a02c",
    ),
    "predecessor_chain_map_obstruction": (
        "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json",
        "4863e00186e719e933e20fe58f2bc0429b1cb0a13db8481b6f8152680b3255fb",
    ),
    "minimal_bv_chain": (
        "field_bv_identification/certificates/minimal_bv_chain.json",
        "3f9d04dd729c911fbe07768158d96ae411634b7a91bf70a139e8c7cf1dcd8c64",
    ),
    "selected_polarized_receiver": (
        "field_bv_identification/polarized_state/certificates/polarized_state_complex.json",
        "efe492946333578e91d880fde0008166ba8960bc366840413883e5c0e39d0ec1",
    ),
    "selected_hpl_transfer": (
        "bridge/certificates/full_hpl_transfer.json",
        "18acc197a45ba9256e0979e7b04c0cd5e7ca36de94b7540aa2038fc1f9e3511a",
    ),
    "all_energy_eal_spectrum": (
        "covariant_completion/certificates/curved_EAL_spectrum_all_level.json",
        "253b13da55b1e139ed7af0d1af32a142a6824f8c515ef6d82296a162fa9ef16d",
    ),
    "causal_endpoint_complex": (
        "covariant_completion/certificates/curved_prolonged_metric_endpoint_complex.json",
        "870621ae6750b1e66e3f3316c5a2680d1244c7fca3be4d6aeaabbfdc2178fd79",
    ),
    "full_causal_homotopy": (
        "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json",
        "1f8aae727a06fb82c70732f7207499d427894247d09fea22f677a0f9b38be0ee",
    ),
}


class CylinderQ2TimeSliceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CylinderQ2TimeSliceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def _imports() -> tuple[list[dict[str, str]], dict[str, dict[str, Any]]]:
    ledger: list[dict[str, str]] = []
    payloads: dict[str, dict[str, Any]] = {}
    for name, (relative, expected) in INPUTS.items():
        path = ROOT / relative
        _require(path.exists(), f"missing input: {relative}")
        actual = _sha256(path)
        _require(actual == expected, f"input hash drift: {name}")
        payload = _load(path)
        payloads[name] = payload
        ledger.append(
            {
                "name": name,
                "path": relative,
                "sha256": actual,
                "result_id": str(payload.get("result_id", payload.get("schema", "NO_RESULT_ID"))),
            }
        )
    return ledger, payloads


def _audit(payloads: dict[str, dict[str, Any]]) -> None:
    receiver = payloads["intrinsic_derived_receiver"]
    selected = payloads["selected_polarized_receiver"]
    spectrum = payloads["all_energy_eal_spectrum"]
    endpoint = payloads["causal_endpoint_complex"]
    causal = payloads["full_causal_homotopy"]
    _require(receiver["derived_carrier"]["constraint_count"] == 15, "receiver generator count drifted")
    _require(selected["maximum_regression_energy"] == 4, "selected receiver cutoff drifted")
    _require(selected["physical_dimensions"] == {"2": 10, "3": 40, "4": 82}, "selected physical window drifted")
    _require(selected["positive_frequency_dimension"] == 132, "selected receiver dimension drifted")
    _require(spectrum["all_level_not_finite_cutoff"] is True, "all-energy theorem weakened")
    _require([row["family"] for row in spectrum["branches"]] == ["E", "A", "L"], "E/A/L ledger drifted")
    _require(endpoint["dimension"] == 30, "minimal causal endpoint dimension drifted")
    _require(endpoint["local_graph_maps"]["support"]["finite_order_differential"] is True, "endpoint maps lost locality")
    _require(causal["causal_green_homotopy"] is True, "386-row causal homotopy drifted")
    _require(causal["dimension_ledger"]["prolonged"] == 386, "causal carrier rank drifted")


def obstruction_witness(selected_energies: tuple[int, ...] = (2, 3, 4)) -> dict[str, Any]:
    """Reconstruct the first equivariant SDR defect independently of matrices."""
    energy = 5
    one_chirality = energy**2 + 2 * energy - 3
    both_chiralities = 2 * one_chirality
    target_weight_dimension = both_chiralities if energy in selected_energies else 0
    composite_rank = min(both_chiralities, target_weight_dimension)
    return {
        "family": "E",
        "energy": energy,
        "one_chirality_dimension": one_chirality,
        "both_chiralities_dimension": both_chiralities,
        "selected_target_weight_dimension": target_weight_dimension,
        "rank_of_iota_pi_on_witness": composite_rank,
        "rank_of_identity_on_witness": both_chiralities,
        "minimum_sdr_defect_rank": both_chiralities - composite_rank,
        "identity": "[iota_cl pi_cl]=0 on H_E,5 but [1]=1 on H_E,5",
    }


def _q2_ansatz() -> dict[str, Any]:
    return {
        "background": "g=gbar, c=omega=gstar=cstar=omegastar=0 on the unit vacuum conformal cylinder",
        "master_action": [
            "S_W[g]",
            "integral gstar^(mu nu)(L_c g_(mu nu)+2 omega g_(mu nu))",
            "integral cstar_mu [c,c]^mu/2",
            "integral omegastar L_c omega",
        ],
        "vector_field": "Q=(S_min,-)_BV",
        "taylor_convention": "Q(epsilon Phi)=epsilon q1(Phi)+epsilon^2 q2(Phi,Phi)+O(epsilon^3); q2=(1/2)D^2Q at the background",
        "complete_minimal_roles": [
            {"degree": -1, "role": "Diff ghost", "symbol": "c_mu", "q2_source_terms": ["cstar[c,c]/2"]},
            {"degree": -1, "role": "Weyl ghost", "symbol": "omega", "q2_source_terms": ["omegastar L_c omega"]},
            {"degree": 0, "role": "metric", "symbol": "h_mu_nu", "q2_source_terms": ["gstar L_c g", "2 gstar omega g"]},
            {"degree": 1, "role": "metric antifield/equation", "symbol": "hstar_mu_nu", "q2_source_terms": ["D^2 Bach[h,h]", "cotangent Diff/Weyl action"]},
            {"degree": 2, "role": "Diff-ghost antifield/identity", "symbol": "cstar_mu", "q2_source_terms": ["metric-antifield Noether Hessian", "ad_c^star cstar", "omega-antifield transport"]},
            {"degree": 2, "role": "Weyl-ghost antifield/identity", "symbol": "omegastar", "q2_source_terms": ["2 h.hstar", "Diff cotangent transport"]},
        ],
        "domain": {
            "local_inputs": "Gamma_c(E_min) tensor Gamma_c(E_min), polarized by bilinearity; one compact and one smooth input is also allowed",
            "local_output": "Gamma_c(E_min)",
            "support_rule": "supp q2(u,v) subset supp(u) intersection supp(v) for two compact inputs",
            "maximum_metric_derivative_order": 4,
            "coefficient_ring": "real rational tensor-natural coefficients in the unit-cylinder curvature normalization",
        },
        "arity_two_master_identity": "q1 q2(u,v)+q2(q1 u,v)+(-1)^|u|q2(u,q1 v)=0",
        "status": "COMPLETE_ACTION_DEFINED_ANSATZ_NOT_SERIALIZED_AS_PORTABLE_COMPONENT_PAYLOAD",
        "reason_not_executed": "the requested composite SDR fails already on unary cohomology before q2 can be projected to the selected receiver",
    }


def build_certificate() -> dict[str, Any]:
    imports, payloads = _imports()
    _audit(payloads)
    witness = obstruction_witness()
    _require(witness["minimum_sdr_defect_rank"] == 64, "energy-five obstruction changed")
    return {
        "schema": "cylinder-arbitrary-support-full-bv-q2-time-slice-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "CYLINDER_ARBITRARY_SUPPORT_FULL_BV_Q2_TIME_SLICE_CHAIN_MAP_OBSTRUCTION_V1",
        "result_state": "ALL_ENERGY_TO_SELECTED_FINITE_RECEIVER_EQUIVARIANT_SDR_OBSTRUCTED_AT_UNARY_ORDER",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "provenance": {
            "producer": str(PRODUCER.relative_to(ROOT)),
            "producer_sha256": _sha256(PRODUCER),
            "imported_artifacts": imports,
        },
        "scope": {
            "theory": "strict pure-Weyl minimal BV and its certified 386-row causal prolongation",
            "background": "unit vacuum conformal cylinder R x S3",
            "boundaries": "closed Cauchy S3; compact/spacelike-compact causal domains",
            "charge_sector": "candidate common zero fibre of all fifteen SO(4,2) moment maps",
            "carrier": "arbitrary-support all-energy 386-row causal source versus selected 132-dimensional positive-frequency E/A/L matter receiver with 15 CE ghosts and 15 BFV/Koszul momenta",
            "degree": "unary SDR gate preceding the declared complete minimal q2 ansatz",
            "parity": "both E/A/L chiralities",
            "ell": "all cylinder harmonics at source; selected compact energies 2,3,4 at target",
            "m": "complete multiplicities at each source energy",
            "k": "NOT_APPLICABLE on S3",
            "omega": "all integer E/A/L frequencies at source; weights 2,3,4 at selected target",
        },
        "frozen_causal_contraction": {
            "full_rank": 386,
            "endpoint_rank": 30,
            "algebraically_contracted_rank": 356,
            "pi_endpoint": "p_end=P_aux P_cyl; finite-order differential, compact and spacelike-compact support preserving",
            "iota_endpoint": "j_end=I_cyl I_aux; finite-order differential, compact and spacelike-compact support preserving",
            "homotopy": "Lambda_plus/minus with supp Lambda_plus/minus f subset J_plus/minus(supp f)",
            "status": "CERTIFIED_TO_ALL_ENERGY_30_ROW_FIELD_BUNDLE_ENDPOINT_NOT_TO_THE_SELECTED_FINITE_RESIDUAL_RECEIVER",
        },
        "local_q2_ansatz": _q2_ansatz(),
        "first_failed_gate": {
            "requested_identity": "pi_cl iota_cl=1 and iota_cl pi_cl=1-q1 s_cl-s_cl q1 on the arbitrary-support full causal complex",
            "hypotheses": [
                "pi_cl and iota_cl are q1-chain maps",
                "the SDR is compatible with the residual SO(4,2) action and hence with D weights",
                "the target physical matter carrier has only weights 2,3,4",
                "the source q1 cohomology contains both E chiralities at every n>=2",
            ],
            "witness": witness,
            "conclusion": "No SO(4,2)-equivariant unary SDR, hence no full arity-two local-to-selected-time-slice chain map, exists for the declared arbitrary-support domain and finite receiver.",
            "kind": "COHOMOLOGY_COKERNEL_AND_WEIGHT_SUPPORT_WITNESS",
        },
        "smallest_repair": {
            "carrier": "rapid-decay all-energy E/A/L Cauchy coefficient completion (and its distributional dual), tensored with the same fifteen CE ghosts and fifteen BFV/Koszul momenta",
            "required_weights": "E_n for n>=2, A_n for n>=3, L_n for n>=4, both chiralities and conjugate Cauchy data",
            "why_direct_sum_is_insufficient": "a generic smooth compactly supported source has infinitely many S3 harmonic coefficients; arbitrary-support reception requires a rapid-decay completion rather than a finite D window",
            "next_checks": [
                "construct the all-energy q1/pi_cl/iota_cl/s_cl time-slice SDR on declared Frechet/Sobolev domains",
                "serialize the action-defined q2 and verify continuity under harmonic convolution",
                "verify arity-two master identity, cyclicity, real structure and SO(4,2) equivariance",
                "only then restrict the three anomaly representatives and compute raw-D Cartan data",
            ],
        },
        "anomaly_receiver_verdicts": {
            "ANOM_OMEGA_C2": "NO_CERTIFIED_MAP",
            "ANOM_OMEGA_E4": "NO_CERTIFIED_MAP",
            "ANOM_OMEGA_C_DUAL_C": "NO_CERTIFIED_MAP",
            "raw_D_Cartan_defect": "NO_CERTIFIED_MAP",
        },
        "classification": {
            "frozen_386_to_30_causal_contraction_imported": True,
            "complete_minimal_q2_ansatz_declared": True,
            "portable_arbitrary_input_q2_component_payload_certified": False,
            "all_energy_to_selected_receiver_unary_sdr_certified": False,
            "all_energy_to_selected_receiver_unary_sdr_obstructed": True,
            "full_arity_two_time_slice_chain_map_certified": False,
            "all_energy_repair_carrier_constructed": False,
            "local_anomaly_images_computed": False,
            "raw_D_Cartan_defect_computed": False,
            "quantum_claim": False,
        },
        "claim_boundary": (
            "This exact obstruction imports the complete all-energy 386-row vacuum-cylinder causal BV contraction and the selected fifteen-generator derived BFV receiver. The frozen contraction to the 30-row field-bundle endpoint remains valid. What fails is the further SO(4,2)-equivariant SDR to the finite weights-2,3,4 receiver: the nonzero two-chirality E_5 cohomology block has dimension 64 while the target weight-five block is zero. Therefore the arbitrary-support chain map is impossible as scoped, before q2 or anomaly coefficients enter. The result does not obstruct a support-local full-BV q2 on the all-energy local carrier, an all-energy completed time-slice receiver, or later anomaly restriction after that repair. It makes no anomaly-cohomology, QME, state, particle, positivity or unitarity claim."
        ),
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.anomaly_restriction.cylinder_arbitrary_support_full_bv_q2_time_slice_obstruction --check",
            "PYTHONPATH=. python3 -m bridge.anomaly_restriction.verify_cylinder_arbitrary_support_full_bv_q2_time_slice_obstruction",
            "PYTHONPATH=. python3 -m unittest bridge.anomaly_restriction.tests.test_cylinder_arbitrary_support_full_bv_q2_time_slice_obstruction -v",
            "python3 residual_atlas/validate_fragment.py residual_atlas/cylinder-arbitrary-support-full-bv-q2-time-slice-obstruction-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any], certificate_path: Path = OUTPUT) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(PRODUCER.relative_to(ROOT)),
        "generated_by_sha256": _sha256(PRODUCER),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "pure_weyl.cylinder.full_bv.arbitrary_support.to_selected_derived_time_slice",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "OBSTRUCTED",
                    "symplectic": "NO_CERTIFIED_MAP",
                    "nonlinear": "OBSTRUCTED",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "CERTIFIED", "statement": "The source has E_n for every n>=2; the selected target stops at n=4."},
                    "lee_wald": {"status": "NO_CERTIFIED_MAP", "statement": "No full composite receiver map exists on the declared domain."},
                    "taub_maps": {"status": "CERTIFIED", "statement": "The intrinsic fifteen selected moment maps remain certified only on their selected finite carrier."},
                    "resonance": {"status": "NOT_APPLICABLE", "statement": "The chain map fails at unary cohomology before a quadratic resonance comparison."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "NO_CERTIFIED_MAP", "statement": "The E_5 rank-64 unary defect blocks transfer to this receiver before correction-class analysis."},
                        "smooth_secular": {"status": "NO_CERTIFIED_MAP", "statement": "The E_5 rank-64 unary defect blocks transfer to this receiver before correction-class analysis."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "The all-energy causal endpoint is certified, but its projection to the finite receiver is obstructed."},
                    },
                },
                "evidence": [
                    {
                        "path": str(certificate_path.relative_to(ROOT)),
                        "sha256": _sha256(certificate_path),
                        "result_id": certificate["result_id"],
                    }
                ],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.check:
        _require(OUTPUT.exists(), "certificate missing")
        _require(_load(OUTPUT) == certificate, "certificate drift")
        _require(ATLAS.exists(), "atlas fragment missing")
        _require(_load(ATLAS) == build_atlas(certificate), "atlas drift")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    atlas = build_atlas(certificate)
    ATLAS.parent.mkdir(parents=True, exist_ok=True)
    ATLAS.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
