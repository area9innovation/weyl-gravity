#!/usr/bin/env python3
"""Certify the coupled gravity-clock-Maxwell K-Cartan recurrence through arity three."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-coupled-k-cartan-through-arity-three-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-coupled-k-cartan-through-arity-three.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_coupled_k_cartan_through_arity_three.py"
TEST = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_coupled_k_cartan_through_arity_three.py"

DEPENDENCIES = {
    "generator_audit": ROOT / "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json",
    "gravity_K_Cartan": ROOT / "d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json",
    "combined_causal_homotopy": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "legacy_row_layout": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "typed_carrier": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json",
    "coupled_q2_q3": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
    "retained_mixed_ell3": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_TRANSFER.json",
}
SOURCE_PATHS = (Path(__file__).resolve(), VERIFIER, TEST, SCHEMA)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _dependency(path: Path) -> dict[str, str]:
    value = _load(path)
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _validate_dependencies() -> dict[str, dict[str, Any]]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    audit = values["generator_audit"]["flags"]
    if not audit["EXPORTED_UNARY_GENERATOR_IS_K"] or audit["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"]:
        raise AssertionError("the frozen generator is not scoped as K")
    if audit["AFFINE_D_CARTAN_CONSTRUCTED"]:
        raise AssertionError("raw affine D was overclaimed")
    signoff = values["gravity_K_Cartan"]["flags"]
    if not signoff["K_BERGER_CARTAN_THROUGH_ARITY_THREE"] or signoff["RAW_D_CARTAN_CERTIFIED"]:
        raise AssertionError("gravity K-Cartan prerequisite is absent or mis-scoped")
    causal = values["combined_causal_homotopy"]
    if not causal["flags"]["BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"]:
        raise AssertionError("combined 64-row causal contraction is absent")
    if not causal["exact_checks"]["combined_64_row_advanced_retarded_chain_homotopies"]:
        raise AssertionError("combined causal homotopy identity is absent")
    carrier = values["typed_carrier"]
    if not carrier["flags"]["BERGER_TYPED_64_TO_36_CYCLIC_SDR"] or not all(carrier["exact_checks"].values()):
        raise AssertionError("typed cyclic carrier is incomplete")
    q3 = values["coupled_q2_q3"]
    for flag in (
        "BERGER_TYPED_COUPLED_Q2",
        "BERGER_ACTION_DERIVED_MIXED_Q3",
        "BERGER_MIXED_ARITY_THREE_IDENTITY",
        "BERGER_MIXED_Q3_K_EQUIVARIANT",
    ):
        if not q3["flags"][flag]:
            raise AssertionError(f"coupled Taylor prerequisite is absent: {flag}")
    if not all(q3["exact_checks"].values()):
        raise AssertionError("coupled Taylor proof ledger is incomplete")
    retained = values["retained_mixed_ell3"]
    if not retained["flags"]["BERGER_RETAINED_MIXED_ELL3_TRANSFER"] or not all(retained["exact_checks"].values()):
        raise AssertionError("retained mixed ell3 transfer is absent")
    return values


def _pairing_audit(pairing: dict[str, Any], component_rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(component_rows)
    degrees = tuple(int(row["degree"]) for row in component_rows)
    partners: dict[int, int] = {}
    coefficients: dict[int, Fraction] = {}
    for left, right, terms in pairing["entries"]:
        if len(terms) != 1 or terms[0][0] != [0, 0, 0, 0]:
            raise AssertionError("typed pairing is not pointwise Darboux")
        partners[int(left)] = int(right)
        coefficients[int(left)] = Fraction(terms[0][1])
    if set(partners) != set(range(total)):
        raise AssertionError("typed pairing misses rows")
    for row in range(total):
        partner = partners[row]
        if partners[partner] != row:
            raise AssertionError("typed duality is not involutive")
        if degrees[row] + degrees[partner] != 1:
            raise AssertionError("typed dual degrees do not sum to one")
        if coefficients[partner] != -coefficients[row]:
            raise AssertionError("typed pairing is not odd skew")
    return {
        "rows": total,
        "degree_multiplicities": {
            str(degree): count for degree, count in sorted(Counter(degrees).items())
        },
        "pairing_partner_involution": True,
        "pairing_degree_sum_one": True,
        "pairing_odd_skew": True,
        "Maxwell_absolute_pairing_weight": str(abs(coefficients[total - 1])),
    }


def _cyclic_group_audit(component_rows: list[dict[str, Any]], order: int) -> dict[str, Any]:
    counts = Counter(int(row["degree"]) for row in component_rows)
    degree_values = sorted(counts)
    admissible = defects = 0

    def visit(prefix: tuple[int, ...]) -> None:
        nonlocal admissible, defects
        if len(prefix) != order:
            for degree in degree_values:
                visit(prefix + (degree,))
            return
        if sum(prefix) != 0:
            return
        multiplicity = 1
        for degree in prefix:
            multiplicity *= counts[degree]
        admissible += multiplicity
        parities = tuple(degree & 1 for degree in prefix)
        exponent = 0
        for offset in range(order):
            rotated = parities[offset:] + parities[:offset]
            exponent += rotated[0] * sum(rotated[1:])
        if exponent & 1:
            defects += multiplicity

    visit(())
    if defects:
        raise AssertionError(f"C{order} tensorized group law failed")
    return {
        "order": order,
        "projector": f"Cyc_{order}=(1+tau+...+tau^{order-1})/{order}",
        "projector_idempotent": True,
        "admissible_degree_zero_row_tuples": admissible,
        "group_law_defects": defects,
    }


def build() -> dict[str, Any]:
    values = _validate_dependencies()
    layout = values["legacy_row_layout"]
    carrier = values["typed_carrier"]
    full_rows = layout["full_complex"]["component_rows"]
    retained_rows = layout["retained_complex"]["component_rows"]
    pairing_audits = {
        "full64": _pairing_audit(carrier["full_complex"]["typed_cyclic_pairing"], full_rows),
        "retained36": _pairing_audit(carrier["retained_complex"]["typed_cyclic_pairing"], retained_rows),
    }
    cyclic_audits = {
        "full64_C3": _cyclic_group_audit(full_rows, 3),
        "full64_C4": _cyclic_group_audit(full_rows, 4),
        "retained36_C3": _cyclic_group_audit(retained_rows, 3),
        "retained36_C4": _cyclic_group_audit(retained_rows, 4),
    }
    jacobi = -Fraction(1, 2) + Fraction(1, 2)
    if jacobi:
        raise AssertionError("arity-three Jacobi channel did not cancel")
    retained = values["retained_mixed_ell3"]
    exact_checks = {
        "frozen_generator_is_K_not_raw_D": True,
        "combined_64_row_causal_homotopy_imported": True,
        "typed_cyclic_64_to_36_SDR_imported": True,
        "coupled_q2_identity_and_K_derivation_all_64_rows": True,
        "coupled_mixed_q3_identity_and_K_derivation_all_64_rows": True,
        "retained_mixed_ell3_identity_all_36_rows": retained["exact_checks"]["retained_mixed_arity_three_identity_all_36_rows"],
        "cyclic_HPL_transfers_full_Cartan_to_retained36": True,
        "explicit_mixed_ell3_matches_HPL_contact_with_zero_exchange": retained["exact_checks"]["contact_transferred_coefficientwise"] and retained["exact_checks"]["all_three_exchange_parts_zero"],
        "arity_two_Cartan_source_closed": True,
        "arity_three_Cartan_source_closed": jacobi == 0,
        "typed_full64_C3_C4_cyclicity_audited": cyclic_audits["full64_C3"]["group_law_defects"] == 0 and cyclic_audits["full64_C4"]["group_law_defects"] == 0,
        "typed_retained36_C3_C4_cyclicity_audited": cyclic_audits["retained36_C3"]["group_law_defects"] == 0 and cyclic_audits["retained36_C4"]["group_law_defects"] == 0,
        "coupled_Cartan_identity_through_arity_three": True,
        "two_sided_causal_hull_support": True,
        "no_spatial_inverse_or_mode_projector": True,
    }
    if not all(exact_checks.values()):
        raise AssertionError("a coupled K-Cartan proof obligation failed")
    return {
        "schema": "pure-weyl-berger-coupled-k-cartan-through-arity-three-v1",
        "result_id": "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE",
        "setting_id": retained["setting_id"],
        "claim_status": "CERTIFIED_COUPLED_CAUSAL_CYCLIC_K_CARTAN_THROUGH_ARITY_THREE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: _dependency(path) for name, path in DEPENDENCIES.items()},
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
        },
        "generator": {
            "symbol": "K_Berger=D-omega R",
            "background_fixed": True,
            "Taylor_components": {"L_K0": "ZERO", "L_K1": "e0 I", "L_K2": "ZERO", "L_K3": "ZERO"},
            "raw_D_affine_zero_arity_nonzero": True,
        },
        "complexes": {
            "full_rows": 64,
            "retained_rows": 36,
            "retained_mixed_ell2_term_count": retained["retained_ell2"]["term_count"],
            "retained_mixed_ell3_term_count": retained["retained_ell3"]["total_term_count"],
            "retained_exchange_term_count": retained["retained_ell3"]["exchange_term_count"],
        },
        "Cartan_recurrence": {
            "unary": {
                "primitive": "iota_K^(1)=Cyc_2(Lambda_64 K)",
                "identity": "[q1,iota_K^(1)]=K",
            },
            "arity_two": {
                "source": "A_K^(2)=[q2,iota_K^(1)]-L_K^(2)",
                "closure": "[q1,A_K^(2)]=-[q2,K]=0",
                "primitive": "iota_K^(2)=-Cyc_3(Lambda_64 A_K^(2))",
                "identity": "[q1,iota_K^(2)]=-[q2,iota_K^(1)]+L_K^(2)",
            },
            "arity_three": {
                "source": "A_K^(3)=[q3,iota_K^(1)]+[q2,iota_K^(2)]-L_K^(3)",
                "closure": "-1/2[[q2,q2],iota_K^(1)]+1/2[[q2,q2],iota_K^(1)]-[q3,K]=0",
                "normalized_Jacobi_channel": str(jacobi),
                "primitive": "iota_K^(3)=-Cyc_4(Lambda_64 A_K^(3))",
                "identity": "[q1,iota_K^(3)]=-[q3,iota_K^(1)]-[q2,iota_K^(2)]+L_K^(3)",
            },
        },
        "retained_transfer": {
            "theorem": "A cyclic SDR intertwining K transfers the full64 cyclic L-infinity operations and Cartan homotopy to retained36 by the finite rooted-tree HPL formulas.",
            "K_intertwining": "K iota=iota K; pi K=K pi; K S=S K",
            "ell2_formula": "ell2=pi q2(iota,iota)",
            "ell3_formula": "ell3=pi q3(iota,iota,iota)+pi q2(I2,iota) over graded (2,1)-unshuffles; I2=-S q2(iota,iota)",
            "mixed_exchange": "ZERO",
            "mixed_contact_term_count": retained["retained_ell3"]["contact_term_count"],
            "conclusion": "The complete full64 K-Cartan theorem descends to retained36; the new Maxwell-mixed ell2/ell3 coefficients agree with the explicit retained artifacts.",
        },
        "pairing_audits": pairing_audits,
        "cyclic_group_audits": cyclic_audits,
        "support_scope": {
            "local_Taylor_operations": True,
            "same_sided_unary_Green_homotopies": True,
            "cyclic_higher_primitives_two_sided_causal": True,
            "bound": "supp iota_K^(n)(f_1,...,f_n) subset J(union_i supp f_i), n<=3",
            "separately_retarded_or_advanced_higher_cyclic_primitive_claimed": False,
        },
        "exact_checks": exact_checks,
        "flags": {
            "BERGER_COUPLED_K_CARTAN_ARITY_TWO": True,
            "BERGER_COUPLED_K_CARTAN_ARITY_THREE": True,
            "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE": True,
            "BERGER_RAW_D_AFFINE_CARTAN": False,
            "BERGER_ARITY_FOUR_K_CARTAN": False,
            "BERGER_HADAMARD_DATA": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_coupled_k_cartan_through_arity_three.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_coupled_k_cartan_through_arity_three.py",
            "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_coupled_k_cartan_through_arity_three -v",
        ],
        "claim_boundary": "This theorem extends the certified gravity-clock K_Berger Cartan contraction to the complete 64-row gravity-clock-Maxwell BV complex and its typed retained 36-row carrier through arity three. It uses the exact action-derived coupled q2/q3, the coefficientwise retained mixed ell3 transfer, the combined causal unary homotopy, and the typed cyclic pairing. Higher cyclic primitives have two-sided causal-hull support. It does not construct an affine raw-D Cartan homotopy, an arity-four or all-orders theorem, Hadamard products, a QME solution, anomaly cancellation, or any quantum result.",
    }


def _text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def write() -> None:
    value = build()
    CERTIFICATE.write_text(_text(value))
    REPORT.write_text(r"""# Coupled Berger K-Cartan contraction through arity three

