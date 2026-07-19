#!/usr/bin/env python3
"""Build the support-local de Rham carrier for the five relative currents."""

from __future__ import annotations

import argparse
from itertools import combinations
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-five-current-de-rham-carrier.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-five-current-de-rham-carrier-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_five_current_de_rham_carrier.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_five_current_de_rham_carrier.py"
GENERATED = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json"

DEPENDENCIES = {
    "cyclic_current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CYCLIC_FIVE_CURRENT_CONE_V1.json",
    "global_charge_replay": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_GLOBAL_FIVE_CHARGE_REPLAY_V1.json",
    "current_cofiber_assembly": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CURRENT_COFIBER_ASSEMBLY_V1.json",
    "candidate13_category_obstruction": ROOT / "d_quotient_classical/certificates/CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1.json",
    "candidate13_derived_source": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1.json",
}

GENERATORS = ("H", "P_x", "J_1", "J_2", "J_3")
COORDINATES = ("t", "x", "theta", "phi")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def basis(p: int) -> list[tuple[int, ...]]:
    return list(combinations(range(4), p))


def permutation_sign(word: tuple[int, ...]) -> int:
    if len(set(word)) != len(word):
        return 0
    inversions = sum(word[i] > word[j] for i in range(len(word)) for j in range(i + 1, len(word)))
    return -1 if inversions % 2 else 1


def exterior_symbol(p: int, zeta: tuple[sp.Symbol, ...]) -> sp.Matrix:
    source, target = basis(p), basis(p + 1)
    matrix = sp.zeros(len(target), len(source))
    target_index = {item: index for index, item in enumerate(target)}
    for column, form in enumerate(source):
        for mu, coefficient in enumerate(zeta):
            if mu in form:
                continue
            raw = (mu,) + form
            ordered = tuple(sorted(raw))
            matrix[target_index[ordered], column] += permutation_sign(raw) * coefficient
    return matrix


def wedge_pairing(p: int) -> sp.Matrix:
    left, right = basis(p), basis(4 - p)
    matrix = sp.zeros(len(left), len(right))
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            matrix[i, j] = permutation_sign(a + b)
    return matrix


def symbol_checks() -> dict[str, Any]:
    zeta = sp.symbols("zeta_0:4")
    d = [exterior_symbol(p, zeta) for p in range(4)]
    square_zero = [d[p + 1] * d[p] == sp.zeros(d[p + 1].rows, d[p].cols) for p in range(3)]
    stokes = []
    for p in range(4):
        # Formal adjunction reverses the derivative covector: d(-zeta)=-d(zeta).
        defect = d[p].T * wedge_pairing(p + 1) + ((-1) ** (p + 1)) * wedge_pairing(p) * d[3 - p]
        stokes.append(defect == sp.zeros(defect.rows, defect.cols))
    fixture = {zeta[i]: value for i, value in enumerate((1, 2, 3, 5))}
    ranks = [int(matrix.subs(fixture).rank()) for matrix in d]
    exactness = []
    dimensions = [1, 4, 6, 4, 1]
    for p in range(5):
        incoming = 0 if p == 0 else ranks[p - 1]
        outgoing = 0 if p == 4 else ranks[p]
        exactness.append(incoming + outgoing == dimensions[p])
    if not all(square_zero + stokes + exactness) or ranks != [1, 3, 3, 1]:
        raise AssertionError("four-dimensional exterior-symbol fixture failed")
    return {
        "symbol_variables": [str(item) for item in zeta],
        "generic_fixture": [1, 2, 3, 5],
        "generic_ranks_d0_to_d3": ranks,
        "d_squared_zero": square_zero,
        "stokes_matrix_identities": stokes,
        "nonzero_covector_koszul_exactness": exactness,
        "stokes_identity": "d_p(zeta)^T W_(p+1)+(-1)^p W_p d_(3-p)(-zeta)=0",
    }


def _component(form: tuple[int, ...]) -> str:
    return "scalar" if not form else "_".join(COORDINATES[index] for index in form)


