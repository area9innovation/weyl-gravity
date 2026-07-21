#!/usr/bin/env python3
"""Classify the first residual-orbit obstruction to the minimal branch repair."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
GIT_ROOT_PREFIX = Path("physics/symplectic-reconstruction")
HERE = ROOT / "d_quotient_classical/backreacted_clock"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_HYPERBOLIC_BRANCH_REPAIR_RESIDUAL_ORBIT_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-v1.md"
ATLAS = ROOT / "residual_atlas/berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-fragment-v1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_berger_minimal_hyperbolic_branch_repair_orbit_obstruction.py"
TESTS = HERE / "tests/test_berger_minimal_hyperbolic_branch_repair_orbit_obstruction.py"

DEPENDENCIES = {
    "page_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json",
    "physical_helicity": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json",
    "principal_anchor": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1.json",
    "contractible_stf2_graph": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json",
    "retained_k_cartan": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
    "phase1_disposition": ROOT / "nonlinear/phase1/NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_hash(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value["result_id"]),
        "sha256": _sha256(path),
    }


def _validate_inputs() -> tuple[dict[str, dict], dict[str, dict[str, str]]]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    page = values["page_obstruction"]
    physical = values["physical_helicity"]
    anchor = values["principal_anchor"]
    graph = values["contractible_stf2_graph"]
    cartan = values["retained_k_cartan"]
    phase1 = values["phase1_disposition"]
    if (
        page.get("first_obstruction_class", {}).get("normalized_evaluation") != [["1", "0"]]
        or page.get("minimal_page_enlargement_classification", {}).get("standard_fibre", {}).get("minimum_cyclic_BV_rows") != 2
        or page.get("claim_flags", {}).get("GLOBAL_EQUIVARIANT_ENLARGEMENT_CONSTRUCTED") is not False
    ):
        raise ValueError("page-level rank-one repair authority drifted")
    if (
        physical.get("null_cone_chart", {}).get("projective_rank") != 2
        or physical.get("normalized_standard_null_fibre", {}).get("little_group_generator") != [[0, 2], [-2, 0]]
        or physical.get("exact_checks", {}).get("SO3_equivariance_three_generators") is not True
    ):
        raise ValueError("physical spin-two representation authority drifted")
    if anchor.get("normalized_obstruction_witness", {}).get("K_Berger_weight") != 0:
        raise ValueError("K_Berger weight authority drifted")
    if (
        graph.get("flags", {}).get("CYCLIC_GRAPH_SDR_46_TO_36") is not True
        or graph.get("carrier", {}).get("added_configuration_rows") != 5
        or graph.get("carrier", {}).get("added_cyclic_dual_rows") != 5
    ):
        raise ValueError("contractible STF2 negative control drifted")
    if (
        cartan.get("claim_status") != "CERTIFIED_COUPLED_CAUSAL_CYCLIC_K_CARTAN_THROUGH_ARITY_THREE"
        or cartan.get("generator", {}).get("symbol") != "K_Berger=D-omega R"
    ):
        raise ValueError("retained K_Berger action authority drifted")
    summary = phase1.get("terminal_summary", {})
    if (
        summary.get("exact_retained_interaction_representative") is not True
        or summary.get("interaction_survival_on_cohomology_proved") is not False
        or phase1.get("branch_and_cohomology", {}).get("einstein_extra_weyl_maxwell_branch_mixing") != "NO_CERTIFIED_MAP"
    ):
        raise ValueError("current retained-ell3 disposition drifted")
    return values, {
        name: _dependency(DEPENDENCIES[name], value) for name, value in values.items()
    }


def _stf2_representation() -> dict[str, object]:
    def symmetric(i: int, j: int) -> sp.Matrix:
        value = sp.zeros(3)
        value[i, j] = 1
        value[j, i] = 1
        return value

    basis = [
        symmetric(0, 1),
        symmetric(0, 2),
        symmetric(1, 2),
        sp.diag(1, -1, 0),
        sp.diag(1, 1, -2),
    ]
    axes = [
        sp.Matrix([[0, 0, 0], [0, 0, -1], [0, 1, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
        sp.Matrix([[0, -1, 0], [1, 0, 0], [0, 0, 0]]),
    ]
    symbols = sp.symbols("x0:5")

    def coordinates(tensor: sp.Matrix) -> sp.Matrix:
        expansion = sum((symbols[i] * basis[i] for i in range(5)), sp.zeros(3))
        solution = sp.solve(list(tensor - expansion), symbols, dict=True)[0]
        return sp.Matrix([solution[item] for item in symbols])

    generators: list[sp.Matrix] = []
    for axis in axes:
        matrix = sp.zeros(5)
        for column, tensor in enumerate(basis):
            matrix[:, column] = coordinates(axis * tensor - tensor * axis)
        generators.append(matrix)
    if any(
        generators[i] * generators[j] - generators[j] * generators[i] != generators[k]
        for i, j, k in ((0, 1, 2), (1, 2, 0), (2, 0, 1))
    ):
        raise AssertionError("STF2 generators lost the so(3) relations")
    if sum((item * item for item in generators), sp.zeros(5)) != -6 * sp.eye(5):
        raise AssertionError("STF2 Casimir is not spin two")

    plus = sp.Matrix([0, 0, 0, sp.Rational(-1, 2), sp.Rational(1, 2)])
    cross = sp.Matrix([0, 0, -1, 0, 0])
    helicity_frame = sp.Matrix.hstack(plus, cross)
    little_columns = []
    for vector in (plus, cross):
        solution = sp.linsolve((helicity_frame, generators[0] * vector))
        little_columns.append(sp.Matrix(list(solution)[0]))
    little = sp.Matrix.hstack(*little_columns)
    if little != sp.Matrix([[0, 2], [-2, 0]]):
        raise AssertionError("little-group generator disagrees with the physical certificate")

    orbit_basis = [plus]
    while True:
        old_rank = sp.Matrix.hstack(*orbit_basis).rank()
        candidates = orbit_basis + [generator * value for generator in generators for value in orbit_basis]
        new_basis: list[sp.Matrix] = []
        for value in candidates:
            if not new_basis or sp.Matrix.hstack(*new_basis, value).rank() > len(new_basis):
                new_basis.append(value)
        orbit_basis = new_basis
        if len(orbit_basis) == old_rank:
            break
    orbit_matrix = sp.Matrix.hstack(*orbit_basis)
    if orbit_matrix.rank() != 5:
        raise AssertionError("the plus obstruction does not generate the full STF2 orbit")

    variables = sp.symbols("c0:25")
    centralizer = sp.Matrix(5, 5, variables)
    equations = []
    for generator in generators:
        equations.extend(list(centralizer * generator - generator * centralizer))
    coefficient_matrix, _ = sp.linear_eq_to_matrix(equations, variables)
    commutant_dimension = 25 - coefficient_matrix.rank()
    if commutant_dimension != 1:
        raise AssertionError("STF2 equivariant zero-order coupling is not scalar")

    return {
        "basis": ["h12", "h13", "h23", "h11-h22", "h11+h22-2h33"],
        "so3_generators": [[[str(entry) for entry in row] for row in matrix.tolist()] for matrix in generators],
        "commutators": "[J_x,J_y]=J_z and cyclic permutations",
        "quadratic_Casimir": "J_x^2+J_y^2+J_z^2=-6 I_5",
        "representation": "real irreducible spin-two STF2 bundle",
        "plus_vector": [str(entry) for entry in plus],
        "cross_vector": [str(entry) for entry in cross],
        "little_group_generator": [[str(entry) for entry in row] for row in little.tolist()],
        "little_group_characteristic_polynomial": "t^2+4",
        "real_little_group_orbit_rank": int(sp.Matrix.hstack(plus, generators[0] * plus).rank()),
        "full_SO3_orbit_rank": int(orbit_matrix.rank()),
        "orbit_basis": [[str(entry) for entry in vector] for vector in orbit_basis],
        "zero_order_equivariant_endomorphism_dimension": int(commutant_dimension),
        "zero_order_equivariant_page_coupling": "a*I_STF2; normalization of beta_1 fixes a=1",
    }


def build() -> dict:
    _, dependency_refs = _validate_inputs()
    representation = _stf2_representation()
    source_manifest = {
        str(GIT_ROOT_PREFIX / path.relative_to(ROOT)): _git_blob_hash(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-v1",
        "result_id": "BERGER_MINIMAL_HYPERBOLIC_BRANCH_REPAIR_RESIDUAL_ORBIT_OBSTRUCTION_V1",
        "result_state": "TWO_ROW_PAGE_REPAIR_OBSTRUCTED_BY_REAL_RESIDUAL_ORBIT_MINIMAL_STF2_ENLARGEMENT_CLASSIFIED",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "mode_scope": {
            "theory": "Weyl gravity coupled to the positive Berger clock and Maxwell field",
            "background": "compact positive rational Berger clock fixture",
            "boundaries": "closed compact slice; support-local filtered PBW category",
            "charge_sector": "fixed gravity-clock-Maxwell bundle",
            "carrier": "retained 36-row cyclic BV complex plus a proposed noncontractible hyperbolic repair",
            "degree": "unary first filtered branch-extension page; retained ell3 is only a downstream compatibility gate",
            "parity": "real spin-two plus/cross polarization plane and its global STF2 closure",
            "ell": "NOT_APPLICABLE_LOCAL_PBW_CARRIER",
            "m": "NOT_APPLICABLE_LOCAL_PBW_CARRIER",
            "k": "standard null-symbol fibre zeta=(1,1,0,0), not compact harmonic momentum",
            "omega": "principal null characteristic; no frequency-space branch crosswalk",
        },
        "two_row_page_candidate": {
            "coefficient_field": "Q(sqrt(10))",
            "new_configuration_space": "Z=span_R{z}, degree zero",
            "new_cyclic_dual_space": "Z^vee=span_R{z^vee}, degree one",
            "odd_pairing": "omega(z,z^vee)=1 with all other new-new pairings zero",
            "page_boundary": "q1_page(z) is the normalized plus obstruction class beta_1=(1,0)",
            "page_incidence": "CERTIFIED",
            "page_cyclicity": "CERTIFIED_BY_HYPERBOLIC_COMPLETION",
            "contractible": False,
            "global_residual_equivariance": "OBSTRUCTED",
        },
        "residual_representation": {
            "K_Berger": {
                "generator": "K_Berger=D-omega R",
                "obstruction_weight": 0,
                "required_new_pair_weights": [0, 0],
                "enlargement_forced_by_K_alone": False,
            },
            "rotational_stabilizer": representation,
            "real_structure": {
                "one_real_SO2_line_exists": False,
                "reason": "the connected compact group SO(2) has only the trivial one-dimensional real representation, while t^2+4 has no real root",
                "complex_helicity_lines": ["weight +2i", "weight -2i"],
                "reality_action": "complex conjugation exchanges the two lines, so both are required",
            },
        },
        "first_later_gate_obstruction": {
            "ordered_gate": "REAL_ROTATIONAL_RESIDUAL_EQUIVARIANCE",
            "equation": "J_W q1_page - q1_page J_Z = 0",
            "rank_one_real_generator": "J_Z=0",
            "exact_defect_on_z": "J_W beta_plus=-2 beta_cross",
            "normalized_dual_functional": "(-1/2) coefficient_of(beta_cross)",
            "normalized_evaluation": "1",
            "annihilates_complete_two_row_ansatz": True,
            "consequence": "the invariant two-row hyperbolic completion does not exist in the declared real residual-equivariant category",
        },
        "minimal_residual_orbit_enlargement": {
            "standard_null_fibre": {
                "configuration_rank": 2,
                "cyclic_dual_rank": 2,
                "minimum_added_BV_rows": 4,
                "representation": "real helicity-two SO(2) plane",
            },
            "global_support_local_tensor_bundle": {
                "configuration_rank": 5,
                "cyclic_dual_rank": 5,
                "minimum_added_BV_rows": 10,
                "representation": "spatial STF2, the full SO(3) orbit closure of beta_plus in the declared finite-free tensor-row category",
                "allowed_zero_order_page_coupling": "unique up to a scalar; the normalized coupling is I_STF2",
                "required_character": "noncontractible image in the obstruction quotient",
            },
            "existing_rank46_graph_negative_control": {
                "same_row_count": 10,
                "representation": "STF2 plus cyclic dual",
                "contractible": True,
                "repairs_beta_1": False,
                "reason": "its cyclic SDR induces an isomorphism on the old obstruction quotient and contributes zero new boundary image",
            },
            "smallest_next_candidate": "a rank-46 noncontractible STF2/mixed-bundle carrier in the declared finite-free tensor-row category, distinct from the landed contractible rank-46 graph",
        },
        "ordered_compatibility_ledger": [
            {"gate": "FIRST_PAGE_CHAIN_INCIDENCE", "status": "CERTIFIED"},
            {"gate": "TYPED_HYPERBOLIC_PAIRING", "status": "CERTIFIED"},
            {"gate": "K_BERGER_WEIGHT", "status": "CERTIFIED"},
            {"gate": "REAL_ROTATIONAL_RESIDUAL_EQUIVARIANCE", "status": "OBSTRUCTED"},
            {"gate": "LATER_FILTERED_CHAIN_PAGES", "status": "NOT_ACTIVATED"},
            {"gate": "Q2_Q3_EXTENSION_TO_REPAIRED_CARRIER", "status": "NOT_ACTIVATED"},
            {"gate": "RETAINED_ELL3_COMPATIBILITY_AND_BRANCH_PROJECTION", "status": "NOT_ACTIVATED"},
        ],
        "retained_ell3_disposition": {
            "representative": "CERTIFIED_ON_PINNED_UNSPLIT_RETAINED_CARRIER",
            "complete_bounded_cyclic_class": "OPEN",
            "branch_projection": "NO_CERTIFIED_MAP",
            "reason_not_activated": "the candidate repair fails unary real residual equivariance before q2/q3 or ell3 extension equations are typed",
        },
        "dependency_refs": dependency_refs,
        "source_manifest": source_manifest,
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_minimal_hyperbolic_branch_repair_orbit_obstruction.py --check",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_minimal_hyperbolic_branch_repair_orbit_obstruction.py",
            "PYTHONPATH=. python3 -m pytest -q d_quotient_classical/backreacted_clock/tests/test_berger_minimal_hyperbolic_branch_repair_orbit_obstruction.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-fragment-v1.json",
        ],
        "claim_flags": {
            "TWO_ROW_PAGE_CHAIN_REPAIR": True,
            "TWO_ROW_TYPED_CYCLIC_COMPLETION": True,
            "TWO_ROW_REAL_RESIDUAL_EQUIVARIANT_REPAIR": False,
            "FIBREWISE_MINIMUM_FOUR_BV_ROWS": True,
            "GLOBAL_SUPPORT_LOCAL_MINIMUM_TEN_BV_ROWS": True,
            "GLOBAL_NONCONTRACTIBLE_STF2_REPAIR_CONSTRUCTED": False,
            "Q2_Q3_REPAIRED_CARRIER_EXTENSION": False,
            "ELL3_BRANCH_PROJECTION_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC obstruction proves that the rank-one first-page repair cannot be globalized as one real field direction and its cyclic dual while preserving the Berger rotational stabilizer. The plus obstruction generates the full real helicity plane at a null fibre and the full five-dimensional STF2 bundle under SO(3); cyclicity therefore forces at least four fibrewise BV rows, or ten global rows in the declared finite-free support-local tensor category without a momentum-dependent projective or mode projector. The already landed ten-row STF2 graph is contractible and is not the required repair. This result does not rule out a separately typed nonfree projective module, construct the noncontractible STF2 carrier, solve its later filtered pages, extend q2/q3, project ell3, or make causal, particle, sign, scattering, observational or quantum claims.",
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return """# Minimal hyperbolic branch repair: residual-orbit obstruction

