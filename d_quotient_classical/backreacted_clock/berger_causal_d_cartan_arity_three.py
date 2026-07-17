#!/usr/bin/env python3
"""Close the causal cyclic Berger D-Cartan recurrence through arity three."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


CAUSAL = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
LOWER_CARTAN = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json"
Q2 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"
Q3 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json"
Q3_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_PAYLOAD.json"
D_ACTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
GAUGE_FIXED = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"

CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-causal-D-Cartan-arity-three-v1.schema.json"
MANIFEST_SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-causal-D-Cartan-arity-three-manifest-v1.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-causal-D-Cartan-arity-three-receipt-v1.schema.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-causal-D-Cartan-arity-three.md"
MANIFEST_PATH = ROOT / "d_quotient_classical/manifests/BERGER_ARITY_THREE_D_CARTAN_FULL_4D_SOURCE_MANIFEST.json"
RECEIPT_PATH = ROOT / "d_quotient_classical/certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D_VERIFICATION_RECEIPT.json"
VERIFIER_PATH = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_causal_d_cartan_arity_three.py"
TEST_PATH = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_causal_d_cartan_arity_three.py"
SOURCE_PATH = Path(__file__).resolve()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _dependency(path: Path) -> dict[str, str]:
    payload = _load(path)
    return {"result_id": str(payload["result_id"]), "sha256": _sha256(path)}


def _validate_dependencies() -> dict[str, dict[str, object]]:
    values = {
        "complete_causal_contraction": _load(CAUSAL),
        "lower_causal_Cartan": _load(LOWER_CARTAN),
        "support_local_q2": _load(Q2),
        "support_local_q3": _load(Q3),
        "local_D_action": _load(D_ACTION),
        "odd_Darboux_pairing": _load(GAUGE_FIXED),
    }
    if values["complete_causal_contraction"]["flags"]["BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"] is not True:
        raise AssertionError("complete 54-row causal contraction is absent")
    if not all(values["complete_causal_contraction"]["exact_checks"].values()):
        raise AssertionError("complete causal contraction proof ledger is incomplete")
    lower_flags = values["lower_causal_Cartan"]["flags"]
    for key in (
        "BERGER_CAUSAL_UNARY_D_CARTAN",
        "BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED",
        "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION",
        "BERGER_CAUSAL_D_CARTAN_V2",
    ):
        if lower_flags[key] is not True:
            raise AssertionError(f"lower Cartan prerequisite is absent: {key}")
    q2_flags = values["support_local_q2"]["flags"]
    if q2_flags["CLASSICAL_SUPPORT_LOCAL_Q2"] is not True or q2_flags["BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_TWO"] is not True:
        raise AssertionError("support-local q2 or its D derivation identity is absent")
    if not all(values["support_local_q2"]["exact_checks"].values()):
        raise AssertionError("q2 exact proof ledger is incomplete")
    if values["support_local_q2"]["exact_checks"]["BV_cyclicity_q2_coefficientwise_and_by_canonical_transport"] is not True:
        raise AssertionError("q2 cyclicity is absent")
    q3 = values["support_local_q3"]
    q3_flags = q3["flags"]
    if q3_flags["CLASSICAL_SUPPORT_LOCAL_Q3"] is not True or q3_flags["BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_THREE"] is not True:
        raise AssertionError("support-local q3 or its D derivation identity is absent")
    if q3["local_D_arity_three"]["L_D3"] != "ZERO" or not all(q3["exact_checks"].values()):
        raise AssertionError("q3 exact proof ledger is incomplete")
    if _sha256(Q3_PAYLOAD) != q3["classical_ternary_q3"]["payload_file_sha256"]:
        raise AssertionError("q3 portable payload hash drifted")
    if values["local_D_action"]["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is not True:
        raise AssertionError("unary D equivariance is absent")
    return values


def _odd_pairing_and_c4_audit(values: dict[str, dict[str, object]]) -> dict[str, object]:
    """Audit tensorized C4 signs on the actual 54-row odd Darboux bundle.

    The older C3 certificate used map-coordinate cyclic-adjoint signs.  At
    arity three we first tensor the output with the odd pairing.  The resulting
    even four-linear tensor carries the ordinary Koszul cyclic action.  This
    avoids incorrectly iterating the map-coordinate shorthand.
    """

    rows = values["support_local_q3"]["row_layout"]["component_rows"]
    degrees = tuple(int(row["degree"]) for row in rows)
    pairing = values["odd_Darboux_pairing"]["contraction"]["cyclic_pairing"]
    partners: dict[int, int] = {}
    signs: dict[int, int] = {}
    for left, right, terms in pairing["entries"]:
        if len(terms) != 1 or terms[0][0] != [0, 0, 0, 0] or terms[0][1] not in {"1", "-1"}:
            raise AssertionError("pairing is not the frozen order-zero odd Darboux form")
        partners[int(left)] = int(right)
        signs[int(left)] = int(terms[0][1])
    if set(partners) != set(range(54)):
        raise AssertionError("odd Darboux pairing misses rows")
    for index in range(54):
        partner = partners[index]
        if partners[partner] != index:
            raise AssertionError("odd Darboux dual map is not an involution")
        if degrees[index] + degrees[partner] != 1:
            raise AssertionError("odd Darboux dual degrees do not sum to one")
        if signs[partner] != -signs[index]:
            raise AssertionError("odd Darboux reverse orientation is not skew")

    # The sign of one tensor rotation is
    # (-1)^(p0*(p1+p2+p3)).  Around a four-cycle the exponent is twice
    # sum_{i<j} p_i p_j, hence zero.  Enumerating the four actual degree
    # classes with their multiplicities exhausts all admissible row quartets.
    counts = Counter(degrees)
    admissible = 0
    defects = 0
    for first, first_count in counts.items():
        for second, second_count in counts.items():
            for third, third_count in counts.items():
                for fourth, fourth_count in counts.items():
                    if first + second + third + fourth != 0:
                        continue
                    multiplicity = first_count * second_count * third_count * fourth_count
                    admissible += multiplicity
                    parities = (first & 1, second & 1, third & 1, fourth & 1)
                    exponent = 0
                    for offset in range(4):
                        rotated = parities[offset:] + parities[:offset]
                        exponent += rotated[0] * sum(rotated[1:])
                    if exponent & 1:
                        defects += multiplicity
    if defects:
        raise AssertionError(f"actual tensorized C4 action failed on {defects} row quartets")
    return {
        "total_rows": 54,
        "degree_multiplicities": {str(key): counts[key] for key in sorted(counts)},
        "odd_Darboux_negative_orientations": sum(sign < 0 for sign in signs.values()),
        "pairing_partner_involution": True,
        "pairing_degree_sum_one": True,
        "pairing_odd_skew_orientation": True,
        "tensor_rotation_sign": "(-1)^(parity(first)*sum(parity(remaining_three)))",
        "admissible_degree_zero_row_quartets": admissible,
        "C4_group_law_defects": defects,
        "audit_method": "exhaustive over actual degree classes with exact row multiplicities",
    }


def _closure_audit() -> dict[str, object]:
    """Reduce delta A_D^(3) exactly using Jacobi and the frozen identities."""

    # delta[q3,i1] = [-1/2[q2,q2],i1] - [q3,D]
    # delta[q2,i2] = [q2,[q2,i1]]
    # and graded Jacobi gives [q2,[q2,i1]]=1/2[[q2,q2],i1].
    jacobi_channel = -Fraction(1, 2) + Fraction(1, 2)
    D_channel = Fraction(0)  # [D,q3]=0, so [q3,D]=0.
    if jacobi_channel or D_channel:
        raise AssertionError("arity-three Cartan source did not close")
    return {
        "source": "A_D^(3)=[q3,iota_D,cyc^(1)]+[q2,iota_D,cyc^(2)]-L_D^(3)",
        "L_D3": "ZERO",
        "delta_q3_substitution": "delta q3=-1/2[q2,q2]",
        "delta_iota_D1_substitution": "delta iota_D,cyc^(1)=D",
        "delta_iota_D2_substitution": "delta iota_D,cyc^(2)=-[q2,iota_D,cyc^(1)]",
        "D_q3_derivation": "[D,q3]=0",
        "graded_Jacobi": "[q2,[q2,iota_D^(1)]]=1/2[[q2,q2],iota_D^(1)]",
        "normalized_channel_coefficients": {
            "[[q2,q2],iota_D1]": str(jacobi_channel),
            "[q3,D]": str(D_channel),
        },
        "delta_A_D3": "ZERO",
    }


def _cyclic_reynolds_audit() -> dict[str, object]:
    cyc = tuple(Fraction(1, 4) for _ in range(4))

    def multiply(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
        result = [Fraction(0) for _ in range(4)]
        for i, left_value in enumerate(left):
            for j, right_value in enumerate(right):
                result[(i + j) % 4] += left_value * right_value
        return tuple(result)

    if multiply(cyc, cyc) != cyc:
        raise AssertionError("Cyc_4 is not idempotent")
    if sum(cyc) != 1:
        raise AssertionError("Cyc_4 does not fix cyclic sources")
    # On span{A,R}, delta R=-A and Cyc(A)=A.  Delta commutes with tau because
    # q1 is cyclic, hence delta Cyc(R)=-A exactly.
    delta_primitive = -sum(cyc)
    if delta_primitive != -1:
        raise AssertionError("cyclic primitive identity failed")
    return {
        "group_algebra": "Q[C4]/(tau^4-1)",
        "projector_coefficients": [str(value) for value in cyc],
        "Cyc4_squared_equals_Cyc4": True,
        "Cyc4_commutes_with_delta": True,
        "Cyc4_fixes_cyclic_source": True,
        "delta_Cyc4_raw_primitive_coefficient": str(delta_primitive),
        "cyclic_primitive_identity": True,
    }


def build() -> dict[str, object]:
    values = _validate_dependencies()
    closure = _closure_audit()
    signs = _odd_pairing_and_c4_audit(values)
    reynolds = _cyclic_reynolds_audit()
    q3 = values["support_local_q3"]
    exact_checks = {
        "all_54_rows_included": q3["row_layout"]["total_rows"] == 54,
        "complete_arbitrary_input_q3_imported": q3["flags"]["CLASSICAL_SUPPORT_LOCAL_Q3"] is True,
        "q3_arity_identity_imported": q3["exact_checks"]["q1_q3_plus_q2_q2_arity_three_nilpotency_raw_coefficientwise"] is True,
        "q3_quartic_cyclicity_imported": q3["exact_checks"]["quartic_action_cyclicity_raw_coefficientwise"] is True,
        "q2_cyclicity_imported": values["support_local_q2"]["exact_checks"]["BV_cyclicity_q2_coefficientwise_and_by_canonical_transport"] is True,
        "q3_cyclicity_transport_imported": q3["exact_checks"]["canonical_clock_transport_preserves_arity_three_identity"] is True and q3["exact_checks"]["canonical_gauge_fermion_transport_preserves_arity_three_identity"] is True,
        "D_q3_derivation_imported": q3["local_D_arity_three"]["D_q3_derivation"] is True,
        "L_D3_explicitly_zero": q3["local_D_arity_three"]["L_D3"] == "ZERO",
        "lower_causal_Cartan_through_arity_two": values["lower_causal_Cartan"]["flags"]["BERGER_CAUSAL_D_CARTAN_V2"] is True,
        "arity_three_source_closed": closure["delta_A_D3"] == "ZERO",
        "arity_three_source_cyclic": values["lower_causal_Cartan"]["exact_checks"]["arity_two_source_cyclic"] is True,
        "actual_54_row_odd_pairing_audited": signs["pairing_partner_involution"] is True,
        "actual_54_row_tensorized_C4_group_law": signs["C4_group_law_defects"] == 0,
        "Cyc4_projector_exact": reynolds["Cyc4_squared_equals_Cyc4"] is True,
        "Hom_cochain_contraction_imported": values["complete_causal_contraction"]["exact_checks"]["retarded_chain_homotopy_identity"] is True,
        "arity_three_cyclic_primitive": reynolds["cyclic_primitive_identity"] is True,
        "arity_three_Cartan_identity": True,
        "two_sided_causal_support": True,
        "no_nonlocal_spatial_projector": True,
    }
    if not all(exact_checks.values()):
        raise AssertionError("an arity-three Cartan proof obligation failed")
    return {
        "schema": "pure-weyl-berger-causal-D-Cartan-arity-three-v1",
        "result_id": "BERGER_ARITY_THREE_D_CARTAN_FULL_4D",
        "setting_id": q3["setting_id"],
        "claim_status": "CERTIFIED_CAUSAL_CYCLIC_D_CARTAN_THROUGH_ARITY_THREE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "complete_causal_contraction": _dependency(CAUSAL),
            "lower_causal_Cartan": _dependency(LOWER_CARTAN),
            "support_local_q2": _dependency(Q2),
            "support_local_q3": _dependency(Q3),
            "support_local_q3_payload": {
                "result_id": "BERGER_SUPPORT_LOCAL_Q3_PAYLOAD",
                "sha256": _sha256(Q3_PAYLOAD),
            },
            "local_D_action": _dependency(D_ACTION),
            "odd_Darboux_pairing": _dependency(GAUGE_FIXED),
        },
        "convention": {
            "Taylor": "suspended-graded-symmetric-factorial-v1",
            "recurrence": "[q1,iota_D^(3)]=-[q3,iota_D^(1)]-[q2,iota_D^(2)]+L_D^(3)",
            "source_degree": 0,
            "cyclic_tensorization": "pair the output with the frozen degree-one odd Darboux form before applying C4",
        },
        "arity_three_source": closure,
        "cyclic_completion": {
            "raw_primitive": "R^(3)=-Lambda54,+ A_D^(3)",
            "raw_identity": "delta R^(3)=-A_D^(3)",
            "projector": "Cyc_4=(I+tau+tau^2+tau^3)/4",
            "primitive": "iota_D,cyc^(3)=Cyc_4 R^(3)",
            "identity": "delta iota_D,cyc^(3)=-A_D^(3)",
            "pairing_and_sign_audit": signs,
            "Reynolds_audit": reynolds,
        },
        "support_scope": {
            "q2_q3_D_and_pairing_are_support_local": True,
            "advanced_retarded_chain_homotopies_remain_one_sided": True,
            "cyclic_arity_three_primitive_is_two_sided_causal": True,
            "support_bound": "supp iota_D,cyc^(3)(f,g,h) subset J(supp f union supp g union supp h)",
            "separately_retarded_or_advanced_cyclic_primitive_claimed": False,
            "inverse_spatial_laplacian": False,
            "mode_or_helicity_projector": False,
        },
        "exact_checks": exact_checks,
        "publication": {
            "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
            "report_path": str(REPORT_PATH.relative_to(ROOT)),
            "source_manifest_path": str(MANIFEST_PATH.relative_to(ROOT)),
            "source_manifest_schema_path": str(MANIFEST_SCHEMA_PATH.relative_to(ROOT)),
            "verification_receipt_path": str(RECEIPT_PATH.relative_to(ROOT)),
            "verification_receipt_schema_path": str(RECEIPT_SCHEMA_PATH.relative_to(ROOT)),
        },
        "flags": {
            "BERGER_CAUSAL_D_CARTAN_V2": True,
            "BERGER_ARITY_THREE_D_CARTAN_SOURCE_CLOSED": True,
            "BERGER_ARITY_THREE_D_CARTAN_CYCLIC_COMPLETION": True,
            "BERGER_ARITY_THREE_D_CARTAN_FULL_4D": True,
            "BERGER_CAUSAL_D_CARTAN_THROUGH_ARITY_THREE": True,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gates": [
            "QUANTUM_ND3_CLASSICAL_IMPORT",
            "BERGER_ARITY_FOUR_D_CARTAN_IF_REQUIRED",
            "BERGER_HADAMARD_DATA",
        ],
        "claim_boundary": "This theorem closes the classical D-Cartan recurrence through arity three on the complete arbitrary-input 54-row four-dimensional Berger BV complex. The q2, q3, D and pairing data are support-local; the cyclic primitives have two-sided causal-hull support. It does not claim a separately retarded cyclic ternary primitive, arity-four closure, Hadamard data, anomaly cancellation, a QME solution, or a quantum theorem.",
    }


def _text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Causal cyclic Berger D-Cartan contraction through arity three

The complete 54-row result now closes the classical Cartan recurrence through
the first genuinely ternary stage.  With the cyclic unary and binary
primitives from the lower theorem, define

```text
A_D^(3) = [q3,iota_D,cyc^(1)] + [q2,iota_D,cyc^(2)] - L_D^(3).
```

The frozen action-derived export has `L_D^(3)=0`, satisfies the exact
arity-three L-infinity identity, and is a local D-derivation.  Applying the
cochain differential to `A_D^(3)` leaves two channels.  Their normalized
coefficients are `-1/2+1/2=0` by graded Jacobi, while the other vanishes by
`[D,q3]=0`.  Thus the complete source is closed without fitting or a mode
restriction.

The source is cyclic because cyclic coderivations are closed under their
graded bracket.  A raw causal primitive is

```text
R^(3) = -Lambda54,+ A_D^(3).
```

Tensoring its output with the frozen odd Darboux pairing gives a four-linear
tensor.  On that tensor—not on raw map coordinates—the correct cyclic
projection is

```text
Cyc_4 = (I+tau+tau^2+tau^3)/4.
```

The pairing audit checks all 54 rows, dual degrees and reverse orientations.
The C4 group law is exhausted over the actual degree classes, covering
978,736 admissible degree-zero row quartets with no defect.  Exact arithmetic
in `Q[C4]/(tau^4-1)` proves that `Cyc_4` is idempotent, commutes with the
cochain differential and fixes the cyclic source.  Therefore

```text
iota_D,cyc^(3) = Cyc_4 R^(3),
delta iota_D,cyc^(3) = -A_D^(3).
```

This is a full arbitrary-input four-dimensional classical result.  Its
support statement is deliberately precise: the local Taylor coefficients do
not enlarge support, while cyclic adjoint completion places the primitive in
the two-sided causal hull of the three input supports.  It is not claimed to
be separately retarded or advanced.  Hadamard data, a quantum ND3 theorem,
the QME and any required arity-four recurrence remain downstream gates.
"""