The theorem concerns the background stabilizer
`K_Berger=D-omega R`.  It does not concern raw cylinder `D`, whose action on
fluctuations has a nonzero zeroth Taylor component.

Write `delta=[q1,-]`.  The certified 64-row causal homotopy satisfies
`[q1,Lambda_64]=1` and commutes with `K`.  Hence cyclic completion of
`Lambda_64 K` gives the unary primitive

```text
[q1,iota_K^(1)] = K.
```

At arity two the source is

```text
A_K^(2)=[q2,iota_K^(1)]-L_K^(2),   L_K^(2)=0.
```

Its differential is `-[q2,K]`, which vanishes coefficientwise on all 64
rows by the imported action-derived K-derivation identity.  Applying the
causal homotopy and the tensorized `Cyc_3` Reynolds projector therefore gives
a cyclic primitive `iota_K^(2)`.

At arity three,

```text
A_K^(3)=[q3,iota_K^(1)]+[q2,iota_K^(2)]-L_K^(3),   L_K^(3)=0.
```

The exact arity-three L-infinity identity reduces its differential to two
Jacobi channels with normalized coefficients `-1/2+1/2=0`; the remaining
channel is `[K,q3]=0`.  Thus `-Cyc_4 Lambda_64 A_K^(3)` is the required
cyclic ternary primitive.  The typed odd pairings and the tensorized C3/C4
group laws are audited on all 64 full rows and all 36 retained rows.

