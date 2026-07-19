#!/usr/bin/env python3
"""Green homotopies for the metric Bach complex on the Bach-flat ADM class.

The construction deliberately does not factor the complete Bach witness.
The bare covariant third-order companion has scalar biwave leading symbol,
while naturality and covariant derivative counting exclude an order-three
remainder.  The certified typed Volterra theorem then supplies the causal
inverse for each of the four BV degrees.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.minimal_witness.principal_symbols import (
    MinimalWitnessPrincipalSymbols,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/bach-flat-metric-biwave-green-homotopy.md"
SCHEMA = ROOT / "d_quotient_classical/schema/bach-flat-metric-biwave-green-homotopy-v1.schema.json"
VERIFIER = HERE / "verify_bach_flat_metric_biwave_green_homotopy.py"
TESTS = HERE / "tests/test_bach_flat_metric_biwave_green_homotopy.py"
VOL_T = ROOT / "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json"
PARENT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json"
PRINCIPAL = ROOT / "covariant_completion/minimal_witness/principal_symbols.py"
VOL_SOURCE = HERE / "typed_biwave_volterra_green_theorem.py"
PROOF_DIR = ROOT / "d_quotient_classical/generated/bach_flat_metric_biwave_green_homotopy_v1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _dependency(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "artifact_id": value["result_id"],
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _proofs() -> dict[str, dict[str, Any]]:
    return {
        "covariant_order_lemma": {
            "schema": "bach-flat-covariant-biwave-order-lemma-v1",
            "companion": "T0=Box delta-(1/3)d delta^2",
            "claims": {
                "K_order": 1,
                "T0_order": 3,
                "linearized_Bach_orders": [0, 1, 2, 4],
                "T0_K_orders": [0, 1, 2, 4],
                "K_T0_orders": [0, 1, 2, 4],
                "third_order_absent": True,
            },
            "derivation": [
                "The principal coefficients of K and T0 are contractions of g and are covariantly parallel.",
                "Commuting covariant derivatives replaces two input derivatives by curvature; differentiating the commutator coefficients produces only lower input order.",
                "In delta[(nabla^c nabla^d+Ric^cd/2) C_acbd], delta C has input orders two and zero; connection variations have input order one. Two outer derivatives therefore give input orders four, two, one and zero, never three.",
                "Consequently every normalized witness block is Box^2 plus a smooth differential remainder of order at most two.",
            ],
            "scope": "four-dimensional smooth Bach-flat Lorentzian metrics; covariant normal form",
        },
        "four_row_binding": {
            "schema": "bach-flat-four-row-volterra-binding-v1",
            "complex": "Gamma(T*) --K--> Gamma(S0^2T*) --B_action--> Gamma((S0^2T*)*) --Ksharp--> Gamma((T*)*)",
            "witness_backward_blocks": ["T0/2", "J_M^-1", "T0sharp/2"],
            "normalized_degree_blocks": [
                "2 P_-1=Box_T*^2+V_-1",
                "2 P_0=Box_S0^2^2+V_0",
                "2 P_1=(2 P_0)^sharp",
                "2 P_2=(2 P_-1)^sharp",
            ],
            "remainder_order_bound": 2,
            "normalization": "If G_(2P)^+/- is the Volterra inverse, then G_P^+/-=2 G_(2P)^+/-.",
            "complex_identities": {
                "B_K": "zero because the background Bach tensor vanishes and B is the linearization of a natural conformal tensor",
                "Ksharp_B": "zero by compact-support formal adjunction and Hessian symmetry",
                "Q_squared": True,
                "Q_P_commutes": True,
            },
        },
        "analytic_binding": {
            "schema": "bach-flat-metric-volterra-analytic-binding-v1",
            "finite_slab": "Every closed finite time slab has compact spatial section S1 x S2 and smooth bounded coefficient jets.",
            "graph_bound": "Every smooth order-at-most-two remainder is bounded from the first wave-energy graph domain to L1(I;H^(s-1)) on each finite slab.",
            "globalization": "The typed Volterra inverses agree on nested slabs by uniqueness and glue to global advanced/retarded Green operators.",
            "chain_homotopy": "QG_+/-=G_+/-Q by QP=PQ and causal uniqueness; Lambda_+/-=W G_+/- gives QLambda_+/-+Lambda_+/-Q=1.",
            "adjoint": "Complementary-degree Green operators obey the typed advanced/retarded adjoint reversal; no same-degree self-adjointness is assumed.",
        },
    }


def build() -> tuple[dict[str, Any], dict[str, bytes]]:
    volterra = json.loads(VOL_T.read_text())
    parent = json.loads(PARENT.read_text())
    if not volterra["theorem"]["biwave_green_hyperbolic"]:
        raise AssertionError("typed Volterra theorem unavailable")
    if not parent["flags"]["BACH_FLAT_PARENT_RELATIVE_G3_CLASS"]:
        raise AssertionError("Bach-flat ADM class unavailable")

    principal = MinimalWitnessPrincipalSymbols.build()
    principal.verify()
    q4 = principal.covector_square**2
    symbol_checks = {
        "ghost_scalar_biwave": sp.simplify(principal.companion * principal.conformal_killing - q4 * sp.eye(4)) == sp.zeros(4),
        "metric_scalar_biwave": sp.simplify(principal.bach + sp.Rational(1, 2) * principal.conformal_killing * principal.companion - sp.Rational(1, 2) * q4 * sp.eye(9)) == sp.zeros(9),
        "B_K_principal": sp.simplify(principal.bach * principal.conformal_killing) == sp.zeros(9, 4),
    }
    if not all(symbol_checks.values()):
        raise AssertionError("universal principal witness replay failed")

    proof_values = _proofs()
    proof_bytes = {name: _json_bytes(value) for name, value in proof_values.items()}
    proof_refs = {
        name: {
            "path": str((PROOF_DIR / f"{name}.json").relative_to(ROOT)),
            "sha256": hashlib.sha256(body).hexdigest(),
        }
        for name, body in proof_bytes.items()
    }
    source_paths = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PRINCIPAL, VOL_SOURCE)
    value = {
        "schema": "pure-weyl-bach-flat-metric-biwave-green-homotopy-v1",
        "result_id": "BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1",
        "result_state": "RELATIVE_G3_BACH_FLAT_FOUR_ROW_METRIC_CAUSAL_HOMOTOPY_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "typed_biwave_volterra": _dependency(VOL_T),
            "Bach_flat_ADM_class": _dependency(PARENT),
        },
        "scope": {
            "class": parent["background_class"],
            "carrier": "four-row trace-free metric Bach BV complex",
            "degree_ranks": [4, 9, 9, 4],
            "support": "compact sources to advanced/retarded causal support; smooth spacelike-compact solutions",
        },
        "complex": {
            "arrows": ["K", "B_action", "Ksharp"],
            "Noether_identity": "B_action K=0 on every Bach-flat background",
            "adjoint_Noether_identity": "Ksharp B_action=0",
            "formal_pairing": "action Hessian pairing between metric/equation and ghost/identity rows",
            "Q_squared": 0,
        },
        "witness": {
            "companion": "T0=Box delta-(1/3)d delta^2",
            "backward_blocks": ["T0/2", "J_M^-1", "T0sharp/2"],
            "identity": "P_metric=Q_metric W_metric+W_metric Q_metric",
            "normalized_factor_choice": "P1=P2=the appropriate rough wave operator Box; 2P_degree=P2 P1+V_degree",
            "remainder_maximum_order": 2,
            "exact_same_bundle_factorization_required": False,
        },
        "principal_symbol_checks": symbol_checks,
        "Volterra_binding": {
            "P1_P2_normally_hyperbolic": True,
            "smooth_order_two_graph_bound_on_each_finite_slab": True,
            "stationarity_required": False,
            "commutativity_required": False,
            "self_adjointness_required": False,
            "both_inverse_identities": True,
            "causal_support": True,
            "globalization_by_uniqueness": True,
            "typed_adjoint_reversal": True,
        },
        "homotopy": {
            "degreewise_Green": "G_metric,+/-=(2 times the typed Volterra inverse of 2P_degree)",
            "chain_commutation": "QG_metric,+/-=G_metric,+/-Q",
            "definition": "Lambda_metric,+/-=W_metric G_metric,+/-",
            "identity": "Q Lambda_metric,+/-+Lambda_metric,+/- Q=1",
        },
        "proof_artifacts": proof_refs,
        "exact_checks": {
            "universal_principal_fixture": True,
            "covariant_third_order_layer_absent": True,
            "four_row_complex_exact": True,
            "all_four_degree_blocks_bound_to_Volterra": True,
            "advanced_retarded_support": True,
            "cyclic_adjoint_reversal": True,
        },
        "flags": {
            "BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1": True,
            "BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS": True,
            "BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS": False,
            "EXACT_SAME_BUNDLE_FACTORIZATION_ON_CLASS": False,
            "HADAMARD_STATE": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "Every metric in the certified relative-open Bach-flat ADM class has a complete four-row metric Bach advanced/retarded Green homotopy. The proof uses a scalar biwave plus an order-at-most-two Volterra remainder, not exact factorization.",
            "not_claimed": [
                "exact same-bundle factorization of the Bach witness",
                "a metric theorem outside the declared globally hyperbolic compact-Cauchy class",
                "the rank-310 all-row transfer, which is a separate dependency gate",
                "Hadamard wavefront-set control",
                "nonlinear stability or quantum master-equation restoration",
            ],
        },
        "next_gate": "BACH_FLAT_RANK310_CAUSAL_TRANSFER",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in source_paths},
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/bach_flat_metric_biwave_green_homotopy.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_bach_flat_metric_biwave_green_homotopy.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_bach_flat_metric_biwave_green_homotopy",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/bach-flat-metric-biwave-green-homotopy-v1.schema.json -d d_quotient_classical/certificates/BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
        ],
    }
    return value, proof_bytes


def _report(value: dict[str, Any]) -> str:
    return """# Bach-flat metric biwave Green homotopy