The certified rank-one first-page branch defect can be cancelled at one
chosen null fibre by adjoining one real degree-zero direction and its cyclic
degree-one dual.  That two-row hyperbolic page completion is not a global
Berger-residual object.

In the certified plus/cross frame the rotational little-group generator is

```text
J = [[0, 2], [-2, 0]],   J^2 = -4 I.
```

The page boundary sends the proposed new field to the normalized plus class.
A one-dimensional real representation of connected `SO(2)` is trivial, so
the equivariance defect is `J beta_plus = -2 beta_cross`.  The functional
`(-1/2) coefficient_of(beta_cross)` evaluates it to one and annihilates the
complete real two-row ansatz.  Complexifying produces the two helicity lines,
but reality exchanges them and restores a two-dimensional real field space.

The exact tensor calculation gives the stronger statement in the declared
finite-free support-local tensor-row category.  In
the spatial STF2 basis `(h12,h13,h23,h11-h22,h11+h22-2h33)`, the three
rotation generators obey the `so(3)` relations, have Casimir `-6 I_5`, and
the orbit of the plus class has rank five.  Their commutant is one-dimensional,
so a zero-order equivariant page coupling is a scalar multiple of the STF2
identity; normalization fixes that scalar.  Cyclicity adds the dual STF2
bundle.  The minimum is therefore four added BV rows at one real null fibre
and ten rows for a global finite-free support-local tensor carrier.  A
separately typed nonfree projective module is outside this row-minimality
claim.