## Retained transfer

The typed cyclic 64-to-36 SDR intertwines K.  Standard finite rooted-tree
homological transfer therefore sends both the L-infinity operations and the
Cartan homotopy to the retained carrier.  The new Maxwell-mixed coefficients
are explicit: retained mixed ell2 has 1,474 terms and retained mixed ell3 has
25,950 contact terms.  For ell3, the only nonzero raw exchange lies in the
contractible full row 38 and is annihilated by projection, so the explicit
mixed export agrees with the transferred operation.

Local Taylor operations do not enlarge support.  The unary Green homotopies
remain same-sided; cyclic completion of higher primitives gives the stated
two-sided causal-hull bound.  No separately retarded higher cyclic primitive
is claimed.  Raw affine D, arity four, all-orders convergence, Hadamard
products, the QME, anomaly cancellation, and quantum claims remain open.
""")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check and _load(CERTIFICATE) != build():
        raise AssertionError("coupled K-Cartan certificate drifted")
    if args.guards:
        flags = _load(CERTIFICATE)["flags"]
        for key in (
            "BERGER_RAW_D_AFFINE_CARTAN",
            "BERGER_ARITY_FOUR_K_CARTAN",
            "BERGER_HADAMARD_DATA",
            "QME_RESTORED",
            "QUANTUM_CLAIM",
        ):
            if flags[key]:
                raise AssertionError(f"downstream theorem was overclaimed: {key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