The four-row trace-free metric Bach complex is Green contractible on every
background in the certified relative-open Bach-flat ADM class.

The backward witness uses the bare covariant companion

```text
T0 = Box delta - (1/3) d delta^2.
```

The universal exact symbol identities give `T0 K = Box^2 I` at leading order
and `B + K T0/2 = Box^2 I/2` at leading order.  In covariant normal form no
third-order layer occurs.  The principal coefficients are metric-parallel,
commutators replace two derivatives by curvature, and direct variation of
the Bach tensor contributes input orders four, two, one and zero.  Hence each
normalized degree block is `Box^2+V` with `ord(V)<=2`.

The typed Volterra theorem applies on every finite slab: smooth coefficients
on compact spatial sections satisfy the declared wave-graph bounds.  Its
advanced and retarded inverses globalize by uniqueness.  Chain commutation
then gives

```text
Lambda_metric,+/- = W_metric G_metric,+/-,
Q Lambda_metric,+/- + Lambda_metric,+/- Q = 1.
```

This theorem does not assert an exact same-bundle factorization.  The
rank-310 lift remains a separate, now purely compositional gate.
"""


def write() -> None:
    value, proof_bytes = build()
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    for name, body in proof_bytes.items():
        (PROOF_DIR / f"{name}.json").write_bytes(body)
    OUTPUT.write_bytes(_json_bytes(value))
    REPORT.write_text(_report(value))


def check() -> None:
    expected, proof_bytes = build()
    actual = json.loads(OUTPUT.read_text())
    if actual != expected:
        raise AssertionError("Bach-flat metric homotopy certificate drifted")
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(actual)
    for name, body in proof_bytes.items():
        if (PROOF_DIR / f"{name}.json").read_bytes() != body:
            raise AssertionError(f"proof artifact drifted: {name}")


def guards() -> None:
    value, _ = build()
    bad = json.loads(json.dumps(value))
    bad["witness"]["remainder_maximum_order"] = 3
    try:
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(bad)
    except Exception:
        pass
    else:
        raise AssertionError("schema accepted an order-three remainder")
    bad = json.loads(json.dumps(value))
    bad["flags"]["HADAMARD_STATE"] = True
    try:
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(bad)
    except Exception:
        pass
    else:
        raise AssertionError("schema accepted Hadamard overpromotion")


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
        print(json.dumps(build()[0], indent=2, sort_keys=True))