def row_layout() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # P_p is the shifted primal de Rham chain, degree p-2.
    # D_p is its cotangent chain, degree p-1.  P_p pairs with D_(4-p).
    for degree in range(-2, 4):
        for generator in GENERATORS:
            primal_p = degree + 2
            if 0 <= primal_p <= 4:
                for form in basis(primal_p):
                    rows.append({
                        "index": len(rows), "generator": generator, "chain": "primal",
                        "form_degree": primal_p, "basis_indices": list(form), "component": _component(form),
                        "degree": degree, "row_id": f"P_{generator}_{primal_p}_{_component(form)}",
                    })
            dual_p = degree + 1
            if 0 <= dual_p <= 4:
                for form in basis(dual_p):
                    rows.append({
                        "index": len(rows), "generator": generator, "chain": "cotangent",
                        "form_degree": dual_p, "basis_indices": list(form), "component": _component(form),
                        "degree": degree, "row_id": f"D_{generator}_{dual_p}_{_component(form)}",
                    })
    lookup = {(row["generator"], row["chain"], row["form_degree"], row["component"]): row["index"] for row in rows}
    for row in rows:
        other_chain = "cotangent" if row["chain"] == "primal" else "primal"
        form = tuple(row["basis_indices"])
        complement = tuple(index for index in range(4) if index not in form)
        complement_component = _component(complement)
        row["dual_row"] = lookup[(row["generator"], other_chain, 4 - row["form_degree"], complement_component)]
    for row in rows:
        if row["chain"] == "primal":
            paired = rows[row["dual_row"]]
            row["pairing_coefficient"] = permutation_sign(tuple(row["basis_indices"]) + tuple(paired["basis_indices"]))
    for row in rows:
        if row["chain"] == "cotangent":
            row["pairing_coefficient"] = -rows[row["dual_row"]]["pairing_coefficient"]
    return rows