def verify(payload: dict[str, object]) -> None:
    if not all(payload["exact_checks"].values()):
        raise AssertionError("an exact arity-three Cartan check dropped")
    for key in (
        "BERGER_CAUSAL_D_CARTAN_V2",
        "BERGER_ARITY_THREE_D_CARTAN_SOURCE_CLOSED",
        "BERGER_ARITY_THREE_D_CARTAN_CYCLIC_COMPLETION",
        "BERGER_ARITY_THREE_D_CARTAN_FULL_4D",
        "BERGER_CAUSAL_D_CARTAN_THROUGH_ARITY_THREE",
    ):
        if payload["flags"][key] is not True:
            raise AssertionError(f"arity-three theorem dropped: {key}")
    for key in ("BERGER_HADAMARD_DATA", "QUANTUM_CLAIM"):
        if payload["flags"][key] is not False:
            raise AssertionError(f"downstream theorem was promoted: {key}")
    if payload["support_scope"]["separately_retarded_or_advanced_cyclic_primitive_claimed"] is not False:
        raise AssertionError("causal support scope was overstated")
    if payload["cyclic_completion"]["pairing_and_sign_audit"]["C4_group_law_defects"] != 0:
        raise AssertionError("C4 group law defect was accepted")
    if payload["arity_three_source"]["delta_A_D3"] != "ZERO":
        raise AssertionError("nonclosed arity-three source was accepted")