The landed rank-46 STF2 graph has the same ten-row representation content but
is contractible, so its image in the obstruction quotient is zero.  The next
candidate must instead be a noncontractible STF2 or equivalent mixed-bundle
rank-46 carrier.  Later filtered pages, q2/q3, and retained-ell3 compatibility
are not activated because the proposed two-row carrier fails the earlier
residual-equivariance gate.

EVIDENCE: d_quotient_classical/certificates/BERGER_MINIMAL_HYPERBOLIC_BRANCH_REPAIR_RESIDUAL_ORBIT_OBSTRUCTION_V1.json
CLOSE-OUT: OBSTRUCTED — the two-row page repair is not real residual-equivariant and forces a noncontractible STF2 orbit closure with ten added BV rows
"""


def _atlas(certificate: dict, certificate_sha: str) -> dict:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "nonlinear",
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "generated_by": str(Path(__file__).resolve().relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__).resolve()),
        "entries": [
            {
                "id": "nonlinear.berger.branch_repair.two_row.residual_orbit_obstruction",
                "scope": certificate["mode_scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "OBSTRUCTED",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "NOT_APPLICABLE", "statement": "This is a local filtered-symbol carrier obstruction, not a harmonic dispersion theorem."},
                    "lee_wald": {"status": "NOT_APPLICABLE", "statement": "The pairing is the typed odd BV hyperbolic completion, not a Lee-Wald radiative form."},
                    "taub_maps": {"status": "NO_CERTIFIED_MAP", "statement": "No Taub map is used in this unary carrier obstruction."},
                    "resonance": {"status": "NOT_APPLICABLE", "statement": "No second-order resonance equation is reached."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "NOT_APPLICABLE", "statement": "The candidate fails at unary residual equivariance before a second-order correction class is declared."},
                        "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "No secular correction is typed on the failed carrier."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No Green operator or retarded interaction extension is constructed."},
                    },
                },
                "evidence": [{
                    "path": str(OUTPUT.relative_to(ROOT)),
                    "result_id": certificate["result_id"],
                    "sha256": certificate_sha,
                }],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = _render(value)
    atlas = _render(_atlas(value, hashlib.sha256(rendered.encode()).hexdigest()))
    report = _report()
    if args.emit:
        OUTPUT.write_text(rendered, encoding="utf-8")
        REPORT.write_text(report, encoding="utf-8")
        ATLAS.write_text(atlas, encoding="utf-8")
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise AssertionError("branch-repair obstruction certificate drifted")
        if REPORT.read_text(encoding="utf-8") != report:
            raise AssertionError("branch-repair obstruction report drifted")
        if ATLAS.read_text(encoding="utf-8") != atlas:
            raise AssertionError("branch-repair obstruction atlas drifted")
    print("BERGER_MINIMAL_HYPERBOLIC_BRANCH_REPAIR_RESIDUAL_ORBIT_OBSTRUCTION_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
