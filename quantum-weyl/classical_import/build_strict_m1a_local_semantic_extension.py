#!/usr/bin/env python3
"""Build the M1A2 semantic extension for the 356 non-endpoint local rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_3plus1 import stf_basis, weyl_component

HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
REPORT = HERE / "REPORT_STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.md"

LOCAL = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
AUXILIARY = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
GAUGE = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
CONE = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"
HYPERBOLIC = ROOT / "covariant_completion/certificates/curved_weyl_cotton_hyperbolic.json"
THREE_PLUS_ONE = ROOT / "covariant_completion/certificates/curved_weyl_cotton_3plus1.json"

INPUTS = (
    (LOCAL, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "386-row local order and chain degree"),
    (AUXILIARY, "pure-weyl-curved-auxiliary-canonical-split-v1", "action-derived shifted auxiliary SDR"),
    (GAUGE, "CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1", "shifted internal Weyl/boost transformations"),
    (CONE, "pure-weyl-curvature-mapping-cylinder-kernel-v1", "mapping-cone degrees, incidence and operator orders"),
    (HYPERBOLIC, "pure-weyl-cotton-constraint-adjusted-hyperbolic-v1", "ordered Weyl/Cotton state and constraint equations"),
    (THREE_PLUS_ONE, "pure-weyl-cotton-3plus1-algebra-v1", "Weyl-10 and Cotton-16 geometric origins"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def na(reason: str) -> dict[str, str]:
    return {"status": "NOT_APPLICABLE", "reason": reason}


def load_inputs() -> dict[Path, dict[str, Any]]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, identity, _ in INPUTS:
        value = values[path]
        if identity not in (value.get("result_id"), value.get("schema")):
            raise ValueError(f"dependency identity drift: {path}")
    return values


AUX = {
    "AUX_ETA": ("shifted conformal-boost ghost", 0, 0, 1, 0, "covector ghost"),
    "AUX_F_HAT": ("shifted auxiliary field", 0, 0, 2, 0, "symmetric covariant tensor"),
    "AUX_V": ("Stueckelberg connection field", 0, 0, 1, 0, "covector"),
    "AUX_F_HAT_STAR": ("shifted auxiliary antifield", 1, 4, 2, 0, "symmetric contravariant tensor density"),
    "AUX_V_STAR": ("Stueckelberg connection antifield", 1, 4, 3, 0, "contravariant vector density"),
    "AUX_ETA_STAR": ("shifted boost-ghost antifield", 2, 4, 3, 0, "contravariant vector density"),
}

CONE_BLOCKS = {
    "CONE_X_U": ("X", "U", False),
    "CONE_X_EQ": ("X", "Eq", False),
    "CONE_X_ID": ("X", "Id", False),
    "CONE_Y_U": ("Y", "U", False),
    "CONE_Y_EQ": ("Y", "Eq", False),
    "CONE_Y_ID": ("Y", "Id", False),
    "CONE_X_ID_SHARP": ("X", "Id", True),
    "CONE_X_EQ_SHARP": ("X", "Eq", True),
    "CONE_X_U_SHARP": ("X", "U", True),
    "CONE_Y_ID_SHARP": ("Y", "Id", True),
    "CONE_Y_EQ_SHARP": ("Y", "Eq", True),
    "CONE_Y_U_SHARP": ("Y", "U", True),
}


def primal_component(family: str, index: int) -> tuple[str, int]:
    if family == "U":
        if index < 5:
            return "electric Weyl STF", 2
        if index < 10:
            return "magnetic Weyl STF", 2
        if index < 15:
            return "Cotton X symmetric tracefree", 3
        if index < 18:
            return "Cotton X antisymmetric vector", 3
        if index < 23:
            return "Cotton Y symmetric tracefree", 3
        if index < 26:
            return "Cotton Y antisymmetric vector", 3
    elif family == "Eq":
        if index < 5:
            return "electric Weyl evolution residual", 3
        if index < 10:
            return "magnetic Weyl evolution residual", 3
        if index < 15:
            return "Cotton A evolution residual", 4
        if index < 20:
            return "Cotton C evolution residual", 4
        if index < 23:
            return "Cotton x evolution residual", 4
        if index < 26:
            return "Cotton y evolution residual", 4
        if index < 29:
            return "q constraint", 3
        if index < 32:
            return "r constraint", 3
        if index < 35:
            return "a constraint", 4
        if index < 38:
            return "c constraint", 4
        if index == 38:
            return "s constraint", 4
        if index == 39:
            return "t constraint", 4
    elif family == "Id":
        if index < 3:
            return "q subsidiary identity", 4
        if index < 6:
            return "r subsidiary identity", 4
        if index < 9:
            return "a subsidiary identity", 5
        if index < 12:
            return "c subsidiary identity", 5
        if index == 12:
            return "s subsidiary identity", 5
        if index == 13:
            return "t subsidiary identity", 5
    raise ValueError(f"uncovered {family}[{index}]")


def cotton_non_eigen_witness() -> dict[str, Any]:
    """Check delta(nabla^d W_adbc)=omega^p W_apbc in four dimensions."""

    metric = sp.diag(-1, 1, 1, 1)
    basis = stf_basis()
    checks = defects = nonzero_mixing = 0
    for weyl_basis_index in range(10):
        electric = basis[weyl_basis_index] if weyl_basis_index < 5 else sp.zeros(3)
        magnetic = basis[weyl_basis_index - 5] if weyl_basis_index >= 5 else sp.zeros(3)

        def W(a: int, d: int, b: int, c: int) -> sp.Expr:
            return weyl_component(electric, magnetic, a, d, b, c)

        for omega_index in range(4):
            omega_down = [sp.Integer(int(axis == omega_index)) for axis in range(4)]
            omega_up = [sum(metric[p, q] * omega_down[q] for q in range(4)) for p in range(4)]

            def connection(p: int, e: int, a: int) -> sp.Expr:
                return (
                    int(p == e) * omega_down[a]
                    + int(p == a) * omega_down[e]
                    - metric[e, a] * omega_up[p]
                )

            for a in range(4):
                for b in range(4):
                    for c in range(4):
                        variation = sp.Integer(0)
                        for d in range(4):
                            for e in range(4):
                                if metric[d, e] == 0:
                                    continue
                                term = 2 * omega_down[e] * W(a, d, b, c)
                                term -= sum(connection(p, e, a) * W(p, d, b, c) for p in range(4))
                                term -= sum(connection(p, e, d) * W(a, p, b, c) for p in range(4))
                                term -= sum(connection(p, e, b) * W(a, d, p, c) for p in range(4))
                                term -= sum(connection(p, e, c) * W(a, d, b, p) for p in range(4))
                                variation += metric[d, e] * term
                        expected = sum(omega_up[p] * W(a, p, b, c) for p in range(4))
                        checks += 1
                        defects += int(sp.expand(variation - expected) != 0)
                        nonzero_mixing += int(expected != 0)
    if defects or not nonzero_mixing:
        raise ValueError("Cotton nonlinear Weyl-mixing witness failed")
    return {
        "coordinate_convention": "W_abcd all lowered and V_abc=nabla^d W_adbc",
        "infinitesimal_formula_in_dimension_four": "delta_omega V_abc=omega^p W_apbc",
        "constant_scale_homogeneous_weights": {"W_abcd": 2, "V_abc": 0},
        "component_checks": checks,
        "defects": defects,
        "nonzero_mixing_checks": nonzero_mixing,
        "conclusion": "Cotton rows are not nonlinear Weyl eigenrows; changing to an orthonormal frame changes homogeneous terms but does not remove the gradient-omega times Weyl mixing.",
    }


def local_semantics(row: dict[str, Any]) -> dict[str, Any]:
    degree = row["degree"]
    common = {
        "index": row["index"],
        "row_id": row["row_id"],
        "block": row["block"],
        "chain_degree": degree,
        "bv_ghost_number": -degree,
        "Grassmann_parity": degree % 2,
        "conformal_compact_weight": na("local component row, not a compact conformal eigenspace"),
        "ce_ghost_number": na("local BV coordinate, not a residual CE cochain"),
        "intrinsic_jet_order_bound": 0,
    }
    if row["block"] in AUX:
        role, afn, form, mass, weight, tensor = AUX[row["block"]]
        common.update(
            role=role,
            tensor_type=tensor,
            antifield_number=afn,
            form_degree=form,
            mass_dimension=mass,
            Weyl_weight=weight,
            semantic_state="FULLY_NAMESPACED",
            authority={
                "row": f"{LOCAL.relative_to(ROOT)}#/component_basis/rows/{row['index']}",
                "action_split": f"{AUXILIARY.relative_to(ROOT)}#/factorized_curved_Q_split",
                "gauge_manifest": f"{GAUGE.relative_to(ROOT)}#/shifted_BRST_manifest",
            },
        )
        return common

    copy_name, family, sharp = CONE_BLOCKS[row["block"]]
    component, primal_mass = primal_component(family, row["local_index"])
    mass = 4 - primal_mass if sharp else primal_mass
    role = f"contractible mapping-cone {copy_name}-copy {family} {'cotangent-dual' if sharp else 'primal'} row"
    common.update(
        role=role,
        tensor_type=component + (" formal density dual" if sharp else " component"),
        antifield_number=max(degree, 0),
        form_degree=4 if degree > 0 else 0,
        mass_dimension=mass,
        Weyl_weight=na(
            "fixed-background mapping-cone coordinate, not a nonlinear Weyl eigenfield; the Cotton sector transforms triangularly by delta V_abc=omega^p W_apbc"
        ),
        semantic_state="FULLY_NAMESPACED_NONLINEAR_SCALAR_WEYL_WEIGHT_NOT_APPLICABLE",
        mapping_cone={"copy": copy_name, "curvature_family": family, "cotangent_dual": sharp},
        authority={
            "row": f"{LOCAL.relative_to(ROOT)}#/component_basis/rows/{row['index']}",
            "degree_and_incidence": f"{CONE.relative_to(ROOT)}#/complete_16_block_degree_ledger",
            "geometric_basis": f"{THREE_PLUS_ONE.relative_to(ROOT)}",
            "evolution_and_constraints": f"{HYPERBOLIC.relative_to(ROOT)}",
        },
    )
    return common


def build() -> dict[str, Any]:
    values = load_inputs()
    local_rows = values[LOCAL]["component_basis"]["rows"]
    if len(local_rows) != 386 or [row["index"] for row in local_rows] != list(range(386)):
        raise ValueError("local row order drift")
    rows = [local_semantics(row) for row in local_rows[30:]]
    if len(rows) != 356 or sum(row["semantic_state"] == "FULLY_NAMESPACED" for row in rows) != 36:
        raise ValueError("M1A2 coverage drift")

    # The action density and qv=-eta determine the auxiliary dimensions,
    # independently of the literature labels.
    dimension_equations = [
        {"equation": "2 dim(f_hat)=4", "solution": {"f_hat": 2}},
        {"equation": "2(dim(v)+1)=4 from F(v)^2", "solution": {"v": 1}},
        {"equation": "dim(eta)=dim(v) from qv=-eta and dim(q)=0", "solution": {"eta": 1}},
        {"equation": "dim(z)+dim(z_star)=4", "solution": {"f_hat_star": 2, "v_star": 3, "eta_star": 3}},
    ]
    cone_dimensions = {
        "U": {"dimension_2": 10, "dimension_3": 16},
        "Eq": {"dimension_3": 16, "dimension_4": 24},
        "Id": {"dimension_4": 6, "dimension_5": 8},
        "cotangent_rule": "dim(z_sharp)=4-dim(z)",
        "X_and_Y_copies_share_engineering_dimension": True,
        "unit_cylinder_lower_terms": "powers of inverse cylinder radius carry the missing engineering dimension",
    }
    counts = {
        "extension_rows": 356,
        "auxiliary_rows_fully_namespaced": 36,
        "mapping_cone_rows_fully_namespaced": 320,
        "mapping_cone_rows_with_not_applicable_scalar_Weyl_weight": 320,
        "rows_with_unresolved_fields": 0,
        "local_386_rows_fully_namespaced_after_this_result": 386,
        "local_386_rows_remaining_partial": 0,
    }
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-m1a-local-semantic-extension-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-m1a-local-semantic-extension-v1.schema.json",
        "result_id": "STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1",
        "result_kind": "M1A2_LOCAL_AUXILIARY_AND_MAPPING_CONE_SEMANTIC_EXTENSION",
        "result_state": "ALL_356_NAMESPACED_FIXED_BACKGROUND_CONE_SCALAR_WEYL_WEIGHT_NOT_APPLICABLE",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "f8709e9bee7e72b48a17b45f2b8666e97980029f",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Which M1A semantics of the 356 non-endpoint local rows are forced by the action and mapping-cylinder sources, and what remains genuinely unspecified?",
        "answer": "All 36 shifted auxiliary rows and all 320 contractible mapping-cone rows are fully namespaced. A scalar nonlinear Weyl weight is explicitly not applicable to the fixed-background cone coordinates: the Cotton/divergence-of-Weyl slot has the exact triangular law delta V_abc=omega^p W_apbc in four dimensions. M1A2 is complete; M1A remains open at the represented-carrier crosswalk M1A3.",
        "scope": {
            "theory": "strict pure-Weyl local linear BV graph on the unit conformal cylinder",
            "arithmetic": "exact integer gradings and finite component partitions",
            "primary_source": "R. R. Metsaev, arXiv:0707.4437v3, equations 5.21 and 6.2-6.7",
            "primary_source_pdf_sha256": "80bbe298159e4fdfc35c0f4dd4e33f01e5da51227184a0bed870e5fa3e6b2676",
        },
        "counts": counts,
        "auxiliary_dimension_derivation": dimension_equations,
        "mapping_cone_dimension_functor": cone_dimensions,
        "cotton_nonlinear_weyl_non_eigen_witness": cotton_non_eigen_witness(),
        "operator_order_bounds": {
            "curvature_E_and_N": 1,
            "cone_identity": 0,
            "T_state": 3,
            "A_equation": 2,
            "B_identity": 0,
            "formal_adjoints_match_primal_orders": True,
        },
        "scalar_weyl_weight_applicability": {
            "affected_rows": 320,
            "classification": "NOT_APPLICABLE",
            "not_unknown": True,
            "reason": "These are contractible fixed-background resolution coordinates rather than nonlinear conformal-covariant generator eigenrows, and their Cotton sector has a non-diagonal Weyl action.",
            "future_nonlinear_upgrade_test": "Replace scalar weights by a filtered Weyl-action matrix, including frame/index and cylinder-radius transformations, and verify that it intertwines every curvature and cotangent-cone arrow.",
        },
        "local_extension_rows": rows,
        "foundational_strength": {
            "logic": "primitive-recursive finite scans and exact integer equations",
            "choice_used": False,
            "excluded_middle_used": "decidable finite equality only",
            "analysis_used": False,
        },
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "identity": identity, "sha256": sha(path), "role": role}
                for path, identity, role in INPUTS
            ],
            "producer": str(Path(__file__).resolve().relative_to(ROOT)),
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_m1a_local_semantic_extension.py",
            "method": "Rebuild all 356 row semantics from independent block tables, re-solve the auxiliary dimensions, repartition U/Eq/Id, independently verify the 2,560-component Cotton non-eigen formula, and reject any scalar-weight substitution or gate promotion.",
            "expected_digest": "",
        },
        "claim_flags": {
            "M1A2_AUXILIARY_36_FULLY_NAMESPACED": True,
            "M1A2_MAPPING_CONE_320_FULLY_NAMESPACED": True,
            "M1A2_SCALAR_WEYL_WEIGHT_APPLICABILITY_CLASSIFIED": True,
            "LOCAL_386_FULLY_TYPED": True,
            "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": False,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "a nonlinear filtered Weyl-action representation on the 320 fixed-background mapping-cone rows",
            "a completed represented-carrier M1A ledger",
            "the M1B represented composite contraction",
            "the M1C common manifest replay or a passed classical import gate",
            "a full-complex Hadamard state, renormalized products, QME restoration or residual transfer",
        ],
        "next_gate": "Construct M1A3: crosswalk the 4,080 represented endpoint coordinates, explicitly exclude or source the 410 scalar test-nonminimal coordinates, and type the 470+470 action-residual carrier without promoting the formal 8,980-coordinate comparison.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.md",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    c = value["counts"]
    return f"""# M1A local semantic extension

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