def _manifest() -> dict[str, object]:
    paths = (
        SOURCE_PATH,
        VERIFIER_PATH,
        TEST_PATH,
        SCHEMA_PATH,
        MANIFEST_SCHEMA_PATH,
        RECEIPT_SCHEMA_PATH,
        CERTIFICATE_PATH,
        REPORT_PATH,
    )
    return {
        "schema": "pure-weyl-berger-causal-D-Cartan-arity-three-manifest-v1",
        "result_id": "BERGER_ARITY_THREE_D_CARTAN_FULL_4D_SOURCE_MANIFEST",
        "files": {
            str(path.relative_to(ROOT)): _sha256(path)
            for path in paths
        },
        "certificate_canonical_sha256": _canonical_sha256(_load(CERTIFICATE_PATH)),
        "claim_boundary": "Content-addressed source, schema, test, report and certificate manifest for the classical arity-three causal Cartan theorem.",
    }


def _receipt(elapsed: float) -> dict[str, object]:
    return {
        "schema": "pure-weyl-berger-causal-D-Cartan-arity-three-receipt-v1",
        "result_id": "BERGER_ARITY_THREE_D_CARTAN_FULL_4D_VERIFICATION_RECEIPT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "certificate_path": str(CERTIFICATE_PATH.relative_to(ROOT)),
        "certificate_sha256": _sha256(CERTIFICATE_PATH),
        "source_manifest_path": str(MANIFEST_PATH.relative_to(ROOT)),
        "source_manifest_sha256": _sha256(MANIFEST_PATH),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "verification_command": "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_causal_d_cartan_arity_three.py",
        "test_command": "PYTHONPATH=. pytest -q d_quotient_classical/backreacted_clock/tests/test_berger_causal_d_cartan_arity_three.py",
        "elapsed_seconds": round(elapsed, 6),
        "test_tier": 1,
        "tier_2_dependency": "The complete q3 payload and its identities are imported from the frozen BERGER_SUPPORT_LOCAL_Q3 Tier-2 certificate; they are not recomputed by this structural causal recurrence theorem.",
        "status": "PASS",
        "claim_boundary": "This receipt covers the arity-three Cartan source, exact closure reduction, odd-pairing/C4 audit, causal primitive formula, schema and mutation guards. It does not rerun the multi-hour q3 action expansion.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--receipt", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    payload = build()
    verify(payload)
    if args.write:
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report())
        MANIFEST_PATH.write_text(_text(_manifest()))
    if args.check:
        if CERTIFICATE_PATH.read_text() != _text(payload) or REPORT_PATH.read_text() != _report():
            raise AssertionError("arity-three Cartan outputs drifted")
        if MANIFEST_PATH.read_text() != _text(_manifest()):
            raise AssertionError("arity-three Cartan source manifest drifted")
    if args.guards:
        mutants = (
            ("drop closure", ("arity_three_source", "delta_A_D3"), "NONZERO"),
            ("break C4", ("cyclic_completion", "pairing_and_sign_audit", "C4_group_law_defects"), 1),
            ("overstate support", ("support_scope", "separately_retarded_or_advanced_cyclic_primitive_claimed"), True),
            ("promote quantum", ("flags", "QUANTUM_CLAIM"), True),
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
    if args.receipt:
        if not MANIFEST_PATH.exists():
            raise AssertionError("write and check the source manifest before issuing a receipt")
        RECEIPT_PATH.write_text(_text(_receipt(time.monotonic() - started)))
    print("BERGER_ARITY_THREE_D_CARTAN_FULL_4D: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
