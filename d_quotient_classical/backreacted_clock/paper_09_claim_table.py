#!/usr/bin/env python3
"""Build the fail-closed Paper IX claim-to-certificate table."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_DIR = ROOT / "d_quotient_classical/certificates"
OUTPUT = CERTIFICATE_DIR / "PAPER_09_BERGER_CLAIM_TABLE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/paper-09-berger-claim-table-v1.schema.json"
MAIN_PAPER = ROOT / "paper/09-relational-clocks-berger-d-cartan.tex"
SUPPLEMENT = ROOT / "paper/09-relational-clocks-berger-d-cartan-computational-supplement.tex"


CLAIMS = (
    {
        "claim_id": "P09-C1",
        "paper_sections": ["2"],
        "claim": "An exact smooth non-conformally-flat positive Berger clock family exists.",
        "certificate": "POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "required_true": ["flags.exact_backreacted_background_exists"],
        "required_false": [],
    },
    {
        "claim_id": "P09-C2",
        "paper_sections": ["2"],
        "claim": "The clock has standard-sign matter, timelike phase and positive bounded-below quartic potential.",
        "certificate": "POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "required_true": [
            "flags.positive_standard_scalar_kinetic",
            "flags.everywhere_timelike_phase_clock",
            "flags.bounded_below_quartic",
        ],
        "required_false": ["flags.quantum_admissibility_proved"],
    },
    {
        "claim_id": "P09-C3",
        "paper_sections": ["3"],
        "claim": "The internal clock charge is nonzero and Omega_total(delta,L_D)=omega delta Q_R.",
        "certificate": "BERGER_CLOCK_REDUCED_CHARGE_SEED.json",
        "required_true": [
            "flags.covariant_internal_current_derived",
            "flags.global_internal_charge_computed",
            "flags.helical_presymplectic_identity_derived",
        ],
        "required_false": ["flags.total_covariant_D_charge_computed"],
    },
    {
        "claim_id": "P09-C4",
        "paper_sections": ["3"],
        "claim": "At fixed couplings delta Q_R vanishes on every smooth allowed linearized tangent, so D is gauge in the declared compact phase space.",
        "certificate": "BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
        "required_true": [
            "flags.homogeneous_lapse_constraint_exact",
            "flags.full_mode_average_argument_exact",
            "flags.total_helical_presymplectic_contraction_zero",
            "flags.scoped_D_verdict_promoted",
        ],
        "required_false": ["flags.nonlinear_stability_proved"],
    },
    {
        "claim_id": "P09-C5",
        "paper_sections": ["5"],
        "claim": "The complete 54-row gauge-fixed unary BV complex has a cyclic support-local contraction onto 26 retained rows.",
        "certificate": "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "required_true": [
            "flags.BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT",
            "flags.BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM",
            "flags.BERGER_NONMINIMAL_COMPLETION",
        ],
        "required_false": ["flags.BERGER_HADAMARD_DATA"],
    },
    {
        "claim_id": "P09-C6",
        "paper_sections": ["5"],
        "claim": "The complete 54-row complex has D-equivariant advanced and retarded chain contractions with causal support and adjointness.",
        "certificate": "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
        "required_true": [
            "flags.BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
            "flags.BERGER_CAUSAL_GREEN_HOMOTOPY_V2",
            "exact_checks.advanced_chain_homotopy_identity",
            "exact_checks.retarded_chain_homotopy_identity",
            "exact_checks.D_equivariance",
            "exact_checks.cyclic_advanced_retarded_adjointness",
        ],
        "required_false": ["flags.BERGER_HADAMARD_DATA"],
    },
    {
        "claim_id": "P09-C7",
        "paper_sections": ["6"],
        "claim": "The complete arbitrary-input support-local q2 satisfies the arity-two L-infinity identity, cyclicity and D derivation.",
        "certificate": "BERGER_SUPPORT_LOCAL_Q2.json",
        "required_true": [
            "flags.CLASSICAL_SUPPORT_LOCAL_Q2",
            "flags.BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_TWO",
            "exact_checks.q1_q2_arity_two_nilpotency_raw_coefficientwise",
            "exact_checks.BV_cyclicity_q2_coefficientwise_and_by_canonical_transport",
        ],
        "required_false": ["flags.GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT"],
    },
    {
        "claim_id": "P09-C8",
        "paper_sections": ["6"],
        "claim": "The complete arbitrary-input support-local q3 satisfies the arity-three L-infinity identity, quartic cyclicity and D derivation with L_D3=0.",
        "certificate": "BERGER_SUPPORT_LOCAL_Q3.json",
        "required_true": [
            "flags.CLASSICAL_SUPPORT_LOCAL_Q3",
            "flags.BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_THREE",
            "exact_checks.q1_q3_plus_q2_q2_arity_three_nilpotency_raw_coefficientwise",
            "exact_checks.quartic_action_cyclicity_raw_coefficientwise",
            "local_D_arity_three.D_q3_derivation",
        ],
        "required_false": ["flags.GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT"],
    },
    {
        "claim_id": "P09-C9",
        "paper_sections": ["7"],
        "claim": "The complete 54-row classical complex has a cyclic causal D-Cartan contraction through arity two.",
        "certificate": "BERGER_CAUSAL_D_CARTAN_V2.json",
        "required_true": [
            "flags.BERGER_CAUSAL_D_CARTAN_V2",
            "flags.BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED",
            "flags.BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION",
        ],
        "required_false": ["flags.BERGER_HADAMARD_DATA", "flags.QUANTUM_CLAIM"],
    },
    {
        "claim_id": "P09-C10",
        "paper_sections": ["7"],
        "claim": "The complete 54-row arbitrary-input arity-three Cartan source is closed and has a cyclic two-sided-causal primitive.",
        "certificate": "BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json",
        "required_true": [
            "flags.BERGER_ARITY_THREE_D_CARTAN_SOURCE_CLOSED",
            "flags.BERGER_ARITY_THREE_D_CARTAN_CYCLIC_COMPLETION",
            "flags.BERGER_ARITY_THREE_D_CARTAN_FULL_4D",
            "flags.BERGER_CAUSAL_D_CARTAN_THROUGH_ARITY_THREE",
        ],
        "required_false": ["flags.BERGER_HADAMARD_DATA", "flags.QUANTUM_CLAIM"],
    },
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _lookup(payload: dict[str, object], dotted: str) -> object:
    cursor: object = payload
    for part in dotted.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            raise AssertionError(f"missing certificate field: {dotted}")
        cursor = cursor[part]
    return cursor


def build() -> dict[str, object]:
    claims: list[dict[str, object]] = []
    for spec in CLAIMS:
        path = CERTIFICATE_DIR / str(spec["certificate"])
        payload = _read(path)
        for dotted in spec["required_true"]:
            if _lookup(payload, dotted) is not True:
                raise AssertionError(f"{spec['claim_id']}: required true field failed: {dotted}")
        for dotted in spec["required_false"]:
            if _lookup(payload, dotted) is not False:
                raise AssertionError(f"{spec['claim_id']}: required false field failed: {dotted}")
        claims.append(
            {
                **spec,
                "certificate_path": str(path.relative_to(ROOT)),
                "certificate_result_id": payload["result_id"],
                "certificate_sha256": _sha256(path),
                "certificate_claim_boundary": payload["claim_boundary"],
            }
        )
    return {
        "schema": "pure-weyl-paper-09-berger-claim-table-v1",
        "result_id": "PAPER_09_BERGER_CLAIM_TABLE",
        "paper_state": "WRITING_STARTED",
        "theorem_frozen": False,
        "paper_sources": {
            str(MAIN_PAPER.relative_to(ROOT)): _sha256(MAIN_PAPER),
            str(SUPPLEMENT.relative_to(ROOT)): _sha256(SUPPLEMENT),
        },
        "setting": "compact positive Berger clock; fixed couplings; smooth classical phase space; BV Taylor order through arity three",
        "claims": claims,
        "claim_ids_complete": [spec["claim_id"] for spec in CLAIMS],
        "required_signoffs": {
            "classical_team": "DRAFTED",
            "nonlinear_team": "PENDING_ARITY_THREE_INTERPRETATION_REVIEW",
            "quantum_team": "PENDING_CLAIM_BOUNDARY_REVIEW",
            "einstein_team": "OPTIONAL_INTERNAL_REFEREE",
        },
        "forbidden_promotions": [
            "all-orders nonlinear D-Cartan",
            "Hadamard state",
            "quantum master equation",
            "anomaly cancellation",
            "positive graviton Hilbert space",
            "boundary or asymptotic charge theorem",
        ],
        "next_gate": "PAPER_09_NONLINEAR_SIGNOFF_AND_CLEAN_TREE_REPLAY",
        "claim_boundary": "This table binds the working Paper IX draft to ten scoped classical Berger certificates. It does not freeze the theorem or promote any quantum, all-orders, Hadamard, boundary, scattering, or unitarity claim.",
    }


def verify(payload: dict[str, object]) -> None:
    if payload["theorem_frozen"] is not False or payload["paper_state"] != "WRITING_STARTED":
        raise AssertionError("draft was prematurely frozen")
    expected = [spec["claim_id"] for spec in CLAIMS]
    if payload["claim_ids_complete"] != expected:
        raise AssertionError("claim-id ledger is incomplete or reordered")
    if [entry["claim_id"] for entry in payload["claims"]] != expected:
        raise AssertionError("claim entries are incomplete or reordered")
    main = MAIN_PAPER.read_text()
    supplement = SUPPLEMENT.read_text()
    for claim_id in expected:
        if claim_id not in main or claim_id not in supplement:
            raise AssertionError(f"claim id is absent from a paper source: {claim_id}")
    if payload["required_signoffs"]["nonlinear_team"] != "PENDING_ARITY_THREE_INTERPRETATION_REVIEW":
        raise AssertionError("nonlinear sign-off was promoted")
    for entry in payload["claims"]:
        path = ROOT / entry["certificate_path"]
        if _sha256(path) != entry["certificate_sha256"]:
            raise AssertionError(f"certificate hash drifted: {entry['claim_id']}")
        certificate = _read(path)
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"{entry['claim_id']}: required true flag drifted")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"{entry['claim_id']}: forbidden promotion detected")


def _text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        OUTPUT.write_text(_text(payload))
    if args.check and OUTPUT.read_text() != _text(payload):
        raise AssertionError("Paper IX claim table drifted")
    if args.guards:
        mutants = (
            ("freeze early", ("theorem_frozen",), True),
            (
                "forge nonlinear signoff",
                ("required_signoffs", "nonlinear_team"),
                "APPROVED",
            ),
            ("drop claim", ("claim_ids_complete",), payload["claim_ids_complete"][:-1]),
        )
        for name, path, value in mutants:
            mutant = deepcopy(payload)
            cursor = mutant
            for part in path[:-1]:
                cursor = cursor[part]
            cursor[path[-1]] = value
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("PAPER_09_BERGER_CLAIM_TABLE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