**Lifecycle:** `CLASSIFIED`; M1A and Gate A remain fail closed.

## Result

The action and shifted BRST source fully determine all
{c['auxiliary_rows_fully_namespaced']} generalized-auxiliary rows.  The
mapping-cylinder sources also determine chain degree, BV ghost number,
antifield filtration, form degree, parity, geometric role, engineering
dimension and intrinsic jet status for all
{c['mapping_cone_rows_fully_namespaced']} contractible cone rows.

Scalar nonlinear Weyl weight is explicitly `NOT_APPLICABLE` to those 320
fixed-background resolution rows.  This is not an unknown value: the exact
four-dimensional law is `delta V_abc=omega^p W_apbc`, so the Cotton slot is
not a Weyl eigenrow.  An orthonormal-frame change alters homogeneous terms but
does not remove this triangular mixing.

This raises fully namespaced local coverage from 30 to
{c['local_386_rows_fully_namespaced_after_this_result']} of 386 rows and
reduces the partial local set to {c['local_386_rows_remaining_partial']}.

## Exact engineering filtration

The four-dimensional action gives `dim(f_hat)=2`, `dim(v)=dim(eta)=1`, and
cotangent dimensions `2`, `3`, `3`.  For the curvature complex, the geometric
origin gives Weyl-10 dimension two and Cotton-16 dimension three.  Evolution,
constraint and subsidiary rows then have the displayed dimensions three
through five; lower unit-cylinder terms carry the corresponding inverse-radius
powers.  Cotangent rows obey `dim(z_sharp)=4-dim(z)`.

## Next construction

M1A2 is complete.  M1A3 must now crosswalk the 4,080 represented endpoint
coordinates, separate the 410 scalar test-nonminimal coordinates, and type the
470 primal plus 470 action-dual residual rows.  A future nonlinear cone would
need a filtered Weyl-action matrix rather than scalar row weights.

## Boundary

This result does not complete M1A, M1B or M1C and does not pass Gate A.  It
constructs no full-complex Hadamard state, renormalized product, QME or
residual quantum transfer.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    outputs = {
        RESULT: json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        REPORT: report(value),
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text() != content]
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1: generated artifacts current")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print("STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