def unary_terms(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup = {(row["generator"], row["chain"], tuple(row["basis_indices"])): row["index"] for row in rows}
    terms: list[dict[str, Any]] = []
    for generator in GENERATORS:
        for chain in ("primal", "cotangent"):
            for p in range(4):
                for form in basis(p):
                    source = lookup[(generator, chain, form)]
                    for mu in range(4):
                        if mu in form:
                            continue
                        raw = (mu,) + form
                        target_form = tuple(sorted(raw))
                        terms.append({
                            "generator": generator,
                            "chain": chain,
                            "source_row": source,
                            "target_row": lookup[(generator, chain, target_form)],
                            "derivative": COORDINATES[mu],
                            "coefficient": permutation_sign(raw),
                        })
    if len(terms) != 320:
        raise AssertionError("de Rham unary incidence count changed")
    return terms


def embedding(rows: list[dict[str, Any]]) -> dict[str, Any]:
    current_rows = _load(ROOT / "d_quotient_classical/generated/einstein_weyl_relative_cyclic_five_current_cone_v1/layout.json")["row_layout"]
    index = {(row["generator"], row["chain"], row["form_degree"], row["component"]): row["index"] for row in rows}
    records = []
    for old in current_rows:
        parts = old["row_id"].split("_")
        if old["row_id"].startswith("rho_div_"):
            generator, chain, p, component, coefficient = old["row_id"][8:], "cotangent", 0, "scalar", 1
        elif old["row_id"].startswith("rho_current_"):
            generator, component = old["row_id"][12:].rsplit("_", 1)
            chain, p, coefficient = "cotangent", 1, -1
        elif old["row_id"].startswith("current_"):
            generator, component = old["row_id"][8:].rsplit("_", 1)
            mu = COORDINATES.index(component)
            form = tuple(i for i in range(4) if i != mu)
            chain, p, component, coefficient = "primal", 3, _component(form), (-1) ** mu
        elif old["row_id"].startswith("div_"):
            generator, chain, p, component, coefficient = old["row_id"][4:], "primal", 4, _component(tuple(range(4))), 1
        else:
            raise AssertionError(f"unknown current-cone row: {parts}")
        records.append({"old_row": old["index"], "old_row_id": old["row_id"], "new_row": index[(generator, chain, p, component)], "coefficient": coefficient})
    if len(records) != 50 or len({record["new_row"] for record in records}) != 50:
        raise AssertionError("current-cone embedding is not injective")
    return {
        "embedded_rows": 50,
        "row_layout_injective": True,
        "old_unary_subcomplex_preserved": False,
        "reason": "the new cotangent de Rham chain continues the formerly terminal rho_current rows into the added dual-two-form rows",
        "records": records,
    }


def exact_data() -> dict[str, Any]:
    rows = row_layout()
    ranks = [sum(row["degree"] == degree for row in rows) for degree in range(-2, 4)]
    if len(rows) != 160 or ranks != [5, 25, 50, 50, 25, 5]:
        raise AssertionError("de Rham cotangent carrier rank changed")
    if any(rows[row["dual_row"]]["dual_row"] != row["index"] for row in rows):
        raise AssertionError("row duality is not involutive")
    pairing = [{"left_row": row["index"], "right_row": row["dual_row"], "coefficient": row["pairing_coefficient"]} for row in rows]
    terms = unary_terms(rows)
    return {"rows": rows, "degree_ranks": ranks, "embedding": embedding(rows), "pairing": pairing, "unary_terms": terms, "symbol": symbol_checks()}


def _generated(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-relative-five-current-de-rham-layout-v1",
        "result_id": f"{RESULT_ID}_LAYOUT",
        "row_count": 160,
        "degree_ranks_minus2_to3": data["degree_ranks"],
        "rows": data["rows"],
        "odd_pairing": data["pairing"],
        "unary_terms": data["unary_terms"],
        "current_cone_row_embedding": data["embedding"],
    }


def build() -> dict[str, Any]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not dependencies["cyclic_current_cone"]["classification"]["finite_order_support_local"]:
        raise AssertionError("local current cone unavailable")
    if not dependencies["global_charge_replay"]["classification"]["all_four_complete_standard_blocks_replayed"]:
        raise AssertionError("five-charge replay unavailable")
    if dependencies["candidate13_derived_source"]["derived_source_pullback"]["CAUSAL_RETARDED"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 causal category unexpectedly promoted")
    data = exact_data()
    generated = _generated(data)
    generated_hash = hashlib.sha256((json.dumps(generated, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    return {
        "schema": "pure-weyl-relative-five-current-de-rham-carrier-v1",
        "result_id": RESULT_ID,
        "result_state": "SUPPORT_LOCAL_CYCLIC_DERIVED_SOURCE_CARRIER_SELECTED_Q2_AND_CAUSAL_OPEN",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product, including the candidate-13 circumference",
            "boundaries": "M=R_t x closed oriented S1_L x S2 with fixed magnetic bundle P_N, N=2",
            "charge_sector": "five connected stabilizers H,P_x,J_1,J_2,J_3",
            "carrier": "five copies of the shifted de Rham current-resolution and its cyclic cotangent completion",
            "degree": "-2 through 3 with ranks (5,25,50,50,25,5)",
            "parity": "odd cotangent pairing; both physical parities feed the current operation",
            "ell": "not harmonic-reduced", "m": "not harmonic-reduced", "k": "not harmonic-reduced", "omega": "not harmonic-reduced",
        },
        "dependencies": {name: _artifact(path, dependencies[name]) for name, path in DEPENDENCIES.items()},
        "carrier": {
            "row_count": 160,
            "degree_ranks_minus2_to3": data["degree_ranks"],
            "per_generator_primal_chain": "Omega^0[-2] -> Omega^1[-1] -> Omega^2[0] -> Omega^3[1] -> Omega^4[2]",
            "per_generator_cotangent_chain": "Omega^0[-1] -> Omega^1[0] -> Omega^2[1] -> Omega^3[2] -> Omega^4[3]",
            "unary_operator": "horizontal exterior derivative on both chains, with the coordinate-density signs fixed by the wedge pairing",
            "current_equation": "d_H B_X + j_X(u,u)/2 = 0 in the Omega^3[1] row",
            "support_local": True,
            "uses_mode_projector": False,
            "uses_differential_inverse": False,
            "existing_current_cone_row_embedding": {"embedded_rows": 50, "added_rows": 110, "injective": True, "unary_subcomplex": False},
        },
        "symbol_certificate": data["symbol"],
        "topological_equivalence": {
            "homotopy_type": "R x S1 x S2 deformation-retracts onto S1 x S2",
            "third_de_rham_cohomology": "H^3(M;R)=R generated by the oriented Cauchy volume class",
            "criterion": "for a horizontally closed three-current j_X, a global two-form B_X with d_H B_X=-j_X exists iff integral_S1xS2 j_X=0",
            "five_copy_consequence": "the five local potential equations present the simultaneous zero locus of H,P_x,J_1,J_2,J_3 without a global charge projector",
            "noncontractible_content": "the de Rham endpoint classes are retained; no support-local splitting of them is asserted",
        },
        "candidate13_disposition": {
            "bounded_pullback": "remains the certified REDUCED-MODE origin-only result; boundedness is not encoded by this local carrier",
            "smooth_pullback": "its five-current zero condition has this support-local derived presentation; the selected eighteen resonance receivers are not imported",
            "causal_retarded": "OPEN; requires the full augmented q2 identities and Green homotopy",
            "direct_mode_receiver_upgrade": "remains obstructed",
        },
        "generated_layout": {"path": str(GENERATED.relative_to(ROOT)), "sha256": generated_hash},
        "classification": {
            "support_local_de_rham_carrier_selected": True,
            "unary_square_zero_exact": True,
            "unary_cyclicity_exact": True,
            "nonzero_symbol_koszul_complex_exact": True,
            "existing_five_current_cone_row_layout_embeds": True,
            "existing_five_current_cone_unary_subcomplex_embeds": False,
            "five_charge_zero_locus_presented_without_projectors": True,
            "full_augmented_q2_identity_certified": False,
            "causal_green_homotopy_certified": False,
            "relative_arity_two_morphism_repaired": False,
            "candidate13_causal_crosswalk_certified": False,
            "arity_three_authorized": False,
            "quantum_claim": False,
        },
        "next_gate": "EXTEND_THE_ACTION_DERIVED_CURRENT_Q2_TO_THE_160_ROW_CARRIER_AND_VERIFY_THE_COMPLETE_ARITY_TWO_IDENTITY",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_five_current_de_rham_carrier --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_five_current_de_rham_carrier",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_five_current_de_rham_carrier",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-five-current-de-rham-carrier-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem selects a 160-row support-local cyclic de Rham/cotangent carrier whose two-form potential equation represents vanishing of the five global stabilizer charges without Fourier or harmonic projectors. It certifies the unary complex, symbol exactness away from the zero covector, the injective row-layout embedding of the existing 50 current-cone rows and the ordinary de Rham topological criterion. The old 50-row unary complex is not a subcomplex because the new cotangent resolution continues its terminal dual-current rows. The theorem does not yet extend or replay the full q2 operations, construct a relative f2, impose bounded quasiperiodicity, solve the eighteen candidate-13 resonance rows, construct Green homotopies, or imply arity-three, observable, particle or quantum claims.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return """# Five-current de Rham derived-source carrier

The global five-charge receiver now has a projector-free local carrier.  For
each connected stabilizer `X`, adjoin the shifted de Rham chain

```text
Omega0[-2] -> Omega1[-1] -> Omega2[0] -> Omega3[1] -> Omega4[2]
```

and its cyclic cotangent chain.  The five-copy carrier has 160 rows and degree
ranks `(5,25,50,50,25,5)`.  The previously certified 50 current/divergence
and dual row labels embed injectively; 110 potential, reducibility and
cotangent rows are new.  This is a row-layout embedding, not a unary-subcomplex
embedding: the new cotangent chain continues the old terminal dual-current
rows.  Every unary map is a finite-order exterior derivative, so the
carrier is support-local and uses no spectral projector or differential
inverse.

The middle Maurer--Cartan row is `d_H B_X+j_X/2=0`.  Since
`R x S1 x S2` retracts onto the closed oriented Cauchy surface and its third
de Rham cohomology is one-dimensional, a closed current admits such a global
two-form potential exactly when its Cauchy charge vanishes.  This is the local
derived presentation that the constant five-charge fibre itself could not
provide.

This certificate selects and verifies the unary carrier only.  The complete
action-derived `q2` extension, its cyclic adjoints, the relative morphism and
the causal Green homotopy remain fail-closed.  Candidate-13's bounded result
remains origin-only and reduced-mode; the eighteen spectral resonance rows
are not reinterpreted as local equations.
"""


def write() -> None:
    value = build()
    data = exact_data()
    GENERATED.parent.mkdir(parents=True, exist_ok=True)
    GENERATED.write_text(_render(_generated(data)))
    OUTPUT.write_text(_render(value))
    REPORT.write_text(_report())


def check() -> None:
    value = build()
    if _load(OUTPUT) != value:
        raise AssertionError("five-current de Rham carrier drifted")
    validate(value)
    generated = _generated(exact_data())
    if _load(GENERATED) != generated:
        raise AssertionError("generated de Rham layout drifted")


def guards() -> None:
    schema = _load(SCHEMA)
    for key in ("full_augmented_q2_identity_certified", "causal_green_homotopy_certified", "candidate13_causal_crosswalk_certified", "arity_three_authorized", "quantum_claim"):
        bad = build()
        bad["classification"][key] = True
        try:
            Draft202012Validator(schema).validate(bad)
        except Exception:
            continue
        raise AssertionError(f"schema accepted forbidden promotion: {key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check:
        check()
    if args.guards:
        guards()
    if not (args.write or args.check or args.guards):
        print(_render(build()), end="")
